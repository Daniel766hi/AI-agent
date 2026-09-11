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
import sys

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
    args = ap.parse_args()

    # Build the universe as (label, close series) pairs.
    assets = []
    if args.synthetic:
        assets = [(f"noise_{i:03d}", data.synthetic(n=1200, seed=5000 + i)["close"])
                  for i in range(args.synthetic)]
    elif args.coingecko_top:
        for coin in data.coingecko_top(args.coingecko_top):
            try:
                assets.append((coin, data.fetch_coingecko(coin, days=args.days)["close"]))
            except Exception as exc:
                print(f"  skip {coin}: {exc}", file=sys.stderr)
    elif args.yahoo:
        for symbol in args.yahoo:
            try:
                assets.append((symbol, data.fetch_yahoo(symbol)["close"]))
            except Exception as exc:
                print(f"  skip {symbol}: {exc}", file=sys.stderr)
    else:
        from pathlib import Path
        for path in sorted(Path(args.csv_dir).glob("*.csv")):
            try:
                assets.append((path.stem, data.load_csv(path)["close"]))
            except Exception as exc:
                print(f"  skip {path.name}: {exc}", file=sys.stderr)

    if not assets:
        sys.exit("No assets loaded.")

    rows, n_combos = [], 0
    for label, close in assets:
        try:
            strat, bench, p_raw, n_combos = evaluate(close, args.strategy, args.folds)
            rows.append({"asset": label, "sharpe": strat["sharpe"], "bench_sharpe": bench["sharpe"],
                         "total_return": strat["total_return"], "max_dd": strat["max_drawdown"],
                         "p_raw": p_raw})
        except ValueError as exc:
            print(f"  skip {label}: {exc}", file=sys.stderr)

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
