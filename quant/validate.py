"""Out-of-sample validation and significance testing.

In-sample backtests are free to look brilliant; the only number worth reading is
one the strategy never got to train on. Everything here exists to make the
result harder to fool yourself with.
"""
import itertools

import numpy as np
import pandas as pd

from .backtest import backtest, metrics


def _param_combos(grid):
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[k] for k in keys))]


def walk_forward(close, strategy_fn, param_grid, n_folds=5, train_ratio=2.0,
                 fee_bps=10.0, slippage_bps=5.0, periods_per_year=365):
    """Rolling walk-forward: fit params on a training window, trade the next window.

    Splits the series into `n_folds` test windows. Before each one, parameters
    are chosen by Sharpe on the preceding training window only. The returns that
    come back are stitched from test windows exclusively, so no bar contributed
    to the parameters that traded it.
    """
    close = pd.Series(close).astype(float)
    combos = _param_combos(param_grid)
    n = len(close)

    # Each fold: train window of `train_ratio` x test length, then the test window.
    test_len = int(n / (n_folds + train_ratio))
    train_len = int(test_len * train_ratio)
    if test_len < 30 or train_len < 30:
        raise ValueError(
            f"Series too short: {n} bars gives {train_len}-bar train / {test_len}-bar test. "
            "Use more history or fewer folds."
        )

    oos_returns, fold_rows = [], []
    for fold in range(n_folds):
        train_start = fold * test_len
        train_end = train_start + train_len
        test_end = min(train_end + test_len, n)
        if test_end - train_end < 10:
            break

        train = close.iloc[train_start:train_end]
        test = close.iloc[train_end:test_end]

        best, best_sharpe = combos[0], -np.inf
        for params in combos:
            result = backtest(train, strategy_fn(train, **params), fee_bps, slippage_bps, periods_per_year)
            sharpe = metrics(result["net_return"], periods_per_year)["sharpe"]
            if sharpe > best_sharpe:
                best, best_sharpe = params, sharpe

        # Warm up indicators on training history, then keep only test-window bars.
        warmup = close.iloc[train_start:test_end]
        signal = strategy_fn(warmup, **best).iloc[-len(test):]
        result = backtest(test, signal, fee_bps, slippage_bps, periods_per_year)

        oos_returns.append(result["net_return"])
        fold_rows.append({
            "fold": fold,
            "train_start": str(train.index[0].date()),
            "test_start": str(test.index[0].date()),
            "test_end": str(test.index[-1].date()),
            "params": best,
            "train_sharpe": round(best_sharpe, 3),
            "test_sharpe": round(metrics(result["net_return"], periods_per_year)["sharpe"], 3),
            "test_return": round(metrics(result["net_return"], periods_per_year)["total_return"], 4),
        })

    if not oos_returns:
        raise ValueError("No folds produced results; series too short.")

    stitched = pd.concat(oos_returns)
    benchmark = close.pct_change().reindex(stitched.index).fillna(0.0)
    return stitched, pd.DataFrame(fold_rows), benchmark, len(combos)


def block_bootstrap_pvalue(strategy_returns, benchmark_returns, n_boot=10_000, seed=0):
    """One-sided p-value for 'strategy beats benchmark', via moving-block bootstrap.

    Returns are autocorrelated and fat-tailed, so a plain t-test overstates
    significance. Resampling contiguous blocks preserves the local dependence
    structure. H0: mean(strategy - benchmark) <= 0.
    """
    diff = (pd.Series(strategy_returns) - pd.Series(benchmark_returns)).dropna().to_numpy()
    n = len(diff)
    if n < 30:
        return float("nan"), float("nan")

    observed = diff.mean()
    block = max(1, int(round(n ** (1 / 3))))     # standard MBB block length
    n_blocks = int(np.ceil(n / block))
    centred = diff - observed                     # impose H0: true mean is zero

    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n - block + 1, size=(n_boot, n_blocks))
    offsets = np.arange(block)
    samples = centred[(starts[:, :, None] + offsets).reshape(n_boot, -1)[:, :n]]

    p = float((samples.mean(axis=1) >= observed).mean())
    return p, float(observed)


def deflate(p_value, n_trials):
    """Sidak correction: the p-value you earned after searching `n_trials` configs.

    Searching 9 parameter sets and reporting the best one's raw p-value is how
    backtests lie. Assumes roughly independent trials, which is conservative-ish
    for overlapping parameter grids.
    """
    if np.isnan(p_value) or n_trials <= 1:
        return p_value
    return float(1.0 - (1.0 - p_value) ** n_trials)
