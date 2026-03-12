import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import Body, FastAPI

import core.server_account_api as server_account_api
import core.server_info_api as server_info_api
import core.server_models_api as server_models_api
import core.server_status_api as server_status_api
import core.server_ui_api as server_ui_api
from core.config.settings import get_settings
from core.io.bitfinex import read_helpers as bfx_read
from core.io.bitfinex.exchange_client import aclose_http_client, get_exchange_client
from core.server_config_api import router as config_router
from core.server_strategy_api import router as strategy_router
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)

_CANDLES_CACHE = {}  # key -> {ts: float, data: dict}
_CANDLES_TTL = 10.0  # 10s cache for candles

_ACCOUNT_CACHE = server_account_api._ACCOUNT_CACHE
_ACCOUNT_TTL = server_account_api._ACCOUNT_TTL
TEST_SPOT_WHITELIST = server_info_api.TEST_SPOT_WHITELIST
paper_whitelist = server_info_api.paper_whitelist
observability_dashboard = server_info_api.observability_dashboard
info_router = server_info_api.router
_AUTH = server_status_api._AUTH
health = server_status_api.health
debug_auth = server_status_api.debug_auth
status_router = server_status_api.router
reload_models = server_models_api.reload_models
models_router = server_models_api.router
auth_check = server_account_api.auth_check
account_wallets = server_account_api.account_wallets
account_positions = server_account_api.account_positions
account_orders = server_account_api.account_orders
account_router = server_account_api.router
ui_page = server_ui_api.ui_page
ui_router = server_ui_api.router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown."""
    # Startup
    try:
        _, h, v = _AUTH.get()
        print(f"CONFIG_VERSION={v} CONFIG_HASH={h[:12]}")
    except Exception as e:
        print(f"CONFIG_READ_FAILED: {e}")

    yield

    # Shutdown (cleanup if needed)
    try:
        await aclose_http_client()
    except Exception as e:
        _LOGGER.debug("shutdown_close_http_client_error: %s", e)


app = FastAPI(lifespan=lifespan)
app.include_router(config_router)
app.include_router(info_router)
app.include_router(status_router)
app.include_router(models_router)
app.include_router(account_router)
app.include_router(ui_router)
app.include_router(strategy_router)


# Minsta orderstorlek per test-ticker (kan uppdateras via probing)
MIN_ORDER_SIZE: dict[str, float] = {
    "tTESTADA:TESTUSD": 4.0,
    "tTESTALGO:TESTUSD": 8.0,
    "tTESTAPT:TESTUSD": 0.03,
    "tTESTAVAX:TESTUSD": 0.08,
    "tTESTBTC:TESTUSD": 0.001,
    "tTESTBTC:TESTUSDT": 0.001,
    "tTESTDOGE:TESTUSD": 22.0,
    "tTESTDOT:TESTUSD": 0.2,
    "tTESTEOS:TESTUSD": 2.0,
    "tTESTETH:TESTUSD": 0.001,
    "tTESTFIL:TESTUSD": 0.2,
    "tTESTLTC:TESTUSD": 0.04,
    "tTESTNEAR:TESTUSD": 0.4,
    "tTESTSOL:TESTUSD": 0.02,
    "tTESTXAUT:TESTUSD": 0.002,
    "tTESTXTZ:TESTUSD": 2.0,
}
# Liten säkerhetsmarginal över minsta storlek
MIN_ORDER_MARGIN: float = 0.05


def _real_from_test(sym: str) -> str:
    u = sym.upper().lstrip("T")
    if ":" in u:
        base_part, quote_part = u.split(":", 1)
    else:
        base_part, quote_part = u, "USD"
    base_part = base_part.replace("TEST", "")
    quote_part = quote_part.replace("TEST", "")
    return "t" + base_part + quote_part


def _base_ccy_from_test(sym: str) -> str:
    u = sym.upper().lstrip("T")
    base_part = u.split(":", 1)[0] if ":" in u else u
    return base_part.replace("TEST", "")


@app.get("/public/candles")
async def public_candles(symbol: str = "tBTCUSD", timeframe: str = "1m", limit: int = 120) -> dict:
    """Proxy till Bitfinex public candles och normaliserar till {open,high,low,close,volume}."""
    import time

    # Check cache
    cache_key = f"{symbol}:{timeframe}:{limit}"
    now = time.time()
    if cache_key in _CANDLES_CACHE:
        entry = _CANDLES_CACHE[cache_key]
        if now - entry["ts"] < _CANDLES_TTL:
            return entry["data"]

    # Fetch fresh
    # Justera limit inom rimliga gränser
    safe_limit = max(1, min(int(limit), 1000))
    endpoint = f"candles/trade:{timeframe}:{symbol}/hist"
    params = {"limit": safe_limit, "sort": 1}

    ec = get_exchange_client()
    r = await ec.public_request(method="GET", endpoint=endpoint, params=params, timeout=10)
    data = r.json()

    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    volumes: list[float] = []

    if isinstance(data, list):
        for row in data:
            # Bitfinex format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
            if isinstance(row, list) and len(row) >= 6:
                opens.append(float(row[1]))
                closes.append(float(row[2]))
                highs.append(float(row[3]))
                lows.append(float(row[4]))
                volumes.append(float(row[5]))

    result = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }

    # Update cache
    _CANDLES_CACHE[cache_key] = {"ts": now, "data": result}

    return result


@app.post("/paper/submit")
async def paper_submit(payload: dict = Body(...)) -> dict:
    """Skicka en order till Bitfinex Paper (auth krävs via .env).

    OBS: Paper only – vi tillåter endast TEST-spotpar från whitelist.
    Icke-whitelistad symbol returnerar explicit invalid_symbol-svar.

      payload: {symbol, side:"LONG"|"SHORT"|"NONE", size:float, type?:"MARKET"|"LIMIT", price?:float}
    """
    # Använd endast symboler från whitelist
    requested_symbol_raw = str(payload.get("symbol") or "")
    key = requested_symbol_raw.upper()
    allowed_map = {s.upper(): s for s in TEST_SPOT_WHITELIST}
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

    # Minimikrav + liten marginal, auto-klampa om under
    required_min = float(MIN_ORDER_SIZE.get(symbol, 0.0))
    min_with_margin = required_min * (1.0 + MIN_ORDER_MARGIN)
    auto_clamped = False
    wallet_clamped = False
    size_before = size
    if abs(size) < min_with_margin:
        size = min_with_margin
        auto_clamped = True

    # Wallet-medveten cap (opt-in): begränsa köp till tillgänglig USD och sälj till innehav av bas
    try:
        s = get_settings()
        if (
            int(getattr(s, "WALLET_CAP_ENABLED", 0) or 0) == 1
            and s.BITFINEX_API_KEY
            and s.BITFINEX_API_SECRET
        ):
            # Hämta wallets
            wallets = await bfx_read.get_wallets()
            avail_by_ccy: dict[str, float] = {}
            if isinstance(wallets, list):
                for w in wallets:
                    # Förvänta v2-format: [type, currency, balance, unsettled, available]
                    if isinstance(w, list) and len(w) >= 5:
                        ccy = str(w[1]).upper()
                        try:
                            avail = float(w[4])
                        except Exception:  # nosec B112
                            continue
                        # endast exchange-wallet
                        if str(w[0]).lower() == "exchange":
                            avail_by_ccy[ccy] = avail_by_ccy.get(ccy, 0.0) + max(0.0, avail)
                    elif isinstance(w, dict):
                        ccy = str(w.get("currency") or "").upper()
                        avail = float(w.get("available") or 0.0)
                        if str(w.get("type") or "").lower() == "exchange" and ccy:
                            avail_by_ccy[ccy] = avail_by_ccy.get(ccy, 0.0) + max(0.0, avail)

            # Derivera real-symbol för pris (tTESTDOGE:TESTUSD -> tDOGEUSD)
            def _real_from_test(sym: str) -> str:
                u = sym.upper().lstrip("T")  # ta bort ledande 't'
                if ":" in u:
                    base_part, quote_part = u.split(":", 1)
                else:
                    base_part, quote_part = u, "USD"
                base_part = base_part.replace("TEST", "")
                quote_part = quote_part.replace("TEST", "")
                return "t" + base_part + quote_part

            def _base_ccy_from_test(sym: str) -> str:
                u = sym.upper().lstrip("T")
                base_part = u.split(":", 1)[0] if ":" in u else u
                return base_part.replace("TEST", "")

            real_sym = _real_from_test(symbol)
            base_ccy = _base_ccy_from_test(symbol)
            # LONG: begränsa efter USD
            if side == "LONG":
                usd_avail = avail_by_ccy.get("USD", 0.0) or avail_by_ccy.get("TESTUSD", 0.0) or 0.0
                px = None
                try:
                    resp = await get_exchange_client().public_request(
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
            # SHORT: begränsa efter innehav av bas
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
        # Ignorera wallet-cap om något går fel
        pass

    amount = size if side == "LONG" else -size

    # Bitfinex v2 order submit (MARKET/LIMIT):
    # endpoint: auth/w/order/submit, body: {type, symbol, amount, price?}
    # Bitfinex kräver EXCHANGE-* typer för spot/paper
    bfx_type = (
        "EXCHANGE MARKET"
        if order_type == "MARKET"
        else ("EXCHANGE LIMIT" if order_type == "LIMIT" else order_type)
    )
    body = {"type": bfx_type, "symbol": symbol, "amount": str(amount)}
    if order_type == "LIMIT" and price is not None:
        body["price"] = str(float(price))

    ec = get_exchange_client()
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
    except httpx.HTTPStatusError as e:
        error_id = uuid.uuid4().hex[:12]
        status = getattr(e.response, "status_code", None)
        text = getattr(e.response, "text", "")
        _LOGGER.warning(
            "paper_submit upstream HTTP error (status=%s error_id=%s): %s",
            status,
            error_id,
            text,
        )
        return {"ok": False, "status": status, "error": "bitfinex_http_error", "error_id": error_id}
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("paper_submit failed (error_id=%s)", error_id)
        return {"ok": False, "error": "internal_error", "error_id": error_id}


@app.get("/paper/estimate")
async def paper_estimate(symbol: str) -> dict:
    """Beräkna minsta storlek (med marginal) och ungefärlig max-storlek utifrån USD-saldo.

    Returnerar även senaste pris och tillgängligt basinnehav för ev. sälj.
    """
    allowed_map = {s.upper(): s for s in TEST_SPOT_WHITELIST}
    sym = allowed_map.get(symbol.upper(), "tTESTBTC:TESTUSD")
    required_min = float(MIN_ORDER_SIZE.get(sym, 0.0))
    min_with_margin = required_min * (1.0 + MIN_ORDER_MARGIN)
    usd_avail: float | None = None
    base_avail: float | None = None
    last_price: float | None = None

    # Hämta wallets (om nycklar finns)
    try:
        s = get_settings()
        if s.BITFINEX_API_KEY and s.BITFINEX_API_SECRET:
            wallets = await bfx_read.get_wallets()
            avail_by_ccy: dict[str, float] = {}
            if isinstance(wallets, list):
                for w in wallets:
                    if isinstance(w, list) and len(w) >= 5:
                        ccy = str(w[1]).upper()
                        try:
                            avail = float(w[4])
                        except Exception:  # nosec B112
                            continue
                        if str(w[0]).lower() == "exchange":
                            avail_by_ccy[ccy] = avail_by_ccy.get(ccy, 0.0) + max(0.0, avail)
                    elif isinstance(w, dict):
                        ccy = str(w.get("currency") or "").upper()
                        avail = float(w.get("available") or 0.0)
                        if str(w.get("type") or "").lower() == "exchange" and ccy:
                            avail_by_ccy[ccy] = avail_by_ccy.get(ccy, 0.0) + max(0.0, avail)
            usd_avail = avail_by_ccy.get("USD") or avail_by_ccy.get("TESTUSD") or 0.0
            base = _base_ccy_from_test(sym)
            base_avail = avail_by_ccy.get(base) or avail_by_ccy.get("TEST" + base) or 0.0
    except Exception:  # nosec B110
        pass

    # Hämta senaste pris
    try:
        real_sym = _real_from_test(sym)
        resp = await get_exchange_client().public_request(
            method="GET",
            endpoint=f"ticker/{real_sym}",
            timeout=5,
        )
        arr = resp.json()
        if isinstance(arr, list) and len(arr) >= 7:
            last_price = float(arr[6])
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
