"""Self-checks for the engine. Run: python tests/test_quant.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data
from quant.backtest import backtest, buy_and_hold, metrics
from quant.strategies import REGISTRY
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward


def test_no_lookahead():
    """A signal that knows tomorrow must NOT be able to profit from it."""
    close = data.synthetic(n=500, seed=1)["close"]
    future = (close.shift(-1) > close).astype(float)   # perfect foresight
    result = backtest(close, future, fee_bps=0, slippage_bps=0)
    # The shift inside backtest turns foresight into a same-bar signal, so the
    # position on bar t reflects t-1's guess about t. It must not be clairvoyant.
    assert result["position"].iloc[1] == future.iloc[0], "position must lag signal by one bar"
    aligned = pd.concat([result["position"], future.shift(1)], axis=1).dropna()
    assert (aligned.iloc[:, 0] == aligned.iloc[:, 1]).all(), "lookahead leak in execution"


def test_costs_reduce_returns():
    close = data.synthetic(n=500, seed=2)["close"]
    signal = REGISTRY["sma_cross"][0](close, fast=5, slow=20)
    free = backtest(close, signal, fee_bps=0, slippage_bps=0)["net_return"].sum()
    paid = backtest(close, signal, fee_bps=10, slippage_bps=5)["net_return"].sum()
    assert paid < free, "costs must reduce returns"


def test_buy_and_hold_tracks_asset():
    close = data.synthetic(n=300, seed=3)["close"]
    result = buy_and_hold(close)
    actual = close.iloc[-1] / close.iloc[0] - 1
    # One entry cost (15bps) separates the two.
    assert abs(result["equity"].iloc[-1] - 1 - actual) < 0.01, "buy & hold must track the asset"


def test_metrics_sane():
    flat = pd.Series([0.0] * 100)
    m = metrics(flat)
    assert m["sharpe"] == 0.0 and m["max_drawdown"] == 0.0

    steady = pd.Series([0.001] * 365)
    m = metrics(steady, periods_per_year=365)
    assert 0.43 < m["cagr"] < 0.45, f"CAGR wrong: {m['cagr']}"
    assert m["max_drawdown"] == 0.0


def test_walk_forward_is_out_of_sample():
    close = data.synthetic(n=2000, seed=4)["close"]
    fn, grid = REGISTRY["sma_cross"]
    oos, folds, benchmark, n_trials = walk_forward(close, fn, grid, n_folds=4)
    assert len(folds) == 4 and n_trials == 9
    assert len(oos) == len(benchmark)
    assert oos.index.is_monotonic_increasing
    assert not oos.index.duplicated().any(), "folds must not overlap"


def test_no_edge_on_random_walk():
    """The headline check: random data must not produce significant edge.

    Run across several seeds. At p<0.05 we tolerate the odd false positive by
    construction, but a majority of seeds showing 'edge' means the engine lies.
    """
    fn, grid = REGISTRY["sma_cross"]
    significant = 0
    for seed in range(8):
        close = data.synthetic(n=2000, seed=seed)["close"]
        oos, _, benchmark, n_trials = walk_forward(close, fn, grid, n_folds=4)
        p, _ = block_bootstrap_pvalue(oos, benchmark, n_boot=2000)
        if deflate(p, n_trials) < 0.05:
            significant += 1
    assert significant <= 2, f"{significant}/8 random series showed edge — engine has a leak"


def test_deflate():
    assert deflate(0.05, 1) == 0.05
    assert deflate(0.01, 10) > 0.09          # searching 10 configs costs you
    assert np.isnan(deflate(float("nan"), 5))


def test_short_series_rejected():
    close = data.synthetic(n=50, seed=9)["close"]
    fn, grid = REGISTRY["sma_cross"]
    try:
        walk_forward(close, fn, grid, n_folds=5)
    except ValueError:
        return
    raise AssertionError("should reject a series too short to split")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
