#!/usr/bin/env python3
"""Screen one strategy across many assets, with honest multiple-testing control.

  python screen.py --synthetic 50 --strategy breakout
  python screen.py --coingecko-top 30 --strategy sma_cross
  python screen.py --yahoo BBCA.JK TLKM.JK ASII.JK BBRI.JK --strategy breakout
  python screen.py --csv-dir data/ --strategy rsi_reversion

Screening N assets means N times more chances to find a winner by luck. This
charges you for every one of them: the reported p-value is deflated by
(assets x parameter combinations), not just the combinations.
"""
import argparse
import os
import sys
import time

from quant import data
from quant.backtest import metrics
from quant.strategies import REGISTRY
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward


def evaluate(close, strategy, folds=4):
    """Walk-forward one asset. Returns (metrics, raw p-value, n_param_combos)."""
    fn, grid = REGISTRY[strategy]
    oos, _, benchmark, n_combos = walk_forward(close, fn, grid, n_folds=folds)
    p_raw, _ = block_bootstrap_pvalue(oos, benchmark, n_boot=3000)
    return metrics(oos), metrics(benchmark), p_raw, n_combos


def _progress(done, total, label, ok):
    mark = "." if ok else "x"
    end = "\n" if done == total else ""
    print(f"\r  fetching {done}/{total} {mark} {label[:18]:<18}", end=end, file=sys.stderr, flush=True)


def _report_failures(failures):
    for label, reason in failures.items():
        print(f"  skip {label}: {reason}", file=sys.stderr)


def _evaluate_one(job):
    """Worker entry point. Must be module level to survive pickling.

    Returns a plain dict rather than raising, so one bad asset cannot take the
    pool down with it — the screen reports the skip and carries on.
    """
    label, close, strategy, folds = job
    try:
        strat, bench, p_raw, n_combos = evaluate(close, strategy, folds)
        return {"asset": label, "ok": True, "sharpe": strat["sharpe"],
                "bench_sharpe": bench["sharpe"], "total_return": strat["total_return"],
                "max_dd": strat["max_drawdown"], "p_raw": p_raw, "n_combos": n_combos}
    except (ValueError, KeyError) as exc:
        return {"asset": label, "ok": False, "error": str(exc)}


def evaluate_all(assets, strategy, folds=4, workers=None):
    """Evaluate every asset, across processes when it is worth the overhead.

    Each asset is independent and each bootstrap is seeded, so results do not
    depend on how the work is divided — a parallel screen and a serial one
    return the same numbers. A test asserts that.
    """
    jobs = [(label, close, strategy, folds) for label, close in assets]
    if workers is None:
        workers = min(os.cpu_count() or 1, 8)

    # Process startup costs more than the work itself on a handful of assets.
    if workers <= 1 or len(jobs) < 8:
        return [_evaluate_one(job) for job in jobs]

    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_evaluate_one, jobs, chunksize=max(1, len(jobs) // (workers * 4))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    universe = ap.add_mutually_exclusive_group(required=True)
    universe.add_argument("--synthetic", type=int, metavar="N", help="N random-walk assets (the null)")
    universe.add_argument("--coingecko-top", type=int, metavar="N", help="top N coins by market cap")
    universe.add_argument("--yahoo", nargs="+", metavar="SYMBOL", help="Yahoo tickers, e.g. BBCA.JK AAPL")
    universe.add_argument("--csv-dir", help="directory of OHLCV CSVs")

    ap.add_argument("--strategy", default="breakout", choices=sorted(REGISTRY))
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--days", type=int, default=730, help="CoinGecko history length")
    ap.add_argument("--workers", type=int, default=None,
                    help="processes for the maths (default: one per core, max 8)")
    ap.add_argument("--fetch-workers", type=int, default=4,
                    help="concurrent downloads; raise only with an API key")
    args = ap.parse_args()

    # Build the universe as (label, close series) pairs.
    assets = []
    if args.synthetic:
        assets = [(f"noise_{i:03d}", data.synthetic(n=1200, seed=5000 + i)["close"])
                  for i in range(args.synthetic)]
    elif args.coingecko_top:
        ids = data.coingecko_top(args.coingecko_top)
        frames, failures = data.fetch_many(ids, days=args.days, workers=args.fetch_workers,
                                           on_progress=_progress)
        assets = [(c, f["close"]) for c, f in frames]
        _report_failures(failures)
    elif args.yahoo:
        frames, failures = data.fetch_many_yahoo(args.yahoo, workers=args.fetch_workers,
                                                 on_progress=_progress)
        assets = [(s, f["close"]) for s, f in frames]
        _report_failures(failures)
    else:
        from pathlib import Path
        for path in sorted(Path(args.csv_dir).glob("*.csv")):
            try:
                assets.append((path.stem, data.load_csv(path)["close"]))
            except Exception as exc:
                print(f"  skip {path.name}: {exc}", file=sys.stderr)

    if not assets:
        sys.exit("No assets loaded.")

    started = time.time()
    outcomes = evaluate_all(assets, args.strategy, args.folds, workers=args.workers)
    rows = [o for o in outcomes if o["ok"]]
    n_combos = rows[0]["n_combos"] if rows else 0
    for failed in (o for o in outcomes if not o["ok"]):
        print(f"  skip {failed['asset']}: {failed['error']}", file=sys.stderr)
    elapsed = time.time() - started

    if not rows:
        sys.exit("No asset had enough history to validate.")

    # THE correction that matters: every asset screened is another trial.
    total_trials = len(rows) * n_combos
    for row in rows:
        row["p_naive"] = deflate(row["p_raw"], n_combos)        # what a careless screen reports
        row["p_honest"] = deflate(row["p_raw"], total_trials)   # what you actually earned

    rows.sort(key=lambda r: r["p_raw"])

    print(f"\n{'=' * 82}")
    print(f"  {args.strategy} screened across {len(rows)} assets, {n_combos} configs each")
    print(f"  {total_trials} total trials — that is the number the p-value must survive")
    print(f"  evaluated in {elapsed:.1f}s")
    print(f"{'=' * 82}\n")
    print(f"{'Asset':<22}{'Sharpe':>9}{'vs hold':>9}{'Return':>10}{'MaxDD':>9}{'p (naive)':>12}{'p (honest)':>12}")
    print("-" * 82)
    for row in rows[:20]:
        print(f"{row['asset'][:21]:<22}{row['sharpe']:>9.2f}{row['bench_sharpe']:>9.2f}"
              f"{row['total_return']:>10.1%}{row['max_dd']:>9.1%}"
              f"{row['p_naive']:>12.4f}{row['p_honest']:>12.4f}")
    if len(rows) > 20:
        print(f"  ... {len(rows) - 20} more")

    naive_hits = [r for r in rows if r["p_naive"] < 0.05]
    honest_hits = [r for r in rows if r["p_honest"] < 0.05]

    print(f"\nLook significant per-asset : {len(naive_hits)}")
    print(f"Survive the full screen    : {len(honest_hits)}")
    if honest_hits:
        print("\n  -> Survived: " + ", ".join(r["asset"] for r in honest_hits))
        print("     Paper-trade before risking anything. Still not proof.")
    elif naive_hits:
        print(f"\n  -> Nothing survives {total_trials} trials. The {len(naive_hits)} that looked")
        print("     significant per-asset are what luck produces at this many attempts.")
    else:
        print(f"\n  -> No edge found, before or after correction. The honest and usual result.")
    print()


if __name__ == "__main__":
    main()
