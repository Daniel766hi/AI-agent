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



def test_rejects_zero_price():
    """A zero price makes the next return infinite — it would top any screen."""
    close = data.synthetic(n=300, seed=10)["close"].copy()
    close.iloc[100] = 0.0
    try:
        backtest(close, pd.Series(1.0, index=close.index))
    except ValueError as exc:
        assert "non-positive" in str(exc)
        return
    raise AssertionError("a zero price must be rejected, not modelled")


def test_rejects_negative_and_missing_prices():
    base = data.synthetic(n=300, seed=11)["close"]
    for label, value in [("negative", -5.0), ("missing", float("nan"))]:
        close = base.copy()
        close.iloc[100] = value
        try:
            backtest(close, pd.Series(1.0, index=close.index))
        except ValueError:
            continue
        raise AssertionError(f"a {label} price must be rejected")


def test_rejects_empty_series():
    try:
        backtest(pd.Series([], dtype=float), pd.Series([], dtype=float))
    except ValueError:
        return
    raise AssertionError("an empty series must be rejected")


def test_bad_price_error_names_the_location():
    """The message has to be actionable — which bar, and what was wrong with it."""
    close = data.synthetic(n=200, seed=12)["close"].copy()
    close.iloc[57] = 0.0
    try:
        backtest(close, pd.Series(1.0, index=close.index))
    except ValueError as exc:
        assert str(close.index[57]) in str(exc), f"error must name the bad bar: {exc}"
        return
    raise AssertionError("expected rejection")


def test_load_csv_drops_missing_closes():
    """Holidays and halts leave blank closes; those are ordinary and droppable."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "gappy.csv"
        df = data.synthetic(n=100, seed=13).reset_index(names="date")
        df.loc[[10, 20, 30], "close"] = None
        df.to_csv(path, index=False)

        loaded = data.load_csv(path)
        assert len(loaded) == 97, f"expected 3 rows dropped, got {len(loaded)}"
        assert loaded["close"].notna().all()
        # and the cleaned series must now pass the backtest guard
        backtest(loaded["close"], pd.Series(1.0, index=loaded.index))


def test_positive_period_rate_is_not_a_trade_win_rate():
    """It counts exposed periods, not trades. The name must not overclaim."""
    close = data.synthetic(n=600, seed=14)["close"]
    result = backtest(close, REGISTRY["sma_cross"][0](close, 10, 50))
    m = metrics(result["net_return"])

    assert "hit_rate" not in m, "the misleading name must be gone"
    assert 0.0 <= m["positive_period_rate"] <= 1.0
    n_trades = int((result["turnover"] > 0).sum())
    n_exposed = int((result["net_return"] != 0).sum())
    assert n_exposed > n_trades, "periods and trades differ — that is why it was renamed"



def test_walk_forward_carries_position_across_folds():
    """No phantom round trip at a fold seam.

    Backtesting folds separately forces the position flat at each boundary, so a
    strategy holding straight through a seam would show a spurious exit and
    re-entry. Turnover must match a single continuous backtest of the same
    stitched signal.
    """
    close = data.synthetic(n=2000, seed=30)["close"]
    fn, grid = REGISTRY["sma_cross"]
    oos, folds, _, _ = walk_forward(close, fn, grid, n_folds=5)

    # Rebuild the identical stitched signal and backtest it in one pass.
    from quant.validate import _param_combos
    n, combos = len(close), _param_combos(grid)
    test_len = int(n / (5 + 2.0)); train_len = int(test_len * 2.0)
    signals = []
    for f in range(5):
        ts, te = f * test_len, f * test_len + train_len
        tend = min(te + test_len, n)
        train, test = close.iloc[ts:te], close.iloc[te:tend]
        best, bs = combos[0], float("-inf")
        for params in combos:
            sh = metrics(backtest(train, fn(train, **params))["net_return"])["sharpe"]
            if sh > bs:
                best, bs = params, sh
        signals.append(fn(close.iloc[ts:tend], **best).iloc[-len(test):])

    stitched_signal = pd.concat(signals)
    one_pass = backtest(close.loc[stitched_signal.index], stitched_signal)
    assert abs(float(one_pass["net_return"].sum()) - float(oos.sum())) < 1e-12, \
        "walk-forward must equal one continuous backtest of the stitched signal"


def test_walk_forward_oos_windows_are_contiguous():
    """Stitched returns must be one unbroken span — no gaps, no overlaps."""
    close = data.synthetic(n=2000, seed=31)["close"]
    oos, folds, benchmark, _ = walk_forward(close, *REGISTRY["breakout"], n_folds=4)

    assert not oos.index.duplicated().any(), "folds overlapped"
    positions = close.index.get_indexer(oos.index)
    assert (np.diff(positions) == 1).all(), "out-of-sample span has a gap"
    assert len(benchmark) == len(oos)


def test_fold_rows_sum_to_the_whole():
    """Per-fold rows are slices of the same run, so they must tile it exactly."""
    close = data.synthetic(n=1800, seed=32)["close"]
    oos, folds, _, _ = walk_forward(close, *REGISTRY["sma_cross"], n_folds=4)

    covered = 0
    for _, row in folds.iterrows():
        covered += len(oos.loc[row["test_start"]:row["test_end"]])
    assert covered == len(oos), f"folds covered {covered} of {len(oos)} bars"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
