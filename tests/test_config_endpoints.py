from fastapi.testclient import TestClient

from core.config.validator import diff_config, validate_config
from core.server import app


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

    # runtime get
    r = c.get("/config/runtime")
    assert r.status_code == 200
    assert set(r.json().keys()) >= {"cfg", "version", "hash"}


def test_runtime_endpoints_do_not_leak_exceptions(monkeypatch):
    c = TestClient(app)

    # validate should not echo exception details
    r = c.post("/config/runtime/validate", json={"ev": {"R_default": "SECRET_SHOULD_NOT_LEAK"}})
    assert r.status_code == 200
    assert r.json().get("valid") is False
    assert "SECRET_SHOULD_NOT_LEAK" not in r.text

    # propose should not leak runtime exceptions
    import core.server_config_api as api

    def _boom(*args, **kwargs):  # noqa: ARG001
        raise RuntimeError("some internal SECRET_SHOULD_NOT_LEAK")

    monkeypatch.setattr(api.authority, "propose_update", _boom)
    monkeypatch.delenv("BEARER_TOKEN", raising=False)
    r = c.post(
        "/config/runtime/propose",
        json={
            "patch": {"thresholds": {"entry_conf_overall": 0.6}},
            "actor": "test",
            "expected_version": 0,
        },
    )
    assert r.status_code == 500
    assert "SECRET_SHOULD_NOT_LEAK" not in r.text
