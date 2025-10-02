from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from typing import Any

import websockets

from core.config.settings import get_settings
from core.utils.logging_redaction import get_logger
from core.utils.backoff import exponential_backoff_delay


WS_URL = "wss://api.bitfinex.com/ws/2"
logger = get_logger(__name__)


def _build_ws_auth_message() -> dict[str, Any]:
    s = get_settings()
    api_key = (s.BITFINEX_WS_API_KEY or s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_WS_API_SECRET or s.BITFINEX_API_SECRET or "").strip()
    # Nonce i ms; återanvänd µs‑tanke men här räcker ms
    nonce_ms = str(int(asyncio.get_running_loop().time() * 1000))
    payload = f"AUTH{nonce_ms}"
    sig = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha384).hexdigest()
    return {
        "event": "auth",
        "apiKey": api_key,
        "authSig": sig,
        "authPayload": payload,
        "authNonce": nonce_ms,
    }


class WSReconnectClient:
    """Minimal WS reconnect‑skelett med ping/pong och åter‑auth.

    Håller sig enkel: ingen topic‑hantering, endast anslutning, auth och watchdog.
    """

    def __init__(
        self,
        *,
        url: str = WS_URL,
        enable_auth: bool = True,
        ping_interval: float = 20.0,
        ping_timeout: float = 10.0,
        max_backoff: float = 10.0,
    ) -> None:
        self.url = url
        self.enable_auth = enable_auth
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.max_backoff = max_backoff

    async def _backoff_delay(self, attempt: int) -> float:
        # Använd util för konsekvent backoff/jitter-policy
        return exponential_backoff_delay(
            attempt,
            base_delay=0.5,
            max_backoff=self.max_backoff,
            jitter_min_ms=100,
            jitter_max_ms=400,
        )

    async def _ping_watchdog(self, ws: websockets.WebSocketClientProtocol) -> None:
        while True:
            try:
                waiter = ws.ping()
                await asyncio.wait_for(waiter, timeout=self.ping_timeout)
                await asyncio.sleep(self.ping_interval)
            except Exception as watchdog_err:
                # Låt ytterloopen reconnecta
                try:
                    await ws.close()
                except (OSError, RuntimeError, websockets.exceptions.WebSocketException) as close_err:  # type: ignore[attr-defined]
                    logger.debug("ws_close_error: %s", close_err)
                logger.debug("ws_watchdog_break: %s", watchdog_err)
                break

    async def run(self) -> None:
        attempt = 0
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=None) as ws:
                    attempt = 0  # reset backoff
                    if self.enable_auth:
                        await ws.send(json.dumps(_build_ws_auth_message()))
                    # Starta ping‑watchdog; blocka tills den bryts
                    await self._ping_watchdog(ws)
            except Exception:
                attempt += 1
                await asyncio.sleep(await self._backoff_delay(attempt))


_WS_CLIENT: WSReconnectClient | None = None


def get_ws_reconnect_client() -> WSReconnectClient:
    global _WS_CLIENT
    if _WS_CLIENT is None:
        _WS_CLIENT = WSReconnectClient()
    return _WS_CLIENT
