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


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
