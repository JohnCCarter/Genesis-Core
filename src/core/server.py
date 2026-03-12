from contextlib import asynccontextmanager

from fastapi import FastAPI

import core.api.account as server_account_api
import core.api.info as server_info_api
import core.api.models as server_models_api
import core.api.paper as server_paper_api
import core.api.public as server_public_api
import core.api.status as server_status_api
import core.api.ui as server_ui_api
from core.api.config import router as config_router
from core.api.strategy import router as strategy_router
from core.config.settings import get_settings  # noqa: F401
from core.io.bitfinex import read_helpers as bfx_read  # noqa: F401
from core.io.bitfinex.exchange_client import aclose_http_client, get_exchange_client  # noqa: F401
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)

_CANDLES_CACHE = server_public_api._CANDLES_CACHE
_CANDLES_TTL = server_public_api._CANDLES_TTL

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
public_candles = server_public_api.public_candles
public_router = server_public_api.router
paper_estimate = server_paper_api.paper_estimate
paper_submit = server_paper_api.paper_submit
paper_router = server_paper_api.router


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
app.include_router(public_router)
app.include_router(paper_router)
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
