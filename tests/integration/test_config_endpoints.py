import subprocess
import sys

from fastapi.testclient import TestClient

from core.config.validator import diff_config, validate_config
from core.server import app


def test_config_module_alias_resolves_to_same_module_object():
    import sys

    import core.api.config as new_api
    import core.server_config_api as old_api

    assert old_api is new_api
    assert sys.modules["core.server_config_api"] is sys.modules["core.api.config"] is old_api


def test_config_module_alias_resolves_to_same_module_object_when_old_path_imports_first():
    code = "\n".join(
        [
            "import sys",
            "import core.server_config_api as old_api",
            "assert 'core.server' not in sys.modules",
            "import core.api.config as new_api",
            "assert old_api is new_api",
            "assert sys.modules['core.server_config_api'] is sys.modules['core.api.config'] is old_api",
        ]
    )

    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_config_validation_and_diff_helpers():
    good = {"dry_run": True, "position_cap_pct": 20}
    bad = {"dry_run": "yes"}
    assert validate_config(good) == []
    assert any("is not of type" in e for e in validate_config(bad))

    a = {"x": 1}
    b = {"x": 2, "y": 3}
    d = diff_config(a, b)
    keys = {c["key"] for c in d}
    assert keys == {"x", "y"}


def test_config_endpoints():
    c = TestClient(app)

    # runtime validate (new API)
    good_rt = {"thresholds": {"entry_conf_overall": 0.6}}
    bad_rt = {"ev": {"R_default": "invalid"}}

    r = c.post("/config/runtime/validate", json=good_rt)
    assert r.status_code == 200 and r.json().get("valid") is True

    r = c.post("/config/runtime/validate", json=bad_rt)
    assert r.status_code == 200 and r.json().get("valid") is False

    good_authority_mode = {
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}
    }
    good_authority_mode_alias = {"regime_unified": {"authority_mode": "regime_module"}}
    bad_authority_mode = {
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}}
    }
    bad_authority_mode_alias_non_dict = {"regime_unified": "regime_module"}
    bad_authority_mode_alias_extra_key = {
        "regime_unified": {"authority_mode": "regime_module", "extra": 1}
    }
    bad_conflicting_authority_mode = {
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}},
        "regime_unified": {"authority_mode": "regime_module"},
    }

    r = c.post("/config/runtime/validate", json=good_authority_mode)
    assert r.status_code == 200 and r.json().get("valid") is True

    r = c.post("/config/runtime/validate", json=good_authority_mode_alias)
    assert r.status_code == 200 and r.json().get("valid") is True

    r = c.post("/config/runtime/validate", json=bad_authority_mode)
    assert r.status_code == 200 and r.json().get("valid") is False

    r = c.post("/config/runtime/validate", json=bad_authority_mode_alias_non_dict)
    assert r.status_code == 200 and r.json().get("valid") is False

    r = c.post("/config/runtime/validate", json=bad_authority_mode_alias_extra_key)
    assert r.status_code == 200 and r.json().get("valid") is False

    r = c.post("/config/runtime/validate", json=bad_conflicting_authority_mode)
    assert r.status_code == 200 and r.json().get("valid") is False

    # runtime get
    r = c.get("/config/runtime")
    assert r.status_code == 200
    assert set(r.json().keys()) >= {"cfg", "version", "hash"}


def test_runtime_validate_uses_config_authority_validate(monkeypatch):
    c = TestClient(app)

    import core.api.config as new_api
    import core.server_config_api as api

    assert api is new_api

    calls = {"n": 0, "payload": None}

    class _FakeCfg:
        def model_dump_canonical(self):
            return {"_source": "authority.validate"}

    def _fake_validate(payload):
        calls["n"] += 1
        calls["payload"] = payload
        return _FakeCfg()

    monkeypatch.setattr(api.authority, "validate", _fake_validate)

    payload = {"thresholds": {"entry_conf_overall": 0.61}}
    r = c.post("/config/runtime/validate", json=payload)

    assert r.status_code == 200
    assert r.json() == {
        "valid": True,
        "errors": [],
        "cfg": {"_source": "authority.validate"},
    }
    assert calls["n"] == 1
    assert calls["payload"] == payload


def test_runtime_endpoints_do_not_leak_exceptions(monkeypatch):
    c = TestClient(app)

    # validate should not echo exception details
    r = c.post("/config/runtime/validate", json={"ev": {"R_default": "SECRET_SHOULD_NOT_LEAK"}})
    assert r.status_code == 200
    assert r.json().get("valid") is False
    assert "SECRET_SHOULD_NOT_LEAK" not in r.text

    # propose should not leak runtime exceptions
    import core.api.config as new_api
    import core.server_config_api as api

    assert api is new_api

    def _boom(*_args, **_kwargs):
        raise RuntimeError("some internal SECRET_SHOULD_NOT_LEAK")

    monkeypatch.setattr(api.authority, "propose_update", _boom)
    monkeypatch.setenv("BEARER_TOKEN", "test-secret")
    r = c.post(
        "/config/runtime/propose",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "patch": {"thresholds": {"entry_conf_overall": 0.6}},
            "actor": "test",
            "expected_version": 0,
        },
    )
    assert r.status_code == 500
    assert "SECRET_SHOULD_NOT_LEAK" not in r.text
