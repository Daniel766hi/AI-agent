"""The trading loop. Paper by default; live requires deliberate opt-in.

Runs the same strategy functions the backtester validated, against a broker.
Writes state to JSON on every tick so the dashboard can read it without
sharing memory with this process.
"""
import json
import os
import time
import traceback
from pathlib import Path

import pandas as pd
import requests

from .backtest import DEFAULT_FEE_BPS, DEFAULT_SLIPPAGE_BPS
from .broker import BinanceBroker, InsufficientFunds, PaperBroker
from .strategies import REGISTRY

STATE_FILE = Path("data/live_state.json")
KLINES = "https://api.binance.com/api/v3/klines"


def recent_bars(symbol="BTCUSDT", interval="1d", limit=500):
    """Latest closed bars. The in-progress bar is dropped — it can still change."""
    response = requests.get(
        KLINES, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=30)
    response.raise_for_status()
    rows = response.json()
    if len(rows) < 2:
        raise RuntimeError(f"Binance returned {len(rows)} bars for {symbol}")
    closes = [float(r[4]) for r in rows[:-1]]
    times = pd.to_datetime([r[0] for r in rows[:-1]], unit="ms")
    return pd.Series(closes, index=times, name="close")


class Trader:
    """One strategy, one symbol, one broker, with kill switches."""

    def __init__(self, strategy, params, broker, symbol="BTCUSDT", interval="1d",
                 max_drawdown_pct=20.0, state_file=STATE_FILE):
        if strategy not in REGISTRY:
            raise ValueError(f"unknown strategy {strategy!r}; have {sorted(REGISTRY)}")
        self.strategy_name = strategy
        self.strategy_fn = REGISTRY[strategy][0]
        self.params = params or {}
        self.broker = broker
        self.symbol = symbol
        self.interval = interval
        self.max_drawdown_pct = max_drawdown_pct
        self.state_file = Path(state_file)
        self.peak_equity = None
        self.halted = False
        self.halt_reason = None
        self.last_error = None

    def tick(self):
        """One cycle: read the market, compute the target, move the position."""
        bars = recent_bars(self.symbol, self.interval)
        price = float(bars.iloc[-1])

        signal = self.strategy_fn(bars, **self.params)
        target = float(signal.iloc[-1])          # last CLOSED bar — never the live one

        equity = self.broker.equity(price)
        self.peak_equity = equity if self.peak_equity is None else max(self.peak_equity, equity)
        drawdown = (equity / self.peak_equity - 1.0) * 100.0 if self.peak_equity else 0.0

        # Kill switch runs BEFORE the order: flatten and stop, don't average down.
        if drawdown <= -self.max_drawdown_pct and not self.halted:
            self.halted = True
            self.halt_reason = f"drawdown {drawdown:.1f}% breached -{self.max_drawdown_pct}% limit"
            target = 0.0

        trade = None
        if not self.halted or target == 0.0:
            try:
                trade = self.broker.set_target(target, price, self.symbol)
            except InsufficientFunds as exc:
                self.halted = True
                self.halt_reason = str(exc)

        state = {
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": self.symbol,
            "interval": self.interval,
            "strategy": self.strategy_name,
            "params": self.params,
            "price": round(price, 2),
            "target_position": target,
            "drawdown_pct": round(drawdown, 2),
            "peak_equity": round(self.peak_equity, 2) if self.peak_equity else None,
            "halted": self.halted,
            "halt_reason": self.halt_reason,
            "last_trade": trade,
            "last_error": self.last_error,
            **self.broker.state(price),
        }
        self._write(state)
        return state

    def run(self, poll_seconds=3600, max_ticks=None):
        ticks = 0
        while max_ticks is None or ticks < max_ticks:
            try:
                state = self.tick()
                flag = "HALTED" if state["halted"] else f"pos {state['position_fraction']:.2f}"
                print(f"[{state['updated']}] {self.symbol} {state['price']:>10,.2f}  "
                      f"target {state['target_position']:.2f}  equity {state['equity']:>10,.2f}  {flag}")
                self.last_error = None
                if state["halted"]:
                    print(f"  HALTED: {state['halt_reason']}")
                    return state
            except Exception as exc:               # a transient API error must not kill the loop
                self.last_error = f"{type(exc).__name__}: {exc}"
                print(f"  error: {self.last_error}")
                traceback.print_exc()
            ticks += 1
            if max_ticks is None or ticks < max_ticks:
                time.sleep(poll_seconds)

    def _write(self, state):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, indent=2, default=str))


def make_broker(mode, symbol, starting_cash=1000.0, max_notional=None):
    """Build a broker. Live mode reads credentials from the environment only."""
    if mode == "paper":
        return PaperBroker(starting_cash=starting_cash, fee_bps=DEFAULT_FEE_BPS,
                           slippage_bps=DEFAULT_SLIPPAGE_BPS,
                           state_path="data/paper_broker.json")
    if mode == "live":
        return BinanceBroker(
            api_key=os.environ.get("BINANCE_API_KEY"),
            api_secret=os.environ.get("BINANCE_API_SECRET"),
            symbol=symbol,
            base_url=os.environ.get("BINANCE_API_URL", "https://api.binance.com"),
            max_notional=max_notional,
        )
    raise ValueError(f"mode must be 'paper' or 'live', got {mode!r}")


def read_state(state_file=STATE_FILE):
    """Last written state, or None. Used by the dashboard."""
    path = Path(state_file)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
