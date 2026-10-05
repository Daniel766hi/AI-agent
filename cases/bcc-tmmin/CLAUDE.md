# BCC TMMIN — M3C 2026 (MTI-Consulting × AKTI Case Competition)

## What this project is

A team of 3 is solving the M3C 2026 case on PT Toyota Motor Manufacturing Indonesia (TMMIN), theme *Next-Level Kaizen: Transforming Manufacturing by Integrating Future Technology and People*. The submission is a paper (PDF, Bahasa Indonesia) plus a presentation deck. The organizers confirmed that AI tools may be used.

## Key question

How can TMMIN redefine how it manufactures in 2026–2030 by combining future technology such as AI with people's mindset, skills and knowledge, to stay competitive in cost and quality in the C.A.S.E. era?

Answered through 4 sub-questions: (1) future manufacturing vision and biggest gap, (2) transformative idea, (3) roadmap and capability building, (4) competitive and financial impact with KPIs.

## Hard constraints

- The answer must describe **how manufacturing changes**, not recommend a product, device or equipment.
- Must be transformative, people-centred (M3C theme: Human-Centered AI Kaizen).
- Period 2026–2030; investment Rp40–120 billion; discount rate 10%; technology life 5 years; cost escalation 4% a year.
- Exhibits 3–9 are dummy data.

## Current answer (team's chosen idea)

**Closed-Loop Kaizen** — a plant that learns from itself. Three loops with people at the center:
1. Quality loop (jidoka): every abnormality returns to the process that caused it within minutes.
2. Data & equipment loop (standardized work): one in-house interface standard; a new variant becomes configuration.
3. People & knowledge loop (kaizen, yokoten): operator-built AI tools, one-tap idea channel, captured senior know-how.

Pilot: sealer → inspection. Funding: pilot-light (10/15/40/25/10% of Rp80B) with a go/no-go gate at end-2027.

Headline numbers (base case): cost index 106 → 96.9; variant change 9 → 5.9 months; Software & AI engineers at L3+ 2 → ~14; NPV Rp27B at 10%; payback 2029; P(NPV>0) 85% across 10,000 simulations.

## Rules for working here

- Use the `case-solution-design` skill when designing, testing or rewriting any part of the solution.
- Every number must come from `data/facts.md` or `model/`. Never invent figures; label assumptions.
- After changing assumptions in `model/build_model.py`, run `cd model && python build_model.py && python run_tests.py`, then update the deck and paper numbers.
- Write deliverables in Bahasa Indonesia unless asked otherwise; keep TPS terms (jidoka, kaizen, yokoten).
- Keep explanations plain enough for a non-engineer judge.

## Token rules

- Find before reading: `grep -n` in `data/*.md`, then read only the matching lines. Never read a whole data file to find one number.
- Binary files (`.xlsx`, `.docx`, `.pdf`, images) are blocked from Read in `.claude/settings.json`. Get numbers by running the scripts and reading their printed summary.
- Edit files in place with small edits; never paste a whole file back into chat.
- Chat replies: answer first, no recap. Use the `concise` skill by default; `caveman` when the user asks for maximum savings. Files written for judges stay in full, normal sentences.
- Skills to use:
  - `case-solution-design` (the workflow)
  - `judge-panel` (cheap pressure test)
  - `verification-before-completion` (before saying a number or file is correct)
  - `mckinsey-strategy-team`: only once, for the final stress test, because it runs many agents.

## Team roles

| Code | Role |
|---|---|
| M1 | Lead, storyline & people (SQ1, close, Q&A routing) |
| M2 | Operations, TPS & roadmap (SQ2, SQ3, design) |
| M3 | Quant, finance & evidence (SQ4, model, appendix) |
