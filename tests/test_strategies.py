"""Checks on strategy behaviour, especially claims made in docstrings."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data
from quant.backtest import backtest, metrics
from quant.strategies import REGISTRY, ts_momentum, vol_target
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward


def test_garch_clusters_vol_but_not_direction():
    """The generator must have the property it claims, or tests using it are void."""
    acf1 = lambda x: float(np.corrcoef(x[:-1], x[1:])[0, 1])
    garch = data.synthetic_garch(n=3000, seed=1)["close"].pct_change().dropna().to_numpy()
    gbm = data.synthetic(n=3000, seed=1)["close"].pct_change().dropna().to_numpy()

    assert acf1(np.abs(garch)) > 0.08, "GARCH must show volatility clustering"
    assert abs(acf1(np.abs(gbm))) < 0.05, "GBM must not"
    assert abs(acf1(garch)) < 0.05, "direction must stay unforecastable in GARCH"


def test_garch_rejects_nonstationary_params():
    try:
        data.synthetic_garch(alpha=0.5, beta=0.6)
    except ValueError:
        return
    raise AssertionError("alpha+beta >= 1 must be rejected")


def test_vol_target_hits_its_target():
    """Realised vol should land near the target, well below the raw asset's."""
    close = data.synthetic_garch(n=2000, base_annual_vol=0.6, seed=3)["close"]
    hold = pd.Series(1.0, index=close.index)
    sized = metrics(backtest(close, vol_target(hold, close, target_annual_vol=0.4))["net_return"])
    plain = metrics(backtest(close, hold)["net_return"])

    assert sized["volatility"] < plain["volatility"], "sizing must reduce realised vol"
    assert 0.3 < sized["volatility"] < 0.5, f"should land near the 40% target, got {sized['volatility']:.1%}"


def test_vol_target_reduces_drawdown():
    """The measured benefit. Holds across paths, not just a lucky seed."""
    better = 0
    for seed in range(20):
        close = data.synthetic_garch(n=2000, annual_drift=0.25, seed=seed)["close"]
        hold = pd.Series(1.0, index=close.index)
        plain = metrics(backtest(close, hold)["net_return"])["max_drawdown"]
        sized = metrics(backtest(close, vol_target(hold, close))["net_return"])["max_drawdown"]
        better += sized > plain            # drawdowns are negative; larger is shallower
    assert better >= 18, f"drawdown improved on only {better}/20 paths"


def test_vol_target_never_levers_by_default():
    close = data.synthetic_garch(n=1000, base_annual_vol=0.05, seed=4)["close"]
    # Very calm asset: the naive scale factor would be far above 1.
    assert vol_target(pd.Series(1.0, index=close.index), close, target_annual_vol=0.4).max() <= 1.0


def test_vol_target_claims_no_alpha():
    """Guards the honest finding: this must NOT manufacture edge from noise.

    If a future change makes vol targeting look profitable on data with no
    forecastable direction, that change introduced a lookahead bug.
    """
    significant = 0
    for seed in range(6):
        close = data.synthetic_garch(n=2000, seed=100 + seed)["close"]
        fn, grid = REGISTRY["ts_momentum_vol_targeted"]
        oos, _, bench, n_trials = walk_forward(close, fn, grid, n_folds=4)
        p, _ = block_bootstrap_pvalue(oos, bench, n_boot=1500)
        significant += deflate(p, n_trials) < 0.05
    assert significant <= 2, f"{significant}/6 noise paths showed edge — likely a leak"


def test_ts_momentum_is_causal():
    """Position must depend only on past prices, never on a future one."""
    close = data.synthetic(n=500, seed=5)["close"]
    signal = ts_momentum(close, lookback=90)

    altered = close.copy()
    altered.iloc[300:] *= 3.0                    # change only the future
    altered_signal = ts_momentum(altered, lookback=90)
    assert (signal.iloc[:300] == altered_signal.iloc[:300]).all(), \
        "changing future prices altered a past signal — lookahead"


def test_every_registry_strategy_runs():
    close = data.synthetic(n=800, seed=6)["close"]
    for name, (fn, grid) in REGISTRY.items():
        params = {k: v[0] for k, v in grid.items()}
        signal = fn(close, **params)
        assert len(signal) == len(close), f"{name} returned wrong length"
        assert signal.notna().all(), f"{name} left NaNs in the signal"
        assert signal.abs().max() <= 1.0, f"{name} exceeded full position"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
