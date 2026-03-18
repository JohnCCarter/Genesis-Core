from __future__ import annotations

from fastapi.testclient import TestClient

from core.server import app


def _legacy_runtime_patch(*, entry_conf_overall: float = 0.26) -> dict:
    return {
        "strategy_family": "legacy",
        "thresholds": {
            "entry_conf_overall": entry_conf_overall,
            "regime_proba": {"balanced": 0.5},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "low": {"entry_conf_overall": 0.24, "regime_proba": 0.36},
                    "mid": {"entry_conf_overall": 0.30, "regime_proba": 0.44},
                    "high": {"entry_conf_overall": 0.36, "regime_proba": 0.56},
                },
            },
        },
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
    }


def test_runtime_endpoints_e2e(monkeypatch):
    c = TestClient(app)

    # Read current runtime
    r = c.get("/config/runtime")
    assert r.status_code == 200
    data = r.json()
    assert "cfg" in data and "version" in data and "hash" in data
    v0 = int(data["version"]) or 0
    legacy_patch = _legacy_runtime_patch(entry_conf_overall=0.61)

    # Validate good patch
    r = c.post(
        "/config/runtime/validate",
        json=legacy_patch,
    )
    assert r.status_code == 200
    assert r.json().get("valid") is True

    # Enforce auth: set BEARER_TOKEN and ensure 401 without header
    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    r = c.post(
        "/config/runtime/propose",
        json={
            "patch": legacy_patch,
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
            "patch": legacy_patch,
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert r.status_code == 200
    out = r.json()
    assert int(out.get("version", -1)) == v0 + 1
    assert out.get("cfg", {}).get("thresholds", {}).get("entry_conf_overall") == 0.61


def test_runtime_endpoints_e2e_regime_unified_alias_bridge(monkeypatch):
    c = TestClient(app)

    r = c.get("/config/runtime")
    assert r.status_code == 200
    data = r.json()
    v0 = int(data["version"]) or 0

    ri_payload = {
        "strategy_family": "ri",
        "thresholds": {
            "entry_conf_overall": 0.25,
            "regime_proba": {"balanced": 0.36},
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                    "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                    "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                },
            },
        },
        "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
        "regime_unified": {"authority_mode": "regime_module"},
    }

    r = c.post(
        "/config/runtime/validate",
        json=ri_payload,
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
            "patch": {
                "strategy_family": "ri",
                "thresholds": ri_payload["thresholds"],
                "gates": ri_payload["gates"],
                "regime_unified": {"authority_mode": "regime_module"},
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
    assert out.get("cfg", {}).get("strategy_family") == "ri"
    assert "regime_unified" not in (out.get("cfg", {}) or {})

    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {
                **_legacy_runtime_patch(),
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
    assert out2.get("cfg", {}).get("strategy_family") == "legacy"
