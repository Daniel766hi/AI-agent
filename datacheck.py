#!/usr/bin/env python3
"""Check which market data sources actually work from this machine.

  python datacheck.py                      # test all sources
  python datacheck.py --save               # also write a CSV and backtest it

Run this first. It reports, per source, whether the request succeeded, was rate
limited, needed a key, or could not be reached — and says what to do about each.

Nothing here has been verified against the live APIs from the machine that wrote
it; that sandbox blocks all three hosts. This tool exists precisely because that
verification has to happen on yours.
"""
import argparse
import os
import sys
import time

from quant import data
from quant.data import DataError

PROBES = [
    ("Binance",   "BTCUSDT daily",
     lambda: data.fetch_binance("BTCUSDT", "1d", start="2024-01-01", cache_dir=None)),
    ("CoinGecko", "bitcoin, 90 days",
     lambda: data.fetch_coingecko("bitcoin", days=90, cache_dir=None)),
    ("Yahoo (crypto)", "BTC-USD 1y",
     lambda: data.fetch_yahoo("BTC-USD", range_="1y", cache_dir=None)),
    ("Yahoo (IDX)", "BBCA.JK 1y",
     lambda: data.fetch_yahoo("BBCA.JK", range_="1y", cache_dir=None)),
    ("Yahoo (US)", "AAPL 1y",
     lambda: data.fetch_yahoo("AAPL", range_="1y", cache_dir=None)),
]


def probe(name, description, call):
    started = time.time()
    try:
        frame = call()
    except DataError as exc:
        return {"name": name, "ok": False, "detail": str(exc), "kind": "refused"}
    except Exception as exc:
        return {"name": name, "ok": False, "detail": f"{type(exc).__name__}: {exc}",
                "kind": "broken"}

    elapsed = time.time() - started
    close = frame["close"]
    return {
        "name": name, "ok": True, "rows": len(close),
        "first": str(close.index[0].date()), "last": str(close.index[-1].date()),
        "latest": float(close.iloc[-1]), "seconds": elapsed, "frame": frame,
        "detail": description,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--save", action="store_true",
                    help="write each working source to data/ and backtest one")
    ap.add_argument("--symbol", help="also try this Yahoo ticker (e.g. TLKM.JK)")
    args = ap.parse_args()

    probes = list(PROBES)
    if args.symbol:
        probes.append((f"Yahoo ({args.symbol})", f"{args.symbol} 1y",
                       lambda: data.fetch_yahoo(args.symbol, range_="1y", cache_dir=None)))

    key = os.environ.get("COINGECKO_API_KEY", "").strip()
    print(f"\n{'=' * 74}")
    print("  Market data connectivity")
    print(f"  CoinGecko key: {'set (' + os.environ.get('COINGECKO_PLAN', 'demo') + ')' if key else 'not set — free tier, rate limited'}")
    print(f"{'=' * 74}\n")

    results = []
    for name, description, call in probes:
        print(f"  {name:<18} {description:<22} ", end="", flush=True)
        result = probe(name, description, call)
        results.append(result)
        if result["ok"]:
            print(f"OK   {result['rows']:>5} bars  {result['first']} to {result['last']}  "
                  f"last {result['latest']:,.2f}  ({result['seconds']:.1f}s)")
        else:
            print("FAILED")
            for line in _wrap(result["detail"]):
                print(f"                     {line}")
        time.sleep(1.0)          # be a good citizen between probes

    working = [r for r in results if r["ok"]]
    print(f"\n  {len(working)} of {len(results)} sources working.\n")

    if args.save and working:
        print("  Saving samples to data/ …")
        from pathlib import Path
        Path("data").mkdir(exist_ok=True)
        for result in working:
            slug = result["name"].lower().replace(" ", "_").replace("(", "").replace(")", "")
            path = Path("data") / f"check_{slug}.csv"
            result["frame"].reset_index(names="date").to_csv(path, index=False)
            print(f"    {path}")

        best = max(working, key=lambda r: r["rows"])
        print(f"\n  Backtesting the longest series ({best['name']}, {best['rows']} bars):\n")
        _quick_backtest(best["frame"]["close"])

    if not working:
        print("  Nothing reachable. Either this machine has no outbound HTTPS, or a")
        print("  proxy or firewall is blocking these hosts. A Claude Code web sandbox")
        print("  blocks all of them by design — run this on your own machine.\n")
        return 1

    print("  Next:")
    print("    python screen.py --yahoo BBCA.JK TLKM.JK ASII.JK BBRI.JK --strategy breakout")
    print("    python run.py --csv data/check_yahoo_idx.csv --strategy sma_cross --periods-per-year 252")
    print("    python analyze.py --csv data/check_binance.csv --strategy sma_cross\n")
    return 0


def _quick_backtest(close):
    from quant.strategies import REGISTRY
    from quant.validate import block_bootstrap_pvalue, deflate, walk_forward
    from quant.backtest import metrics

    fn, grid = REGISTRY["sma_cross"]
    try:
        oos, _, bench, trials = walk_forward(close, fn, grid, n_folds=4)
    except ValueError as exc:
        print(f"    not enough history to validate: {exc}")
        return
    p, _ = block_bootstrap_pvalue(oos, bench)
    strat, hold = metrics(oos), metrics(bench)
    print(f"    strategy  CAGR {strat['cagr']:>7.1%}   Sharpe {strat['sharpe']:>6.2f}")
    print(f"    holding   CAGR {hold['cagr']:>7.1%}   Sharpe {hold['sharpe']:>6.2f}")
    print(f"    p after {trials} configs searched: {deflate(p, trials):.4f}")
    print("\n    Real data, real verdict. Expect no edge — that is the usual answer.")


def _wrap(text, width=52):
    words, line, out = text.split(), "", []
    for word in words:
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


if __name__ == "__main__":
    sys.exit(main())
