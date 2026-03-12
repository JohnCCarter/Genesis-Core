from fastapi.testclient import TestClient

from core.server import app


def test_info_module_alias_resolves_to_same_module_object():
    import sys

    import core.api.info as new_info_api
    import core.server_info_api as old_info_api

    assert old_info_api is new_info_api
    assert sys.modules["core.server_info_api"] is sys.modules["core.api.info"] is old_info_api


def test_observability_dashboard():
    c = TestClient(app)
    r = c.get("/observability/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "counters" in data and isinstance(data["counters"], dict)
    assert "gauges" in data and isinstance(data["gauges"], dict)
    assert "events" in data and isinstance(data["events"], list)


def test_observability_dashboard_passthrough(monkeypatch):
    import core.api.info as new_info_api
    import core.server_info_api as info_api

    assert info_api is new_info_api

    sentinel = {
        "counters": {"route_calls": 7},
        "gauges": {"latency_ms": 12.5},
        "events": [{"kind": "sentinel"}],
        "extra": {"source": "patched"},
    }

    monkeypatch.setattr(info_api, "get_dashboard", lambda: sentinel)

    c = TestClient(app)
    r = c.get("/observability/dashboard")

    assert r.status_code == 200
    assert r.json() == sentinel
