"""Vectorised backtest with realistic costs, plus the metrics that matter."""
import numpy as np
import pandas as pd

# Round-trip cost assumptions. Binance spot taker is 10bps; 5bps slippage is
# optimistic for illiquid alts and generous for BTC/ETH.
DEFAULT_FEE_BPS = 10.0
DEFAULT_SLIPPAGE_BPS = 5.0


def _reject_bad_prices(close):
    """Refuse to model prices that cannot be real.

    Every backtest, screen and live tick routes through backtest(), so this is
    the one place the check has to live. Real feeds do produce these: a zero
    from an API error, a gap over a halt, a negative from a bad parse. Filling
    them silently is worse than failing — a single zero makes the next return
    infinite, which would top the ranking in any screen.
    """
    if len(close) == 0:
        raise ValueError("no price data")

    n_missing = int(close.isna().sum())
    if n_missing:
        first = close.index[close.isna()][0]
        raise ValueError(
            f"{n_missing} missing price(s), first at {first}. Drop or fill them "
            "deliberately before backtesting — they cannot be modelled as zero returns."
        )

    bad = close <= 0
    if bad.any():
        first = close.index[bad][0]
        raise ValueError(
            f"{int(bad.sum())} non-positive price(s), first at {first} ({close[bad].iloc[0]}). "
            "A zero or negative price makes the next return infinite or nonsensical."
        )


def backtest(close, signal, fee_bps=DEFAULT_FEE_BPS, slippage_bps=DEFAULT_SLIPPAGE_BPS,
             periods_per_year=365):
    """Run `signal` against `close` and return a DataFrame of the run.

    `signal` is the TARGET position for a bar, computed from information up to
    and including that bar's close. It is shifted forward one bar before being
    applied: you cannot trade on a close you have not yet observed. This single
    shift is what separates a backtest from a fantasy.
    """
    close = pd.Series(close).astype(float)
    _reject_bad_prices(close)
    signal = pd.Series(signal, index=close.index).astype(float).fillna(0.0)

    position = signal.shift(1).fillna(0.0)          # <- the no-lookahead guard
    asset_return = close.pct_change().fillna(0.0)

    turnover = position.diff().abs().fillna(position.abs())
    cost = turnover * (fee_bps + slippage_bps) / 10_000.0

    net_return = position * asset_return - cost

    return pd.DataFrame({
        "close": close,
        "position": position,
        "asset_return": asset_return,
        "turnover": turnover,
        "cost": cost,
        "net_return": net_return,
        "equity": (1.0 + net_return).cumprod(),
    })


def metrics(net_return, periods_per_year=365):
    """Summary stats for a return series. Returns a plain dict."""
    r = pd.Series(net_return).dropna()
    n = len(r)
    if n == 0:
        return {k: float("nan") for k in
                ("cagr", "sharpe", "max_drawdown", "volatility", "total_return",
                 "n_periods", "positive_period_rate")}

    equity = (1.0 + r).cumprod()
    total = equity.iloc[-1] - 1.0
    years = n / periods_per_year

    # ponytail: a wiped-out account has no meaningful CAGR; report -100%.
    cagr = (equity.iloc[-1] ** (1.0 / years) - 1.0) if equity.iloc[-1] > 0 and years > 0 else -1.0

    sd = r.std(ddof=1)
    sharpe = (r.mean() / sd) * np.sqrt(periods_per_year) if sd > 0 else 0.0
    drawdown = (equity / equity.cummax() - 1.0).min()
    # Periods with a nonzero result — NOT a per-trade win rate. One trade spans
    # many periods, so this is "how often did an exposed day gain", nothing more.
    exposed = r[r != 0]

    return {
        "cagr": float(cagr),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown),
        "volatility": float(sd * np.sqrt(periods_per_year)),
        "total_return": float(total),
        "n_periods": int(n),
        "positive_period_rate": float((exposed > 0).mean()) if len(exposed) else float("nan"),
    }


def buy_and_hold(close, periods_per_year=365):
    """The benchmark every strategy has to beat to justify existing."""
    return backtest(close, pd.Series(1.0, index=pd.Series(close).index),
                    periods_per_year=periods_per_year)
