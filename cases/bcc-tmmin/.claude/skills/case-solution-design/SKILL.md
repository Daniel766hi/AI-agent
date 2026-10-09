---
name: case-solution-design
description: Design, test and write a business case competition solution step by step (frame, diagnose, ideate, score, test with numbers, roadmap, finance, storyline). Use for the TMMIN M3C 2026 case or any operations / manufacturing case competition.
---

# Case Solution Design

A repeatable workflow for turning a casebook into a winning, evidence-backed solution. Work through the stages in order. Each stage has an output file and a "done when" check. Never skip the check.

## Ground rules

- **Facts first.** Every number must trace to a casebook exhibit (`data/facts.md`) or a labelled assumption. If a number is missing, write it as an assumption with a range, never as a fact.
- **Answer the question asked.** Re-read the key question and sub-questions in `data/problem.md` before every stage. If the case says "not a product or device", the answer must change how work is done.
- **One idea, not a list.** Judges reward one integrated answer explained through one pilot.
- **Test, don't claim.** Any claim about impact needs a calculation, simulation or cited benchmark.
- **Plain language.** Write so a non-specialist judge understands each slide in one reading.
- **Language.** Match the user's language (Indonesian or English). Keep technical TPS terms (jidoka, kaizen, yokoten) as is.

## Companion skills and token budget

- Read only the stage you are working on and the input files that stage names. Search with `grep -n` before opening a file.
- Stage 2 and Stage 3: when you need a deeper method, read one framework file from `.claude/skills/mckinsey-strategy-team/references/`. For Stage 2 use `01-diagnosis-and-framing/situation-assessment.md`; for Stage 3 use `03-strategic-choice-and-economics/strategic-options.md`. Read its "Output Format" section first.
- Stage 5: before reporting any number, follow `verification-before-completion`. Rerun the script and quote its output.
- Stage 6: `04-operating-model-and-execution/transformation-roadmap.md`. Stage 7: `05-risk-performance-and-value-governance/kpi-architect.md`.
- Stage 8: run `judge-panel`. Run `mckinsey-strategy-team` only once, as the final stress test, because it costs many agents.

## Stage 1 — Frame the problem

Output: `work/1_frame.md`

1. Restate the key question in one sentence.
2. Write the **SCQ**: Situation (what is true), Complication (what changed and why it hurts), Question.
3. List **constraints**: scope, period, budget, financial parameters, what the answer must not be.
4. List **success criteria** in the judges' words, one per sub-question.

Done when: someone who has not read the casebook can say what the team must answer and within which limits.

## Stage 2 — Diagnose the gap

Output: `work/2_diagnosis.md`

1. Build an **issue tree** from the key question down to measurable drivers (MECE: no overlaps, no gaps).
2. For each driver, attach the exhibit number and the 2023 → 2025 trend.
3. Build a **gap heat map**: process × impact on cost and quality, using maturity levels and baseline data.
4. Find the **root cause** that links the complications (5-whys). Look especially for gaps *between* processes, not only inside them.
5. Note hidden opportunities in the data, such as survey answers showing willingness to change.

Done when: one root-cause sentence explains all complications, and the priority area is backed by at least two data points.

## Stage 3 — Generate options

Output: `work/3_options.md`

1. Generate at least 8 options across different levers: process, data, people, knowledge, equipment, organisation.
2. For each option write: core mechanism, gap it closes, TPS principle it rests on, a public precedent (cite the source), strength, weakness.
3. Combine compatible options into one **integrated idea** if they reinforce each other.

Done when: at least one option is clearly a system change rather than a purchase, and each option has a precedent or a reason it is new.

## Stage 4 — Score and choose

Output: `work/4_scoring.md` (or the Ideation tab of `model/TMMIN_Case_Model.xlsx`)

1. Agree weighted criteria with the team, for example: cost and quality impact, flexibility, people and knowledge, hard to buy off the shelf, feasible in budget, fits the case ask.
2. Score 1–5, compute weighted totals, rank.
3. Record why the losers lose; these become the "options we rejected" slide.
4. Choose **one idea and one pilot area**.

Done when: the choice is written in one line with three reasons, and the team has agreed it.

## Stage 5 — Test with numbers

Output: `work/5_tests.md`, updated `model/`

1. **Mechanism test:** simulate or calculate how the idea changes the key operational metric versus the do-nothing case and versus the "just buy technology" case. See `model/run_tests.py`.
2. **Financial model:** savings by lever × adoption ramp × escalation, minus capex and opex; NPV, payback, three scenarios. Use the casebook financial parameters only.
3. **Break-even:** how much of the gap must close to pay back the investment.
4. **Stress test:** Monte Carlo over uncertain inputs; compare funding strategies (front-loaded vs pilot-light, with and without a gate) and a delay case.
5. **Tornado:** which assumptions move the result most. These are the ones to defend in Q&A.
6. Back each lever with a cited external benchmark; keep assumptions below the benchmark.

Done when: every headline number in the deck comes from the model, and the weakest scenario is known and has an answer in the roadmap.

## Stage 6 — Roadmap and capability

Output: `work/6_roadmap.md`

1. Phases with dates and share of capex: prepare, pilot, standardise, roll out, scale.
2. A **go/no-go gate** with measurable criteria before the big spend.
3. A **first 100 days** plan using only what the company already has.
4. Capability plan: who learns what, how fast, how knowledge is captured.
5. Build vs partner per component, with a knowledge-transfer rule.
6. Risk register: likelihood × impact, mitigation, early-warning KPI.

Done when: each phase has an owner, a deliverable and a gate criterion.

## Stage 7 — KPIs and impact

Output: `work/7_kpis.md`

1. Outcome KPIs (cost, quality, time, flexibility) and driver KPIs (people, knowledge, adoption).
2. Baseline from the exhibits, pilot target, final target, all consistent with the model.

Done when: the pilot targets double as the gate criteria.

## Stage 8 — Storyline and deliverables

Output: deck, paper and `work/8_qa.md`

1. Write action titles first; they must tell the full story when read alone.
2. Order: hook → executive summary → situation → complication → root cause → vision → idea → how it works → proof → people → alternatives → roadmap → first 100 days → capability → financials → stress test → KPIs → ask → appendix.
3. Executive summary: answer + three numbers + the ask.
4. Q&A bank: at least 15 likely judge questions, each with an answer, the evidence and an owner.
5. Final checks: every number ties to the model; every source is cited; placeholders are replaced; slide and page limits are met.

Done when: a timed mock run fits the limit and every Q&A answer points to a slide or appendix.

## Files in this project

| Path | What it holds |
|---|---|
| `CLAUDE.md` | Case context and project rules |
| `data/problem.md` | Key question, sub-questions, constraints, complications, issue tree |
| `data/facts.md` | All casebook exhibits, verified against the PDF |
| `data/research.md` | Toyota precedents, benchmarks, simulation results, GitHub repos |
| `data/ideation.md` | Options, scoring, chosen idea |
| `model/` | Excel model, build script, simulation script |
| `outputs/` | Proposal draft, charts, Word template |
