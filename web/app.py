#!/usr/bin/env python3
"""Private dashboard for the trading engine.

  python web/app.py                      # 127.0.0.1:5000, token printed on start
  DASHBOARD_TOKEN=... python web/app.py  # fixed token

Binds to localhost by default, so only processes on this machine can reach it.
Exposing it beyond localhost needs --host and is a deliberate, warned-about act.
"""
import argparse
import hmac
import os
import secrets
import sys
import time
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data                                                    # noqa: E402
from quant.backtest import buy_and_hold, metrics                          # noqa: E402
from quant.live import read_state                                         # noqa: E402
from quant.risk import cost_drag, live_cost_report                        # noqa: E402
from quant.strategies import REGISTRY                                     # noqa: E402
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward  # noqa: E402

app = Flask(__name__)
app.secret_key = os.environ.get("DASHBOARD_SECRET") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=86400,
    # Templates are cached when debug is off; this is a local tool you will edit,
    # so pick up changes on refresh instead of needing a restart.
    TEMPLATES_AUTO_RELOAD=True,
)

TOKEN = os.environ.get("DASHBOARD_TOKEN") or secrets.token_urlsafe(32)


@app.after_request
def _harden(response):
    """Defence in depth. Cheap, and this app can be bound beyond localhost.

    SameSite=Lax already keeps the session cookie out of cross-site frames, so
    these are a second layer rather than the only one — but the page shows
    positions and can place orders, and a header costs nothing.
    """
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Content-Security-Policy",
        # Fonts are the only third party. Everything else is same-origin, and
        # nothing may frame this page or post form data elsewhere.
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'none'"
    )
    return response


def require_auth(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("authed"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("login"))
        return view(*a, **kw)
    return wrapped


FAVICON = (
    b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'>"
    b"<text y='14' font-size='14'>&#128200;</text></svg>"
)


@app.route("/favicon.ico")
def favicon():
    return FAVICON, 200, {"Content-Type": "image/svg+xml", "Cache-Control": "max-age=86400"}


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        # compare_digest: constant time, so a wrong token leaks no timing signal
        if hmac.compare_digest(request.form.get("token", ""), TOKEN):
            session["authed"] = True
            session.permanent = True
            return redirect(url_for("index"))
        time.sleep(1.0)   # ponytail: crude throttle; a 256-bit token needs no more
        error = "Invalid token."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@require_auth
def index():
    return render_template("index.html", strategies=sorted(REGISTRY))


@app.route("/api/state")
@require_auth
def api_state():
    state = read_state()
    if state is None:
        return jsonify({"running": False, "message": "No trader has run yet. Start trade.py."})
    if state.get("unreadable"):
        # Never render this as "no position" — that reads as flat when it is unknown.
        return jsonify({"running": False, "unreadable": True,
                        "message": f"Cannot read {state['state_file']}. The file exists but is "
                                   "corrupt — check the trader process before assuming you are flat."}), 503
    stale = (time.time() - Path("data/live_state.json").stat().st_mtime) > 7200
    return jsonify({"running": True, "stale": stale, **state})


@app.route("/api/costs")
@require_auth
def api_costs():
    """What this run is paying to trade, versus what it would pay trading less."""
    state = read_state()
    if state is None or state.get("unreadable"):
        return jsonify({"running": False})

    report = live_cost_report(state.get("trades", []), state.get("equity") or 0.0)
    pace = report.get("round_trips_per_year")
    return jsonify({
        "running": True,
        **report,
        "reference": [
            {"label": "monthly", "round_trips": 12, "drag": cost_drag(12)},
            {"label": "weekly", "round_trips": 52, "drag": cost_drag(52)},
            {"label": "daily", "round_trips": 250, "drag": cost_drag(250)},
        ],
        "pace_drag": cost_drag(pace) if pace else None,
    })


@app.route("/api/backtest")
@require_auth
def api_backtest():
    """Walk-forward a strategy and return the honest verdict."""
    strategy = request.args.get("strategy", "sma_cross")
    if strategy not in REGISTRY:
        return jsonify({"error": f"unknown strategy {strategy}"}), 400

    csv_path = request.args.get("csv")
    try:
        if csv_path:
            safe = Path(csv_path).resolve()
            # Path containment check: the browser must not read arbitrary files.
            if not safe.is_relative_to(Path.cwd()) or not safe.exists():
                return jsonify({"error": "csv must be an existing file under the project directory"}), 400
            try:
                close, label = data.load_csv(safe)["close"], safe.name
            except ValueError as exc:
                # load_csv names the absolute path and quotes the columns it
                # found, which reflects file contents and deployment layout back
                # to the caller. Log that; return only what the user can act on.
                app.logger.warning("rejected %s: %s", safe, exc)
                return jsonify({"error": f"{safe.name} is not usable OHLCV data — "
                                         "it needs a date column and a close column."}), 400
        else:
            seed = int(request.args.get("seed", 0))
            close, label = data.synthetic(seed=seed)["close"], f"synthetic (seed {seed})"

        fn, grid = REGISTRY[strategy]
        oos, folds, benchmark, n_trials = walk_forward(close, fn, grid, n_folds=5)
        p_raw, edge = block_bootstrap_pvalue(oos, benchmark, n_boot=4000)
        p_deflated = deflate(p_raw, n_trials)

        strat_m = metrics(oos)
        hold_m = metrics(benchmark)
        equity = (1 + oos).cumprod()

        return jsonify({
            "strategy": strategy,
            "dataset": label,
            "strategy_metrics": strat_m,
            "benchmark_metrics": hold_m,
            "full_hold": metrics(buy_and_hold(close)["net_return"]),
            "p_raw": p_raw,
            "p_deflated": p_deflated,
            "n_trials": n_trials,
            "daily_edge": edge,
            "passed": bool(p_deflated < 0.05 and strat_m["sharpe"] > hold_m["sharpe"]),
            "folds": folds.to_dict("records"),
            "equity_curve": [round(v, 4) for v in equity.tolist()],
            "benchmark_curve": [round(v, 4) for v in (1 + benchmark).cumprod().tolist()],
        })
    except (pd.errors.ParserError, UnicodeDecodeError):
        # ParserError subclasses ValueError, so it must be caught first or the
        # handler below returns pandas' internals to the browser verbatim.
        app.logger.warning("unparseable CSV: %s", csv_path)
        return jsonify({"error": "Could not parse that file as CSV. It needs a "
                                 "date column and a close column."}), 400
    except (ValueError, FileNotFoundError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        # A malformed CSV raises parser internals that mean nothing to a reader
        # and describe our stack to anyone who reaches this endpoint.
        app.logger.exception("backtest failed for %s", csv_path or "synthetic")
        return jsonify({"error": "Could not read that file as OHLCV data. "
                                 "It needs a date column and a close column."}), 400


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()

    if args.host not in ("127.0.0.1", "localhost"):
        # Off loopback the token crosses a network. Mark the cookie Secure so a
        # browser refuses to send it over plain HTTP at all — better a session
        # that will not work than one that leaks in transit.
        app.config["SESSION_COOKIE_SECURE"] = True
        print("\n  !! Binding beyond localhost. Anyone who can reach this host and")
        print("     guess the token can see your positions. Use a tunnel or VPN,")
        print("     not a public bind, and never without HTTPS.")
        print("     The session cookie is now marked Secure, so sign-in will fail")
        print("     over plain HTTP by design.\n")

    print(f"\n  Dashboard   http://{args.host}:{args.port}")
    if not os.environ.get("DASHBOARD_TOKEN"):
        print(f"  Token       {TOKEN}")
        print("  (generated for this run — set DASHBOARD_TOKEN to keep it stable)\n")
    else:
        print("  Token       from DASHBOARD_TOKEN\n")

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
