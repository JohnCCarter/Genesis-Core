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
    good = {"dry_run": True, "position_cap_pct": 20}
    bad = {"dry_run": "yes"}

    r = c.post("/config/validate", json=good)
    assert r.status_code == 200 and r.json()["valid"] is True

    r = c.post("/config/validate", json=bad)
    assert r.status_code == 200 and r.json()["valid"] is False

    r = c.post("/config/diff", json={"old": {"x": 1}, "new": {"x": 2}})
    assert r.status_code == 200
    assert r.json()["changes"][0]["key"] == "x"
