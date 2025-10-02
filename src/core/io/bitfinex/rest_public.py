from __future__ import annotations

import httpx

BASE_PUB = "https://api-pub.bitfinex.com/v2"


async def get_platform_status() -> int:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE_PUB}/platform/status")
        r.raise_for_status()
        data = r.json()
        return int(data[0]) if isinstance(data, list) else 0
