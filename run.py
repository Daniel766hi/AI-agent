#!/usr/bin/env python3
"""Walk-forward evaluation of a strategy against buy-and-hold.

  python run.py --synthetic --strategy sma_cross
  python run.py --csv data/BTCUSDT_1d.csv --strategy breakout
  python run.py --fetch BTCUSDT --strategy rsi_reversion      # needs open network
"""
import argparse

from quant import data
from quant.backtest import DEFAULT_FEE_BPS, DEFAULT_SLIPPAGE_BPS, buy_and_hold, metrics
from quant.strategies import REGISTRY
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", help="OHLCV CSV with date and close columns")
    source.add_argument("--fetch", metavar="SYMBOL", help="download from Binance, e.g. BTCUSDT")
    source.add_argument("--synthetic", action="store_true", help="random walk (the null hypothesis)")

    ap.add_argument("--strategy", default="sma_cross", choices=sorted(REGISTRY))
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--fee-bps", type=float, default=DEFAULT_FEE_BPS)
    ap.add_argument("--slippage-bps", type=float, default=DEFAULT_SLIPPAGE_BPS)
    ap.add_argument("--periods-per-year", type=int, default=365, help="365 crypto, 252 equities")
    ap.add_argument("--seed", type=int, default=0, help="synthetic data seed")
    args = ap.parse_args()

    if args.csv:
        df, label = data.load_csv(args.csv), args.csv
    elif args.fetch:
        df, label = data.fetch_binance(args.fetch), f"Binance {args.fetch} 1d"
    else:
        df, label = data.synthetic(seed=args.seed), f"synthetic GBM (seed {args.seed})"

    close = df["close"]
    fn, grid = REGISTRY[args.strategy]

    oos, folds, benchmark, n_trials = walk_forward(
        close, fn, grid, n_folds=args.folds,
        fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
        periods_per_year=args.periods_per_year,
    )

    strat = metrics(oos, args.periods_per_year)
    hold = metrics(benchmark, args.periods_per_year)
    hold_full = metrics(buy_and_hold(close, args.periods_per_year)["net_return"], args.periods_per_year)
    p_raw, edge = block_bootstrap_pvalue(oos, benchmark)
    p_deflated = deflate(p_raw, n_trials)

    print(f"\n{'=' * 66}")
    print(f"  {args.strategy}  on  {label}")
    print(f"  {len(close)} bars, {args.folds} folds, costs {args.fee_bps + args.slippage_bps:.0f}bps round trip")
    print(f"{'=' * 66}\n")

    print("Per-fold (out-of-sample only):")
    for _, row in folds.iterrows():
        print(f"  fold {row['fold']}  {row['test_start']} to {row['test_end']}  "
              f"train Sharpe {row['train_sharpe']:>6.2f}  test Sharpe {row['test_sharpe']:>6.2f}  "
              f"return {row['test_return']:>8.1%}   {row['params']}")

    print(f"\n{'Metric':<18}{'Strategy (OOS)':>18}{'Buy & hold':>18}")
    print("-" * 54)
    for key, label_, fmt in [
        ("cagr", "CAGR", "{:.1%}"), ("sharpe", "Sharpe", "{:.2f}"),
        ("max_drawdown", "Max drawdown", "{:.1%}"), ("volatility", "Volatility", "{:.1%}"),
        ("total_return", "Total return", "{:.1%}"), ("positive_period_rate", "Up periods", "{:.1%}"),
    ]:
        print(f"{label_:<18}{fmt.format(strat[key]):>18}{fmt.format(hold[key]):>18}")

    print(f"\nBuy & hold over the full series (incl. training): {hold_full['total_return']:.1%} "
          f"total, Sharpe {hold_full['sharpe']:.2f}")

    print(f"\nDaily edge over benchmark : {edge:+.5%}")
    print(f"Bootstrap p-value         : {p_raw:.4f}")
    print(f"After {n_trials} configs searched : {p_deflated:.4f}  (Sidak-deflated)")

    if p_deflated < 0.05 and strat["sharpe"] > hold["sharpe"]:
        print("\n  -> Survives out-of-sample at p<0.05. Worth paper-trading. Not proof.")
    else:
        print("\n  -> No significant edge. This is the expected and honest result for")
        print("     most strategies. Do not risk money on it.")
    print()


if __name__ == "__main__":
    main()
