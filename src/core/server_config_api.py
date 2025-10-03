from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.config.authority import ConfigAuthority

router = APIRouter()
authority = ConfigAuthority()


@router.get("/config/runtime")
def get_runtime() -> dict:
    cfg, h, ver = authority.get()
    return {"cfg": cfg.model_dump_canonical(), "hash": h, "version": ver}


@router.post("/config/runtime/validate")
def validate_runtime(payload: dict) -> dict:
    try:
        cfg = authority.validate(payload or {})
        return {"valid": True, "errors": [], "cfg": cfg.model_dump_canonical()}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


@router.post("/config/runtime/propose")
def propose_runtime(payload: dict) -> dict:
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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        if "version_conflict" in str(e):
            raise HTTPException(status_code=409, detail="version_conflict") from e
        raise HTTPException(status_code=500, detail=str(e)) from e
