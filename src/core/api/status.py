from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.config.authority import ConfigAuthority
from core.config.settings import get_settings
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger("core.server")
_AUTH = ConfigAuthority()

router = APIRouter()


@router.get("/health", response_model=None)
def health() -> dict | JSONResponse:
    try:
        _, h, v = _AUTH.get()
        return {"status": "ok", "config_version": v, "config_hash": h}
    except Exception as exc:
        _LOGGER.warning("health_config_read_failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "error", "config_version": None, "config_hash": None},
        )


@router.get("/debug/auth")
def debug_auth() -> dict:
    """Maskerad vy av laddade auth-nycklar (endast längd + suffix)."""
    s = get_settings()
    k = (s.BITFINEX_API_KEY or "").strip()
    masked = {
        "present": bool(k),
        "length": len(k),
        "suffix": k[-4:] if len(k) >= 4 else k,
    }
    return {"rest_api_key": masked}
