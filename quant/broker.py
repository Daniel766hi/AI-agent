"""Brokers: simulated and real.

PaperBroker uses the same cost model as the backtest, so paper results are
comparable to backtest results. BinanceBroker places real orders with real
money and is deliberately harder to reach.
"""
import hashlib
import hmac
import json
import time
import urllib.parse
from pathlib import Path

import requests

BINANCE_API = "https://api.binance.com"
MIN_NOTIONAL = 10.0      # Binance rejects spot orders below ~$10
DUST_FRACTION = 0.005    # don't churn on rebalances smaller than 0.5% of equity


class InsufficientFunds(Exception):
    pass


class PaperBroker:
    """Simulated fills at the last price, charged the backtest's cost model."""

    def __init__(self, starting_cash=1000.0, fee_bps=10.0, slippage_bps=5.0, state_path=None):
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.state_path = Path(state_path) if state_path else None
        self.cash = float(starting_cash)
        self.units = 0.0
        self.trades = []
        if self.state_path and self.state_path.exists():
            self._load()

    mode = "paper"

    def equity(self, price):
        return self.cash + self.units * price

    def position_fraction(self, price):
        eq = self.equity(price)
        return (self.units * price / eq) if eq > 0 else 0.0

    def set_target(self, target_fraction, price, symbol="?"):
        """Move to `target_fraction` of equity in the asset. Returns a trade dict or None."""
        if price <= 0:
            raise ValueError(f"bad price: {price}")
        target_fraction = max(-1.0, min(1.0, float(target_fraction)))

        equity = self.equity(price)
        if equity <= 0:
            raise InsufficientFunds("account wiped out")

        delta_units = (target_fraction * equity / price) - self.units
        notional = abs(delta_units) * price

        # ponytail: two filters, both real. Dust avoids fee-bleed on noise;
        # MIN_NOTIONAL mirrors the exchange's own rejection so paper matches live.
        if notional < max(MIN_NOTIONAL, DUST_FRACTION * equity):
            return None

        rate = (self.fee_bps + self.slippage_bps) / 10_000.0

        # A buy must fund both the units and their own fee out of the same cash,
        # so full-equity targets are capped just below 100%. Without this, any
        # target of 1.0 asks for more cash than exists.
        if delta_units > 0:
            affordable = self.cash / (price * (1.0 + rate))
            delta_units = min(delta_units, affordable)
            notional = delta_units * price

        cost = notional * rate
        proceeds = delta_units * price + cost
        if proceeds > self.cash + 1e-9 and delta_units > 0:
            raise InsufficientFunds(f"need {proceeds:.2f}, have {self.cash:.2f}")

        self.cash -= proceeds
        self.units += delta_units

        trade = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "side": "BUY" if delta_units > 0 else "SELL",
            "units": round(abs(delta_units), 8),
            "price": round(price, 2),
            "notional": round(notional, 2),
            "cost": round(cost, 4),
            "equity_after": round(self.equity(price), 2),
            "mode": self.mode,
        }
        self.trades.append(trade)
        self._save()
        return trade

    def state(self, price=None):
        return {
            "mode": self.mode,
            "cash": round(self.cash, 2),
            "units": round(self.units, 8),
            "equity": round(self.equity(price), 2) if price else None,
            "position_fraction": round(self.position_fraction(price), 4) if price else None,
            "n_trades": len(self.trades),
            "trades": self.trades[-20:],
        }

    def _save(self):
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(
            {"cash": self.cash, "units": self.units, "trades": self.trades}, indent=2))

    def _load(self):
        saved = json.loads(self.state_path.read_text())
        self.cash = saved["cash"]
        self.units = saved["units"]
        self.trades = saved.get("trades", [])


class BinanceBroker:
    """Real spot orders on Binance. Real money. Untested against the live API.

    The signing logic is unit-tested against Binance's published example, but no
    order has ever been placed through this class. Run it against
    testnet.binance.vision first and read every fill before trusting it.
    """

    mode = "live"

    def __init__(self, api_key, api_secret, symbol, base_url=BINANCE_API, max_notional=None):
        if not api_key or not api_secret:
            raise ValueError("live mode needs BINANCE_API_KEY and BINANCE_API_SECRET")
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.symbol = symbol
        self.base_url = base_url
        self.max_notional = max_notional
        self.trades = []

    def _sign(self, params):
        query = urllib.parse.urlencode(params)
        signature = hmac.new(self.api_secret, query.encode(), hashlib.sha256).hexdigest()
        return f"{query}&signature={signature}"

    def _request(self, method, path, params=None, signed=True):
        params = dict(params or {})
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000
            url = f"{self.base_url}{path}?{self._sign(params)}"
            body = None
        else:
            url = f"{self.base_url}{path}"
            body = params
        response = requests.request(
            method, url, params=body, headers={"X-MBX-APIKEY": self.api_key}, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(f"Binance {response.status_code}: {response.text[:300]}")
        return response.json()

    def price(self):
        data = self._request("GET", "/api/v3/ticker/price",
                             {"symbol": self.symbol}, signed=False)
        return float(data["price"])

    def balances(self):
        account = self._request("GET", "/api/v3/account")
        return {b["asset"]: float(b["free"]) for b in account["balances"] if float(b["free"]) > 0}

    def _holdings(self):
        base, quote = self.symbol[:-4], self.symbol[-4:]   # e.g. BTC / USDT
        balances = self.balances()
        return balances.get(base, 0.0), balances.get(quote, 0.0)

    def equity(self, price):
        units, cash = self._holdings()
        return cash + units * price

    def position_fraction(self, price):
        units, _ = self._holdings()
        eq = self.equity(price)
        return (units * price / eq) if eq > 0 else 0.0

    def set_target(self, target_fraction, price, symbol=None):
        target_fraction = max(0.0, min(1.0, float(target_fraction)))   # spot: no shorting
        units, cash = self._holdings()
        equity = cash + units * price
        delta_units = (target_fraction * equity / price) - units
        notional = abs(delta_units) * price

        if delta_units > 0:
            # Leave room for the taker fee, as in PaperBroker; the exchange
            # rejects an order that spends every unit of quote balance.
            affordable = cash / (price * 1.002)
            delta_units = min(delta_units, affordable)
            notional = delta_units * price

        if notional < max(MIN_NOTIONAL, DUST_FRACTION * equity):
            return None
        if self.max_notional and notional > self.max_notional:
            # Hard cap at the trust boundary: clamp, never silently exceed.
            delta_units = (self.max_notional / price) * (1 if delta_units > 0 else -1)
            notional = self.max_notional

        order = self._request("POST", "/api/v3/order", {
            "symbol": self.symbol,
            "side": "BUY" if delta_units > 0 else "SELL",
            "type": "MARKET",
            "quantity": f"{abs(delta_units):.6f}",
        })

        filled = float(order.get("executedQty", 0) or 0)
        spent = float(order.get("cummulativeQuoteQty", 0) or 0)
        trade = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": self.symbol,
            "side": order.get("side"),
            "units": round(filled, 8),
            "price": round(spent / filled, 2) if filled else price,
            "notional": round(spent, 2),
            "cost": None,
            "equity_after": round(self.equity(price), 2),
            "mode": "live",
            "order_id": order.get("orderId"),
        }
        self.trades.append(trade)
        return trade

    def state(self, price=None):
        units, cash = self._holdings()
        return {
            "mode": "live",
            "cash": round(cash, 2),
            "units": round(units, 8),
            "equity": round(self.equity(price), 2) if price else None,
            "position_fraction": round(self.position_fraction(price), 4) if price else None,
            "n_trades": len(self.trades),
            "trades": self.trades[-20:],
        }
