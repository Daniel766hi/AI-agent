"""Checks on the cost and survival arithmetic."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data
from quant.backtest import backtest
from quant.risk import breakeven, cost_drag, kelly_fraction, leverage_table, risk_of_ruin
from quant.strategies import REGISTRY


def test_cost_drag_arithmetic():
    # 250 round trips at 15bps: each pays the cost twice.
    assert abs(cost_drag(250, 10, 5) - 0.75) < 1e-9
    assert abs(cost_drag(12, 10, 5) - 0.036) < 1e-9
    assert cost_drag(0) == 0.0
    assert cost_drag(100, 30, 20) > cost_drag(100, 10, 5), "higher fees must cost more"


def test_breakeven_counts_trades_and_costs():
    close = data.synthetic(n=1460, seed=1)["close"]   # 4 years
    fn, _ = REGISTRY["sma_cross"]
    result = backtest(close, fn(close, fast=20, slow=100))
    stats = breakeven(result)

    assert abs(stats["years"] - 4.0) < 0.05
    assert stats["annual_cost_drag"] > 0, "any strategy that trades must show cost"
    assert 0.0 <= stats["time_in_market"] <= 1.0
    assert stats["round_trips_per_year"] > 0


def test_breakeven_zero_for_buy_and_hold():
    """Holding trades once; its ongoing drag is ~zero and it is always invested."""
    close = data.synthetic(n=1095, seed=2)["close"]
    result = backtest(close, pd.Series(1.0, index=close.index))
    stats = breakeven(result)
    assert stats["round_trips_per_year"] < 0.4, "holding should barely trade"
    assert stats["time_in_market"] > 0.99
    assert stats["annual_cost_drag"] < 0.01


def test_risk_of_ruin_rises_with_leverage():
    """The core survival claim: leverage does not scale outcomes symmetrically."""
    close = data.synthetic(n=2000, annual_vol=0.6, seed=3)["close"]
    returns = backtest(close, pd.Series(1.0, index=close.index))["net_return"]

    p1 = risk_of_ruin(returns, 0.5, leverage=1, n_sims=3000)
    p3 = risk_of_ruin(returns, 0.5, leverage=3, n_sims=3000)
    assert p3 > p1, f"3x leverage must be riskier than 1x ({p3:.2f} vs {p1:.2f})"

    wipe1 = risk_of_ruin(returns, 0.95, leverage=1, n_sims=3000)
    wipe5 = risk_of_ruin(returns, 0.95, leverage=5, n_sims=3000)
    assert wipe5 > wipe1, "5x must carry more wipeout risk than 1x"


def test_risk_of_ruin_bounds_and_monotonicity():
    close = data.synthetic(n=1500, seed=4)["close"]
    returns = backtest(close, pd.Series(1.0, index=close.index))["net_return"]

    shallow = risk_of_ruin(returns, 0.10, n_sims=2000)
    deep = risk_of_ruin(returns, 0.80, n_sims=2000)
    assert 0.0 <= deep <= shallow <= 1.0, "a deeper drawdown cannot be more likely than a shallow one"


def test_risk_of_ruin_needs_enough_data():
    assert np.isnan(risk_of_ruin(pd.Series([0.01] * 5)))


def test_equity_never_goes_negative_under_leverage():
    """A wiped-out path must stay wiped out, not rebound from negative equity."""
    brutal = pd.Series([-0.5] * 200)      # -50% every bar
    p = risk_of_ruin(brutal, 0.95, leverage=5, horizon_years=0.5, n_sims=500)
    assert p == 1.0, "guaranteed losses must give certain ruin, not a nonsense number"


def test_kelly_is_zero_for_negative_edge():
    losing = pd.Series(np.random.default_rng(0).normal(-0.002, 0.02, 1000))
    assert kelly_fraction(losing)["kelly"] < 0, "negative edge must not suggest a position"


def test_kelly_scales_with_edge():
    rng = np.random.default_rng(1)
    weak = pd.Series(rng.normal(0.0005, 0.02, 2000))
    strong = pd.Series(rng.normal(0.0030, 0.02, 2000))
    assert kelly_fraction(strong)["kelly"] > kelly_fraction(weak)["kelly"]
    assert kelly_fraction(weak)["half_kelly"] * 2 == kelly_fraction(weak)["kelly"]


def test_leverage_table_shape():
    close = data.synthetic(n=1200, seed=5)["close"]
    returns = backtest(close, pd.Series(1.0, index=close.index))["net_return"]
    table = leverage_table(returns, levels=(1, 2, 4), n_sims=800)
    assert list(table["leverage"]) == [1, 2, 4]
    assert table["p_down_50pct"].is_monotonic_increasing, "risk must rise with leverage"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
