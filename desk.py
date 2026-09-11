#!/usr/bin/env python3
"""Put a trade idea to the desk. Every agent must approve for it to pass.

  python desk.py --synthetic --strategy breakout
  python desk.py --csv data/BTCUSDT_1d.csv --strategy sma_cross --equity 5000

Each agent has one mandate and a veto. The agent that proposes the trade cannot
approve it, and no agent can overrule a refusal.
"""
import argparse

from quant import data
from quant.agents import CostAgent, Desk, Proposal, ResearchAgent, RiskAgent, SkepticAgent
from quant.strategies import REGISTRY


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv")
    source.add_argument("--synthetic", action="store_true")
    source.add_argument("--seed", type=int, help="synthetic series with this seed")

    ap.add_argument("--strategy", default="sma_cross", choices=sorted(REGISTRY))
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--equity", type=float, default=1000.0)
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--alpha", type=float, default=0.05, help="significance the skeptic demands")
    ap.add_argument("--max-ruin", type=float, default=0.05, help="ruin probability the risk agent allows")
    args = ap.parse_args()

    if args.csv:
        close, label = data.load_csv(args.csv)["close"], args.csv
    else:
        seed = args.seed if args.seed is not None else 0
        close, label = data.synthetic(seed=seed)["close"], f"synthetic (seed {seed})"

    desk = Desk([
        ResearchAgent(folds=args.folds),
        SkepticAgent(alpha=args.alpha),
        CostAgent(),
        RiskAgent(max_ruin_probability=args.max_ruin),
    ])

    print(f"\n{'=' * 72}")
    print(f"  {args.strategy} on {args.symbol} — {label}")
    print(f"{'=' * 72}\n")
    for agent in desk.agents:
        print(f"  {agent.name:<16} {agent.mandate}")
    print()

    decision = desk.evaluate(Proposal(
        symbol=args.symbol, strategy=args.strategy, close=close, account_equity=args.equity))
    print(decision.summary())

    if decision.approved:
        stake = decision.proposal.target_position * args.equity
        print(f"  {stake:,.2f} of {args.equity:,.2f} at risk\n")
        print("  Approval is not a forecast. It means the idea survived every check")
        print("  this desk knows how to make — paper-trade it before it sees real money.\n")
    else:
        print()
    return 0 if decision.approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
