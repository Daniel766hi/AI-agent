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
import re
import secrets
import sys
import threading
import time
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data                                                    # noqa: E402
from quant.backtest import buy_and_hold, metrics                          # noqa: E402
from quant.live import read_state                                         # noqa: E402
from quant.agents import Desk, Proposal                                   # noqa: E402
from quant.risk import (breakeven, cost_drag, kelly_fraction,             # noqa: E402
                        leverage_table, live_cost_report)
from quant.backtest import backtest                                       # noqa: E402
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


# ---------------------------------------------------------------- screening
# A screen over real coins is minutes of network, far past any request timeout,
# so it runs in a thread and the page polls. One process, one user: a dict is
# the right registry, not a queue.
_JOBS = {}
_JOBS_LOCK = threading.Lock()
MAX_JOBS_KEPT = 8


def _start_job(kind, worker, *args):
    """Run `worker(note, *args)` in a thread, tracked in the shared registry.

    Three long operations now need this — screening, connectivity checks, and
    fetching — so it lives in one place. `note` is the only way a worker reports
    progress, and it tolerates a job that has been evicted: losing a status line
    is survivable, losing the thread that produces the result is not.
    """
    with _JOBS_LOCK:
        for existing, job in _JOBS.items():
            if job["kind"] == kind and job["stage"] not in ("done", "failed"):
                return existing, True

        finished = [j for j in _JOBS if _JOBS[j]["stage"] in ("done", "failed")]
        for stale in sorted(finished, key=lambda j: _JOBS[j]["started"])[:-MAX_JOBS_KEPT]:
            _JOBS.pop(stale, None)

        job_id = secrets.token_urlsafe(8)
        _JOBS[job_id] = {"kind": kind, "stage": "queued", "started": time.time()}

    def note(**fields):
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.update(fields)

    def run():
        try:
            worker(note, *args)
        except Exception as exc:
            app.logger.exception("%s job failed", kind)
            note(stage="failed", error=f"{type(exc).__name__}: {exc}")

    threading.Thread(target=run, daemon=True).start()
    return job_id, False


# Symbols reach a URL, so they are constrained to what a ticker can contain.
SYMBOL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,23}$")


def _short_reason(exc):
    """One readable line, not a urllib3 stack dump.

    Four sources failing the same way produced four near-identical 240-character
    blocks on a screen whose only job is saying what is wrong. Keep the cause
    and drop the retry chatter and the echoed URL.
    """
    text = str(exc)
    if "Tunnel connection failed" in text or "ProxyError" in text:
        host = re.search(r"host='([^']+)'", text)
        return (f"No outbound connection to {host.group(1) if host else 'the host'} — "
                "a proxy or firewall refused it.")
    if "NameResolution" in text or "Name or service not known" in text:
        return "DNS could not resolve the host. Check the network."
    if "timed out" in text.lower():
        return "The request timed out."
    # Our own DataError messages are already written for a reader; keep them.
    return text.split(" (Caused by")[0][:200]


def _check_sources(note):
    """Probe each data source the way datacheck.py does, reporting as it goes."""
    probes = [
        ("Binance", "BTCUSDT daily",
         lambda: data.fetch_binance("BTCUSDT", "1d", start="2024-06-01", cache_dir=None)),
        ("CoinGecko", "bitcoin, 90 days",
         lambda: data.fetch_coingecko("bitcoin", days=90, cache_dir=None)),
        ("Yahoo crypto", "BTC-USD 1y",
         lambda: data.fetch_yahoo("BTC-USD", range_="1y", cache_dir=None)),
        ("Yahoo IDX", "BBCA.JK 1y",
         lambda: data.fetch_yahoo("BBCA.JK", range_="1y", cache_dir=None)),
    ]
    results = []
    note(stage="checking", total=len(probes), results=results)
    for name, description, call in probes:
        try:
            frame = call()
            close = frame["close"]
            results.append({"source": name, "ok": True, "detail": description,
                            "rows": len(close), "first": str(close.index[0].date()),
                            "last": str(close.index[-1].date()),
                            "latest": round(float(close.iloc[-1]), 4)})
        except Exception as exc:
            results.append({"source": name, "ok": False, "detail": description,
                            "error": _short_reason(exc)})
        note(results=list(results), done=len(results))
    note(stage="done", results=results,
         working=sum(r["ok"] for r in results), total=len(probes))


def _fetch_symbols(note, source, symbols):
    """Fetch into data/ so the Screen and Research views can use real prices."""
    note(stage="fetching", total=len(symbols), done=0, results=[])
    results = []

    def progress(done, total, label, ok):
        note(done=done, total=total, current=label)

    if source == "yahoo":
        frames, failures = data.fetch_many_yahoo(symbols, on_progress=progress)
    else:
        frames, failures = data.fetch_many(symbols, on_progress=progress)

    for label, frame in frames:
        close = frame["close"]
        results.append({"symbol": label, "ok": True, "rows": len(close),
                        "first": str(close.index[0].date()), "last": str(close.index[-1].date())})
    for label, reason in failures.items():
        results.append({"symbol": label, "ok": False, "error": str(reason)[:240]})

    note(stage="done", results=results, fetched=len(frames), failed=len(failures))


def _run_screen(job_id, strategy, universe, count, folds):
    from screen import evaluate_all

    TERMINAL = ("done", "failed")

    def note(**fields):
        """Record progress, tolerating a job that has been evicted.

        Eviction used to race a running job: the thread would KeyError here,
        and so would the handler meant to record the failure. Losing a status
        update is survivable; taking down the thread that produces the result
        is not.
        """
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.update(fields)

    try:
        note(stage="loading")
        if universe == "synthetic":
            assets = [(f"noise_{i:03d}", data.synthetic(n=1200, seed=5000 + i)["close"])
                      for i in range(count)]
        elif universe == "cached":
            paths = sorted(Path("data").glob("*.csv"))
            assets = []
            for path in paths[:count]:
                try:
                    assets.append((path.stem, data.load_csv(path)["close"]))
                except ValueError:
                    continue          # a non-OHLCV CSV in data/ is not an error
        else:
            note(stage="failed", error=f"unknown universe {universe!r}")
            return

        if not assets:
            note(stage="failed",
                 error="No usable assets. For 'cached', fetch some first: python datacheck.py --save")
            return

        note(stage="evaluating", total=len(assets))
        outcomes = evaluate_all(assets, strategy, folds=folds)
        rows = [o for o in outcomes if o["ok"]]
        if not rows:
            note(stage="failed", error="No asset had enough history to validate.")
            return

        n_combos = rows[0]["n_combos"]
        total_trials = len(rows) * n_combos
        for row in rows:
            row["p_naive"] = deflate(row["p_raw"], n_combos)
            row["p_honest"] = deflate(row["p_raw"], total_trials)
        rows.sort(key=lambda r: r["p_raw"])

        note(stage="done", rows=rows, n_combos=n_combos, total_trials=total_trials,
             skipped=[{"asset": o["asset"], "error": o["error"]}
                      for o in outcomes if not o["ok"]],
             naive_hits=sum(r["p_naive"] < 0.05 for r in rows),
             honest_hits=sum(r["p_honest"] < 0.05 for r in rows))
    except Exception as exc:
        app.logger.exception("screen job failed")
        note(stage="failed", error=f"{type(exc).__name__}: {exc}")


@app.route("/api/screen", methods=["POST"])
@require_auth
def api_screen_start():
    payload = request.get_json(silent=True) or {}
    strategy = payload.get("strategy", "breakout")
    if strategy not in REGISTRY:
        return jsonify({"error": f"unknown strategy {strategy}"}), 400

    universe = payload.get("universe", "synthetic")
    if universe not in ("synthetic", "cached"):
        return jsonify({"error": f"unknown universe {universe!r}"}), 400
    count = max(2, min(int(payload.get("count", 40)), 300))
    folds = max(2, min(int(payload.get("folds", 4)), 8))

    job_id = secrets.token_urlsafe(8)
    with _JOBS_LOCK:
        # One screen at a time. Each spawns a process pool, and several at once
        # oversubscribe the machine badly enough to slow all of them down. Hand
        # back the running job so the page attaches to it rather than queueing.
        for existing, job in _JOBS.items():
            if job.get("kind") == "screen" and job["stage"] not in ("done", "failed"):
                return jsonify({"job": existing, "already_running": True})

        # Only finished jobs may be evicted; a running one still needs its slot.
        finished = [j for j in _JOBS if _JOBS[j]["stage"] in ("done", "failed")]
        for stale in sorted(finished, key=lambda j: _JOBS[j]["started"])[:-MAX_JOBS_KEPT]:
            _JOBS.pop(stale, None)

        _JOBS[job_id] = {"kind": "screen", "stage": "queued", "started": time.time(),
                         "strategy": strategy, "universe": universe, "requested": count}

    threading.Thread(target=_run_screen, args=(job_id, strategy, universe, count, folds),
                     daemon=True).start()
    return jsonify({"job": job_id})


@app.route("/api/screen/<job_id>")
@require_auth
def api_screen_status(job_id):
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return jsonify({"error": "no such job"}), 404
        snapshot = dict(job)
    snapshot["elapsed"] = round(time.time() - snapshot["started"], 1)
    return jsonify(snapshot)


# -------------------------------------------------------------------- desk
# ---------------------------------------------------------------- data
@app.route("/api/data")
@require_auth
def api_data_status():
    """What is cached, and whether a key is configured. No network."""
    cached = []
    for path in sorted(Path("data").glob("*.csv")) if Path("data").exists() else []:
        try:
            close = data.load_csv(path)["close"]
        except (ValueError, OSError):
            continue           # a non-OHLCV CSV sitting in data/ is not an error
        cached.append({"file": path.name, "rows": len(close),
                       "first": str(close.index[0].date()), "last": str(close.index[-1].date())})
    return jsonify({
        "cached": cached,
        "coingecko_key": bool(os.environ.get("COINGECKO_API_KEY", "").strip()),
        "coingecko_plan": os.environ.get("COINGECKO_PLAN", "demo"),
    })


@app.route("/api/data/check", methods=["POST"])
@require_auth
def api_data_check():
    job_id, reused = _start_job("check", _check_sources)
    return jsonify({"job": job_id, "already_running": reused})


@app.route("/api/data/fetch", methods=["POST"])
@require_auth
def api_data_fetch():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "yahoo")
    if source not in ("yahoo", "coingecko"):
        return jsonify({"error": f"unknown source {source!r}"}), 400

    raw = payload.get("symbols") or []
    if isinstance(raw, str):
        raw = re.split(r"[\s,]+", raw)
    symbols = [sym.strip() for sym in raw if sym.strip()]

    bad = [sym for sym in symbols if not SYMBOL_RE.match(sym)]
    if bad:
        return jsonify({"error": f"not valid symbols: {', '.join(bad[:4])}"}), 400
    if not symbols:
        return jsonify({"error": "no symbols given"}), 400
    if len(symbols) > 60:
        return jsonify({"error": "at most 60 symbols per fetch"}), 400

    job_id, reused = _start_job("fetch", _fetch_symbols, source, symbols)
    return jsonify({"job": job_id, "already_running": reused})


@app.route("/api/job/<job_id>")
@require_auth
def api_job(job_id):
    """Status for any background job — screen, check or fetch."""
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return jsonify({"error": "no such job"}), 404
        snapshot = dict(job)
    snapshot["elapsed"] = round(time.time() - snapshot["started"], 1)
    return jsonify(snapshot)


@app.route("/api/desk")
@require_auth
def api_desk():
    """Put one proposal to the agents and return every verdict, not just the outcome."""
    strategy = request.args.get("strategy", "breakout")
    if strategy not in REGISTRY:
        return jsonify({"error": f"unknown strategy {strategy}"}), 400
    seed = int(request.args.get("seed", 0))
    universe = request.args.get("universe", "synthetic")

    close = (data.synthetic_regimes(seed=seed) if universe == "regimes"
             else data.synthetic(seed=seed))["close"]

    proposal = Proposal(symbol=request.args.get("symbol", "SYNTH"),
                        strategy=strategy, close=close)
    decision = Desk().evaluate(proposal)
    evidence = proposal.evidence

    return jsonify({
        "approved": decision.approved,
        "dataset": f"{universe} (seed {seed})",
        "params": proposal.params,
        "position": proposal.target_position,
        "verdicts": [{"agent": v.agent, "approved": v.approved, "reason": v.reason}
                     for v in decision.verdicts],
        "mandates": {a.name: a.mandate for a in Desk().agents},
        "p_deflated": evidence.get("p_deflated"),
        "n_trials": evidence.get("n_trials"),
    })


# ----------------------------------------------------------------- analysis
@app.route("/api/analyze")
@require_auth
def api_analyze():
    """Cost hurdle, leverage ruin and Kelly for a walk-forward fitted strategy."""
    strategy = request.args.get("strategy", "sma_cross")
    if strategy not in REGISTRY:
        return jsonify({"error": f"unknown strategy {strategy}"}), 400
    seed = int(request.args.get("seed", 0))

    close = data.synthetic(seed=seed)["close"]
    fn, grid = REGISTRY[strategy]
    try:
        _, folds, _, _ = walk_forward(close, fn, grid, n_folds=4)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    params = folds.iloc[-1]["params"]
    result = backtest(close, fn(close, **params))
    stats = breakeven(result)
    kelly = kelly_fraction(result["net_return"])
    table = leverage_table(result["net_return"], levels=(1, 2, 3, 5), n_sims=3000)

    return jsonify({
        "strategy": strategy, "params": params,
        "basis": "fitted out-of-sample on the last of 4 walk-forward folds",
        "round_trips": stats["round_trips_per_year"],
        "drag": stats["annual_cost_drag"],
        "time_in_market": stats["time_in_market"],
        "hurdle": stats["hurdle_vs_holding"],
        "kelly": kelly["kelly"], "half_kelly": kelly["half_kelly"],
        "annual_edge": kelly["annual_edge"],
        "reference": [{"label": l, "round_trips": n, "drag": cost_drag(n)}
                      for l, n in (("monthly", 12), ("weekly", 52), ("daily", 250), ("4x daily", 1000))],
        "leverage": table.to_dict("records"),
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
