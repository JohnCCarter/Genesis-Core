from __future__ import annotations

import json
import re
from typing import Any

import httpx

from core.config.settings import get_settings
from core.observability.metrics import metrics
from core.symbols.symbols import SymbolMapper, SymbolMode
from core.utils.backoff import exponential_backoff_delay
from core.utils.crypto import build_hmac_signature
from core.utils.logging_redaction import get_logger
from core.utils.nonce_manager import bump_nonce, get_nonce

_HTTP_CLIENT: httpx.AsyncClient | None = None
_BASE_URL = "https://api.bitfinex.com"
_LOGGER = get_logger(__name__)
_MAX_SIGNED_REQUEST_ATTEMPTS = 3
_NONCE_ERROR_CODE = 10114
_RETRYABLE_STATUS_CODES = {429}


def _collect_error_markers(payload: Any, *, codes: set[int], texts: list[str]) -> None:
    if isinstance(payload, dict):
        for value in payload.values():
            _collect_error_markers(value, codes=codes, texts=texts)
        return
    if isinstance(payload, list | tuple):
        for value in payload:
            _collect_error_markers(value, codes=codes, texts=texts)
        return
    if isinstance(payload, int):
        codes.add(payload)
        return
    if isinstance(payload, str):
        texts.append(payload.lower())


def _extract_error_markers(response: Any | None) -> tuple[set[int], list[str]]:
    codes: set[int] = set()
    texts: list[str] = []
    if response is None:
        return codes, texts

    try:
        payload = response.json()
    except Exception:
        payload = None
    _collect_error_markers(payload, codes=codes, texts=texts)

    text = getattr(response, "text", "")
    if isinstance(text, str) and text:
        texts.append(text.lower())
        for match in re.findall(r"\b\d+\b", text):
            try:
                codes.add(int(match))
            except ValueError:
                continue
    return codes, texts


async def aclose_http_client() -> None:
    """Close the shared HTTP client (if created).

    This is primarily used from FastAPI lifespan shutdown to avoid resource warnings.
    """

    global _HTTP_CLIENT
    client = _HTTP_CLIENT
    _HTTP_CLIENT = None
    if client is None:
        return
    try:
        await client.aclose()
    except Exception as e:
        _LOGGER.debug("http_client_close_error: %s", e)


def _get_http_client() -> httpx.AsyncClient:
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        _HTTP_CLIENT = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0, pool=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _HTTP_CLIENT


class ExchangeClient:
    """Minimal central REST-klient för Bitfinex v2.

    - Bygger signerade headers med NonceManager
    - Skickar requests (GET/POST)
    - Begränsad retry med jitter-backoff för 10114/429/5xx och transienta request-fel
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
        signature = build_hmac_signature(api_secret, message)
        return {
            "bfx-apikey": api_key,
            "bfx-nonce": nonce,
            "bfx-signature": signature,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _is_retryable_status(status_code: int | None) -> bool:
        return status_code is not None and (
            status_code in _RETRYABLE_STATUS_CODES or status_code >= 500
        )

    @staticmethod
    def _is_nonce_error(response: Any | None) -> bool:
        codes, texts = _extract_error_markers(response)
        return _NONCE_ERROR_CODE in codes or any("nonce" in text for text in texts)

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
        api_key = (self._settings.BITFINEX_API_KEY or "").strip()

        async def _do(request_headers: dict[str, str]) -> httpx.Response:
            # Viktigt: använd exakt samma JSON‑serialisering för innehållet som vid signering
            body_str = json.dumps(body, separators=(",", ":"))
            req = getattr(client, method.lower())
            kwargs: dict[str, Any] = {"headers": request_headers, "content": body_str}
            if timeout is not None:
                kwargs["timeout"] = timeout
            return await req(url, **kwargs)

        for attempt in range(_MAX_SIGNED_REQUEST_ATTEMPTS):
            headers = self._build_headers(endpoint, body)
            try:
                resp = await _do(headers)
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
                status_code = getattr(e.response, "status_code", None)
                if self._is_nonce_error(e.response) and attempt + 1 < _MAX_SIGNED_REQUEST_ATTEMPTS:
                    metrics.inc("rest_auth_nonce_bump")
                    try:
                        _LOGGER.info(
                            "REST nonce bump + retry for %s attempt=%s/%s",
                            endpoint,
                            attempt + 2,
                            _MAX_SIGNED_REQUEST_ATTEMPTS,
                        )
                    except Exception as log_err:
                        _LOGGER.debug("log_error: %s", log_err)
                    bump_nonce(api_key)
                    await self._sleep_jitter(attempt + 1)
                    continue
                if (
                    self._is_retryable_status(status_code)
                    and attempt + 1 < _MAX_SIGNED_REQUEST_ATTEMPTS
                ):
                    metrics.inc("rest_auth_retry_triggered")
                    try:
                        _LOGGER.info(
                            "REST retry %s %s status=%s attempt=%s/%s",
                            method.upper(),
                            endpoint,
                            status_code,
                            attempt + 2,
                            _MAX_SIGNED_REQUEST_ATTEMPTS,
                        )
                    except Exception as log_err:
                        _LOGGER.debug("log_error: %s", log_err)
                    await self._sleep_jitter(attempt + 1)
                    continue
                metrics.inc("rest_auth_error")
                try:
                    metrics.event(
                        "rest_auth_error",
                        {
                            "endpoint": endpoint,
                            "status": status_code,
                        },
                    )
                    _LOGGER.info(
                        "REST error %s %s status=%s",
                        method.upper(),
                        endpoint,
                        status_code,
                    )
                except Exception as log_err:
                    _LOGGER.debug("log_error: %s", log_err)
                raise
            except httpx.RequestError as e:
                if attempt + 1 < _MAX_SIGNED_REQUEST_ATTEMPTS:
                    metrics.inc("rest_auth_retry_triggered")
                    try:
                        _LOGGER.info(
                            "REST retry %s %s request_error=%s attempt=%s/%s",
                            method.upper(),
                            endpoint,
                            type(e).__name__,
                            attempt + 2,
                            _MAX_SIGNED_REQUEST_ATTEMPTS,
                        )
                    except Exception as log_err:
                        _LOGGER.debug("log_error: %s", log_err)
                    await self._sleep_jitter(attempt + 1)
                    continue
                metrics.inc("rest_auth_error")
                try:
                    metrics.event(
                        "rest_auth_error",
                        {
                            "endpoint": endpoint,
                            "status": None,
                        },
                    )
                    _LOGGER.info(
                        "REST error %s %s request_error=%s",
                        method.upper(),
                        endpoint,
                        type(e).__name__,
                    )
                except Exception as log_err:
                    _LOGGER.debug("log_error: %s", log_err)
                raise

        raise RuntimeError("signed_request_retry_loop_exhausted_without_return")

    async def _sleep_jitter(self, attempt: int = 1) -> None:
        # Enhetlig backoff/jitter via util (en mild fördröjning)
        import asyncio

        delay = exponential_backoff_delay(
            attempt,
            base_delay=0.05,
            max_backoff=0.4,
            jitter_min_ms=100,
            jitter_max_ms=300,
        )
        await asyncio.sleep(delay)

    async def public_request(
        self,
        *,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Utför en publik (osignerad) request via den delade klienten."""
        client = _get_http_client()
        url = f"{_BASE_URL}/v2/{endpoint}"

        try:
            req = getattr(client, method.lower())
            kwargs: dict[str, Any] = {"params": params}
            if timeout is not None:
                kwargs["timeout"] = timeout
            resp = await req(url, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            _LOGGER.warning("REST public error %s %s: %s", method, endpoint, e)
            raise


_EXCHANGE_CLIENT: ExchangeClient | None = None


def get_exchange_client() -> ExchangeClient:
    global _EXCHANGE_CLIENT
    if _EXCHANGE_CLIENT is None:
        _EXCHANGE_CLIENT = ExchangeClient()
    return _EXCHANGE_CLIENT
