"""Price data: load from CSV, fetch from Binance, or generate a synthetic null."""
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

BINANCE = "https://api.binance.com/api/v3/klines"


def load_csv(path):
    """Read OHLCV CSV. Needs a date/timestamp column and a 'close' column."""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    date_col = next((c for c in ("date", "timestamp", "time", "open_time") if c in df.columns), None)
    if date_col is None:
        raise ValueError(f"{path}: no date/timestamp column found in {list(df.columns)}")
    if "close" not in df.columns:
        raise ValueError(f"{path}: no 'close' column found in {list(df.columns)}")
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
    df = df.dropna(subset=[date_col]).set_index(date_col).sort_index()
    return df[~df.index.duplicated(keep="first")]


def fetch_binance(symbol="BTCUSDT", interval="1d", start="2019-01-01", cache_dir="data"):
    """Download OHLCV from Binance's public API. No API key needed.

    Won't run inside the Claude Code web sandbox (network policy blocks the host).
    Run it locally, then feed the CSV to the backtester.
    """
    cache = Path(cache_dir) / f"{symbol}_{interval}_{start}.csv"
    if cache.exists():
        return load_csv(cache)

    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    rows = []
    while True:
        r = requests.get(
            BINANCE,
            params={"symbol": symbol, "interval": interval, "startTime": start_ms, "limit": 1000},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < 1000:
            break
        start_ms = batch[-1][0] + 1
        time.sleep(0.25)  # ponytail: fixed sleep, not a rate limiter. Binance allows far more.

    if not rows:
        raise RuntimeError(f"Binance returned no data for {symbol} {interval} from {start}")

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "taker_base", "taker_quote", "ignore",
    ])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df[["date", "open", "high", "low", "close", "volume"]].astype(
        {c: float for c in ("open", "high", "low", "close", "volume")}
    )
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False)
    return df.set_index("date").sort_index()


def synthetic(n=2000, annual_drift=0.0, annual_vol=0.6, periods_per_year=365, seed=0, start_price=100.0):
    """Geometric Brownian motion — a market with no exploitable structure.

    This is the null hypothesis. Any strategy that shows a real edge here is
    reporting a bug (lookahead, survivorship, cost model) and not a signal.
    """
    rng = np.random.default_rng(seed)
    dt = 1.0 / periods_per_year
    shocks = rng.normal(
        (annual_drift - 0.5 * annual_vol**2) * dt,
        annual_vol * np.sqrt(dt),
        n,
    )
    close = start_price * np.exp(np.cumsum(shocks))
    idx = pd.date_range("2015-01-01", periods=n, freq="D")
    return pd.DataFrame({"close": close}, index=idx)
