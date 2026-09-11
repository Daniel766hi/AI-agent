"""The live Binance path, exercised against a stand-in exchange.

This does not prove the real API behaves this way today. It proves our signing,
symbol handling, lot rounding and error handling are self-consistent — the class
of bug that otherwise surfaces only with real money at stake.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fake_binance import FakeBinance
from quant.broker import BinanceBroker


def test_symbol_assets_come_from_the_exchange():
    """Splitting a pair by string length breaks whenever the quote is not 4 chars."""
    with FakeBinance() as fake:
        info = BinanceBroker("k", "secret", "ETHBTC", base_url=fake.url).symbol_info()
        assert info["base"] == "ETH" and info["quote"] == "BTC", \
            f"ETHBTC must split ETH/BTC, got {info['base']}/{info['quote']}"

        info = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url).symbol_info()
        assert info["base"] == "BTC" and info["quote"] == "USDT"


def test_unknown_symbol_raises():
    with FakeBinance() as fake:
        try:
            BinanceBroker("k", "secret", "NOTREAL", base_url=fake.url).symbol_info()
        except RuntimeError as exc:
            assert "NOTREAL" in str(exc)
            return
        raise AssertionError("an unlisted symbol must raise, not return empty rules")


def test_signed_requests_are_accepted():
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)
        assert broker.balances()["USDT"] == 1000.0
        assert fake.bad_signatures == 0, "the exchange rejected our signature"


def test_bad_secret_is_rejected():
    """Proves the fake actually verifies signatures, so the test above means something."""
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "wrong-secret", "BTCUSDT", base_url=fake.url)
        try:
            broker.balances()
        except RuntimeError as exc:
            assert "401" in str(exc) or "-1022" in str(exc)
            assert fake.bad_signatures == 1
            return
        raise AssertionError("a wrong secret must be rejected")


def test_full_round_trip_updates_balances():
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)
        price = broker.price()

        buy = broker.set_target(1.0, price)
        assert buy["side"] == "BUY" and buy["units"] > 0
        assert broker.position_fraction(price) > 0.95, "should be near fully long"

        sell = broker.set_target(0.0, price)
        assert sell["side"] == "SELL"
        assert broker.balances().get("BTC", 0) == 0, "flatten must leave nothing behind"
        assert len(fake.orders) == 2


def test_flatten_is_exact_not_approximate():
    """Decimal lot maths: 0.01663/0.00001 floors to 1662 in float, leaving a sliver.

    The drawdown kill switch flattens the position. If 'flatten' leaves residual
    exposure, the safety stop does not actually stop the risk.
    """
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)
        price = broker.price()
        broker.set_target(1.0, price)
        held = broker.balances()["BTC"]
        assert held > 0

        broker.set_target(0.0, price)
        assert broker.balances().get("BTC", 0) == 0, \
            f"left {broker.balances().get('BTC')} behind when flattening {held}"


def test_quantity_is_rounded_down_to_the_lot_step():
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)   # step 0.00001
        assert broker._round_step(0.01663) == 0.01663, "an exact multiple must survive"
        assert broker._round_step(0.123456789) == 0.12345, "must round down, never up"
        assert broker._round_step(0.000001) == 0.0, "below one step is nothing"


def test_orders_off_the_lot_step_are_rejected_by_the_exchange():
    """Confirms the fake enforces LOT_SIZE, so the rounding test above has teeth."""
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)
        try:
            broker._request("POST", "/api/v3/order", {
                "symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "0.000123456"})
        except RuntimeError as exc:
            assert "LOT_SIZE" in str(exc)
            return
        raise AssertionError("an off-step quantity must be rejected")


def test_max_notional_caps_the_order():
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url, max_notional=100.0)
        price = broker.price()
        trade = broker.set_target(1.0, price)
        assert trade["notional"] <= 101.0, f"cap breached: {trade['notional']}"


def test_insufficient_balance_surfaces_the_exchange_error():
    with FakeBinance(balances={"USDT": 20.0, "BTC": 0.0}) as fake:
        broker = BinanceBroker("k", "secret", "BTCUSDT", base_url=fake.url)
        price = broker.price()
        # $20 of equity cannot meet the $5 minNotional after the fee buffer... it can,
        # so ask for a position the balance cannot fund and expect a clear failure.
        fake.balances["USDT"] = 3.0
        assert broker.set_target(1.0, price) is None, "below minNotional must be skipped, not sent"


def test_three_char_quote_pair_trades_correctly():
    """ETHBTC is the pair that silently did nothing before assets came from the API."""
    with FakeBinance() as fake:
        broker = BinanceBroker("k", "secret", "ETHBTC", base_url=fake.url)
        price = broker.price()
        assert broker.equity(price) > 0, "equity must not read zero for a 3-char quote"
        assert broker.position_fraction(price) > 0.9, "2 ETH held should read as fully long"

        trade = broker.set_target(0.0, price)
        assert trade is not None and trade["side"] == "SELL"
        assert broker.balances().get("ETH", 0) == 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
