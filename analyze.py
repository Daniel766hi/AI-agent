#!/usr/bin/env python3
"""What profit would require, and what is most likely to prevent it.

  python analyze.py --synthetic --strategy sma_cross
  python analyze.py --csv data/BTCUSDT_1d.csv --strategy breakout

Answers three questions no backtest answers on its own:
  1. How much must this earn gross before it earns anything net?
  2. How often can I trade before costs eat the whole edge?
  3. What is the chance this ruins me at a given position size?
"""
import argparse

from quant import data
from quant.backtest import DEFAULT_FEE_BPS, DEFAULT_SLIPPAGE_BPS, backtest, buy_and_hold, metrics
from quant.risk import breakeven, cost_drag, kelly_fraction, leverage_table
from quant.strategies import REGISTRY


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv")
    src.add_argument("--synthetic", action="store_true")

    ap.add_argument("--strategy", default="sma_cross", choices=sorted(REGISTRY))
    ap.add_argument("--fee-bps", type=float, default=DEFAULT_FEE_BPS)
    ap.add_argument("--slippage-bps", type=float, default=DEFAULT_SLIPPAGE_BPS)
    ap.add_argument("--periods-per-year", type=int, default=365)
    args = ap.parse_args()

    if args.csv:
        close, label = data.load_csv(args.csv)["close"], args.csv
    else:
        close, label = data.synthetic(seed=0)["close"], "synthetic GBM"

    fn, grid = REGISTRY[args.strategy]
    params = {k: v[len(v) // 2] for k, v in grid.items()}
    result = backtest(close, fn(close, **params), args.fee_bps, args.slippage_bps, args.periods_per_year)
    stats = breakeven(result, args.periods_per_year, args.fee_bps, args.slippage_bps)
    strat_m = metrics(result["net_return"], args.periods_per_year)
    hold_m = metrics(buy_and_hold(close, args.periods_per_year)["net_return"], args.periods_per_year)

    print(f"\n{'=' * 68}\n  {args.strategy} {params}  on  {label}\n{'=' * 68}")

    print(f"\n1. THE HURDLE  — what it must clear before it earns anything")
    print(f"   Round trips per year     {stats['round_trips_per_year']:>10.1f}")
    print(f"   Annual cost drag         {stats['annual_cost_drag']:>10.2%}")
    print(f"   Time in market           {stats['time_in_market']:>10.1%}")
    forfeited = stats["hurdle_vs_holding"] - stats["annual_cost_drag"]
    print(f"   Return given up in cash  {forfeited:>10.2%}"
          f"{'  (asset fell, so cash helped)' if forfeited < 0 else ''}")
    hurdle = stats["hurdle_vs_holding"]
    note = "must beat this to be worth it" if hurdle > 0 else "negative only because the asset lost money"
    print(f"   {'Total hurdle vs holding':<24}{hurdle:>10.2%}  <- {note}")

    print(f"\n2. THE FREQUENCY CLIFF  — cost drag at {args.fee_bps + args.slippage_bps:.0f}bps")
    print(f"   {'Trading':<14}{'Round trips/yr':>16}{'Annual drag':>14}")
    for name, n in [("monthly", 12), ("weekly", 52), ("daily", 250), ("4x daily", 1000)]:
        drag = cost_drag(n, args.fee_bps, args.slippage_bps)
        flag = "  <- you are here" if abs(n - stats["round_trips_per_year"]) < n * 0.6 else ""
        print(f"   {name:<14}{n:>16}{drag:>14.1%}{flag}")

    print(f"\n3. SURVIVAL  — probability of drawdown within one year")
    table = leverage_table(result["net_return"], periods_per_year=args.periods_per_year)
    print(f"   {'Leverage':<12}{'-20%':>10}{'-50%':>10}{'wiped out':>12}")
    for _, row in table.iterrows():
        print(f"   {int(row['leverage'])}x{'':<10}{row['p_down_20pct']:>10.1%}"
              f"{row['p_down_50pct']:>10.1%}{row['p_wiped_out']:>12.1%}")

    kelly = kelly_fraction(result["net_return"], args.periods_per_year)
    print(f"\n4. POSITION SIZE")
    if kelly["kelly"] <= 0:
        print(f"   Estimated edge is negative ({kelly['annual_edge']:.1%}/yr).")
        print(f"   Growth-optimal size is ZERO. Do not trade this.")
    else:
        print(f"   Full Kelly {kelly['kelly']:.2f}x   Half Kelly {kelly['half_kelly']:.2f}x"
              f"   (edge {kelly['annual_edge']:.1%}/yr)")
        print(f"   Kelly assumes the edge estimate is correct. It is an estimate from")
        print(f"   this sample; if it is too high, full Kelly over-bets and loses.")

    print(f"\n5. VERSUS DOING NOTHING")
    print(f"   {'':<14}{'Strategy':>12}{'Buy & hold':>14}")
    print(f"   {'CAGR':<14}{strat_m['cagr']:>12.1%}{hold_m['cagr']:>14.1%}")
    print(f"   {'Sharpe':<14}{strat_m['sharpe']:>12.2f}{hold_m['sharpe']:>14.2f}")
    print(f"   {'Max drawdown':<14}{strat_m['max_drawdown']:>12.1%}{hold_m['max_drawdown']:>14.1%}")

    if strat_m["cagr"] <= hold_m["cagr"]:
        print(f"\n   -> Holding the asset beat this strategy. That is the usual outcome,")
        print(f"      and buy-and-hold pays costs once instead of {stats['round_trips_per_year']:.0f} times a year.")
    print()


if __name__ == "__main__":
    main()
