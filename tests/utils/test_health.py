from fastapi.testclient import TestClient

from core.server import app


def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_health_returns_exact_payload_from_shared_auth(monkeypatch):
    import core.server as srv

    c = TestClient(app)

    def _ok():
        return object(), "hash-123", 7

    monkeypatch.setattr(srv._AUTH, "get", _ok)

    r = c.get("/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok", "config_version": 7, "config_hash": "hash-123"}


def test_health_failure_logs_with_legacy_server_logger(monkeypatch, caplog):
    import core.server as srv

    c = TestClient(app)

    def _boom():
        raise RuntimeError("config broken")

    monkeypatch.setattr(srv._AUTH, "get", _boom)

    with caplog.at_level("WARNING", logger="core.server"):
        r = c.get("/health")

    assert r.status_code == 503
    assert any(
        record.name == "core.server"
        and "health_config_read_failed: config broken" in record.getMessage()
        for record in caplog.records
    )
