# CLAUDE.md

Trading research engine. The product is **trustworthy measurement**, not profit.
Most changes should make results harder to fake, not prettier.

## The one rule

Every number this repo prints is something a person might risk money on. A
backtest that overstates performance is worse than no backtest, because it
converts caution into confidence. When a change could make results look better
OR make them more honest, pick honest.

## Non-negotiables

Do not weaken these without the user explicitly asking, and say so plainly if
asked:

- **One-bar execution lag.** `backtest()` shifts every signal before applying
  it. Never remove the shift, never let a strategy see a bar it trades on.
- **Costs on every position change.** Fees and slippage are charged on turnover.
  Never default them to zero outside a test that is specifically isolating them.
- **Out-of-sample reporting.** Headline metrics come from walk-forward test
  windows only. Never report in-sample numbers as results.
- **Deflation for search.** Any p-value must be charged for every configuration
  tried — and in a screen, for every asset too (`assets x configs`). A raw
  p-value next to a searched grid is a lie.
- **Live trading stays gated.** `--yes-real-money`, env credentials,
  `--max-notional`, passing validation, drawdown kill switch. Five gates. Do not
  quietly relax one.

## Testing conventions

Self-checks are plain `assert` functions in `tests/test_*.py`, run with
`python tests/test_x.py`. No pytest, no fixtures. **Keep the `__main__` runner at
the end of the file** — it collects tests from `globals()`, so anything defined
below it silently never runs. That bug has already happened once.

Run all three before committing:

```bash
python tests/test_quant.py && python tests/test_strategies.py && python tests/test_trading.py
```

**Synthetic data is the null hypothesis, and it is load-bearing.**
`data.synthetic()` is a random walk; `data.synthetic_garch()` adds volatility
clustering while keeping direction unforecastable. A strategy showing
significant edge on either one is reporting a bug, not a signal. New strategies
get a test asserting they find nothing there.

## Claims must be measured, not asserted

Docstrings state what a thing was **measured** to do, with the test that shows
it. `vol_target` is the model: it claims drawdown reduction and vol stability
because those were measured across 40 paths, and explicitly disclaims Sharpe
improvement because that was tested and did not hold. Do not write a docstring
promising a benefit nobody verified.

If a measurement contradicts what was expected, the finding wins. Report it and
correct the claim.

## Layout

| Path | Role |
|---|---|
| `quant/backtest.py` | Execution, cost model, metrics. The correctness core. |
| `quant/validate.py` | Walk-forward, block bootstrap, Sidak deflation |
| `quant/strategies.py` | Strategy functions + parameter grids + `REGISTRY` |
| `quant/data.py` | CSV, Binance, CoinGecko, Yahoo, synthetic generators |
| `quant/broker.py` | PaperBroker (tested), BinanceBroker (untested live) |
| `quant/live.py` | Trading loop, kill switch, state file |
| `run.py` / `screen.py` / `trade.py` | CLIs |
| `web/app.py` | Token-auth dashboard, localhost-bound |

## Strategy contract

A strategy maps `close` to target positions (`1.0` long, `0.0` flat). Every
value must be computable from data up to and including that bar. Register it in
`REGISTRY` with a **small** grid — every extra combination is charged against
significance.

Prefer strategies with an economic rationale over chart shapes, and state the
rationale honestly, including that a documented past effect is not a promise.

## Known limits — state these, don't paper over them

- `BinanceBroker` has **never placed a real order**. Signing is verified against
  Binance's published vector; nothing else on that path has run live.
- CoinGecko and Yahoo fetchers are tested against captured payload shapes, never
  against the live endpoints (this sandbox blocks them).
- No strategy in the repo has demonstrated edge. That is the expected result and
  not a defect to fix by adding more strategies — more strategies make the
  multiple-testing problem worse.
- Flask's dev server is not a production server.

## Environment

`pip install -r requirements.txt`. Claude Code web sandboxes block exchange and
market-data hosts (403 on CONNECT), so `--fetch`, CoinGecko, and Yahoo only work
on a real machine. Use `--synthetic` / `--csv` in the sandbox.

## Commits

Conventional prose, imperative mood, explain **why**. Never commit `data/`
(gitignored — it holds cached prices and broker state). Never commit
credentials; exchange keys come from the environment only.
