import os
import sys
import json
import asyncio

# Ensure we can import from src/
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
        # Simulerad klient: returnerar stubbsvar och låter oss se body
        self.method = method
        self.endpoint = endpoint
        self.body = body
        return DummyResp()


async def run() -> int:
    # Monkeypatch klienten så att inga riktiga nätverksanrop görs
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]

    # Försök lägga order med tBTCUSD – ska mappas till tTESTBTC:TESTUSD
    payload = {"symbol": "tBTCUSD", "side": "LONG", "size": 0.003, "type": "MARKET"}
    out = await srv.paper_submit(payload)

    symbol = out.get("request", {}).get("symbol")
    ok = bool(out.get("ok"))
    result = {"ok": ok, "mapped_symbol": symbol}
    print(json.dumps(result, ensure_ascii=False))

    # Exit code 0 om symbolen mappats korrekt
    return 0 if symbol == "tTESTBTC:TESTUSD" and ok else 1


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
