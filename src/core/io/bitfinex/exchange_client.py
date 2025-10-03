from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import httpx

from core.config.settings import get_settings
from core.observability.metrics import metrics
from core.symbols.symbols import SymbolMapper, SymbolMode
from core.utils.backoff import exponential_backoff_delay
from core.utils.logging_redaction import get_logger
from core.utils.nonce_manager import bump_nonce, get_nonce

_HTTP_CLIENT: httpx.AsyncClient | None = None
_BASE_URL = "https://api.bitfinex.com"
_LOGGER = get_logger(__name__)


def _get_http_client() -> httpx.AsyncClient:
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        _HTTP_CLIENT = httpx.AsyncClient(timeout=10)
    return _HTTP_CLIENT


class ExchangeClient:
    """Minimal central REST-klient för Bitfinex v2.

    - Bygger signerade headers med NonceManager
    - Skickar requests (GET/POST)
    - Engångs-retry med enkel jitter-backoff vid 10114/429/5xx
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        try:
            self._symbol_mapper = SymbolMapper(self._settings.symbol_mode)
        except Exception:
            self._symbol_mapper = SymbolMapper(SymbolMode.REALISTIC)

    def _build_headers(self, endpoint: str, body: dict[str, Any] | None) -> dict[str, str]:
        api_key = (self._settings.BITFINEX_API_KEY or "").strip()
        api_secret = (self._settings.BITFINEX_API_SECRET or "").strip()
        nonce = get_nonce(api_key)
        payload_str = json.dumps(body or {}, separators=(",", ":"))
        message = f"/api/v2/{endpoint}{nonce}{payload_str}"
        signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha384).hexdigest()
        return {
            "bfx-apikey": api_key,
            "bfx-nonce": nonce,
            "bfx-signature": signature,
            "Content-Type": "application/json",
        }

    async def signed_request(
        self,
        *,
        method: str,
        endpoint: str,
        body: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        body = dict(body or {})
        # Resolve symbol if present
        sym = body.get("symbol")
        if isinstance(sym, str):
            su = sym.upper()
            if su.startswith("TTEST") or ":TEST" in su:
                body["symbol"] = self._symbol_mapper.force(sym)
            else:
                body["symbol"] = self._symbol_mapper.resolve(sym)
        metrics.inc("rest_auth_request")
        try:
            _LOGGER.info("REST %s %s", method.upper(), endpoint)
        except Exception as log_err:
            _LOGGER.debug("log_error: %s", log_err)
        client = _get_http_client()
        url = f"{_BASE_URL}/v2/{endpoint}"
        headers = self._build_headers(endpoint, body)

        async def _do() -> httpx.Response:
            # Viktigt: använd exakt samma JSON‑serialisering för innehållet som vid signering
            body_str = json.dumps(body, separators=(",", ":"))
            req = getattr(client, method.lower())
            return await req(url, headers=headers, content=body_str)

        # Första försök
        try:
            resp = await _do()
            if resp.status_code in (429,) or resp.status_code >= 500:
                metrics.inc("rest_auth_retry_triggered")
                try:
                    _LOGGER.info(
                        "REST retry %s %s status=%s",
                        method.upper(),
                        endpoint,
                        resp.status_code,
                    )
                except Exception as log_err:
                    _LOGGER.debug("log_error: %s", log_err)
                await self._sleep_jitter()
                # Engångs-retry
                headers = self._build_headers(endpoint, body)
                resp = await _do()
            resp.raise_for_status()
            metrics.inc("rest_auth_success")
            try:
                metrics.event(
                    "rest_auth_ok",
                    {"endpoint": endpoint, "status": resp.status_code},
                )
            except Exception as m_err:
                _LOGGER.debug("metrics_error: %s", m_err)
            return resp
        except httpx.HTTPStatusError as e:
            text = e.response.text if e.response is not None else ""
            if "nonce" in text.lower() or "10114" in text:
                # Bumpa noncen och prova en gång till
                api_key = (self._settings.BITFINEX_API_KEY or "").strip()
                metrics.inc("rest_auth_nonce_bump")
                try:
                    _LOGGER.info("REST nonce bump + retry for %s", endpoint)
                except Exception as log_err:
                    _LOGGER.debug("log_error: %s", log_err)
                bump_nonce(api_key)
                headers = self._build_headers(endpoint, body)
                resp2 = await _do()
                resp2.raise_for_status()
                metrics.inc("rest_auth_success")
                try:
                    metrics.event(
                        "rest_auth_ok",
                        {"endpoint": endpoint, "status": resp2.status_code},
                    )
                except Exception as m_err:
                    _LOGGER.debug("metrics_error: %s", m_err)
                return resp2
            metrics.inc("rest_auth_error")
            try:
                metrics.event(
                    "rest_auth_error",
                    {
                        "endpoint": endpoint,
                        "status": getattr(e.response, "status_code", None),
                    },
                )
                _LOGGER.info(
                    "REST error %s %s status=%s",
                    method.upper(),
                    endpoint,
                    getattr(e.response, "status_code", None),
                )
            except Exception as log_err:
                _LOGGER.debug("log_error: %s", log_err)
            raise

    async def _sleep_jitter(self) -> None:
        # Enhetlig backoff/jitter via util (en mild fördröjning)
        import asyncio

        delay = exponential_backoff_delay(
            0, base_delay=0.0, max_backoff=0.3, jitter_min_ms=100, jitter_max_ms=300
        )
        await asyncio.sleep(delay)


_EXCHANGE_CLIENT: ExchangeClient | None = None


def get_exchange_client() -> ExchangeClient:
    global _EXCHANGE_CLIENT
    if _EXCHANGE_CLIENT is None:
        _EXCHANGE_CLIENT = ExchangeClient()
    return _EXCHANGE_CLIENT
