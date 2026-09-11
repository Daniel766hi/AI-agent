"""Calibration of the significance test.

Every verdict in this repo rests on block_bootstrap_pvalue. If it is
mis-calibrated, every "survives out-of-sample" conclusion is worthless, so
these checks test the statistic itself rather than the code around it.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant.validate import _block_length, block_bootstrap_pvalue, deflate


def _ar1(rng, n, rho, sd=0.02):
    """AR(1) noise: autocorrelated, but with no true difference in mean."""
    e = rng.normal(0, sd, n)
    x = np.empty(n)
    x[0] = e[0]
    for i in range(1, n):
        x[i] = rho * x[i - 1] + e[i]
    return x


def test_block_length_scales_with_dependence():
    rng = np.random.default_rng(0)
    iid = rng.normal(0, .02, 800)
    baseline = max(1, int(round(800 ** (1 / 3))))

    assert _block_length(iid) == baseline, "independent data needs no extra block length"
    assert _block_length(_ar1(rng, 800, 0.85)) > baseline, \
        "strong autocorrelation must lengthen the block"
    assert _block_length(_ar1(rng, 800, 0.85)) <= 800 // 8, "block must stay a small fraction of n"


def test_block_length_survives_degenerate_input():
    """A constant series has undefined autocorrelation; must not produce NaN."""
    flat = np.zeros(200)
    assert _block_length(flat) >= 1
    assert _block_length(np.array([1.0, 2.0])) >= 1


def test_no_false_positives_under_the_null():
    """With no true difference, p<0.05 should fire about 5% of the time.

    Bounded loosely: 120 trials carry real Monte Carlo error, so this catches
    gross mis-calibration, not a point estimate.
    """
    rng = np.random.default_rng(1)
    hits = 0
    for i in range(120):
        a, b = rng.normal(0, .02, 500), rng.normal(0, .02, 500)
        p, _ = block_bootstrap_pvalue(a, b, n_boot=400, seed=i)
        hits += p < .05
    assert hits / 120 < 0.15, f"false positive rate {hits/120:.1%} — test is manufacturing significance"


def test_autocorrelation_does_not_break_calibration():
    """The case a plain t-test gets badly wrong (over 20% false positives at rho=0.6)."""
    rng = np.random.default_rng(2)
    hits = 0
    for i in range(120):
        p, _ = block_bootstrap_pvalue(_ar1(rng, 500, 0.6), _ar1(rng, 500, 0.6), n_boot=400, seed=i)
        hits += p < .05
    assert hits / 120 < 0.20, f"false positive rate {hits/120:.1%} under autocorrelation"


def test_a_real_edge_is_detected():
    """Calibration is worthless if the test can never find anything."""
    rng = np.random.default_rng(3)
    detected = 0
    for i in range(30):
        benchmark = rng.normal(0, .02, 500)
        strategy = benchmark + 0.003          # a genuine, large edge
        p, edge = block_bootstrap_pvalue(strategy, benchmark, n_boot=400, seed=i)
        detected += p < .05
        assert edge > 0
    assert detected >= 28, f"only detected a real edge {detected}/30 times"


def test_direction_matters():
    """One-sided: a strategy that loses to the benchmark must not look significant."""
    rng = np.random.default_rng(4)
    benchmark = rng.normal(0, .02, 500)
    worse = benchmark - 0.003
    p, edge = block_bootstrap_pvalue(worse, benchmark, n_boot=600)
    assert edge < 0 and p > 0.5, f"a losing strategy returned p={p:.3f}"


def test_too_little_data_returns_nan():
    p, edge = block_bootstrap_pvalue(np.zeros(10), np.zeros(10))
    assert np.isnan(p) and np.isnan(edge), "must refuse to test on too few points"


def test_deflation_composes_with_the_bootstrap():
    """A borderline raw p must not survive a wide search."""
    rng = np.random.default_rng(5)
    a, b = rng.normal(0.0004, .02, 600), rng.normal(0, .02, 600)
    p, _ = block_bootstrap_pvalue(a, b, n_boot=600)
    assert deflate(p, 50) >= p, "deflation must never make a result look better"
    assert deflate(p, 200) > 0.5 or p > 0.5, "a wide search must wash out a weak signal"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
