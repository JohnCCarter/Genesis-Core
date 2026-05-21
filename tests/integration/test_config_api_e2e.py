from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from core.config.authority import ConfigAuthority
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


def test_runtime_endpoints_e2e_schema_valid_live_blocked_field_returns_coarse_detail(
    monkeypatch,
):
    c = TestClient(app)

    validate_payload = {
        "strategy_family": "legacy",
        "warmup_bars": 12,
    }
    r = c.post(
        "/config/runtime/validate",
        json=validate_payload,
    )
    assert r.status_code == 200
    assert r.json().get("valid") is True
    assert r.json().get("cfg", {}).get("warmup_bars") == 12

    r = c.get("/config/runtime")
    assert r.status_code == 200
    v0 = int(r.json().get("version") or 0)

    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {"warmup_bars": 12},
            "actor": "test",
            "expected_version": v0,
        },
    )

    assert r.status_code == 400
    assert r.json() == {"detail": "non_whitelisted_field"}
    assert "warmup_bars" not in r.text


def test_runtime_endpoints_e2e_exit_enabled_singleton_is_live_and_mixed_patch_is_atomic(
    monkeypatch, tmp_path: Path
):
    c = TestClient(app)

    import core.api.config as api

    monkeypatch.setattr(api, "authority", ConfigAuthority(tmp_path / "runtime.json"))

    r = c.get("/config/runtime")
    assert r.status_code == 200
    initial = r.json()
    v0 = int(initial["version"]) or 0
    initial_exit = initial["cfg"]["exit"]

    monkeypatch.setenv("BEARER_TOKEN", "test-secret")

    accept = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {"exit": {"enabled": False}},
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert accept.status_code == 200
    accepted = accept.json()
    assert int(accepted.get("version", -1)) == v0 + 1
    assert accepted.get("cfg", {}).get("exit", {}).get("enabled") is False
    assert (
        accepted.get("cfg", {}).get("exit", {}).get("stop_loss_pct")
        == initial_exit["stop_loss_pct"]
    )

    after_accept = c.get("/config/runtime")
    assert after_accept.status_code == 200
    after_accept_body = after_accept.json()
    assert int(after_accept_body.get("version", -1)) == v0 + 1
    assert after_accept_body.get("cfg", {}).get("exit", {}).get("enabled") is False
    assert (
        after_accept_body.get("cfg", {}).get("exit", {}).get("stop_loss_pct")
        == initial_exit["stop_loss_pct"]
    )

    reject = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {"exit": {"enabled": True, "stop_loss_pct": 0.01}},
            "actor": "test",
            "expected_version": v0 + 1,
        },
    )
    assert reject.status_code == 400
    assert reject.json() == {"detail": "non_whitelisted_field"}

    after_reject = c.get("/config/runtime")
    assert after_reject.status_code == 200
    after_reject_body = after_reject.json()
    assert int(after_reject_body.get("version", -1)) == v0 + 1
    assert after_reject_body.get("cfg", {}).get("exit", {}).get("enabled") is False
    assert (
        after_reject_body.get("cfg", {}).get("exit", {}).get("stop_loss_pct")
        == initial_exit["stop_loss_pct"]
    )


def test_runtime_endpoints_e2e_version_conflict_detail_preserved(monkeypatch):
    c = TestClient(app)

    r = c.get("/config/runtime")
    assert r.status_code == 200
    v0 = int(r.json().get("version") or 0)

    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    first_patch = _legacy_runtime_patch(entry_conf_overall=0.63)
    first = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": first_patch,
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert first.status_code == 200

    second = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": _legacy_runtime_patch(entry_conf_overall=0.64),
            "actor": "test",
            "expected_version": v0,
        },
    )
    assert second.status_code == 409
    assert second.json() == {"detail": "version_conflict"}
