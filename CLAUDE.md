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
  windows only. Never report in-sample numbers as results. Fold signals are
  stitched and backtested in one pass — never one backtest per fold, which
  forces the position flat at each seam and fabricates a round trip there.
- **The significance test is calibrated, and must stay that way.** Changing
  anything in `block_bootstrap_pvalue` or `_block_length` means re-running
  `tests/test_validate.py`, which asserts the false-positive rate under the
  null. A test that finds edges in noise makes every verdict in the repo
  worthless.
- **On the desk, a veto is final.** `Desk` requires unanimous approval and has
  no scoring or weighting. Never add a majority vote, a confidence weight, or an
  override — the whole point is that optimism cannot outvote risk. An agent that
  raises has not approved.
- **Numbers name the configuration they describe.** Cost drag, the hurdle,
  ruin and Kelly all move with the parameters. Never report them for a set
  nobody chose — fit out-of-sample or take the caller's, and say which on the
  output.
- **Parallelism may change speed, never results.** Screening runs across
  processes; each asset is independent and each bootstrap seeded, so worker
  count cannot move a number. `tests/test_screen.py` asserts serial and
  parallel agree exactly. A worker returns failures rather than raising — one
  bad asset must not lose the batch.
- **Deflation for search.** Any p-value must be charged for every configuration
  tried — and in a screen, for every asset too (`assets x configs`). A raw
  p-value next to a searched grid is a lie.
- **Live trading stays gated.** `--yes-real-money`, env credentials,
  `--max-notional`, passing validation, drawdown kill switch. Five gates. Do not
  quietly relax one.
- **Exchange facts come from the exchange.** Never infer a pair's base/quote by
  slicing the symbol, and never hardcode lot steps or minimums — read
  `exchangeInfo`. Use `Decimal` for lot arithmetic; float division silently
  drops a step and leaves a position that was meant to be flat.
- **Alerting is best-effort, never load-bearing.** A dead webhook must not
  change what the trader does. The kill switch has a test asserting it still
  fires with alerting pointed at a dead port.
- **A supervisor must not restart a halt.** trade.py exits 0 on a kill-switch
  stop so `Restart=on-failure` leaves it stopped. Never change that to
  `Restart=always`.
- **A halt outlives its process.** The drawdown halt and peak persist to the
  state file and reload on start. Never let a restart reset them — that hands a
  just-stopped strategy a fresh allowance to lose. Only `--reset` clears it.
- **Background work outlives its bookkeeping.** A screen job may only be
  evicted once it is finished, and progress updates tolerate a job that is
  already gone. Evicting a running job used to kill its thread *and* the
  handler meant to record the failure, leaving the page polling a 404. Only one
  screen runs at a time — each spawns a process pool, and several oversubscribe
  the machine.
- **State writes are atomic.** The dashboard polls the state file while the
  trader rewrites it, so write to a temp file and rename. And never report an
  unreadable state as "not running" — unknown is not the same as flat.
- **The dashboard says what to fix, never what it found.** An API error must
  not carry an absolute path, a file's contents, or a library's internals —
  log those and return a message the user can act on. `pandas.errors.ParserError`
  subclasses `ValueError`, so catch it first or its text goes straight to the
  browser.
- **Bad prices are rejected, never filled.** `backtest()` refuses missing, zero
  and negative prices. Real feeds produce all three, and a single zero makes the
  next return infinite — which would rank that asset first in any screen. Drop
  bad bars deliberately at load time; never let them reach a result.

## Testing conventions

Self-checks are plain `assert` functions in `tests/test_*.py`, run with
`python tests/test_x.py`. No pytest, no fixtures. **Keep the `__main__` runner at
the end of the file** — it collects tests from `globals()`, so anything defined
below it silently never runs. That bug has already happened once.

Run everything before committing:

```bash
python run_tests.py
```

It exits non-zero when any file fails, so it is safe to gate on.

**Documentation is checked, not trusted.** `tests/test_docs.py` asserts that
every module appears in the Layout table, that no doc names a file that does not
exist, that no doc hardcodes a test count, and that every test file keeps its
runner last. All four checks exist because each of those drifted silently first.
When editing docs from a script, assert the anchor — `str.replace` no-ops when
it misses, and a chain of those quietly did nothing across several commits.

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
| `quant/strategies.py` | Strategy functions, parameter grids, `REGISTRY` |
| `quant/data.py` | CSV, Binance, CoinGecko, Yahoo, synthetic generators |
| `quant/risk.py` | Cost drag, break-even hurdle, ruin probability, Kelly |
| `quant/agents.py` | Research/skeptic/cost/risk agents and the desk |
| `quant/broker.py` | PaperBroker, BinanceBroker (never live-traded) |
| `quant/live.py` | Trading loop, kill switch, state file |
| `quant/notify.py` | Rate-limited webhook alerts for unattended runs |
| `run.py` | Walk-forward one strategy on one asset |
| `screen.py` | Screen many assets, deflating for every trial |
| `analyze.py` | What profit requires and what prevents it |
| `desk.py` | Put a proposal to the agent desk |
| `datacheck.py` | Which market data sources work from this machine |
| `trade.py` | Paper or live trading |
| `run_tests.py` | Runs every self-check, non-zero on failure |
| `web/app.py` | Token-auth dashboard, localhost-bound |
| `deploy/trading-agent.service` | systemd unit for unattended running |

Adding a module means adding a row. `tests/test_docs.py` fails otherwise — the
table drifted silently for seven files before that check existed.

## Strategy contract

A strategy maps `close` to target positions (`1.0` long, `0.0` flat). Every
value must be computable from data up to and including that bar. Register it in
`REGISTRY` with a **small** grid — every extra combination is charged against
significance.

Prefer strategies with an economic rationale over chart shapes, and state the
rationale honestly, including that a documented past effect is not a promise.

## Known limits — state these, don't paper over them

- `BinanceBroker` has **never placed a real order** against the real exchange.
  It is exercised end to end against `tests/fake_binance.py`, which verifies
  signatures and enforces lot filters — that catches our bugs, not the real
  API's current behaviour. Use testnet before real funds.
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
