"""Strategies. A strategy maps (close, **params) -> target position series.

Positions are fractions of equity: 1.0 = fully long, 0.0 = flat, -1.0 = short.
Every value must be computable from data up to and including that bar; the
engine handles execution lag. Keep that contract and the backtest stays honest.
"""
import pandas as pd

# Each entry: name -> (function, param grid searched during walk-forward).
# Grids are deliberately small. Every extra combination is another chance to
# overfit, and the deflated p-value in validate.py charges you for it.


def sma_cross(close, fast=20, slow=100):
    """Long while the fast average sits above the slow one. Classic trend-follow."""
    close = pd.Series(close)
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    return (f > s).astype(float).where(s.notna(), 0.0)


def rsi_reversion(close, window=14, low=30, high=70):
    """Buy oversold, flatten once recovered. Mean-reversion."""
    close = pd.Series(close)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, pd.NA))

    # Stateful: enter below `low`, hold until back above `high`.
    position, holding = [], False
    for value in rsi:
        if pd.isna(value):
            position.append(0.0)
            continue
        if not holding and value < low:
            holding = True
        elif holding and value > high:
            holding = False
        position.append(1.0 if holding else 0.0)
    return pd.Series(position, index=close.index)


def breakout(close, window=55):
    """Long on a new N-bar high, flat on a new N-bar low. Donchian-style."""
    close = pd.Series(close)
    high = close.rolling(window).max()
    low = close.rolling(window).min()

    position, holding = [], False
    for price, hi, lo in zip(close, high.shift(1), low.shift(1)):
        if pd.isna(hi):
            position.append(0.0)
            continue
        if price >= hi:
            holding = True
        elif price <= lo:
            holding = False
        position.append(1.0 if holding else 0.0)
    return pd.Series(position, index=close.index)


REGISTRY = {
    "sma_cross": (sma_cross, {"fast": [10, 20, 50], "slow": [100, 150, 200]}),
    "rsi_reversion": (rsi_reversion, {"window": [7, 14, 21], "low": [25, 30], "high": [65, 70]}),
    "breakout": (breakout, {"window": [20, 55, 100]}),
}
