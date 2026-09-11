"""What profit would actually require, and what is most likely to prevent it.

None of this predicts returns. It is arithmetic on costs, position sizing and
survival — the parts of the outcome you control, as opposed to the part the
market decides.
"""
import numpy as np
import pandas as pd


def cost_drag(round_trips_per_year, fee_bps=10.0, slippage_bps=5.0):
    """Annual return lost to costs. One round trip pays the cost twice."""
    return 2.0 * round_trips_per_year * (fee_bps + slippage_bps) / 10_000.0


def breakeven(result, periods_per_year=365, fee_bps=10.0, slippage_bps=5.0):
    """What a backtested run must earn gross, before it earns anything net.

    Takes a DataFrame from backtest(). Returns the annual cost drag, the implied
    round trips, and the gross annual return needed just to break even with
    holding the asset.
    """
    years = len(result) / periods_per_year
    turnover = float(result["turnover"].sum())
    annual_cost = float(result["cost"].sum()) / years

    time_in_market = float((result["position"] != 0).mean())
    asset_annual = float((1 + result["asset_return"]).prod() ** (1 / years) - 1)

    return {
        "years": years,
        "round_trips_per_year": turnover / 2 / years,
        "annual_cost_drag": annual_cost,
        "time_in_market": time_in_market,
        "asset_annual_return": asset_annual,
        # To beat holding, it must cover its costs AND the return it forfeits
        # by sitting in cash part of the time.
        "hurdle_vs_holding": annual_cost + asset_annual * (1 - time_in_market),
    }


def risk_of_ruin(returns, ruin_drawdown=0.5, horizon_years=1.0, leverage=1.0,
                 periods_per_year=365, n_sims=10_000, seed=0):
    """Probability of a `ruin_drawdown` loss within the horizon.

    Bootstraps from the actual return distribution rather than assuming
    normality, because real returns have fat tails and that is exactly what
    ruin calculations get wrong.

    Leverage multiplies returns; a levered path that touches -100% is dead and
    stays dead, which is why leverage does not scale outcomes symmetrically.
    """
    r = pd.Series(returns).dropna().to_numpy()
    if len(r) < 30:
        return float("nan")

    n_steps = int(horizon_years * periods_per_year)
    rng = np.random.default_rng(seed)
    draws = rng.choice(r, size=(n_sims, n_steps), replace=True) * leverage

    # A path that loses everything is wiped out; clip so equity cannot go negative.
    equity = np.cumprod(1.0 + np.maximum(draws, -1.0), axis=1)
    peak = np.maximum.accumulate(equity, axis=1)

    # Equity of exactly 0 (a full wipeout on the first bar) makes this 0/0. Left
    # as NaN it would compare False and report certain ruin as no ruin, so a
    # zero peak is written as total loss, which is what it is.
    ratio = np.divide(equity, peak, out=np.zeros_like(equity), where=peak > 0)
    worst = ratio.min(axis=1)
    return float((worst <= 1.0 - ruin_drawdown).mean())


def leverage_table(returns, levels=(1, 2, 3, 5), horizon_years=1.0,
                   periods_per_year=365, n_sims=5000):
    """Ruin probability at each leverage level. Shows why leverage is not linear."""
    rows = []
    for lev in levels:
        rows.append({
            "leverage": lev,
            "p_down_20pct": risk_of_ruin(returns, 0.20, horizon_years, lev, periods_per_year, n_sims),
            "p_down_50pct": risk_of_ruin(returns, 0.50, horizon_years, lev, periods_per_year, n_sims),
            "p_wiped_out": risk_of_ruin(returns, 0.95, horizon_years, lev, periods_per_year, n_sims),
        })
    return pd.DataFrame(rows)


def kelly_fraction(returns, periods_per_year=365):
    """Growth-optimal position size, and the practical fraction of it.

    Full Kelly maximises long-run growth but produces drawdowns almost nobody
    tolerates, and it is computed from an ESTIMATED edge — if the estimate is
    too high, full Kelly is over-betting and loses money. Half Kelly or less is
    the usual practice. Negative means the edge is negative: do not trade it.
    """
    r = pd.Series(returns).dropna()
    variance = float(r.var(ddof=1))
    if variance <= 0:
        return {"kelly": 0.0, "half_kelly": 0.0, "annual_edge": 0.0}
    kelly = float(r.mean() / variance)
    return {
        "kelly": kelly,
        "half_kelly": kelly / 2.0,
        "annual_edge": float(r.mean() * periods_per_year),
    }
