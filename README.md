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

## Deliberately not built

No live trading, no exchange keys, no order execution. Paper-trade first, and
wire up real capital only with out-of-sample numbers in front of you.

Also skipped: portfolio-level allocation, position sizing beyond flat/long/short,
intraday microstructure, short borrow costs. Add them when a validated strategy
actually needs them.
