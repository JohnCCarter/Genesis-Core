from __future__ import annotations

from fastapi import APIRouter

from core.strategy.model_registry import ModelRegistry

router = APIRouter()


@router.post("/models/reload")
def reload_models() -> dict:
    """Force reload all model files by clearing cache. Useful after ML training."""
    registry = ModelRegistry()
    registry.clear_cache()
    return {"ok": True, "message": "Model cache cleared"}
