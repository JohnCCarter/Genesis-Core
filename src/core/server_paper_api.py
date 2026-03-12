from __future__ import annotations

from fastapi import APIRouter

from core.config.settings import get_settings as fallback_get_settings
from core.io.bitfinex import read_helpers as fallback_bfx_read
from core.io.bitfinex.exchange_client import get_exchange_client as fallback_get_exchange_client
from core.server_info_api import TEST_SPOT_WHITELIST as fallback_test_spot_whitelist

router = APIRouter()

_DEFAULT_SYMBOL = "tTESTBTC:TESTUSD"
_FALLBACK_MIN_ORDER_SIZE: dict[str, float] = {}
_FALLBACK_MIN_ORDER_MARGIN = 0.05


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
