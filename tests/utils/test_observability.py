from fastapi.testclient import TestClient

from core.server import app


def test_observability_dashboard():
    c = TestClient(app)
    r = c.get("/observability/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "counters" in data and isinstance(data["counters"], dict)
    assert "gauges" in data and isinstance(data["gauges"], dict)
    assert "events" in data and isinstance(data["events"], list)


def test_observability_dashboard_passthrough(monkeypatch):
    import core.server_info_api as info_api

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
