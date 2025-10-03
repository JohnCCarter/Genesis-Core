from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time

import websockets

from core.config.settings import get_settings
from core.observability.metrics import metrics
from core.utils.nonce_manager import get_nonce

WS_URL = "wss://api.bitfinex.com/ws/2"


async def auth_ping(timeout: float = 5.0) -> dict:
    s = get_settings()
    api_key = (s.BITFINEX_WS_API_KEY or s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_WS_API_SECRET or s.BITFINEX_API_SECRET or "").strip()
    # Återanvänd NonceManager (µs) och konvertera till ms för WS
    ws_key = api_key
    try:
        nonce_us = int(get_nonce(ws_key))
        nonce_ms = str(int(nonce_us / 1000))
    except Exception:
        nonce_ms = str(int(time.time() * 1000))
    payload = f"AUTH{nonce_ms}"
    sig = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha384).hexdigest()

    metrics.inc("ws_auth_request")
    async with websockets.connect(WS_URL, ping_interval=None) as ws:
        await ws.send(
            json.dumps(
                {
                    "event": "auth",
                    "apiKey": api_key,
                    "authSig": sig,
                    "authPayload": payload,
                    "authNonce": nonce_ms,
                }
            )
        )
        # read auth reply
        try:
            for _ in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                try:
                    data = json.loads(msg)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(data, dict):
                    ev = data.get("event")
                    if ev == "auth" and data.get("status") == "OK":
                        metrics.inc("ws_auth_success")
                        return {"ok": True}
                    if ev == "error":
                        metrics.inc("ws_auth_error")
                        metrics.event(
                            "ws_auth_error",
                            {"msg": data.get("msg"), "code": data.get("code")},
                        )
                        return {"ok": False, "error": data.get("msg") or str(data)}
                    if ev == "info" and data.get("code") in (20051, 20060):
                        metrics.inc("ws_auth_maintenance")
                        metrics.event(
                            "ws_auth_maintenance",
                            {"code": data.get("code")},
                        )
                        return {
                            "ok": False,
                            "maintenance": True,
                            "code": data.get("code"),
                        }
            metrics.inc("ws_auth_timeout")
            return {"ok": False, "error": "timeout"}
        except TimeoutError:
            metrics.inc("ws_auth_timeout")
            return {"ok": False, "error": "timeout"}
