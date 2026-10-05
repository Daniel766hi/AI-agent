---
name: judge-panel
description: Cheap, single-session pressure test of the case solution before submission or presentation. Attacks the recommendation from 4 judge lenses (assumptions, competitor and market moves, execution and money, story) and writes the Q&A bank. Use for "uji ke juri", "pressure test", "Q&A prep", "cari kelemahan".
---

# Judge Panel (lightweight)

A low-token alternative to `mckinsey-strategy-team`. Same idea (attack the answer before the judges do), but in one session, reading only the framework files it needs.

## Inputs (read only these)

1. `CLAUDE.md` (already loaded) for the answer and headline numbers.
2. `data/problem.md` for the key question and sub-questions.
3. The relevant section of `data/facts.md` only when a lens needs a number. Use `grep -n` first, then read the lines around the match.
4. One framework file per lens from `.claude/skills/mckinsey-strategy-team/references/`. Read the "Output Format" part only.

Do not open `.xlsx`, `.pdf`, `.docx` or images. If a number is needed from the model, run `cd model && python run_tests.py` and read only its printed summary.

## The 4 lenses

| Lens | Framework file | Question it asks |
|---|---|---|
| Assumptions | `01-diagnosis-and-framing/assumption-audit.md` | Which 3 beliefs carry the answer, and what happens to NPV and KPIs if each is wrong? |
| Market and competitor moves | `05-risk-performance-and-value-governance/war-gaming.md` | What if new players cut cost further, EV share hits 70%, or volume drops again? |
| Execution and money | `05-risk-performance-and-value-governance/risk-and-mitigation.md` | Can TMMIN's people actually run this by 2027? Does the gate catch failure early? |
| Story | `06-alignment-and-executive-communication/narrative-builder.md` | Does the executive summary land in 60 seconds? Is any claim unsupported? |

## Steps

1. For each lens, write up to 5 attacks. Each attack has: the attack in one line, severity (fatal / serious / minor), evidence we already have (slide, exhibit or model output), and the fix.
2. **Tally rule:** an attack that 2 or more lenses flag as fatal must change the answer, the numbers or the roadmap. List those first.
3. Turn the attacks into the Q&A bank: at least 15 questions. Each one has a short answer (2–3 sentences), the evidence, and an owner (M1, M2 or M3).
4. Write everything to `work/8_qa.md` in Bahasa Indonesia (or the user's language).

## Done when

- No fatal attack is left without a fix.
- Every Q&A answer points to a slide, an exhibit or a model output.
- The 3 hardest questions also have a 20-second spoken answer.
