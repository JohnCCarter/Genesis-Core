from fastapi import FastAPI
from fastapi import Body
from core.config.validator import validate_config, diff_config, append_audit
from core.observability.metrics import get_dashboard

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/observability/dashboard")
def observability_dashboard() -> dict:
    return get_dashboard()


@app.post("/config/validate")
def config_validate(payload: dict = Body(...)) -> dict:
    errors = validate_config(payload)
    return {"valid": len(errors) == 0, "errors": errors}


@app.post("/config/diff")
def config_diff(payload: dict = Body(...)) -> dict:
    old = payload.get("old", {}) or {}
    new = payload.get("new", {}) or {}
    changes = diff_config(old, new)
    return {"changes": changes}


@app.post("/config/audit")
def config_audit(payload: dict = Body(...)) -> dict:
    changes = payload.get("changes", []) or []
    user = str(payload.get("user") or "system")
    append_audit(changes, user=user)
    return {"status": "ok", "appended": len(changes)}
