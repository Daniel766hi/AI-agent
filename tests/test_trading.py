"""Self-checks for brokers, auth, and the live-mode gates."""
import os
import sys
import tempfile
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


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
