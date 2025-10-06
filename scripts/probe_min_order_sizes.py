import asyncio
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import core.server as srv  # noqa: E402

# Tickers att prova (kan utökas)
TICKERS = [
    "tTESTBTC:TESTUSD",
    "tTESTBTC:TESTUSDT",
    "tTESTETH:TESTUSD",
]


class DummyResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        # simulera OK-respons från exchange
        return {"status": "stubbed", "echo": self._payload}


class DummyClient:
    async def signed_request(self, method: str, endpoint: str, body: dict):
        return DummyResp(body)


async def try_submit(symbol: str, size: float) -> dict:
    # Här använder vi riktiga serverns paper_submit (kan kopplas om till live-klient vid behov)
    # Om du vill prova live, kommentera bort raden som monkeypatchar get_exchange_client
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]
    out = await srv.paper_submit({"symbol": symbol, "side": "LONG", "size": size, "type": "MARKET"})
    return out


async def probe_symbol(symbol: str) -> float:
    # Prova en uppsättning storlekar geometriskt
    candidates = [0.001, 0.002, 0.003, 0.005, 0.01, 0.02, 0.03]
    for sz in candidates:
        out = await try_submit(symbol, sz)
        if out.get("ok") is True:
            return float(sz)
        if out.get("error") == "min_size_required":
            # Vi kan läsa required_min direkt
            return float(out.get("required_min") or sz)
    # fallback
    return float(candidates[-1])


async def run() -> int:
    result = {}
    for sym in TICKERS:
        min_sz = await probe_symbol(sym)
        result[sym] = min_sz
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
