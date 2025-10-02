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
