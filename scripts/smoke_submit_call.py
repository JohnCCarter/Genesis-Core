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
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        return {"status": "stubbed", "echo": self._payload}


class DummyClient:
    async def signed_request(self, method: str, endpoint: str, body: dict):
        return DummyResp(body)


async def run() -> int:
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]
    out = await srv.paper_submit({"symbol": "tTESTETH:TESTUSD", "side": "LONG", "size": 0.0005, "type": "MARKET"})
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
