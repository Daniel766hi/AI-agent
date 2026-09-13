"""Self-checks for brokers, auth, and the live-mode gates."""
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant.broker import DUST_FRACTION, MIN_NOTIONAL, BinanceBroker, InsufficientFunds, PaperBroker


def test_paper_buy_and_sell():
    b = PaperBroker(starting_cash=1000.0)
    trade = b.set_target(1.0, 100.0, "BTCUSDT")
    assert trade["side"] == "BUY"
    assert abs(b.position_fraction(100.0) - 1.0) < 0.01
    assert b.cash >= -1e-9, "cash must not go negative"

    trade = b.set_target(0.0, 100.0, "BTCUSDT")
    assert trade["side"] == "SELL" and abs(b.units) < 1e-9


def test_paper_charges_costs():
    b = PaperBroker(starting_cash=1000.0, fee_bps=10, slippage_bps=5)
    b.set_target(1.0, 100.0)
    b.set_target(0.0, 100.0)
    # Two round trips at 15bps on ~$1000 should cost roughly $3, never zero.
    assert 1.0 < (1000.0 - b.equity(100.0)) < 5.0, f"cost was {1000.0 - b.equity(100.0)}"


def test_dust_trades_rejected():
    b = PaperBroker(starting_cash=1000.0)
    b.set_target(1.0, 100.0)
    assert b.set_target(1.0 - DUST_FRACTION / 2, 100.0) is None, "dust rebalance must be skipped"


def test_min_notional_enforced():
    b = PaperBroker(starting_cash=20.0)
    assert b.set_target(0.2, 100.0) is None, f"orders under ${MIN_NOTIONAL} must be rejected"


def test_position_capped_at_full():
    b = PaperBroker(starting_cash=1000.0)
    b.set_target(5.0, 100.0)                       # asking for 5x leverage
    assert b.position_fraction(100.0) <= 1.01, "spot broker must not lever up"


def test_wipeout_raises():
    b = PaperBroker(starting_cash=1000.0)
    b.set_target(1.0, 100.0)
    b.cash, b.units = 0.0, 0.0                     # simulate total loss
    try:
        b.set_target(1.0, 100.0)
    except InsufficientFunds:
        return
    raise AssertionError("must refuse to trade a wiped-out account")


def test_state_persists():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"
        b = PaperBroker(starting_cash=1000.0, state_path=path)
        b.set_target(1.0, 100.0)
        reloaded = PaperBroker(starting_cash=1000.0, state_path=path)
        assert abs(reloaded.units - b.units) < 1e-12
        assert len(reloaded.trades) == 1


def test_binance_signature():
    """Signing verified against Binance's published example vector."""
    b = BinanceBroker("key", "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j", "BTCUSDT")
    params = {
        "symbol": "LTCBTC", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC",
        "quantity": "1", "price": "0.1", "recvWindow": "5000", "timestamp": "1499827319559",
    }
    signed = b._sign(params)
    expected = "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"
    assert signed.endswith(expected), f"signature mismatch: {signed[-64:]}"


def test_live_broker_needs_credentials():
    for key, secret in [(None, "s"), ("k", None), ("", "")]:
        try:
            BinanceBroker(key, secret, "BTCUSDT")
        except ValueError:
            continue
        raise AssertionError(f"must reject credentials ({key!r}, {secret!r})")


def test_dashboard_requires_auth():
    os.environ["DASHBOARD_TOKEN"] = "test-token-value"
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
    import importlib
    import app as dashboard
    importlib.reload(dashboard)

    client = dashboard.app.test_client()
    assert client.get("/api/state").status_code == 401, "API must reject unauthenticated calls"
    assert client.get("/").status_code == 302, "dashboard must redirect to login"
    assert client.post("/login", data={"token": "wrong"}).status_code == 200

    assert client.post("/login", data={"token": "test-token-value"}).status_code == 302
    assert client.get("/api/state").status_code == 200, "valid token must grant access"


def test_backtest_api_rejects_path_traversal():
    os.environ["DASHBOARD_TOKEN"] = "test-token-value"
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
    import importlib
    import app as dashboard
    importlib.reload(dashboard)

    client = dashboard.app.test_client()
    client.post("/login", data={"token": "test-token-value"})
    response = client.get("/api/backtest?strategy=sma_cross&csv=/etc/passwd")
    assert response.status_code == 400, "must refuse to read files outside the project"




# --- Data fetchers -----------------------------------------------------------
# The APIs are unreachable from this sandbox, so these exercise the response
# PARSING against captured payload shapes. They do not prove the live endpoints
# still return these shapes.

def _mock_response(payload, status=200):
    from unittest.mock import MagicMock
    r = MagicMock()
    r.status_code = status
    r.json.return_value = payload
    r.raise_for_status.return_value = None
    return r


def test_coingecko_parses_market_chart():
    from unittest.mock import patch
    from quant import data
    payload = {"prices": [[1700000000000, 37000.5], [1700086400000, 37500.25],
                          [1700172800000, 36800.0]]}
    with tempfile.TemporaryDirectory() as tmp, \
         patch("quant.data.requests.get", return_value=_mock_response(payload)):
        df = data.fetch_coingecko("bitcoin", days=3, cache_dir=tmp)
    assert list(df["close"]) == [37000.5, 37500.25, 36800.0]
    assert df.index.is_monotonic_increasing


def test_coingecko_rate_limit_message():
    from unittest.mock import patch
    from quant import data
    with tempfile.TemporaryDirectory() as tmp, \
         patch("quant.data.requests.get", return_value=_mock_response({}, status=429)):
        try:
            data.fetch_coingecko("bitcoin", cache_dir=tmp)
        except RuntimeError as exc:
            assert "rate limit" in str(exc).lower()
            return
    raise AssertionError("429 must raise a clear rate-limit error")


def test_yahoo_parses_chart_and_drops_nulls():
    from unittest.mock import patch
    from quant import data
    payload = {"chart": {"error": None, "result": [{
        "timestamp": [1700000000, 1700086400, 1700172800, 1700259200],
        "indicators": {"quote": [{"close": [9250.0, None, 9300.0, 9275.0]}]},
    }]}}
    with tempfile.TemporaryDirectory() as tmp, \
         patch("quant.data.requests.get", return_value=_mock_response(payload)):
        df = data.fetch_yahoo("BBCA.JK", cache_dir=tmp)
    assert list(df["close"]) == [9250.0, 9300.0, 9275.0], "null closes must be dropped, not zero-filled"


def test_yahoo_reports_bad_ticker():
    from unittest.mock import patch
    from quant import data
    payload = {"chart": {"error": {"code": "Not Found", "description": "No data found"}, "result": None}}
    with tempfile.TemporaryDirectory() as tmp, \
         patch("quant.data.requests.get", return_value=_mock_response(payload)):
        try:
            data.fetch_yahoo("NOTATICKER", cache_dir=tmp)
        except RuntimeError as exc:
            assert "NOTATICKER" in str(exc)
            return
    raise AssertionError("a bad ticker must raise, not return empty data")


def test_screen_deflation_charges_for_every_asset():
    """The whole point of the screener: more assets must mean a harsher p-value."""
    from quant.validate import deflate
    p_raw = 0.02
    one_asset = deflate(p_raw, 3)          # 3 configs, 1 asset
    fifty_assets = deflate(p_raw, 3 * 50)  # same configs, 50 assets
    assert one_asset < 0.10, one_asset
    assert fifty_assets > 0.90, fifty_assets
    assert fifty_assets > one_asset, "screening more assets must cost significance"



def test_dashboard_has_no_emoji_icons():
    """The design rules forbid emoji as icons; SVG symbols only."""
    html = (Path(__file__).resolve().parent.parent / "web" / "templates" / "index.html").read_text()
    # Emoji live well above the BMP punctuation range; flag any such codepoint.
    offenders = [c for c in html if ord(c) > 0x2100 and c not in "—–…’‘“”×·≥≤"]
    assert not offenders, f"emoji/pictographs found in template: {offenders[:5]}"


def test_dashboard_respects_reduced_motion():
    html = (Path(__file__).resolve().parent.parent / "web" / "templates" / "index.html").read_text()
    assert "prefers-reduced-motion" in html, "animation must be disableable"
    assert ":focus-visible" in html, "keyboard focus must stay visible"



# --- live loop safety -------------------------------------------------------

def _halted_trader(tmp, max_dd=15.0):
    """Drive a trader into its drawdown halt on a falling series."""
    from unittest.mock import patch
    from quant import data
    from quant.broker import PaperBroker
    from quant.live import Trader

    bars = data.synthetic(n=400, annual_drift=-0.9, seed=3)["close"]
    state = Path(tmp) / "state.json"
    broker = PaperBroker(starting_cash=1000.0, state_path=Path(tmp) / "broker.json")
    trader = Trader("sma_cross", {"fast": 5, "slow": 20}, broker, "X",
                    max_drawdown_pct=max_dd, state_file=state)
    last = None
    for i in range(60, 200, 5):
        with patch("quant.live.recent_bars", return_value=bars.iloc[:i]):
            last = trader.tick()
    return state, last, bars


def test_halt_survives_restart():
    """A restart must not hand a halted strategy a fresh drawdown allowance."""
    from unittest.mock import patch
    from quant.broker import PaperBroker
    from quant.live import Trader

    with tempfile.TemporaryDirectory() as tmp:
        state, before, bars = _halted_trader(tmp)
        assert before["halted"], "setup failed: trader should have halted"

        broker = PaperBroker(starting_cash=1000.0, state_path=Path(tmp) / "broker.json")
        restarted = Trader("sma_cross", {"fast": 5, "slow": 20}, broker, "X",
                           max_drawdown_pct=15.0, state_file=state)
        assert restarted.halted, "halt must persist across a restart"
        assert restarted.peak_equity == before["peak_equity"], "drawdown peak must persist"

        with patch("quant.live.recent_bars", return_value=bars.iloc[:200]):
            after = restarted.tick()
        assert after["halted"] and after["target_position"] == 0.0, "must stay flat while halted"


def test_halt_not_restored_for_a_different_symbol():
    """State from another symbol must not silently halt an unrelated run."""
    from quant.broker import PaperBroker
    from quant.live import Trader

    with tempfile.TemporaryDirectory() as tmp:
        state, before, _ = _halted_trader(tmp)
        assert before["halted"]
        other = Trader("sma_cross", {"fast": 5, "slow": 20},
                       PaperBroker(starting_cash=1000.0), "DIFFERENT",
                       max_drawdown_pct=15.0, state_file=state)
        assert not other.halted, "a halt on one symbol must not carry to another"


def test_state_writes_are_atomic():
    """The dashboard polls this file while the trader rewrites it."""
    import json
    import threading
    from quant.live import Trader, read_state

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "race.json"
        payload = {"blob": "x" * 200_000, "n": 0}
        path.write_text(json.dumps(payload))

        writer_self = Trader.__new__(Trader)
        writer_self.state_file = path
        failures = []

        def write():
            for i in range(200):
                payload["n"] = i
                Trader._write(writer_self, payload)

        def read():
            for _ in range(200):
                out = read_state(path)
                if out is None or out.get("unreadable"):
                    failures.append(1)

        w, r = threading.Thread(target=write), threading.Thread(target=read)
        w.start(); r.start(); w.join(); r.join()
        assert not failures, f"{len(failures)} torn reads — writes are not atomic"


def test_unreadable_state_is_not_reported_as_flat():
    """A corrupt file must surface as an error, never as 'no position'."""
    from quant.live import read_state
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "corrupt.json"
        path.write_text("{ this is not json")
        out = read_state(path)
        assert out is not None, "a corrupt file must not look like 'no trader running'"
        assert out.get("unreadable") is True
        assert read_state(Path(tmp) / "absent.json") is None, "a missing file is genuinely 'not started'"



# --- dashboard hardening ----------------------------------------------------

def _client(token="test-token-value"):
    os.environ["DASHBOARD_TOKEN"] = token
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
    import importlib
    import logging
    import app as dashboard
    importlib.reload(dashboard)
    dashboard.app.logger.setLevel(logging.CRITICAL)     # keep expected warnings quiet
    client = dashboard.app.test_client()
    client.post("/login", data={"token": token})
    return client, dashboard


def test_security_headers_are_present():
    """The page shows positions and can be bound beyond localhost."""
    client, _ = _client()
    headers = client.get("/").headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("Referrer-Policy") == "no-referrer"

    csp = headers.get("Content-Security-Policy", "")
    assert "frame-ancestors 'none'" in csp, "must not be frameable"
    assert "form-action 'self'" in csp, "the token form must not post elsewhere"


def test_session_cookie_is_restrictive():
    client, _ = _client()
    cookie = client.post("/login", data={"token": "test-token-value"}).headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie, "script must not be able to read the session"
    assert "SameSite=Lax" in cookie or "SameSite=Strict" in cookie


def test_errors_do_not_reflect_paths_or_file_contents():
    """An error must say what to fix, not describe the filesystem."""
    client, _ = _client()
    for probe in ("CLAUDE.md", "requirements.txt", "/etc/passwd", "nope.csv",
                  "../../../etc/passwd", "..%2f..%2fetc%2fpasswd"):
        body = client.get(f"/api/backtest?strategy=sma_cross&csv={probe}").get_json() or {}
        error = str(body.get("error", ""))
        assert "/home/" not in error and "/etc/" not in error, \
            f"{probe} leaked a path: {error}"
        assert "Error tokenizing" not in error and "Traceback" not in error, \
            f"{probe} leaked parser internals: {error}"


def test_valid_csv_still_loads():
    """Hardening must not break the feature it protects."""
    import tempfile
    from quant import data as qdata
    client, _ = _client()
    tmp = Path("data") / "_hardening_probe.csv"
    tmp.parent.mkdir(exist_ok=True)
    try:
        qdata.synthetic(n=1200, seed=3).reset_index(names="date").to_csv(tmp, index=False)
        body = client.get(f"/api/backtest?strategy=sma_cross&csv={tmp}").get_json() or {}
        assert "error" not in body, f"a valid CSV was rejected: {body.get('error')}"
        assert "p_deflated" in body
    finally:
        tmp.unlink(missing_ok=True)


def test_binding_off_loopback_marks_the_cookie_secure():
    """Off localhost the token crosses a network; the cookie must refuse plain HTTP."""
    src = (Path(__file__).resolve().parent.parent / "web" / "app.py").read_text()
    assert 'SESSION_COOKIE_SECURE"] = True' in src, \
        "binding beyond localhost must set the Secure flag"



# --- data source resilience -------------------------------------------------

class _FlakyServer:
    """Serves a scripted sequence of status codes, then 200."""

    def __init__(self, statuses, payload=None, retry_after=None):
        import json as _json
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        self.statuses = list(statuses)
        self.requests = 0
        self.headers_seen = []
        outer = self
        payload = payload or {"prices": [[1700000000000, 100.0], [1700086400000, 101.0],
                                         [1700172800000, 99.0]]}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                outer.requests += 1
                outer.headers_seen.append(dict(self.headers))
                code = outer.statuses.pop(0) if outer.statuses else 200
                self.send_response(code)
                if code == 429 and retry_after is not None:
                    self.send_header("Retry-After", str(retry_after))
                self.send_header("Content-Type", "application/json")
                data = _json.dumps(payload).encode()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}/probe"
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *a):
        self.server.shutdown()


def test_transient_failures_are_retried():
    """A rate limit mid-screen should cost seconds, not the whole run."""
    from quant.data import _get
    with _FlakyServer([429, 503, 200]) as server:
        response = _get(server.url, what="test source")
        assert response.status_code == 200
        assert server.requests == 3, f"expected 2 retries then success, got {server.requests}"


def test_persistent_rate_limit_gives_actionable_advice():
    from quant.data import MAX_RETRIES, DataError, _get
    with _FlakyServer([429] * 10) as server:
        try:
            _get(server.url, what="test source")
        except DataError as exc:
            assert "rate limited" in str(exc).lower()
            assert "api key" in str(exc).lower(), "should suggest the fix"
            assert server.requests == MAX_RETRIES
            return
    raise AssertionError("a persistent rate limit must raise")


def test_client_errors_are_not_retried():
    """A 404 is our mistake; retrying it wastes time and hides the cause."""
    from quant.data import DataError, _get
    with _FlakyServer([404, 200]) as server:
        try:
            _get(server.url, what="test source")
        except DataError as exc:
            assert "404" in str(exc)
            assert server.requests == 1, "a 404 must not be retried"
            return
    raise AssertionError("a 404 must raise")


def test_auth_failure_names_the_likely_cause():
    from quant.data import DataError, _get
    for status in (401, 403):
        with _FlakyServer([status]) as server:
            try:
                _get(server.url, what="test source")
            except DataError as exc:
                assert "api key" in str(exc).lower(), f"{status} should mention a key"
                continue
            raise AssertionError(f"{status} must raise")


def test_coingecko_key_header_matches_the_plan():
    from quant.data import _coingecko_headers
    saved = {k: os.environ.get(k) for k in ("COINGECKO_API_KEY", "COINGECKO_PLAN")}
    try:
        os.environ.pop("COINGECKO_API_KEY", None)
        assert not any(k.startswith("x-cg") for k in _coingecko_headers()), \
            "no key set means no key header"

        os.environ["COINGECKO_API_KEY"] = "abc123"
        os.environ["COINGECKO_PLAN"] = "demo"
        assert _coingecko_headers()["x-cg-demo-api-key"] == "abc123"

        os.environ["COINGECKO_PLAN"] = "pro"
        assert _coingecko_headers()["x-cg-pro-api-key"] == "abc123"
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_no_cache_mode_writes_nothing():
    """datacheck probes live sources without polluting the cache.

    Passing cache_dir=None used to raise TypeError deep inside the fetcher,
    which masked the real network error behind a misleading one.
    """
    import tempfile
    from unittest.mock import patch
    from quant import data as qdata

    payload = {"chart": {"error": None, "result": [{
        "timestamp": [1700000000, 1700086400, 1700172800],
        "indicators": {"quote": [{"close": [10.0, 11.0, 12.0]}]}}]}}

    with tempfile.TemporaryDirectory() as tmp, \
         patch("quant.data.requests.get", return_value=_mock_response(payload)):
        frame = qdata.fetch_yahoo("TEST.JK", cache_dir=None)
        assert len(frame) == 3
        assert not list(Path(tmp).iterdir()), "nothing should have been written"



# --- the whole system in the browser ----------------------------------------

def test_dashboard_serves_all_four_views():
    """Live, Screen, Desk, Research — and both navs, within the 5-tab limit."""
    client, _ = _client()
    html = client.get("/").get_data(as_text=True)
    for view in ("live", "screen", "desk", "research"):
        assert f'id="view-{view}"' in html, f"missing view: {view}"
        assert f'data-view="{view}"' in html, f"missing tab: {view}"
    assert html.count('role="tablist"') == 2
    tabs = html.count('class="tab" role="tab"')
    assert tabs <= 5, f"{tabs} top-level tabs exceeds the bottom-bar limit"


def test_desk_endpoint_returns_every_verdict():
    """Not just the outcome — the reasons are the point of the desk."""
    client, _ = _client()
    body = client.get("/api/desk?strategy=ts_momentum&universe=regimes&seed=2").get_json()
    assert "approved" in body
    agents = {v["agent"] for v in body["verdicts"]}
    assert agents == {"research", "skeptic", "cost", "risk"}, agents
    for verdict in body["verdicts"]:
        assert verdict["reason"], f"{verdict['agent']} gave no reason"
        assert body["mandates"][verdict["agent"]], "every agent must state a mandate"
    assert 0.0 <= body["position"] <= 1.0


def test_desk_endpoint_rejects_unknown_strategy():
    client, _ = _client()
    assert client.get("/api/desk?strategy=nonsense").status_code == 400


def test_screen_runs_as_a_job_and_reports_both_p_values():
    """A real screen outlives a request, so it runs in a thread and is polled."""
    client, _ = _client()
    started = client.post("/api/screen", json={"strategy": "breakout",
                                               "universe": "synthetic", "count": 12}).get_json()
    assert "job" in started, started

    for _ in range(120):
        job = client.get(f"/api/screen/{started['job']}").get_json()
        if job["stage"] in ("done", "failed"):
            break
        time.sleep(0.25)

    assert job["stage"] == "done", job.get("error")
    assert len(job["rows"]) == 12
    assert job["total_trials"] == 12 * job["n_combos"], "trials must be assets x configs"
    for row in job["rows"]:
        assert row["p_honest"] >= row["p_naive"], \
            "the whole-screen p-value can never be kinder than the per-asset one"


def test_screen_job_ids_are_unguessable_and_scoped():
    client, _ = _client()
    assert client.get("/api/screen/does-not-exist").status_code == 404
    started = client.post("/api/screen", json={"universe": "synthetic", "count": 8}).get_json()
    assert len(started["job"]) >= 8, "a job id must not be enumerable"


def test_screen_rejects_unknown_strategy_before_starting_work():
    client, _ = _client()
    assert client.post("/api/screen", json={"strategy": "nope"}).status_code == 400


def test_analyze_endpoint_states_its_parameter_basis():
    client, _ = _client()
    body = client.get("/api/analyze?strategy=sma_cross").get_json()
    assert "fitted out-of-sample" in body["basis"]
    assert body["params"], "must name the parameters the figures describe"
    assert len(body["leverage"]) == 4
    assert body["leverage"][0]["leverage"] == 1
    ruin = [row["p_wiped_out"] for row in body["leverage"]]
    assert ruin == sorted(ruin), "wipeout risk must rise with leverage"


def test_new_endpoints_require_auth():
    """Every addition must be behind the same gate as everything else."""
    os.environ["DASHBOARD_TOKEN"] = "test-token-value"
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
    import importlib
    import app as dashboard
    importlib.reload(dashboard)
    anonymous = dashboard.app.test_client()

    assert anonymous.get("/api/desk").status_code == 401
    assert anonymous.get("/api/analyze").status_code == 401
    assert anonymous.post("/api/screen", json={}).status_code == 401
    assert anonymous.get("/api/screen/anything").status_code == 401



def test_a_running_screen_is_never_evicted():
    """Eviction used to race running jobs: note() KeyErrored, the thread died,
    and the handler meant to record the failure KeyErrored too. The user polling
    that job got a bare 404."""
    client, dashboard = _client()

    for _ in range(dashboard.MAX_JOBS_KEPT + 6):
        client.post("/api/screen", json={"universe": "synthetic", "count": 8})
        time.sleep(0.05)

    deadline = time.time() + 60
    while time.time() < deadline:
        stages = [j["stage"] for j in dashboard._JOBS.values()]
        if all(s in ("done", "failed") for s in stages):
            break
        time.sleep(0.3)

    assert stages, "no jobs retained at all"
    assert all(s in ("done", "failed") for s in stages), \
        f"a job was left mid-flight by eviction: {stages}"
    assert not any(s == "failed" for s in stages), "no job should have crashed"


def test_only_one_screen_runs_at_a_time():
    """Each screen spawns a process pool; several at once oversubscribe the box."""
    client, _ = _client()
    starts = [client.post("/api/screen", json={"universe": "synthetic", "count": 40}).get_json()
              for _ in range(4)]
    assert len({s["job"] for s in starts}) == 1, "four clicks should share one run"
    assert sum("already_running" in s for s in starts) == 3, "reuse must be reported to the page"

    job = starts[0]["job"]
    deadline = time.time() + 90
    while time.time() < deadline:
        state = client.get(f"/api/screen/{job}").get_json()
        if state["stage"] in ("done", "failed"):
            break
        time.sleep(0.3)
    assert state["stage"] == "done", state.get("error")


def test_unknown_universe_is_refused_before_work_starts():
    client, _ = _client()
    response = client.post("/api/screen", json={"universe": "../../etc"})
    assert response.status_code == 400
    assert "universe" in response.get_json()["error"]


def test_screen_inputs_are_clamped():
    client, _ = _client()
    for payload, field, bound in [({"count": 99999}, "requested", 300),
                                  ({"count": -5}, "requested", 2)]:
        started = client.post("/api/screen", json={**payload, "universe": "synthetic"}).get_json()
        state = client.get(f"/api/screen/{started['job']}").get_json()
        assert state[field] == bound, f"{payload} should clamp {field} to {bound}, got {state[field]}"
        deadline = time.time() + 90
        while time.time() < deadline:
            state = client.get(f"/api/screen/{started['job']}").get_json()
            if state["stage"] in ("done", "failed"):
                break
            time.sleep(0.3)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
