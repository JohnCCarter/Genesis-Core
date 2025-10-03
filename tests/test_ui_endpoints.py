from __future__ import annotations

from fastapi.testclient import TestClient
from core.server import app
from pathlib import Path


def test_ui_get_and_evaluate_post():
    c = TestClient(app)
    r = c.get("/ui")
    assert r.status_code == 200
    assert "Minimal test" in r.text

    payload = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
        "configs": {
            "features": {
                "percentiles": {"ema": [-10, 10], "rsi": [-10, 10]},
                "versions": {"feature_set": "v1"},
            },
            "thresholds": {
                "entry_conf_overall": 0.7,
                "regime_proba": {"balanced": 0.55},
            },
            "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
            "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
            "ev": {"R_default": 1.5},
        },
        "candles": {
            "open": [1, 2, 3, 4],
            "high": [2, 3, 4, 5],
            "low": [0.5, 1.5, 2.5, 3.5],
            "close": [1.5, 2.5, 3.5, 4.5],
            "volume": [10, 11, 12, 13],
        },
        "state": {},
    }
    r2 = c.post("/strategy/evaluate", json=payload)
    assert r2.status_code == 200
    data = r2.json()
    assert "result" in data and "meta" in data


def test_public_candles_endpoint_smoke(monkeypatch):
    from core.server import public_candles as pc

    class DummyResp:
        def __init__(self):
            self._json = [[0, 1, 1.5, 2, 0.5, 10]]

        def raise_for_status(self):
            return None

        def json(self):
            return self._json

    def fake_get(url, params=None, timeout=10):  # noqa: ARG001
        return DummyResp()

    import core.server as srv

    orig = srv.httpx.get
    srv.httpx.get = fake_get  # type: ignore
    try:
        out = pc(symbol="tBTCUSD", timeframe="1m", limit=1)
        assert set(out.keys()) == {"open", "high", "low", "close", "volume"}
        assert out["open"] and out["close"]
    finally:
        srv.httpx.get = orig  # type: ignore


def test_auth_check_uses_helpers(monkeypatch):
    from core.server import auth_check

    async def fake_wallets():
        return []

    async def fake_positions():
        return []

    import core.server as srv

    orig_wh = srv.bfx_read.get_wallets
    orig_ph = srv.bfx_read.get_positions
    srv.bfx_read.get_wallets = fake_wallets  # type: ignore
    srv.bfx_read.get_positions = fake_positions  # type: ignore
    try:
        import asyncio

        out = asyncio.get_event_loop().run_until_complete(auth_check())
        assert out.get("ok") is True
        assert out.get("wallets") == 0 and out.get("positions") == 0
    finally:
        srv.bfx_read.get_wallets = orig_wh  # type: ignore
        srv.bfx_read.get_positions = orig_ph  # type: ignore


def test_runtime_endpoints_exist():
    from core.server import app
    c = TestClient(app)
    r = c.get("/config/runtime")
    assert r.status_code == 200


def test_paper_submit_monkeypatched(monkeypatch):
    from core.server import paper_submit

    class DummyResp:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"status": "OK"}

    class DummyEC:
        async def signed_request(self, **kwargs):  # noqa: D401, ARG002
            return DummyResp()

    import core.server as srv

    orig_get = srv.get_exchange_client
    srv.get_exchange_client = lambda: DummyEC()  # type: ignore
    try:
        import asyncio

        out = asyncio.get_event_loop().run_until_complete(
            paper_submit({"symbol": "tBTCUSD", "side": "LONG", "size": 0.003, "type": "MARKET"})
        )
        assert out.get("ok") is True and out.get("exchange") == "bitfinex"
    finally:
        srv.get_exchange_client = orig_get  # type: ignore


def test_debug_auth_masked():
    from core.server import debug_auth

    out = debug_auth()
    assert "rest_api_key" in out
    m = out["rest_api_key"]
    assert set(m.keys()) >= {"present", "length", "suffix"}
