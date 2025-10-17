import asyncio
import json
import os
import sys

from starlette.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import core.server as srv  # noqa: E402
from core.server import app  # noqa: E402

client = TestClient(app)


class DummyResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        return {"status": "stubbed", "echo": self._payload}


class DummyClient:
    async def signed_request(self, method: str, endpoint: str, body: dict):
        return DummyResp(body)


async def run() -> int:
    # Monkeypatch exchange client to avoid network
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]

    # 1) Hämta UI
    r = client.get("/ui")
    if r.status_code != 200:
        print(json.dumps({"ui": False}))
        return 1

    # 2) Kör evaluate med default policy/configs/candles
    payload = {
        "policy": {"symbol": "tETHUSD", "timeframe": "1m"},
        "configs": {
            "thresholds": {"entry_conf_overall": 0.5, "regime_proba": {"balanced": 0.5}},
            "risk": {"risk_map": [[0.5, 0.0011]]},
        },
        "candles": {
            "open": [1, 2, 3, 4],
            "high": [2, 3, 4, 5],
            "low": [0.5, 1.5, 2.5, 3.5],
            "close": [1.5, 2.5, 3.5, 4.5],
            "volume": [10, 11, 12, 13],
        },
        "state": {},
    }
    r2 = client.post("/strategy/evaluate", json=payload)
    d2 = r2.json()
    action = (d2.get("result") or {}).get("action")
    size = float((d2.get("meta") or {}).get("decision", {}).get("size", 0.0))

    # 3) Submit (auto-clamp i backend ska hantera size om <= 0)
    submit_payload = {
        "symbol": "tTESTETH:TESTUSD",
        "side": action or "LONG",
        "size": size or 0.0005,
        "type": "MARKET",
    }
    r3 = await asyncio.get_event_loop().run_in_executor(
        None, lambda: client.post("/paper/submit", json=submit_payload)
    )
    d3 = r3.json()
    ok = bool(d3.get("ok"))
    meta = d3.get("meta") or {}

    print(
        json.dumps(
            {"action": action, "size": size, "submit_ok": ok, "meta": meta}, ensure_ascii=False
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
