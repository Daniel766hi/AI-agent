# Trading Research Engine

A backtesting framework that tries hard not to lie to you.

Most backtests look profitable because of lookahead bias, ignored costs, or
parameter search presented as discovery. This one is built so those three
failure modes are structurally hard to commit, and it reports "no edge" loudly
when that's the truth — which it usually is.

## Quick start

```bash
pip install -r requirements.txt
python tests/test_quant.py                          # 8 self-checks
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

**Block-bootstrap significance.** Returns are autocorrelated and fat-tailed, so
a t-test overstates confidence. A moving-block bootstrap resamples contiguous
runs, preserving local dependence, and tests whether the edge over buy-and-hold
could be luck.

**Multiple-testing deflation.** Search 9 parameter sets, report the best one's
raw p-value, and you've fooled yourself. Every run applies a Šidák correction
for the number of configurations tried and prints both numbers. A raw p of 0.13
becomes 0.70 after nine trials — same data, honest verdict.

**A random-walk null.** `data.synthetic()` generates geometric Brownian motion:
no exploitable structure by construction. `test_no_edge_on_random_walk` runs
eight seeds through the full pipeline and fails if more than two show
significance. If your engine finds edge in noise, it has a leak.

## Layout

| File | Role |
|---|---|
| `quant/data.py` | CSV loading, Binance fetch with cache, synthetic GBM |
| `quant/backtest.py` | Execution, cost model, performance metrics |
| `quant/strategies.py` | Strategy functions + their parameter grids |
| `quant/validate.py` | Walk-forward splits, block bootstrap, deflation |
| `run.py` | CLI |
| `tests/test_quant.py` | Self-checks, no framework needed |

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

```bash
export BINANCE_API_KEY=... BINANCE_API_SECRET=...
python trade.py --strategy sma_cross --mode live \
  --validate-csv data/BTCUSDT_1d.csv --max-notional 50 --max-drawdown 15 --yes-real-money
```

The validation gate is overridable with `--skip-validation`, which prints
`You are trading noise.` and means it.

**The live broker has never placed a real order.** Its request signing is
unit-tested against Binance's published example vector, but nothing else on that
path has run against the exchange. Point `BINANCE_API_URL` at
`https://testnet.binance.vision` and read every fill before you trust it with
real funds. Restrict your API key to spot trading, never enable withdrawals, and
IP-allowlist it.

## Dashboard

```bash
python web/app.py                          # prints an access token
DASHBOARD_TOKEN=... python web/app.py      # stable token across restarts
```

Live position, equity, drawdown, trade history, and on-demand walk-forward
validation with an equity curve. Polls every 15s. Works at phone width.

**Access control.** It binds to `127.0.0.1`, so only processes on your machine can
reach it at all — that is the real boundary, and it needs no password to be
effective. On top of that, every route requires a 256-bit token compared in
constant time, and the API returns 401 rather than redirecting. `--host 0.0.0.0`
prints a warning; if you want it from your phone, use an SSH tunnel or Tailscale
rather than a public bind, and put HTTPS in front of it. Flask's dev server is
not a production server.

Set `DASHBOARD_SECRET` as well as `DASHBOARD_TOKEN` if you want sessions to
survive a restart.

## Deliberately not built

Multi-user accounts, a hosted deployment, and order types beyond market orders.
No profit guarantee, because none exists: this measures strategies honestly, it
does not make them work.

Also skipped: portfolio-level allocation, position sizing beyond flat/long/short,
intraday microstructure, short borrow costs. Add them when a validated strategy
actually needs them.
