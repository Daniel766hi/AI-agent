"""A desk of agents, each with one mandate and the power to refuse.

Why this shape rather than one function that returns a decision: the way a
trading system fails is self-deception — the same process that wants the trade
also judges whether the trade is sound. Real desks separate those roles, and a
risk officer who can only advise is not a risk officer.

So every agent here has a narrow mandate, sees the same evidence, and returns
a verdict. Approval must be unanimous. No agent can overrule a veto, including
the one that proposed the trade. Enthusiasm cannot outvote risk.

The agents are deterministic and rule-based. They encode the checks this
repository already validates, so their reasoning is auditable and reproducible
rather than persuasive. An LLM-backed agent could implement the same Agent
contract, but nothing here needs one to work, and a component that costs money
per call and answers differently each time has no place on the veto path.
"""
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from .backtest import DEFAULT_FEE_BPS, DEFAULT_SLIPPAGE_BPS, backtest, metrics
from .risk import breakeven, kelly_fraction, risk_of_ruin
from .strategies import REGISTRY
from .validate import block_bootstrap_pvalue, deflate, walk_forward


@dataclass
class Proposal:
    """A trade idea, as it moves through the desk."""
    symbol: str
    strategy: str
    close: pd.Series
    params: dict = field(default_factory=dict)
    target_position: float = 1.0
    account_equity: float = 1000.0
    evidence: dict = field(default_factory=dict)   # filled in as agents examine it


@dataclass
class Verdict:
    agent: str
    approved: bool
    reason: str
    detail: dict = field(default_factory=dict)

    def __str__(self):
        return f"{'PASS' if self.approved else 'VETO'}  {self.agent:<16} {self.reason}"


class Agent:
    """One mandate, one judgement. Subclasses implement review().

    `requires` names the evidence keys this agent needs another agent to have
    produced. The desk checks these when it is built, so a mis-ordered roster
    fails loudly at construction instead of quietly returning a rejection that
    is about the wiring rather than the trade.
    """

    name = "agent"
    mandate = ""
    requires = ()
    provides = ()

    def review(self, proposal: Proposal) -> Verdict:
        raise NotImplementedError

    def _ok(self, reason, **detail):
        return Verdict(self.name, True, reason, detail)

    def _veto(self, reason, **detail):
        return Verdict(self.name, False, reason, detail)


class ResearchAgent(Agent):
    """Fits parameters out-of-sample and reports what it found.

    It is allowed to be optimistic — that is its job — but it reports the
    evidence rather than the conclusion, and it cannot approve its own work.
    """

    name = "research"
    mandate = "find the best out-of-sample parameters, and show the working"
    provides = ("p_raw", "n_trials", "oos_returns", "benchmark_returns",
                "strategy_metrics", "benchmark_metrics", "folds")

    def __init__(self, folds=4):
        self.folds = folds

    def review(self, proposal):
        fn, grid = REGISTRY[proposal.strategy]

        # Pinned parameters are validated as given, not searched past. Otherwise
        # the evidence describes the grid's best fit while everything
        # downstream trades the caller's choice — approving one thing on the
        # strength of another. Pinning also means one trial, not len(grid):
        # you did not search, so you are not charged for searching. That is only
        # honest if the parameters were chosen before seeing this data, which
        # the code cannot check and the caller must.
        pinned = bool(proposal.params)
        search_grid = {k: [v] for k, v in proposal.params.items()} if pinned else grid

        try:
            oos, folds, benchmark, n_trials = walk_forward(
                proposal.close, fn, search_grid, n_folds=self.folds)
        except ValueError as exc:
            return self._veto(f"cannot validate: {exc}")

        p_raw, edge = block_bootstrap_pvalue(oos, benchmark)
        strat, bench = metrics(oos), metrics(benchmark)

        proposal.params = folds.iloc[-1]["params"]     # what the evidence describes
        proposal.evidence.update({
            "oos_returns": oos, "benchmark_returns": benchmark,
            "p_raw": p_raw, "n_trials": n_trials, "daily_edge": edge,
            "strategy_metrics": strat, "benchmark_metrics": bench,
            "folds": folds,
        })
        verb = "validated pinned" if pinned else "fitted"
        return self._ok(
            f"{verb} {proposal.params}, OOS Sharpe {strat['sharpe']:.2f} "
            f"vs {bench['sharpe']:.2f} holding",
            sharpe=strat["sharpe"], params=proposal.params, searched=n_trials)


class SkepticAgent(Agent):
    """Assumes the result is luck until the evidence rules it out.

    Deliberately adversarial. It applies the multiple-testing correction the
    research agent's own search earned, and demands the strategy beat holding —
    not merely make money, which any long position does in a rising market.
    """

    name = "skeptic"
    mandate = "assume it is noise; demand the evidence survive the search that found it"
    requires = ("p_raw", "n_trials", "strategy_metrics", "benchmark_metrics")
    provides = ("p_deflated",)

    def __init__(self, alpha=0.05):
        self.alpha = alpha

    def review(self, proposal):
        ev = proposal.evidence
        if "p_raw" not in ev:
            return self._veto("no validation evidence to examine")

        p_deflated = deflate(ev["p_raw"], ev["n_trials"])
        strat, bench = ev["strategy_metrics"], ev["benchmark_metrics"]
        ev["p_deflated"] = p_deflated

        if pd.isna(p_deflated):
            return self._veto("p-value could not be computed; too few observations")
        if p_deflated >= self.alpha:
            return self._veto(
                f"p={p_deflated:.3f} after {ev['n_trials']} configs searched — indistinguishable from luck",
                p_deflated=p_deflated, n_trials=ev["n_trials"])
        if strat["sharpe"] <= bench["sharpe"]:
            return self._veto(
                f"Sharpe {strat['sharpe']:.2f} does not beat holding at {bench['sharpe']:.2f}",
                strategy_sharpe=strat["sharpe"], benchmark_sharpe=bench["sharpe"])

        return self._ok(f"survives {ev['n_trials']} trials at p={p_deflated:.3f}",
                        p_deflated=p_deflated)


class CostAgent(Agent):
    """Checks the edge is bigger than the bill for capturing it.

    A strategy can be statistically real and still lose money, because the
    hurdle is cost drag plus the return forfeited while sitting in cash.
    """

    name = "cost"
    mandate = "confirm the edge exceeds what it costs to trade"
    requires = ("strategy_metrics", "benchmark_metrics")
    provides = ("breakeven",)

    def __init__(self, fee_bps=DEFAULT_FEE_BPS, slippage_bps=DEFAULT_SLIPPAGE_BPS):
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps

    def review(self, proposal):
        fn, _ = REGISTRY[proposal.strategy]
        result = backtest(proposal.close, fn(proposal.close, **proposal.params),
                          self.fee_bps, self.slippage_bps)
        stats = breakeven(result, fee_bps=self.fee_bps, slippage_bps=self.slippage_bps)
        proposal.evidence["breakeven"] = stats

        # Compare like with like: the strategy's figure is out-of-sample, so the
        # benchmark must be the same window. Measuring holding over the whole
        # series, training included, silently compares different periods.
        strat_cagr = proposal.evidence["strategy_metrics"]["cagr"]
        hold_cagr = proposal.evidence["benchmark_metrics"]["cagr"]

        if stats["annual_cost_drag"] > 0.40:
            return self._veto(
                f"{stats['round_trips_per_year']:.0f} round trips/yr costs "
                f"{stats['annual_cost_drag']:.1%} a year — more than the asset plausibly returns",
                drag=stats["annual_cost_drag"])
        if strat_cagr <= hold_cagr:
            return self._veto(
                f"after costs it returns {strat_cagr:.1%} against {hold_cagr:.1%} for holding "
                f"over the same out-of-sample window",
                strategy_cagr=strat_cagr, hold_cagr=hold_cagr)

        return self._ok(
            f"drag {stats['annual_cost_drag']:.1%}/yr at "
            f"{stats['round_trips_per_year']:.0f} round trips, edge clears it",
            drag=stats["annual_cost_drag"])


class RiskAgent(Agent):
    """Sizes the position, and refuses sizes that can end the account.

    The only agent that may reduce a proposal rather than merely reject it —
    position size is its mandate, so it sets it.
    """

    name = "risk"
    mandate = "ensure a bad run cannot end the account"
    requires = ("oos_returns",)
    provides = ("kelly", "ruin_probability")

    def __init__(self, max_ruin_probability=0.05, ruin_drawdown=0.50):
        self.max_ruin = max_ruin_probability
        self.ruin_drawdown = ruin_drawdown

    def review(self, proposal):
        returns = proposal.evidence.get("oos_returns")
        if returns is None or len(returns) < 30:
            return self._veto("not enough out-of-sample history to size a position")

        kelly = kelly_fraction(returns)
        ruin = risk_of_ruin(returns, self.ruin_drawdown, n_sims=4000)
        proposal.evidence.update({"kelly": kelly, "ruin_probability": ruin})

        if kelly["kelly"] <= 0:
            return self._veto(
                f"estimated edge is negative ({kelly['annual_edge']:.1%}/yr); correct size is zero",
                kelly=kelly["kelly"])
        if ruin > self.max_ruin:
            return self._veto(
                f"{ruin:.1%} chance of a {self.ruin_drawdown:.0%} drawdown "
                f"exceeds the {self.max_ruin:.0%} limit",
                ruin_probability=ruin)

        # Half Kelly, capped at fully long. Kelly assumes the edge estimate is
        # right; it is an estimate from one sample, so bet less than it says.
        sized = max(0.0, min(kelly["half_kelly"], 1.0))
        proposal.target_position = sized
        return self._ok(
            f"size {sized:.0%} (half Kelly), {ruin:.1%} chance of a {self.ruin_drawdown:.0%} drawdown",
            position=sized, ruin_probability=ruin)


@dataclass
class Decision:
    approved: bool
    verdicts: list
    proposal: Proposal

    @property
    def vetoes(self):
        return [v for v in self.verdicts if not v.approved]

    def summary(self):
        lines = [f"  {v}" for v in self.verdicts]
        if self.approved:
            lines.append(f"\n  APPROVED — trade {self.proposal.symbol} at "
                         f"{self.proposal.target_position:.0%} of equity")
        else:
            reasons = "; ".join(v.reason for v in self.vetoes)
            lines.append(f"\n  REJECTED by {', '.join(v.agent for v in self.vetoes)} — {reasons}")
        return "\n".join(lines)


class Desk:
    """Runs a proposal past every agent. Approval must be unanimous.

    Every agent reviews even after a veto, so the report shows all the reasons
    at once rather than one at a time across repeated runs. But a single veto
    is final: there is no score, no weighting, no majority. A structure where
    two optimistic agents can outvote the risk agent is how accounts die.
    """

    def __init__(self, agents=None):
        self.agents = agents or [ResearchAgent(), SkepticAgent(), CostAgent(), RiskAgent()]
        self._check_roster()

    def _check_roster(self):
        """Fail at construction if an agent runs before its evidence exists."""
        available = set()
        for agent in self.agents:
            missing = sorted(set(agent.requires) - available)
            if missing:
                raise ValueError(
                    f"{agent.name!r} needs {missing} but no earlier agent provides it. "
                    f"Order the desk so producers run before consumers."
                )
            available.update(agent.provides)

    def evaluate(self, proposal: Proposal) -> Decision:
        verdicts = []
        for agent in self.agents:
            try:
                verdict = agent.review(proposal)
            except Exception as exc:
                # An agent that crashes has not approved anything.
                verdict = Verdict(agent.name, False, f"agent failed: {type(exc).__name__}: {exc}")
            verdicts.append(verdict)

        return Decision(all(v.approved for v in verdicts), verdicts, proposal)
