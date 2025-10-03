import os
import sys
import json
import asyncio

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import core.server as srv  # noqa: E402


class DummyResp:
    def json(self):
        return {"status": "stubbed"}


class DummyClient:
    async def signed_request(self, method: str, endpoint: str, body: dict):
        self.method = method
        self.endpoint = endpoint
        self.body = body
        return DummyResp()


async def run() -> int:
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]

    payload = {"symbol": "tTESTETH:TESTUSD", "side": "LONG", "size": 0.003, "type": "MARKET"}
    out = await srv.paper_submit(payload)

    symbol = out.get("request", {}).get("symbol")
    ok = bool(out.get("ok"))
    print(json.dumps({"ok": ok, "symbol": symbol}, ensure_ascii=False))

    return 0 if symbol == "tTESTETH:TESTUSD" and ok else 1


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
