"""Checks on unattended alerting. An agent nobody watches must be able to shout."""
import importlib
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class _Hook:
    """A throwaway webhook server that records what it was sent."""

    def __init__(self):
        self.received = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                outer.received.append(json.loads(body))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}/hook"

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        os.environ["NOTIFY_WEBHOOK"] = self.url
        import quant.notify
        importlib.reload(quant.notify)
        return self

    def __exit__(self, *a):
        self.server.shutdown()
        os.environ.pop("NOTIFY_WEBHOOK", None)
        import quant.notify
        importlib.reload(quant.notify)


def test_silent_when_unconfigured():
    """No webhook set must be a no-op, never an error."""
    os.environ.pop("NOTIFY_WEBHOOK", None)
    import quant.notify
    importlib.reload(quant.notify)
    n = quant.notify.Notifier()
    assert not n.enabled
    assert n.halted("X", "reason", 100.0) is False
    assert n.summary({"symbol": "X"}) is False


def test_halt_alert_is_never_throttled():
    """Everything else can wait. A halt cannot."""
    with _Hook() as hook:
        import quant.notify
        n = quant.notify.Notifier()
        assert n.halted("BTCUSDT", "drawdown breached", 812.44)
        assert n.halted("BTCUSDT", "again", 800.0), "a second halt must still send"
        assert len(hook.received) == 2
        assert "HALTED" in hook.received[0]["text"]
        assert "--reset" in hook.received[0]["text"], "must say how to resume"


def test_error_alert_waits_for_a_streak_then_throttles():
    """One failed tick is noise; three in a row means it is not working."""
    with _Hook() as hook:
        import quant.notify
        n = quant.notify.Notifier()
        assert n.errors("X", 1, "boom") is False
        assert n.errors("X", 2, "boom") is False
        assert n.errors("X", 3, "boom") is True
        assert n.errors("X", 4, "boom") is False, "must throttle after the first"
        assert len(hook.received) == 1


def test_summary_is_daily():
    with _Hook() as hook:
        import quant.notify
        n = quant.notify.Notifier()
        state = {"symbol": "X", "mode": "paper", "equity": 1000.0,
                 "position_fraction": 0.5, "drawdown_pct": -3.2, "n_trades": 4}
        assert n.summary(state) is True
        assert n.summary(state) is False, "a second summary the same day must be suppressed"
        assert len(hook.received) == 1


def test_payload_suits_slack_and_discord():
    with _Hook() as hook:
        import quant.notify
        quant.notify.Notifier().halted("X", "r", 1.0)
        sent = hook.received[0]
        assert "text" in sent and "content" in sent, "needs both keys to suit either service"


def test_unreachable_webhook_does_not_raise():
    """Alerting is best-effort; it must never take the trader down."""
    os.environ["NOTIFY_WEBHOOK"] = "http://127.0.0.1:9/dead"
    import quant.notify
    importlib.reload(quant.notify)
    try:
        assert quant.notify.Notifier().halted("X", "r", 1.0) is False
    finally:
        os.environ.pop("NOTIFY_WEBHOOK", None)
        importlib.reload(quant.notify)


def test_trader_still_halts_when_alerting_is_down():
    """The safety stop must not depend on the notifier working."""
    import tempfile
    from unittest.mock import patch

    os.environ["NOTIFY_WEBHOOK"] = "http://127.0.0.1:9/dead"
    import quant.live
    import quant.notify
    importlib.reload(quant.notify)
    importlib.reload(quant.live)
    try:
        from quant import data
        from quant.broker import PaperBroker

        bars = data.synthetic(n=400, annual_drift=-0.9, seed=3)["close"]
        with tempfile.TemporaryDirectory() as tmp:
            trader = quant.live.Trader(
                "sma_cross", {"fast": 5, "slow": 20},
                PaperBroker(starting_cash=1000.0, state_path=Path(tmp) / "b.json"),
                "BTCUSDT", max_drawdown_pct=15.0, state_file=Path(tmp) / "s.json")
            last = None
            for i in range(60, 220, 5):
                with patch("quant.live.recent_bars", return_value=bars.iloc[:i]):
                    last = trader.tick()
            assert last["halted"], "halt must fire even when the webhook is dead"
    finally:
        os.environ.pop("NOTIFY_WEBHOOK", None)
        importlib.reload(quant.notify)
        importlib.reload(quant.live)


def test_systemd_unit_does_not_restart_a_halt():
    """Restart=on-failure plus exit 0 on halt: a stopped strategy stays stopped."""
    unit = (Path(__file__).resolve().parent.parent / "deploy" / "trading-agent.service").read_text()
    assert "Restart=on-failure" in unit, "must not be Restart=always — that resumes a halted strategy"
    assert "EnvironmentFile=" in unit, "secrets belong in an env file, not the unit"
    assert "ReadWritePaths=" in unit and "ProtectSystem=strict" in unit


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  pass  {t.__name__}")
    print(f"\n{len(tests)} checks passed")
