"""Outbound alerts, so an unattended agent can reach you.

Set NOTIFY_WEBHOOK to a Slack or Discord incoming-webhook URL. Unset, every
call here is a silent no-op — the trader never fails because alerting is down.
"""
import json
import os
import time
import urllib.error
import urllib.request

WEBHOOK_ENV = "NOTIFY_WEBHOOK"
TIMEOUT = 10


def _post(message):
    """Send one message. Returns True on success, False on any failure."""
    url = os.environ.get(WEBHOOK_ENV, "").strip()
    if not url:
        return False

    # Slack reads "text", Discord reads "content". Sending both satisfies either
    # without asking which service this URL belongs to.
    payload = json.dumps({"text": message, "content": message}).encode()
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, OSError, ValueError):
        # Alerting must never take the trader down with it.
        return False


class Notifier:
    """Rate-limited alerts. Silent when NOTIFY_WEBHOOK is unset.

    An unattended trader runs for weeks, so the job here is to stay quiet and
    then be unmissable. Only three things send: a halt, a run of consecutive
    failed ticks, and one summary a day. Per-trade alerts are deliberately
    absent — an alert you learn to ignore is worse than no alert.
    """

    def __init__(self, min_gap_seconds=3600, summary_every_hours=24):
        self.enabled = bool(os.environ.get(WEBHOOK_ENV, "").strip())
        self.min_gap = min_gap_seconds
        self.summary_every = summary_every_hours * 3600
        self._last = {}
        self._last_summary = 0.0

    def _throttled(self, key, gap=None):
        now = time.time()
        if now - self._last.get(key, 0) < (self.min_gap if gap is None else gap):
            return True
        self._last[key] = now
        return False

    def halted(self, symbol, reason, equity):
        """Fires once per halt. This is the one that must always get through."""
        if self._throttled(f"halt:{symbol}", gap=0):   # never suppress a halt
            return False
        return _post(
            f"[HALTED] {symbol}\n{reason}\n"
            f"Equity {equity:,.2f}. Position flattened; the trader has stopped.\n"
            f"It will stay halted across restarts until you run trade.py --reset."
        )

    def errors(self, symbol, streak, last_error):
        """Fires when ticks keep failing — the agent is up but not working."""
        if streak < 3 or self._throttled(f"err:{symbol}"):
            return False
        return _post(
            f"[DEGRADED] {symbol}: {streak} consecutive failed ticks.\n"
            f"Last error: {last_error}\n"
            f"The trader is running but not trading. Check network or API limits."
        )

    def summary(self, state):
        """One line a day: still alive, this is the position, this is the cost."""
        now = time.time()
        if now - self._last_summary < self.summary_every:
            return False
        self._last_summary = now
        return _post(
            f"[DAILY] {state.get('symbol')} {state.get('mode')} · "
            f"equity {state.get('equity', 0):,.2f} · "
            f"position {float(state.get('position_fraction') or 0):.0%} · "
            f"drawdown {state.get('drawdown_pct', 0):.1f}% · "
            f"{state.get('n_trades', 0)} trades"
        )

    def started(self, symbol, mode, strategy):
        return _post(f"[START] {strategy} on {symbol} in {mode} mode.")
