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

**Closed-Loop Kaizen v2** — a plant that learns from itself. Three loops with people at the center, plus a time rule:
1. Quality loop (jidoka): every abnormality returns to the process that caused it within minutes.
2. Data & equipment loop (standardized work): one in-house interface standard; a new variant becomes configuration.
3. People & knowledge loop (kaizen, yokoten): operator-built AI tools, one-tap idea channel, captured senior know-how.
4. Protected improvement time: 30% of engineer/team-leader time, phased in over 6 months, plus a ratchet that locks in time the loops free. Protecting 35-40% was tested and dropped (it costs NPV); protecting nothing makes the gate stop working programs (46% vs 22% of runs).

Pilot: sealer → inspection (final assembly is rollout wave 1). Funding: pilot-light (10/15/40/25/10% of Rp80B) with a go/no-go gate at end-2027 (six criteria in `work/6_roadmap.md`). A mid-2027 gate was tested and is too early.

Headline numbers (each tied out by `python work/8_tieout.py`):
- Cost index 2030 at constant 2025 prices: **97-101** (spreadsheet 96.9; system dynamics 100.8) vs 113.9 with no action.
- NPV 2026-30 at 10%: **Rp27-31B** (spreadsheet 27.0; system dynamics 31.4 vs no action). Against a frozen-2025 baseline: -65.4 (2026-30), +17.0 (2026-35). Quote both.
- P(NPV>0): 86% (spreadsheet, 10,000 runs) / 94% (system dynamics, 1,500 runs). One year late: 32% / 21%. Loop fails: pilot-light 90% vs front-loaded 60%.
- Variant change 9 → 7.2 months (vs 10.4 no action); Software & AI L3+ 2 → 13.6; know-how 33% → 64%; dependence on 1-2 seniors 48% → 26%.
- Sustainability: ~1,765 t CO2/yr avoided in 2030; scrap -40% vs no action; 2035 index 98.4 if the way of working is kept, 105.2 if stopped in 2031.
- Against a competitor that keeps falling, the gap widens 1.7 pts/yr instead of 6.7; the program does **not** close it by 2030. Never claim otherwise.

## Work products

| Path | What |
|---|---|
| `work/2_diagnosis.md` + `2_diagnosis_calc.py` | Issue tree, heat map, root cause |
| `work/3_options.md` | 12 options, integrated idea |
| `work/4_scoring.md` + `4_scoring.py` | Weighted scoring with random-weight check; pilot choice |
| `work/5_tests.md` | All three models, stress tests, sustainability, design changes they forced |
| `work/6_roadmap.md`, `work/7_kpis.md` | Phases, gate, 100 days, risks; KPI targets consistent with the models |
| `work/8_storyline.md`, `work/8_qa.md` | Action titles; judge-panel attacks and 20-question Q&A |
| `work/8_tieout.py` | Fails if any headline number in the docs or deck does not match a model |
| `model/sd_model.py` | System dynamics model (economics + sustainability); `--quick` skips Monte Carlo and leaves `sd_results.json` alone |
| `outputs/proposal_draft.md` | Paper text for the Word template |
| `outputs/deck_closed_loop_kaizen.pptx` | Deck, built by `outputs/build_deck.js` from `model/sd_results.json` |

## Rules for working here

- Use the `case-solution-design` skill when designing, testing or rewriting any part of the solution.
- Every number must come from `data/facts.md` or `model/`. Never invent figures; label assumptions.
- After changing assumptions in `model/build_model.py` or `model/sd_model.py`, run `cd model && python build_model.py && python run_tests.py && python sd_model.py`, rebuild the deck (`NODE_PATH=<pptxgenjs> node outputs/build_deck.js`), then `python work/8_tieout.py` must pass before any number is quoted.
- If a model contradicts a target or a claim, the model wins: lower the target in the open (see `work/7_kpis.md` §4).
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
