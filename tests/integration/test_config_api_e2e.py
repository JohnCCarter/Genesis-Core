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
    r = c.post(
        "/config/runtime/validate",
        json={"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}},
    )
    assert r.status_code == 200
    assert r.json().get("valid") is True

    # Enforce auth: set BEARER_TOKEN and ensure 401 without header
    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    r = c.post(
        "/config/runtime/propose",
        json={
            "patch": {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}
            },
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert r.status_code == 401

    # Propose with correct bearer
    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}
            },
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert r.status_code == 200
    out = r.json()
    assert int(out.get("version", -1)) == v0 + 1
    assert (
        out.get("cfg", {})
        .get("multi_timeframe", {})
        .get("regime_intelligence", {})
        .get("authority_mode")
        == "regime_module"
    )


def test_runtime_endpoints_e2e_regime_unified_alias_bridge(monkeypatch):
    c = TestClient(app)

    r = c.get("/config/runtime")
    assert r.status_code == 200
    data = r.json()
    v0 = int(data["version"]) or 0

    r = c.post(
        "/config/runtime/validate",
        json={"regime_unified": {"authority_mode": "regime_module"}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("valid") is True
    assert (
        body.get("cfg", {})
        .get("multi_timeframe", {})
        .get("regime_intelligence", {})
        .get("authority_mode")
        == "regime_module"
    )
    assert "regime_unified" not in (body.get("cfg", {}) or {})

    monkeypatch.setenv("BEARER_TOKEN", "test-secret")

    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {"regime_unified": {"authority_mode": "regime_module"}},
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert r.status_code == 200
    out = r.json()
    assert int(out.get("version", -1)) == v0 + 1
    assert (
        out.get("cfg", {})
        .get("multi_timeframe", {})
        .get("regime_intelligence", {})
        .get("authority_mode")
        == "regime_module"
    )
    assert "regime_unified" not in (out.get("cfg", {}) or {})

    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            "actor": "test",
            "expected_version": v0 + 1,
        },
    )
    assert r.status_code == 200
    out2 = r.json()
    assert int(out2.get("version", -1)) == v0 + 2
    assert (
        out2.get("cfg", {})
        .get("multi_timeframe", {})
        .get("regime_intelligence", {})
        .get("authority_mode")
        == "legacy"
    )
