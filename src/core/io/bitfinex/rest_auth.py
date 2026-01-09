from __future__ import annotations

import json
from typing import Any

import httpx

from core.config.settings import get_settings
from core.symbols.symbols import SymbolMapper, SymbolMode
from core.utils.crypto import build_hmac_signature
from core.utils.nonce_manager import bump_nonce, get_nonce

BASE = "https://api.bitfinex.com"


def _sign_v2(endpoint: str, body: dict[str, Any] | None) -> dict[str, str]:
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_API_SECRET or "").strip()
    nonce = get_nonce(api_key)
    payload_str = json.dumps(body or {}, separators=(",", ":"))
    message = f"/api/v2/{endpoint}{nonce}{payload_str}"
    sig = build_hmac_signature(api_secret, message)
    return {
        "bfx-apikey": api_key,
        "bfx-nonce": nonce,
        "bfx-signature": sig,
        "Content-Type": "application/json",
    }


async def post_auth(endpoint: str, body: dict[str, Any] | None = None) -> httpx.Response:
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    mapper = SymbolMapper(
        SymbolMode.REALISTIC
        if str(s.SYMBOL_MODE).lower() not in ("synthetic", "realistic")
        else SymbolMode(str(s.SYMBOL_MODE).lower())
    )
    b = dict(body or {})
    sym = b.get("symbol")
    if isinstance(sym, str):
        su = sym.upper()
        if su.startswith("TTEST") or ":TEST" in su:
            b["symbol"] = mapper.force(sym)
        else:
            b["symbol"] = mapper.resolve(sym)
    headers = _sign_v2(endpoint, b)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            # Använd samma kompakta JSON‑sträng för content som vid signeringen
            body_str = json.dumps(b or {}, separators=(",", ":"))
            r = await client.post(f"{BASE}/v2/{endpoint}", headers=headers, content=body_str)
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            # Engångs‑retry vid misstänkt nonce‑fel
            text = e.response.text if e.response is not None else ""
            if "nonce" in text.lower():
                bump_nonce(api_key)
                headers = _sign_v2(endpoint, b)
                body_str = json.dumps(b or {}, separators=(",", ":"))
                r2 = await client.post(
                    f"{BASE}/v2/{endpoint}",
                    headers=headers,
                    content=body_str,
                )
                r2.raise_for_status()
                return r2
            raise
