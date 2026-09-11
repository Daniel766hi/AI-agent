#!/usr/bin/env python3
"""Run a strategy against a broker.

  python trade.py --strategy breakout --mode paper
  python trade.py --strategy breakout --mode live --max-notional 50 --yes-real-money

Live mode reads BINANCE_API_KEY / BINANCE_API_SECRET from the environment and
refuses to start unless the strategy has passed walk-forward validation.
"""
import argparse
import os
import sys

from quant import data
from pathlib import Path

from quant.live import STATE_FILE, Trader, make_broker
from quant.strategies import REGISTRY
from quant.validate import block_bootstrap_pvalue, deflate, walk_forward


def validation_verdict(strategy, csv_path, folds=5):
    """Re-run walk-forward. Returns (passed, deflated_p, best_params)."""
    close = data.load_csv(csv_path)["close"]
    fn, grid = REGISTRY[strategy]
    oos, folds_df, benchmark, n_trials = walk_forward(close, fn, grid, n_folds=folds)
    p_raw, _ = block_bootstrap_pvalue(oos, benchmark)
    p_deflated = deflate(p_raw, n_trials)
    best = folds_df.iloc[-1]["params"]          # most recent fold's fitted params
    return p_deflated < 0.05, p_deflated, best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategy", required=True, choices=sorted(REGISTRY))
    ap.add_argument("--mode", default="paper", choices=["paper", "live"])
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--interval", default="1d")
    ap.add_argument("--params", default="", help="e.g. 'window=55' — overrides validation-fitted params")
    ap.add_argument("--cash", type=float, default=1000.0, help="paper starting cash")
    ap.add_argument("--poll", type=int, default=3600, help="seconds between ticks")
    ap.add_argument("--ticks", type=int, default=None, help="stop after N ticks (default: forever)")
    ap.add_argument("--max-drawdown", type=float, default=20.0, help="halt at this %% drawdown")
    ap.add_argument("--max-notional", type=float, default=None, help="live: cap per-order size in quote currency")
    ap.add_argument("--validate-csv", help="CSV to validate against before going live")
    ap.add_argument("--yes-real-money", action="store_true", help="required to place live orders")
    ap.add_argument("--skip-validation", action="store_true", help="go live on an unvalidated strategy")
    ap.add_argument("--reset", action="store_true",
                    help="clear a saved halt and drawdown peak before starting")
    args = ap.parse_args()

    params = {}
    for pair in filter(None, args.params.split(",")):
        key, _, value = pair.partition("=")
        params[key.strip()] = int(value) if value.strip().lstrip("-").isdigit() else float(value)

    if args.mode == "live":
        if not args.yes_real_money:
            sys.exit("Refusing to trade live without --yes-real-money.")
        if not (os.environ.get("BINANCE_API_KEY") and os.environ.get("BINANCE_API_SECRET")):
            sys.exit("Live mode needs BINANCE_API_KEY and BINANCE_API_SECRET in the environment.")
        if args.max_notional is None:
            sys.exit("Live mode requires --max-notional. Start small.")

        if args.skip_validation:
            print("!! Going live on an UNVALIDATED strategy. You are trading noise.\n")
        elif not args.validate_csv:
            sys.exit("Live mode needs --validate-csv (history to validate on) or --skip-validation.")
        else:
            passed, p_value, fitted = validation_verdict(args.strategy, args.validate_csv)
            print(f"Validation: deflated p = {p_value:.4f}  ->  {'PASS' if passed else 'FAIL'}")
            if not passed:
                sys.exit(
                    f"'{args.strategy}' shows no significant out-of-sample edge (p={p_value:.4f}).\n"
                    "Trading it live is expected to lose money to fees. Override with --skip-validation."
                )
            params = params or fitted
            print(f"Using walk-forward fitted params: {params}\n")

    if args.reset:
        # A halt is a safety stop; clearing it is deliberate and announced.
        removed = [p for p in (STATE_FILE, Path("data/paper_broker.json")) if p.exists()]
        for path in removed:
            path.unlink()
        print(f"Reset: cleared {', '.join(str(p) for p in removed) or 'nothing (no saved state)'}\n")

    broker = make_broker(args.mode, args.symbol, args.cash, args.max_notional)
    trader = Trader(args.strategy, params, broker, args.symbol, args.interval,
                    max_drawdown_pct=args.max_drawdown)

    print(f"{args.mode.upper()}  {args.strategy}{params or ''}  {args.symbol} {args.interval}  "
          f"halt at -{args.max_drawdown}%\n")
    trader.run(poll_seconds=args.poll, max_ticks=args.ticks)


if __name__ == "__main__":
    main()
