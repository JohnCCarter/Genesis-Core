from __future__ import annotations

import uuid

import httpx
from fastapi import APIRouter, Body

from core.config.settings import get_settings as fallback_get_settings
from core.io.bitfinex import read_helpers as fallback_bfx_read
from core.io.bitfinex.exchange_client import get_exchange_client as fallback_get_exchange_client
from core.server_info_api import TEST_SPOT_WHITELIST as fallback_test_spot_whitelist
from core.utils.logging_redaction import get_logger

router = APIRouter()

_DEFAULT_SYMBOL = "tTESTBTC:TESTUSD"
_FALLBACK_MIN_ORDER_SIZE: dict[str, float] = {}
_FALLBACK_MIN_ORDER_MARGIN = 0.05
_FALLBACK_LOGGER = get_logger("core.server")


def _resolve_server_module():
    try:
        import core.server as server_mod

        return server_mod
    except Exception:
        return None


def _resolve_test_spot_whitelist() -> list[str]:
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "TEST_SPOT_WHITELIST"):
        return list(server_mod.TEST_SPOT_WHITELIST)
    return list(fallback_test_spot_whitelist)


def _resolve_min_order_size() -> dict[str, float]:
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "MIN_ORDER_SIZE"):
        return server_mod.MIN_ORDER_SIZE
    return _FALLBACK_MIN_ORDER_SIZE


def _resolve_min_order_margin() -> float:
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "MIN_ORDER_MARGIN"):
        return float(server_mod.MIN_ORDER_MARGIN)
    return _FALLBACK_MIN_ORDER_MARGIN


def _resolve_get_settings():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "get_settings"):
        return server_mod.get_settings
    return fallback_get_settings


def _resolve_bfx_read():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "bfx_read"):
        return server_mod.bfx_read
    return fallback_bfx_read


def _resolve_get_exchange_client():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "get_exchange_client"):
        return server_mod.get_exchange_client
    return fallback_get_exchange_client


def _resolve_real_from_test():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "_real_from_test"):
        return server_mod._real_from_test
    return lambda sym: sym


def _resolve_base_ccy_from_test():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "_base_ccy_from_test"):
        return server_mod._base_ccy_from_test
    return lambda sym: sym.upper().lstrip("T").split(":", 1)[0]


def _resolve_logger():
    server_mod = _resolve_server_module()
    if server_mod is not None and hasattr(server_mod, "_LOGGER"):
        return server_mod._LOGGER
    return _FALLBACK_LOGGER


@router.get("/paper/estimate")
async def paper_estimate(symbol: str) -> dict:
    """Beräkna minsta storlek (med marginal) och ungefärlig max-storlek utifrån USD-saldo.

    Returnerar även senaste pris och tillgängligt basinnehav för ev. sälj.
    """
    allowed_map = {value.upper(): value for value in _resolve_test_spot_whitelist()}
    sym = allowed_map.get(symbol.upper(), _DEFAULT_SYMBOL)
    min_order_size = _resolve_min_order_size()
    min_order_margin = _resolve_min_order_margin()
    required_min = float(min_order_size.get(sym, 0.0))
    min_with_margin = required_min * (1.0 + min_order_margin)
    usd_avail: float | None = None
    base_avail: float | None = None
    last_price: float | None = None

    try:
        settings = _resolve_get_settings()()
        if settings.BITFINEX_API_KEY and settings.BITFINEX_API_SECRET:
            wallets = await _resolve_bfx_read().get_wallets()
            avail_by_ccy: dict[str, float] = {}
            if isinstance(wallets, list):
                for wallet in wallets:
                    if isinstance(wallet, list) and len(wallet) >= 5:
                        currency = str(wallet[1]).upper()
                        try:
                            available = float(wallet[4])
                        except Exception:  # nosec B112
                            continue
                        if str(wallet[0]).lower() == "exchange":
                            avail_by_ccy[currency] = avail_by_ccy.get(currency, 0.0) + max(
                                0.0, available
                            )
                    elif isinstance(wallet, dict):
                        currency = str(wallet.get("currency") or "").upper()
                        available = float(wallet.get("available") or 0.0)
                        if str(wallet.get("type") or "").lower() == "exchange" and currency:
                            avail_by_ccy[currency] = avail_by_ccy.get(currency, 0.0) + max(
                                0.0, available
                            )
            usd_avail = avail_by_ccy.get("USD") or avail_by_ccy.get("TESTUSD") or 0.0
            base = _resolve_base_ccy_from_test()(sym)
            base_avail = avail_by_ccy.get(base) or avail_by_ccy.get("TEST" + base) or 0.0
    except Exception:  # nosec B110
        pass

    try:
        real_sym = _resolve_real_from_test()(sym)
        response = await _resolve_get_exchange_client()().public_request(
            method="GET",
            endpoint=f"ticker/{real_sym}",
            timeout=5,
        )
        payload = response.json()
        if isinstance(payload, list) and len(payload) >= 7:
            last_price = float(payload[6])
    except Exception:
        last_price = None

    est_max_size: float | None = None
    if (usd_avail is not None) and (last_price is not None) and last_price > 0:
        est_max_size = usd_avail / last_price

    return {
        "symbol": sym,
        "required_min": required_min,
        "min_with_margin": min_with_margin,
        "usd_available": usd_avail,
        "base_available": base_avail,
        "last_price": last_price,
        "est_max_size": est_max_size,
    }


@router.post("/paper/submit")
async def paper_submit(payload: dict = Body(...)) -> dict:
    """Skicka en order till Bitfinex Paper (auth krävs via .env).

    OBS: Paper only – vi tillåter endast TEST-spotpar från whitelist.
    Icke-whitelistad symbol returnerar explicit invalid_symbol-svar.

      payload: {symbol, side:"LONG"|"SHORT"|"NONE", size:float, type?:"MARKET"|"LIMIT", price?:float}
    """
    requested_symbol_raw = str(payload.get("symbol") or "")
    key = requested_symbol_raw.upper()
    allowed_map = {value.upper(): value for value in _resolve_test_spot_whitelist()}
    symbol = allowed_map.get(key)
    if symbol is None:
        return {
            "ok": False,
            "error": "invalid_symbol",
            "requested_symbol": requested_symbol_raw,
            "message": "symbol must be one of TEST_SPOT_WHITELIST",
        }
    side = str(payload.get("side") or "NONE").upper()
    size = float(payload.get("size") or 0.0)
    order_type = str(payload.get("type") or "MARKET").upper()
    price = payload.get("price")
    if side not in ("LONG", "SHORT") or size <= 0:
        return {"ok": False, "error": "invalid_action_or_size"}

    min_order_size = _resolve_min_order_size()
    min_order_margin = _resolve_min_order_margin()
    required_min = float(min_order_size.get(symbol, 0.0))
    min_with_margin = required_min * (1.0 + min_order_margin)
    auto_clamped = False
    wallet_clamped = False
    size_before = size
    if abs(size) < min_with_margin:
        size = min_with_margin
        auto_clamped = True

    try:
        settings = _resolve_get_settings()()
        if (
            int(getattr(settings, "WALLET_CAP_ENABLED", 0) or 0) == 1
            and settings.BITFINEX_API_KEY
            and settings.BITFINEX_API_SECRET
        ):
            wallets = await _resolve_bfx_read().get_wallets()
            avail_by_ccy: dict[str, float] = {}
            if isinstance(wallets, list):
                for wallet in wallets:
                    if isinstance(wallet, list) and len(wallet) >= 5:
                        currency = str(wallet[1]).upper()
                        try:
                            available = float(wallet[4])
                        except Exception:  # nosec B112
                            continue
                        if str(wallet[0]).lower() == "exchange":
                            avail_by_ccy[currency] = avail_by_ccy.get(currency, 0.0) + max(
                                0.0, available
                            )
                    elif isinstance(wallet, dict):
                        currency = str(wallet.get("currency") or "").upper()
                        available = float(wallet.get("available") or 0.0)
                        if str(wallet.get("type") or "").lower() == "exchange" and currency:
                            avail_by_ccy[currency] = avail_by_ccy.get(currency, 0.0) + max(
                                0.0, available
                            )

            real_sym = _resolve_real_from_test()(symbol)
            base_ccy = _resolve_base_ccy_from_test()(symbol)
            if side == "LONG":
                usd_avail = avail_by_ccy.get("USD", 0.0) or avail_by_ccy.get("TESTUSD", 0.0) or 0.0
                px = None
                try:
                    resp = await _resolve_get_exchange_client()().public_request(
                        method="GET",
                        endpoint=f"ticker/{real_sym}",
                        timeout=5,
                    )
                    arr = resp.json()
                    if isinstance(arr, list) and len(arr) >= 7:
                        px = float(arr[6])
                except Exception:
                    px = None
                if px and px > 0 and usd_avail > 0:
                    max_affordable = usd_avail / px
                    if size > max_affordable:
                        size = max(max_affordable, min_with_margin)
                        wallet_clamped = True
            elif side == "SHORT":
                base_avail = (
                    avail_by_ccy.get(base_ccy, 0.0)
                    or avail_by_ccy.get("TEST" + base_ccy, 0.0)
                    or 0.0
                )
                if base_avail > 0 and abs(size) > base_avail:
                    size = base_avail
                    wallet_clamped = True
    except Exception:  # nosec B110
        pass

    amount = size if side == "LONG" else -size
    bfx_type = (
        "EXCHANGE MARKET"
        if order_type == "MARKET"
        else ("EXCHANGE LIMIT" if order_type == "LIMIT" else order_type)
    )
    body = {"type": bfx_type, "symbol": symbol, "amount": str(amount)}
    if order_type == "LIMIT" and price is not None:
        body["price"] = str(float(price))

    ec = _resolve_get_exchange_client()()
    try:
        resp = await ec.signed_request(method="POST", endpoint="auth/w/order/submit", body=body)
        data = resp.json() if hasattr(resp, "json") else {"status": resp.status_code}
        return {
            "ok": True,
            "exchange": "bitfinex",
            "request": body,
            "response": data,
            "meta": {
                "auto_clamped": auto_clamped,
                "wallet_clamped": wallet_clamped,
                "size_before": size_before,
                "size_after": size,
                "required_min": required_min,
                "min_with_margin": min_with_margin,
            },
        }
    except httpx.HTTPStatusError as exc:
        error_id = uuid.uuid4().hex[:12]
        status = getattr(exc.response, "status_code", None)
        text = getattr(exc.response, "text", "")
        _resolve_logger().warning(
            "paper_submit upstream HTTP error (status=%s error_id=%s): %s",
            status,
            error_id,
            text,
        )
        return {"ok": False, "status": status, "error": "bitfinex_http_error", "error_id": error_id}
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _resolve_logger().exception("paper_submit failed (error_id=%s)", error_id)
        return {"ok": False, "error": "internal_error", "error_id": error_id}
