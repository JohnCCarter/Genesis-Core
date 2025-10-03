from core.config.validator import validate_config, diff_config
from fastapi.testclient import TestClient
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
