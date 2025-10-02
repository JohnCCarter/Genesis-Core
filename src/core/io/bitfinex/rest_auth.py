from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import httpx

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce, bump_nonce

BASE = "https://api.bitfinex.com"


def _sign_v2(endpoint: str, body: dict[str, Any] | None) -> dict[str, str]:
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_API_SECRET or "").strip()
    nonce = get_nonce(api_key)
    payload_str = json.dumps(body or {}, separators=(",", ":"))
    message = f"/api/v2/{endpoint}{nonce}{payload_str}"
    sig = hmac.new(api_secret.encode(), message.encode(), hashlib.sha384).hexdigest()
    return {
        "bfx-apikey": api_key,
        "bfx-nonce": nonce,
        "bfx-signature": sig,
        "Content-Type": "application/json",
    }


async def post_auth(
    endpoint: str, body: dict[str, Any] | None = None
) -> httpx.Response:
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    headers = _sign_v2(endpoint, body)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(
                f"{BASE}/v2/{endpoint}", headers=headers, content=json.dumps(body or {})
            )
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            # Engångs‑retry vid misstänkt nonce‑fel
            text = e.response.text if e.response is not None else ""
            if "nonce" in text.lower():
                bump_nonce(api_key)
                headers = _sign_v2(endpoint, body)
                r2 = await client.post(
                    f"{BASE}/v2/{endpoint}",
                    headers=headers,
                    content=json.dumps(body or {}),
                )
                r2.raise_for_status()
                return r2
            raise
