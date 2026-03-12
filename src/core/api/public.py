from __future__ import annotations

import time

from fastapi import APIRouter

router = APIRouter()

_CANDLES_CACHE = {}  # key -> {ts: float, data: dict}
_CANDLES_TTL = 10.0  # 10s cache for candles


def _resolve_get_exchange_client():
    try:
        import core.server as server_mod

        return server_mod.get_exchange_client
    except Exception:
        from core.io.bitfinex.exchange_client import get_exchange_client

        return get_exchange_client


@router.get("/public/candles")
async def public_candles(symbol: str = "tBTCUSD", timeframe: str = "1m", limit: int = 120) -> dict:
    """Proxy till Bitfinex public candles och normaliserar till {open,high,low,close,volume}."""
    cache_key = f"{symbol}:{timeframe}:{limit}"
    now = time.time()
    if cache_key in _CANDLES_CACHE:
        entry = _CANDLES_CACHE[cache_key]
        if now - entry["ts"] < _CANDLES_TTL:
            return entry["data"]

    safe_limit = max(1, min(int(limit), 1000))
    endpoint = f"candles/trade:{timeframe}:{symbol}/hist"
    params = {"limit": safe_limit, "sort": 1}

    ec = _resolve_get_exchange_client()()
    response = await ec.public_request(method="GET", endpoint=endpoint, params=params, timeout=10)
    data = response.json()

    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    volumes: list[float] = []

    if isinstance(data, list):
        for row in data:
            if isinstance(row, list) and len(row) >= 6:
                opens.append(float(row[1]))
                closes.append(float(row[2]))
                highs.append(float(row[3]))
                lows.append(float(row[4]))
                volumes.append(float(row[5]))

    result = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }

    _CANDLES_CACHE[cache_key] = {"ts": now, "data": result}
    return result
