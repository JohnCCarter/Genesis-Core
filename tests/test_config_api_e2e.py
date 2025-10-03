from __future__ import annotations

from fastapi.testclient import TestClient

from core.server import app


def test_runtime_endpoints_e2e(monkeypatch):
    c = TestClient(app)

    # Read current runtime
    r = c.get("/config/runtime")
    assert r.status_code == 200
    data = r.json()
    assert "cfg" in data and "version" in data and "hash" in data
    v0 = int(data["version"]) or 0

    # Validate good patch
    r = c.post("/config/runtime/validate", json={"thresholds": {"entry_conf_overall": 0.6}})
    assert r.status_code == 200
    assert r.json().get("valid") is True

    # Enforce auth: set BEARER_TOKEN and ensure 401 without header
    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    r = c.post(
        "/config/runtime/propose",
        json={"patch": {"thresholds": {"entry_conf_overall": 0.6}}, "actor": "test", "expected_version": v0},
    )
    assert r.status_code == 401

    # Propose with correct bearer
    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={"patch": {"thresholds": {"entry_conf_overall": 0.6}}, "actor": "test", "expected_version": v0},
    )
    assert r.status_code == 200
    out = r.json()
    assert int(out.get("version", -1)) == v0 + 1


