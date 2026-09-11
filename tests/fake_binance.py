"""A stand-in Binance spot API, enough to exercise the live broker.

It is NOT the real exchange and proves nothing about the real one's current
behaviour. What it does prove is that our request signing, symbol handling, lot
rounding and response parsing are self-consistent — bugs that would otherwise
only surface with real money on the line.
"""
import hashlib
import hmac
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

SYMBOLS = {
    "BTCUSDT": {"base": "BTC", "quote": "USDT", "step": "0.00001", "minQty": "0.00001", "minNotional": "5.0"},
    "ETHBTC":  {"base": "ETH", "quote": "BTC",  "step": "0.0001",  "minQty": "0.0001",  "minNotional": "0.0001"},
}
PRICES = {"BTCUSDT": 60000.0, "ETHBTC": 0.05}


class FakeBinance:
    def __init__(self, secret=b"secret", balances=None):
        self.secret = secret
        self.balances = balances or {"USDT": 1000.0, "BTC": 0.0, "ETH": 2.0}
        self.orders = []
        self.bad_signatures = 0
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body):
                payload = json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def _check_signature(self, query):
                """Reject anything not signed exactly as Binance requires."""
                params = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
                given = params.pop("signature", None)
                if given is None:
                    return False
                unsigned = query.rsplit("&signature=", 1)[0]
                expected = hmac.new(outer.secret, unsigned.encode(), hashlib.sha256).hexdigest()
                if not hmac.compare_digest(given, expected):
                    outer.bad_signatures += 1
                    return False
                return True

            def do_GET(self):
                path, _, query = self.path.partition("?")
                params = dict(urllib.parse.parse_qsl(query))

                if path == "/api/v3/exchangeInfo":
                    spec = SYMBOLS.get(params.get("symbol"))
                    if not spec:
                        return self._send(200, {"symbols": []})
                    return self._send(200, {"symbols": [{
                        "symbol": params["symbol"],
                        "baseAsset": spec["base"], "quoteAsset": spec["quote"],
                        "filters": [
                            {"filterType": "LOT_SIZE", "stepSize": spec["step"], "minQty": spec["minQty"]},
                            {"filterType": "NOTIONAL", "minNotional": spec["minNotional"]},
                        ],
                    }]})

                if path == "/api/v3/ticker/price":
                    return self._send(200, {"symbol": params["symbol"],
                                            "price": str(PRICES[params["symbol"]])})

                if path == "/api/v3/account":
                    if not self._check_signature(query):
                        return self._send(401, {"code": -1022, "msg": "Signature for this request is not valid."})
                    return self._send(200, {"balances": [
                        {"asset": a, "free": str(v), "locked": "0"} for a, v in outer.balances.items()]})

                return self._send(404, {"code": -1121, "msg": "Invalid path"})

            def do_POST(self):
                path, _, query = self.path.partition("?")
                if path != "/api/v3/order":
                    return self._send(404, {"code": -1121, "msg": "Invalid path"})
                if not self._check_signature(query):
                    return self._send(401, {"code": -1022, "msg": "Signature for this request is not valid."})

                params = dict(urllib.parse.parse_qsl(query))
                symbol, side = params["symbol"], params["side"]
                spec = SYMBOLS[symbol]
                qty = float(params["quantity"])
                step = float(spec["step"])

                # Binance rejects quantities off the lot step — so does this.
                if abs(round(qty / step) - qty / step) > 1e-9:
                    return self._send(400, {"code": -1013, "msg": "LOT_SIZE filter failure"})
                if qty < float(spec["minQty"]):
                    return self._send(400, {"code": -1013, "msg": "Quantity less than minQty"})

                price = PRICES[symbol]
                cost = qty * price
                base, quote = spec["base"], spec["quote"]
                if side == "BUY":
                    if cost > outer.balances.get(quote, 0) + 1e-9:
                        return self._send(400, {"code": -2010, "msg": "Account has insufficient balance"})
                    outer.balances[quote] = outer.balances.get(quote, 0) - cost
                    outer.balances[base] = outer.balances.get(base, 0) + qty
                else:
                    if qty > outer.balances.get(base, 0) + 1e-9:
                        return self._send(400, {"code": -2010, "msg": "Account has insufficient balance"})
                    outer.balances[base] = outer.balances.get(base, 0) - qty
                    outer.balances[quote] = outer.balances.get(quote, 0) + cost

                outer.orders.append({"symbol": symbol, "side": side, "qty": qty})
                return self._send(200, {
                    "orderId": 1000 + len(outer.orders), "symbol": symbol, "side": side,
                    "status": "FILLED", "executedQty": f"{qty:.8f}",
                    "cummulativeQuoteQty": f"{cost:.8f}",
                })

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *a):
        self.server.shutdown()
