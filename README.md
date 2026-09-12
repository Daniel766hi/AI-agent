# Trading Research Engine

A backtesting framework that tries hard not to lie to you.

Most backtests look profitable because of lookahead bias, ignored costs, or
parameter search presented as discovery. This one is built so those three
failure modes are structurally hard to commit, and it reports "no edge" loudly
when that's the truth — which it usually is.

## Quick start

```bash
pip install -r requirements.txt
python run_tests.py                                  # every self-check
python run.py --synthetic --strategy sma_cross      # random-walk sanity run
```

Then with real data:

```bash
python run.py --fetch BTCUSDT --strategy breakout   # Binance public API, no key
python run.py --csv data/your_data.csv --strategy sma_cross --periods-per-year 252
```

`--fetch` needs open network access — it won't run inside a Claude Code web
sandbox, whose policy blocks exchange hosts. Run it locally; it caches to
`data/` and the CSV path works anywhere.

## What keeps it honest

**One-bar execution lag.** `backtest()` shifts every signal forward a bar before
applying it. A signal derived from today's close trades at tomorrow's. This is
one line and it's the difference between a backtest and a fantasy.

**Costs on every position change.** Turnover is charged 15bps round-trip by
default (10 fee + 5 slippage). Strategies that churn are penalised the way a
real broker penalises them. Raise it for illiquid alts.

**Walk-forward parameter fitting.** Parameters are chosen on a training window
and traded on the window that follows — never on the bars they were fitted to.
Reported metrics are stitched from out-of-sample windows only.

The per-fold signals are stitched and backtested in a *single* pass. Running
each fold as its own backtest forces the position flat at every seam, losing
that bar's exposure and charging a re-entry, which moved the reported total
return by about 2 percentage points — in either direction, depending on how the
market happened to move across the seam.

**Block-bootstrap significance.** Returns are autocorrelated and fat-tailed, so
a t-test overstates confidence. A moving-block bootstrap resamples contiguous
runs, preserving local dependence, and tests whether the edge over buy-and-hold
could be luck.

This is measured, not assumed. Against 800 paired runs of autocorrelated noise
containing no real difference, where a correct test should report p<0.05 about
5% of the time:

| Autocorrelation | t-test | Block bootstrap |
|---|---|---|
| 0.0 | 4.7% | 5.1% |
| 0.3 | 10.3% | 6.6% |
| 0.6 | **20.3%** | 6.4% |
| 0.8 | **26.7%** | 7.4% |

A t-test on daily returns with mild autocorrelation manufactures significance
four times out of five that it claims. The block length scales with the
measured autocorrelation time — a fixed `n**(1/3)` left the rate at 11.1% at
rho=0.8 — and some inflation remains at extreme dependence, which is a known
limit of the method rather than something to tune away. A real edge is still
detected in 30 of 30 trials, so the conservatism does not come from blindness.

**Multiple-testing deflation.** Search 9 parameter sets, report the best one's
raw p-value, and you've fooled yourself. Every run applies a Šidák correction
for the number of configurations tried and prints both numbers. A raw p of 0.13
becomes 0.70 after nine trials — same data, honest verdict.

**A random-walk null.** `data.synthetic()` generates geometric Brownian motion:
no exploitable structure by construction. `test_no_edge_on_random_walk` runs
eight seeds through the full pipeline and fails if more than two show
significance. If your engine finds edge in noise, it has a leak.

## What profit would actually require

```bash
python analyze.py --csv data/BTCUSDT_1d.csv --strategy sma_cross
```

No backtest answers the questions that decide most outcomes, so `analyze.py`
does. None of it predicts returns — it is arithmetic on the parts you control.

**The frequency cliff.** Costs are the one guaranteed negative in trading, and
they scale with how often you trade. At 15bps round trip:

| Trading | Round trips/yr | Annual drag |
|---|---|---|
| monthly | 12 | 3.6% |
| weekly | 52 | 15.6% |
| daily | 250 | **75.0%** |
| 4x daily | 1000 | 300.0% |

Bitcoin's long-run return is roughly 40-60% a year. Trade it daily and you must
out-earn a 75% headwind before making a single rupiah. This is why most active
traders lose to people who did nothing — not because their strategies were
worse, but because they paid the toll 250 times instead of once.

**The hurdle.** A strategy sitting in cash part of the time forfeits the return
it would have earned holding. `analyze.py` adds that to the cost drag and prints
the total a strategy must beat to have been worth running.

**Survival.** Ruin probabilities bootstrapped from the actual return
distribution rather than a normal assumption, because fat tails are exactly what
ruin calculations get wrong. On a 60%-volatility asset over one year:

| Leverage | P(-20%) | P(-50%) | P(wiped out) |
|---|---|---|---|
| 1x | 88% | 11% | 0% |
| 2x | 100% | 66% | 0% |
| 3x | 100% | 91% | 2.7% |
| 5x | 100% | 99.9% | **42%** |

Leverage does not scale outcomes symmetrically. A wiped-out account cannot
recover, so 5x is not "5x the returns" — it is a 42% chance of having nothing.

**Position size.** Kelly sizing, with the caveat that matters: Kelly assumes the
edge estimate is correct. It is an estimate from one sample, and if it is too
high, full Kelly over-bets and loses money. When the estimated edge is negative
the tool says the growth-optimal size is zero and to not trade it.

## On guaranteed profit

There isn't any, here or anywhere. A system that reliably printed money would be
an arbitrage, and arbitrages close. Any backtest that looks like a guarantee is
overfitted, and this repo is built to catch exactly that.

What is actually within your control: trade less often, keep costs low, avoid
leverage, size positions so a bad run cannot end you, and compare everything
against simply holding the asset. Those are not consolation prizes — across
large populations of traders they explain more of the outcome spread than
strategy selection does.

## Layout

| File | Role |
|---|---|
| `quant/data.py` | CSV loading, Binance fetch with cache, synthetic GBM |
| `quant/backtest.py` | Execution, cost model, performance metrics |
| `quant/strategies.py` | Strategy functions + their parameter grids |
| `quant/validate.py` | Walk-forward splits, block bootstrap, deflation |
| `run.py` | CLI |
| `quant/risk.py` | Cost drag, break-even, ruin probability, Kelly |
| `analyze.py` | What profit requires and what prevents it |
| `tests/` | Self-checks, plain asserts, no framework |

## Writing a strategy

A strategy maps prices to target positions — `1.0` long, `0.0` flat, `-1.0`
short. Every value must be computable from data up to and including that bar;
the engine handles the execution lag.

```python
def my_strategy(close, window=30):
    return (close > close.rolling(window).mean()).astype(float)

REGISTRY["my_strategy"] = (my_strategy, {"window": [20, 30, 50]})
```

Keep grids small. Every extra combination is another chance to overfit, and the
deflation charges you for it.

## Reading the output

A strategy is worth paper-trading only if the **deflated** p-value is below 0.05
*and* out-of-sample Sharpe beats buy-and-hold. Both, not either.

Even then it is not proof. It means the result survived a deliberately hostile
test on historical data. Markets change, and a backtest cannot see that coming.

## Data sources

| Source | Covers | Key needed |
|---|---|---|
| `data.fetch_binance()` | Binance spot pairs (BTCUSDT, ETHUSDT, ...) | no |
| `data.fetch_coingecko()` | thousands of coins by slug ("bitcoin", "solana") | no |
| `data.coingecko_top(n)` | top n coin ids by market cap — a screening universe | no |
| `data.fetch_yahoo()` | equities and crypto: `BBCA.JK`, `TLKM.JK`, `AAPL`, `BTC-USD` | no |
| `data.load_csv()` | anything with a date and close column | — |

IDX tickers take a `.JK` suffix. CoinGecko's free tier allows roughly 10-30
calls a minute; the fetchers cache to `data/` so a repeated screen costs nothing.

These were written against each API's documented response shape and their
parsers are unit-tested against captured payloads, but **none has been run
against the live endpoints** — this sandbox's network policy blocks them. Expect
to fix a field name or two on first real use.

**Ajaib is not supported.** There is no public Ajaib market-data or trading API
that I can point you at, scraping a broker's private endpoints generally breaches
their terms, and automating an account without an official API puts the account
at risk. Yahoo gives you the same IDX prices legitimately. For automated
execution on Indonesian equities you need a broker that publishes a trading API.

## Screening many assets

```bash
python screen.py --yahoo BBCA.JK TLKM.JK ASII.JK BBRI.JK --strategy breakout
python screen.py --coingecko-top 30 --strategy sma_cross
python screen.py --synthetic 120 --strategy breakout     # the null, for calibration
```

Screening is where backtests do their worst lying, so the screener is built
around one correction. Testing 120 assets with 3 configs each is **360 trials**,
and at 360 trials something will look brilliant by chance. The output shows both
numbers side by side:

```
Asset                    Sharpe  vs hold    Return    MaxDD   p (naive)  p (honest)
noise_066                 -0.45    -1.34    -41.8%   -65.0%      0.0578      0.9992
```

That asset is pure synthetic noise. Per-asset it looks near-significant; charged
for the whole screen it is nothing. Run `--synthetic N` at your real screen size
occasionally — it tells you what your setup produces from noise alone.

## Risk sizing, and a finding that went against expectation

`vol_target()` scales any strategy's position by (target volatility / recent
realised volatility). The rationale is the one claim in empirical finance that
holds up well: **volatility is persistent and forecastable; direction is not.**
So size by the thing you can actually predict.

To test that properly the repo has a second null. `data.synthetic_garch()`
generates volatility clustering while keeping direction unforecastable — so a
strategy that exploits clustering shows up, and one that just curve-fits does
not. Verified: |return| autocorrelation 0.144 on GARCH vs -0.001 on plain GBM,
with return autocorrelation ~0.015 on both.

The prediction going in was that vol targeting would improve Sharpe on clustered
data. **It did not** — measured over 40 paths, the Sharpe change was -0.02,
statistically indistinguishable from zero. Return and risk scale down together.

What it does deliver, same 40 paths:

| | Unsized | Vol-targeted |
|---|---|---|
| Realised volatility | 59.2% | 41.3% (target: 40%) |
| Max drawdown | -75.1% | -61.9% |
| Volatility of volatility | 0.154 | 0.074 |
| Shallower drawdown | — | **40 of 40 paths** |

So it is risk control, not alpha, and the docstring now says exactly that. Use
it to hold a risk budget you can live with, not to make money appear. The
finding is pinned by `test_vol_target_claims_no_alpha`, which fails if a future
change ever makes vol targeting look profitable on unforecastable data — that
would mean a lookahead bug, not a discovery.

`ts_momentum` is included on similar terms: time-series momentum is among the
better-documented cross-asset effects (Moskowitz, Ooi & Pedersen 2012), usually
attributed to slow information diffusion. A documented past effect is still not
a promise about your data.

## Bad data is rejected, not absorbed

Real feeds produce bad ticks: a zero from an API error, a gap over a trading
halt, a negative from a bad parse. `backtest()` refuses all three at the one
point every backtest, screen and live tick passes through.

This is not pedantry. Before the check, a single zero price produced an
**infinite** return — and an asset with an infinite return ranks first in any
screen you run. The failure mode was to hand you a fabricated winner.

Missing bars are ordinary, so `load_csv()` drops them and says how many; zero
and negative prices are not ordinary, so they raise with the offending
timestamp named. A screen skips the bad asset and continues, and the
multiple-testing count drops to match the assets that actually ran.

## Paper and live trading

```bash
python trade.py --strategy sma_cross --mode paper --poll 3600
```

Paper mode simulates fills with the **same cost model as the backtest**, so paper
results are comparable to backtest results rather than flattering to them. State
persists to `data/`, survives restarts, and is what the dashboard reads.

Live mode places real orders on Binance spot and has to get past five gates:

| Gate | Why |
|---|---|
| `--yes-real-money` | No accidental live run from shell history |
| `BINANCE_API_KEY` / `_SECRET` in env | Never on the command line, never in a file |
| `--max-notional` | Caps every single order; clamped, never silently exceeded |
| Walk-forward validation passes | Refuses to trade a strategy with no measured edge |
| `--max-drawdown` kill switch | Flattens and halts; does not average down |

The halt persists. A trader that stopped at -15% reloads that halt and its
drawdown peak on restart, so restarting does not hand it a fresh -15% of room
to lose. Clearing it is a deliberate act — `trade.py --reset` — and it prints
what it cleared.

State is written atomically (temp file, then rename), because the dashboard
polls the same file while the trader rewrites it. A plain write is truncated
mid-rewrite, and a reader landing there sees invalid JSON. That mattered: the
dashboard reported "no trader has run yet" while a position was open. If the
file is ever genuinely corrupt the dashboard says so and returns 503, rather
than rendering an unknown position as flat.

```bash
export BINANCE_API_KEY=... BINANCE_API_SECRET=...
python trade.py --strategy sma_cross --mode live \
  --validate-csv data/BTCUSDT_1d.csv --max-notional 50 --max-drawdown 15 --yes-real-money
```

The validation gate is overridable with `--skip-validation`, which prints
`You are trading noise.` and means it.

**The live broker has still never placed a real order**, but it is no longer
untested. `tests/fake_binance.py` is a stand-in exchange that verifies HMAC
signatures, enforces `LOT_SIZE` and `minNotional`, and settles balances, and the
broker is driven through full buy/sell round trips against it. That proves our
signing, symbol handling and lot maths are self-consistent; it proves nothing
about the real API's behaviour today.

Two bugs it caught, both of which would only have shown up with money at stake:

- Base and quote assets were split by string position (`symbol[:-4]`), so any
  pair without a four-character quote parsed as nonsense — `ETHBTC` became
  `ET`/`HBTC`. Balances then read zero, orders were skipped as dust, and the
  kill switch never saw a drawdown. It looked healthy while doing nothing.
  Assets and lot rules now come from `exchangeInfo`.
- Lot rounding used float division, and `0.01663 / 0.00001` is
  `1662.9999999999998`, so flooring dropped a whole step. An order meant to
  flatten the position left a sliver of it behind — and flattening is exactly
  what the drawdown kill switch does. Lot arithmetic now uses `Decimal`.

Point `BINANCE_API_URL` at `https://testnet.binance.vision` and read every fill
before trusting it with real funds. Restrict the API key to spot trading, never
enable withdrawals, and IP-allowlist it.

## The desk: one idea, four mandates, any veto final

```bash
python desk.py --synthetic --strategy breakout
python desk.py --csv data/BTCUSDT_1d.csv --strategy ts_momentum --equity 5000
```

The way a trading system fails is self-deception: the same process that wants
the trade also judges whether the trade is sound. Real desks separate those
roles, and a risk officer who can only advise is not a risk officer. So the
decision is split across agents with narrow mandates:

| Agent | Mandate | Can it approve? |
|---|---|---|
| `research` | Fit parameters out-of-sample, show the working | Reports evidence; **cannot approve its own work** |
| `skeptic` | Assume noise until the evidence survives the search that found it | Veto |
| `cost` | Confirm the edge exceeds what it costs to capture | Veto |
| `risk` | Ensure a bad run cannot end the account | Veto, and sets position size |

**Approval is unanimous and a veto is final.** No score, no weighting, no
majority — a structure where two optimistic agents can outvote the risk agent is
how accounts die. An agent that crashes has not approved anything.

Run across six regime-switching series with genuine structure, the desk approved
one. The rejections are the interesting part:

```
seed 1  research: OOS Sharpe 2.89 vs 2.39 holding    ->  VETO skeptic: p=0.635
seed 5  research: OOS Sharpe 2.13 vs 1.53 holding    ->  VETO skeptic: p=0.563
seed 3  research: OOS Sharpe 1.30 vs 1.35 holding    ->  VETO cost: returns 43% vs 59% holding
seed 2  research: OOS Sharpe 0.78 vs -1.28 holding   ->  APPROVED, p=0.000
```

A Sharpe of 2.89 is the number that gets people to wire money. It was refused
because it is not distinguishable from luck, by an agent with no stake in the
idea. The one that passed had a *lower* headline Sharpe and better evidence.

Two things the desk reports that are easy to misread as good news. A half-Kelly
above 100% is **capped**, and the verdict says so — a Kelly that large implies a
Sharpe that out-of-sample results almost never sustain, so read it as evidence
the edge estimate is inflated rather than as a case for leverage. And pinning
parameters is charged one trial instead of the whole grid, which is only honest
if you chose them before seeing the data; the code cannot check that and does
not pretend to.

The agents are deterministic and rule-based, so their reasoning is auditable
and reproducible rather than persuasive. An LLM-backed agent could implement the
same `Agent` contract, but nothing here needs one, and a component that costs
money per call and answers differently each time does not belong on a veto path.

`data.synthetic_regimes()` generates the alternating bull/bear series used
above — the one generator here that *does* contain exploitable structure,
so the pipeline can be checked for being a rejection machine rather than a
filter.

## Running it unattended

```bash
export NOTIFY_WEBHOOK="https://hooks.slack.com/services/..."   # or a Discord webhook
python trade.py --strategy sma_cross --mode paper --poll 3600
```

To survive reboots and crashes, use the supplied systemd unit rather than a
terminal you have to keep open:

```bash
sudo cp deploy/trading-agent.service /etc/systemd/system/   # edit paths first
sudo systemctl enable --now trading-agent
journalctl -u trading-agent -f
```

**`Restart=on-failure`, deliberately not `always`.** A crash is worth retrying;
a halt is not. `trade.py` exits 0 when the drawdown kill switch fires, so
systemd leaves it stopped. Auto-restarting a strategy that just protected you
is exactly the wrong behaviour at 3am. Secrets go in `/etc/trading-agent.env`
(root, `chmod 600`) — never in the unit file or on the command line.

### What it tells you

An agent that runs for weeks has to stay quiet and then be unmissable, so only
three things send:

| Alert | When | Throttle |
|---|---|---|
| `[HALTED]` | The kill switch fired, or funds ran out | **Never throttled** |
| `[DEGRADED]` | Three consecutive failed ticks — running but not trading | Hourly |
| `[DAILY]` | Equity, position, drawdown, trade count | Once a day |

There are no per-trade alerts by design. An alert you learn to ignore is worse
than no alert.

Alerting is best-effort and never fatal: with `NOTIFY_WEBHOOK` unset every call
is a silent no-op, and an unreachable webhook is swallowed. A test asserts the
kill switch still fires with the webhook pointed at a dead port — the safety
stop must never depend on the notifier working.

## Dashboard

```bash
python web/app.py                          # prints an access token
DASHBOARD_TOKEN=... python web/app.py      # stable token across restarts
```

An app shell with four views — Overview, Costs, Validation, Trades — as top
tabs on desktop and a bottom tab bar on mobile. Each view is a real history
entry, so the browser back button works and a view can be linked directly
(`#costs`). Polls every 15s, with a live/stale/stopped indicator in the bar.

Built to the app-UI rules: SVG icons rather than emoji, 44px minimum touch
targets, visible keyboard focus, `prefers-reduced-motion` honoured, and every
table in its own scroll container so the page never scrolls sideways. Committed
to dark — an ops console read in long sessions — with green and red reserved for
state, never decoration.

**Access control.** It binds to `127.0.0.1`, so only processes on your machine can
reach it at all — that is the real boundary, and it needs no password to be
effective. On top of that, every route requires a 256-bit token compared in
constant time, and the API returns 401 rather than redirecting. `--host 0.0.0.0`
prints a warning; if you want it from your phone, use an SSH tunnel or Tailscale
rather than a public bind, and put HTTPS in front of it. Flask's dev server is
not a production server.

Set `DASHBOARD_SECRET` as well as `DASHBOARD_TOKEN` if you want sessions to
survive a restart.

Probed rather than assumed: every API route returns 401 unauthenticated, the
token never appears in a response, and path traversal is refused including the
URL-encoded and `data/../../` forms. Responses carry `X-Frame-Options`,
`X-Content-Type-Options`, `Referrer-Policy` and a CSP with `frame-ancestors
'none'` and `form-action 'self'`; the session cookie is `HttpOnly` and
`SameSite=Lax`, and gains `Secure` automatically when bound off loopback — so
sign-in fails over plain HTTP by design rather than leaking the token in
transit.

Errors say what to fix and nothing else. They previously echoed the absolute
path and the file's first line back to the caller, which reflects deployment
layout to whoever reaches the endpoint.

## Deliberately not built

Multi-user accounts, a hosted deployment, and order types beyond market orders.
No profit guarantee, because none exists: this measures strategies honestly, it
does not make them work.

Also skipped: portfolio-level allocation, position sizing beyond flat/long/short,
intraday microstructure, short borrow costs. Add them when a validated strategy
actually needs them.
