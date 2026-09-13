"""Parallel screening must be faster without being different.

Speed is worthless here if it changes a verdict. These checks pin that a screen
returns the same numbers however the work is divided, and that one bad asset
cannot take the run down with it.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data
from screen import _evaluate_one, evaluate_all


def _assets(n=12, bars=900, seed0=9000):
    return [(f"a{i:03d}", data.synthetic(n=bars, seed=seed0 + i)["close"]) for i in range(n)]


def test_parallel_matches_serial_exactly():
    """Every figure must be identical regardless of worker count."""
    assets = _assets(12)
    serial = evaluate_all(assets, "breakout", folds=4, workers=1)
    parallel = evaluate_all(assets, "breakout", folds=4, workers=3)

    assert [r["asset"] for r in serial] == [r["asset"] for r in parallel], "order changed"
    for a, b in zip(serial, parallel):
        for key in ("sharpe", "bench_sharpe", "total_return", "max_dd", "p_raw", "n_combos"):
            assert a[key] == b[key], f"{a['asset']} {key}: {a[key]} != {b[key]}"


def test_order_follows_the_input_not_completion():
    """Workers finish out of order; the report must not."""
    assets = _assets(10)
    result = evaluate_all(assets, "breakout", folds=4, workers=3)
    assert [r["asset"] for r in result] == [label for label, _ in assets]


def test_one_bad_asset_does_not_kill_the_run():
    """A corrupt feed is normal. It must be skipped, not fatal."""
    assets = _assets(10)
    broken = assets[4][1].copy()
    broken.iloc[300] = 0.0                    # the zero price backtest() refuses
    assets[4] = (assets[4][0], broken)

    for workers in (1, 3):
        result = evaluate_all(assets, "breakout", folds=4, workers=workers)
        assert len(result) == 10, "every asset must be accounted for"
        failed = [r for r in result if not r["ok"]]
        assert len(failed) == 1 and failed[0]["asset"] == "a004"
        assert "non-positive" in failed[0]["error"]
        assert sum(r["ok"] for r in result) == 9


def test_too_short_a_series_is_skipped_not_raised():
    assets = [("tiny", data.synthetic(n=60, seed=1)["close"])]
    result = evaluate_all(assets, "breakout", folds=4, workers=1)
    assert not result[0]["ok"] and "short" in result[0]["error"].lower()


def test_small_batches_stay_serial():
    """Process startup costs more than the work on a handful of assets."""
    assets = _assets(3, bars=600)
    result = evaluate_all(assets, "breakout", folds=4, workers=4)
    assert len(result) == 3 and all(r["ok"] for r in result)


def test_worker_entry_point_returns_rather_than_raises():
    """The pool must never see an exception — a raise loses the whole batch."""
    close = data.synthetic(n=600, seed=5)["close"].copy()
    close.iloc[100] = -1.0
    outcome = _evaluate_one(("bad", close, "breakout", 4))
    assert outcome["ok"] is False and outcome["asset"] == "bad"
    assert "error" in outcome


def test_parallel_is_actually_faster_on_a_real_batch():
    """Guards against the pool silently degrading to serial.

    Bounded loosely — CI machines vary and this asserts a speedup exists, not
    a particular one. Skips rather than fails on a single-core machine, where
    there is nothing to parallelise.
    """
    import os
    if (os.cpu_count() or 1) < 2:
        return

    assets = _assets(24, bars=900)
    t = time.perf_counter(); evaluate_all(assets, "breakout", folds=4, workers=1)
    serial = time.perf_counter() - t
    t = time.perf_counter(); evaluate_all(assets, "breakout", folds=4, workers=4)
    parallel = time.perf_counter() - t

    assert parallel < serial, f"parallel {parallel:.2f}s was not faster than serial {serial:.2f}s"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
