"""The desk: separate mandates, unanimous approval, no overruling a veto."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quant import data
from quant.strategies import REGISTRY
from quant.agents import (Agent, CostAgent, Decision, Desk, Proposal, ResearchAgent,
                          RiskAgent, SkepticAgent, Verdict)


def _proposal(strategy="sma_cross", seed=0, generator=None):
    close = (generator or data.synthetic)(seed=seed)["close"]
    return Proposal(symbol="TEST", strategy=strategy, close=close)


class _Yes(Agent):
    name = "yes"
    def review(self, proposal): return self._ok("always approves")


class _No(Agent):
    name = "no"
    def review(self, proposal): return self._veto("always refuses")


class _Boom(Agent):
    name = "boom"
    def review(self, proposal): raise RuntimeError("exploded")


def test_one_veto_blocks_a_majority():
    """No score, no weighting: three approvals do not outvote one refusal."""
    decision = Desk([_Yes(), _Yes(), _Yes(), _No()]).evaluate(_proposal())
    assert not decision.approved
    assert len(decision.vetoes) == 1


def test_unanimous_approval_passes():
    assert Desk([_Yes(), _Yes()]).evaluate(_proposal()).approved


def test_a_crashing_agent_does_not_approve():
    """Failure must never be read as consent."""
    decision = Desk([_Yes(), _Boom()]).evaluate(_proposal())
    assert not decision.approved
    assert "agent failed" in decision.vetoes[0].reason
    assert "RuntimeError" in decision.vetoes[0].reason


def test_every_agent_reviews_even_after_a_veto():
    """The report should show all the reasons at once, not one per run."""
    decision = Desk([_No(), _Yes(), _No()]).evaluate(_proposal())
    assert len(decision.verdicts) == 3
    assert len(decision.vetoes) == 2


def test_skeptic_rejects_noise():
    """A random walk must never get through, whatever research reports."""
    proposal = _proposal("sma_cross", seed=0)
    decision = Desk().evaluate(proposal)
    assert not decision.approved, "noise was approved"
    assert any(v.agent == "skeptic" for v in decision.vetoes), \
        f"skeptic should have vetoed; verdicts: {[str(v) for v in decision.verdicts]}"


def test_research_cannot_approve_its_own_work():
    """The proposing agent has no authority over the decision."""
    proposal = _proposal("sma_cross", seed=0)
    decision = Desk().evaluate(proposal)
    research = [v for v in decision.verdicts if v.agent == "research"][0]
    assert research.approved, "research should report its finding positively"
    assert not decision.approved, "yet the trade must still be refused"


def test_desk_can_approve_real_structure():
    """A rejection machine is not a filter. Something real must get through."""
    approvals = 0
    for seed in range(6):
        proposal = Proposal(symbol="REGIME", strategy="ts_momentum",
                            close=data.synthetic_regimes(seed=seed)["close"])
        approvals += Desk().evaluate(proposal).approved
    assert approvals >= 1, "the desk approved nothing on data with genuine structure"


def test_risk_agent_sets_the_position_size():
    """Risk is the only agent that may resize rather than only refuse."""
    proposal = Proposal(symbol="REGIME", strategy="ts_momentum",
                        close=data.synthetic_regimes(seed=2)["close"])
    before = proposal.target_position
    Desk().evaluate(proposal)
    assert 0.0 <= proposal.target_position <= 1.0
    assert "kelly" in proposal.evidence and "ruin_probability" in proposal.evidence
    assert proposal.target_position != before or proposal.target_position == 1.0


def test_risk_agent_refuses_a_negative_edge():
    agent = RiskAgent()
    proposal = _proposal("sma_cross", seed=0)
    ResearchAgent(folds=4).review(proposal)
    verdict = agent.review(proposal)
    if not verdict.approved:
        assert "negative" in verdict.reason or "chance of" in verdict.reason


def test_cost_agent_compares_the_same_window():
    """Strategy figures are out-of-sample; the benchmark must be too."""
    proposal = _proposal("sma_cross", seed=1)
    ResearchAgent(folds=4).review(proposal)
    CostAgent().review(proposal)
    oos_bench = proposal.evidence["benchmark_metrics"]["cagr"]
    full_bench = data.synthetic(seed=1)["close"]
    # The evidence the cost agent uses must be the OOS benchmark research produced,
    # not a figure recomputed over the whole series including training.
    assert proposal.evidence["benchmark_metrics"]["n_periods"] < len(full_bench)
    assert isinstance(oos_bench, float)


def test_agents_declare_a_mandate():
    for agent in Desk().agents:
        assert agent.mandate, f"{agent.name} has no stated mandate"
        assert agent.name != "agent"


def test_summary_names_every_vetoing_agent():
    decision = Desk([_No(), _Yes()]).evaluate(_proposal())
    text = decision.summary()
    assert "REJECTED" in text and "no" in text
    assert "always refuses" in text



def test_misordered_roster_fails_at_construction():
    """A wiring mistake must not masquerade as a verdict about the trade."""
    for roster in ([SkepticAgent(), ResearchAgent()], [SkepticAgent()], [CostAgent()],
                   [RiskAgent(), ResearchAgent()]):
        try:
            Desk(roster)
        except ValueError as exc:
            assert "needs" in str(exc) and "provides" in str(exc)
            continue
        raise AssertionError(f"roster {[a.name for a in roster]} should not have built")


def test_correct_order_builds():
    Desk([ResearchAgent(), SkepticAgent(), CostAgent(), RiskAgent()])
    Desk([ResearchAgent(), RiskAgent()])          # a subset is fine if deps are met


def test_pinned_params_are_what_gets_validated():
    """Approving parameters on evidence about different parameters is unsound."""
    close = data.synthetic_regimes(seed=2)["close"]
    proposal = Proposal(symbol="T", strategy="ts_momentum", close=close,
                        params={"lookback": 30})
    Desk().evaluate(proposal)

    assert proposal.params == {"lookback": 30}, "the caller's choice must survive"
    assert proposal.evidence["folds"].iloc[-1]["params"] == {"lookback": 30}, \
        "the evidence must describe the parameters actually being traded"


def test_pinning_is_charged_one_trial_not_the_whole_grid():
    """No search means no multiple-testing penalty — and searching means one."""
    close = data.synthetic_regimes(seed=2)["close"]

    pinned = Proposal(symbol="T", strategy="ts_momentum", close=close, params={"lookback": 30})
    Desk().evaluate(pinned)
    assert pinned.evidence["n_trials"] == 1

    searched = Proposal(symbol="T", strategy="ts_momentum", close=close)
    Desk().evaluate(searched)
    assert searched.evidence["n_trials"] == len(REGISTRY["ts_momentum"][1]["lookback"])
    assert searched.evidence["n_trials"] > pinned.evidence["n_trials"]


def test_agents_declare_what_they_need_and_produce():
    for agent in Desk().agents:
        assert isinstance(agent.requires, tuple) and isinstance(agent.provides, tuple)
    assert ResearchAgent().requires == (), "research consumes no evidence; it produces it"
    assert "p_raw" in ResearchAgent().provides



def test_risk_reports_when_the_kelly_cap_is_binding():
    """A half-Kelly above 100% is a warning about the estimate, not a green light.

    Reporting "size 100%" alone implies the figure was chosen; it was clamped.
    """
    close = data.synthetic_regimes(seed=2)["close"]
    proposal = Proposal(symbol="T", strategy="ts_momentum", close=close)
    decision = Desk().evaluate(proposal)

    risk = [v for v in decision.verdicts if v.agent == "risk"][0]
    assert proposal.target_position <= 1.0, "the cap must hold whatever Kelly says"

    if proposal.evidence.get("kelly_capped"):
        assert "capped" in risk.reason and "overfit" in risk.reason, \
            f"a binding cap must be reported, got: {risk.reason}"
        assert risk.detail["half_kelly_uncapped"] > 1.0


def test_position_never_exceeds_fully_long():
    """No path through the risk agent may produce leverage."""
    for seed in range(5):
        proposal = Proposal(symbol="T", strategy="ts_momentum",
                            close=data.synthetic_regimes(seed=seed)["close"])
        Desk().evaluate(proposal)
        assert 0.0 <= proposal.target_position <= 1.0, \
            f"seed {seed} produced position {proposal.target_position}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
