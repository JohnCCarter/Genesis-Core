from __future__ import annotations

import asyncio
import time
import uuid

from fastapi import APIRouter

from core.io.bitfinex import read_helpers as bfx_read
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger("core.server")

_ACCOUNT_CACHE = {
    "wallets": {"ts": 0.0, "data": {"items": []}},
    "positions": {"ts": 0.0, "data": {"items": []}},
    "orders": {"ts": 0.0, "data": {"items": []}},
}
_ACCOUNT_TTL = 5.0

router = APIRouter()


@router.get("/auth/check")
async def auth_check() -> dict:
    """Read-only smoke: wallets + positions (paper). Return only ok and item counts."""
    w, p = await asyncio.gather(bfx_read.get_wallets(), bfx_read.get_positions())
    w_count = len(w) if isinstance(w, list) else 0
    p_count = len(p) if isinstance(p, list) else 0
    return {"ok": True, "wallets": w_count, "positions": p_count}


@router.get("/account/wallets")
async def account_wallets() -> dict:
    now = time.time()
    if now - _ACCOUNT_CACHE["wallets"]["ts"] < _ACCOUNT_TTL:
        return _ACCOUNT_CACHE["wallets"]["data"]
    try:
        data = await bfx_read.get_wallets()
        items = []
        if isinstance(data, list):
            for w in data:
                if isinstance(w, list) and len(w) >= 5 and str(w[0]).lower() == "exchange":
                    items.append(
                        {
                            "type": w[0],
                            "currency": str(w[1]).upper(),
                            "balance": float(w[2]),
                            "available": float(w[4]) if w[4] is not None else None,
                        }
                    )
        out = {"items": items}
        _ACCOUNT_CACHE["wallets"] = {"ts": now, "data": out}
        return out
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/account/wallets failed (error_id=%s)", error_id)
        return {"items": [], "error": "internal_error", "error_id": error_id}


@router.get("/account/positions")
async def account_positions() -> dict:
    now = time.time()
    if now - _ACCOUNT_CACHE["positions"]["ts"] < _ACCOUNT_TTL:
        return _ACCOUNT_CACHE["positions"]["data"]
    try:
        data = await bfx_read.get_positions()
        items = []
        if isinstance(data, list):
            for p in data:
                if isinstance(p, list) and len(p) >= 4:
                    sym = str(p[0])
                    if not (sym.startswith("tTEST") or ":TEST" in sym):
                        continue
                    items.append(
                        {
                            "symbol": sym,
                            "status": p[1],
                            "amount": float(p[2]),
                            "base_price": float(p[3]) if p[3] is not None else None,
                        }
                    )
        out = {"items": items}
        _ACCOUNT_CACHE["positions"] = {"ts": now, "data": out}
        return out
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/account/positions failed (error_id=%s)", error_id)
        return {"items": [], "error": "internal_error", "error_id": error_id}


@router.get("/account/orders")
async def account_orders() -> dict:
    now = time.time()
    if now - _ACCOUNT_CACHE["orders"]["ts"] < _ACCOUNT_TTL:
        return _ACCOUNT_CACHE["orders"]["data"]
    try:
        data = await bfx_read.get_orders()
        items = []
        if isinstance(data, list):
            for o in data:
                if isinstance(o, list) and len(o) >= 8:
                    sym = str(o[3])
                    if not (sym.startswith("tTEST") or ":TEST" in sym):
                        continue
                    items.append(
                        {
                            "symbol": sym,
                            "amount": float(o[6]) if o[6] is not None else None,
                            "type": o[8] if len(o) > 8 else None,
                            "status": o[13] if len(o) > 13 else None,
                        }
                    )
        out = {"items": items}
        _ACCOUNT_CACHE["orders"] = {"ts": now, "data": out}
        return out
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/account/orders failed (error_id=%s)", error_id)
        return {"items": [], "error": "internal_error", "error_id": error_id}
