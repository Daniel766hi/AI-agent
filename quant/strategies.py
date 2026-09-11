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


def vol_target(position, close, target_annual_vol=0.40, window=30,
               periods_per_year=365, max_leverage=1.0):
    """Scale an existing position by (target vol / recent realised vol).

    Rationale: volatility is strongly persistent — a turbulent week predicts a
    turbulent next week — while direction is not. Sizing by recent volatility
    uses the one thing that is genuinely forecastable.

    What it actually delivers, measured on volatility-clustered synthetic data
    (40 paths, see test_vol_target_*): realised volatility pulled to target
    (59% -> 41%), max drawdown shallower on 40 of 40 paths (-75% -> -62%), and
    realised risk about half as erratic. What it does NOT deliver is a Sharpe
    improvement — return and risk scale down together, so risk-adjusted return
    is roughly unchanged. This is risk control, not alpha. Use it to hold a risk
    budget you can live with, not to make money appear.

    Capped at max_leverage, so by default it can only ever cut exposure, never
    borrow. Raising it above 1.0 means leverage and real liquidation risk.
    """
    close = pd.Series(close)
    realised = close.pct_change().rolling(window).std() * (periods_per_year ** 0.5)
    scale = (target_annual_vol / realised.replace(0, pd.NA)).clip(upper=max_leverage)
    return (pd.Series(position, index=close.index) * scale).fillna(0.0)


def ts_momentum(close, lookback=90):
    """Long when the trailing return over `lookback` bars is positive.

    Rationale: time-series momentum is among the better-documented return
    patterns across asset classes (Moskowitz, Ooi & Pedersen 2012), usually
    attributed to gradual diffusion of information and investor underreaction.
    That is a real economic story rather than a shape on a chart — but a
    documented past effect is still not a promise about your data. Test it.
    """
    close = pd.Series(close)
    return (close / close.shift(lookback) - 1.0 > 0).astype(float).where(
        close.shift(lookback).notna(), 0.0)


def ts_momentum_vol_targeted(close, lookback=90, target_annual_vol=0.40, window=30):
    """Time-series momentum, sized by inverse volatility. Direction + risk control."""
    return vol_target(ts_momentum(close, lookback), close,
                      target_annual_vol=target_annual_vol, window=window)


REGISTRY = {
    "sma_cross": (sma_cross, {"fast": [10, 20, 50], "slow": [100, 150, 200]}),
    "rsi_reversion": (rsi_reversion, {"window": [7, 14, 21], "low": [25, 30], "high": [65, 70]}),
    "breakout": (breakout, {"window": [20, 55, 100]}),
    "ts_momentum": (ts_momentum, {"lookback": [30, 90, 180]}),
    "ts_momentum_vol_targeted": (ts_momentum_vol_targeted,
                                 {"lookback": [30, 90, 180], "target_annual_vol": [0.3, 0.5]}),
}
