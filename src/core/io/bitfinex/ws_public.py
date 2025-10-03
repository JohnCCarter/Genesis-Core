from __future__ import annotations

import asyncio
import json

import websockets

from core.observability.metrics import metrics
from core.utils.logging_redaction import get_logger

WS_PUB = "wss://api-pub.bitfinex.com/ws/2"
_LOGGER = get_logger(__name__)


async def one_message_ticker(symbol: str = "tBTCUSD", timeout: float = 5.0) -> dict:
    """Prenumerera på ticker och vänta på ACK eller fel (minimalt)."""
    metrics.inc("ws_public_request")
    async with websockets.connect(WS_PUB, ping_interval=None) as ws:
        try:
            _LOGGER.info("WS pub subscribe ticker %s", symbol)
        except Exception as log_err:
            _LOGGER.debug("log_error: %s", log_err)
        await ws.send(json.dumps({"event": "subscribe", "channel": "ticker", "symbol": symbol}))
        try:
            for _ in range(10):
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                try:
                    data = json.loads(msg)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(data, dict):
                    ev = data.get("event")
                    if ev == "subscribed" and data.get("channel") == "ticker":
                        metrics.inc("ws_public_success")
                        return {"ok": True, "chanId": data.get("chanId")}
                    if ev == "error":
                        metrics.inc("ws_public_error")
                        return {"ok": False, "error": data.get("msg") or str(data)}
                    if ev == "info" and data.get("code") in (20051, 20060):
                        metrics.inc("ws_public_maintenance")
                        return {
                            "ok": False,
                            "maintenance": True,
                            "code": data.get("code"),
                        }
            metrics.inc("ws_public_timeout")
            return {"ok": False, "error": "timeout"}
        except TimeoutError:
            metrics.inc("ws_public_timeout")
            return {"ok": False, "error": "timeout"}


async def one_message_candles(
    symbol: str = "tBTCUSD", timeframe: str = "1m", timeout: float = 5.0
) -> dict:
    """Prenumerera på candles och vänta på ACK eller fel (minimalt)."""
    metrics.inc("ws_public_request")
    async with websockets.connect(WS_PUB, ping_interval=None) as ws:
        key = f"trade:{timeframe}:{symbol}"
        try:
            _LOGGER.info("WS pub subscribe candles %s", key)
        except Exception as log_err:
            _LOGGER.debug("log_error: %s", log_err)
        await ws.send(json.dumps({"event": "subscribe", "channel": "candles", "key": key}))
        try:
            for _ in range(10):
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                try:
                    data = json.loads(msg)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(data, dict):
                    ev = data.get("event")
                    if ev == "subscribed" and data.get("channel") == "candles":
                        metrics.inc("ws_public_success")
                        return {
                            "ok": True,
                            "chanId": data.get("chanId"),
                            "key": data.get("key"),
                        }
                    if ev == "error":
                        metrics.inc("ws_public_error")
                        return {"ok": False, "error": data.get("msg") or str(data)}
                    if ev == "info" and data.get("code") in (20051, 20060):
                        metrics.inc("ws_public_maintenance")
                        return {
                            "ok": False,
                            "maintenance": True,
                            "code": data.get("code"),
                        }
            metrics.inc("ws_public_timeout")
            return {"ok": False, "error": "timeout"}
        except TimeoutError:
            metrics.inc("ws_public_timeout")
            return {"ok": False, "error": "timeout"}
