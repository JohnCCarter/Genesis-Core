from __future__ import annotations

import uuid

from fastapi import APIRouter, Header, HTTPException

from core.config.authority import ConfigAuthority
from core.utils.logging_redaction import get_logger

router = APIRouter()
authority = ConfigAuthority()
_LOGGER = get_logger(__name__)


@router.get("/config/runtime")
def get_runtime() -> dict:
    cfg, h, ver = authority.get()
    return {"cfg": cfg.model_dump_canonical(), "hash": h, "version": ver}


@router.post("/config/runtime/validate")
def validate_runtime(payload: dict) -> dict:
    try:
        cfg = authority.validate(payload or {})
        return {"valid": True, "errors": [], "cfg": cfg.model_dump_canonical()}
    except Exception:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/config/runtime/validate failed (error_id=%s)", error_id)
        return {"valid": False, "errors": ["invalid_config"], "error_id": error_id}


@router.post("/config/runtime/propose")
def propose_runtime(payload: dict, authorization: str | None = Header(default=None)) -> dict:
    from core.config.settings import get_settings

    s = get_settings()
    expected_bearer = (s.BEARER_TOKEN or "").strip()
    if not expected_bearer:
        # Fail-closed: never allow runtime config writes without an explicit bearer token.
        raise HTTPException(status_code=403, detail="forbidden")

    token = (authorization or "").replace("Bearer ", "").strip()
    if token != expected_bearer:
        raise HTTPException(status_code=401, detail="unauthorized")
    patch = payload.get("patch") or {}
    actor = str(payload.get("actor") or "system")
    expected_version = int(payload.get("expected_version") or 0)
    try:
        snap = authority.propose_update(patch, actor=actor, expected_version=expected_version)
        return {
            "cfg": snap.cfg.model_dump_canonical(),
            "hash": snap.hash,
            "version": snap.version,
        }
    except ValueError as e:
        # Avoid leaking exception-derived details; callers should treat 400 uniformly.
        raise HTTPException(status_code=400, detail="bad_request") from e
    except RuntimeError as e:
        if "version_conflict" in str(e):
            raise HTTPException(status_code=409, detail="version_conflict") from e
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/config/runtime/propose failed (error_id=%s)", error_id)
        raise HTTPException(status_code=500, detail="internal_error") from e
    except Exception as e:
        error_id = uuid.uuid4().hex[:12]
        _LOGGER.exception("/config/runtime/propose failed (error_id=%s)", error_id)
        raise HTTPException(status_code=500, detail="internal_error") from e
