import os
import sys
import json
import re
import asyncio
from typing import Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from core.config.settings import get_settings  # noqa: E402
from core.io.bitfinex.exchange_client import ExchangeClient  # noqa: E402
from core.server import TEST_SPOT_WHITELIST  # noqa: E402

CANDIDATES = [0.001, 0.002, 0.003, 0.005, 0.01, 0.02, 0.03]


async def try_submit(ec: ExchangeClient, symbol: str, size: float) -> tuple[bool, Any, str | None]:
    body = {"type": "EXCHANGE MARKET", "symbol": symbol, "amount": str(size)}
    try:
        resp = await ec.signed_request(method="POST", endpoint="auth/w/order/submit", body=body)
        try:
            data = resp.json()
        except Exception:
            data = {"text": resp.text}
        return True, data, None
    except Exception as e:  # httpx.HTTPStatusError eller annat
        text = getattr(getattr(e, "response", None), "text", "") or str(e)
        return False, None, text


def parse_min_from_error(text: str) -> float | None:
    # Grov regex för att hitta något som ser ut som en decimal i feltexten
    # Exempel: "minimum order size is 0.02" -> 0.02
    m = re.search(r"(minimum[^0-9]*)(\d+\.\d+|\d+)", text, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(2))
        except Exception:
            return None
    return None


async def probe_symbol(ec: ExchangeClient, symbol: str) -> float:
    for sz in CANDIDATES:
        ok, data, err = await try_submit(ec, symbol, sz)
        if ok:
            return float(sz)
        if err:
            guess = parse_min_from_error(err)
            if guess is not None:
                return float(guess)
    return float(CANDIDATES[-1])


async def run() -> int:
    s = get_settings()
    if not (s.BITFINEX_API_KEY and s.BITFINEX_API_SECRET):
        print(json.dumps({"error": "missing_api_keys"}))
        return 1

    ec = ExchangeClient()
    results: dict[str, float] = {}
    for sym in sorted(TEST_SPOT_WHITELIST):
        ms = await probe_symbol(ec, sym)
        results[sym] = ms
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
