from __future__ import annotations

from fastapi.testclient import TestClient

from core.server import app


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


def test_evaluate_missing_candles_returns_invalid_candles_error():
    c = TestClient(app)
    payload = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
        "configs": {},
        "state": {},
    }

    r = c.post("/strategy/evaluate", json=payload)

    assert r.status_code == 200
    assert r.json() == {
        "ok": False,
        "error": {
            "code": "INVALID_CANDLES",
            "message": "candles must include non-empty equal-length open/high/low/close/volume arrays",
        },
    }


def test_evaluate_empty_candles_lists_returns_invalid_candles_error():
    c = TestClient(app)
    payload = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
        "configs": {},
        "candles": {
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
        },
        "state": {},
    }

    r = c.post("/strategy/evaluate", json=payload)

    assert r.status_code == 200
    assert r.json() == {
        "ok": False,
        "error": {
            "code": "INVALID_CANDLES",
            "message": "candles must include non-empty equal-length open/high/low/close/volume arrays",
        },
    }


def test_evaluate_invalid_candles_type_returns_invalid_candles_error():
    c = TestClient(app)
    payload = {
        "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
        "configs": {},
        "candles": "not-a-dict",
        "state": {},
    }

    r = c.post("/strategy/evaluate", json=payload)

    assert r.status_code == 200
    assert r.json() == {
        "ok": False,
        "error": {
            "code": "INVALID_CANDLES",
            "message": "candles must include non-empty equal-length open/high/low/close/volume arrays",
        },
    }


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

    class DummyEC:
        async def public_request(self, **kwargs):  # noqa: D401, ARG002
            return fake_get("unused")

    import asyncio

    import core.server as srv

    orig = srv.get_exchange_client
    srv.get_exchange_client = lambda: DummyEC()  # type: ignore
    try:
        out = asyncio.get_event_loop().run_until_complete(
            pc(symbol="tBTCUSD", timeframe="1m", limit=1)
        )
        assert set(out.keys()) == {"open", "high", "low", "close", "volume"}
        assert out["open"] and out["close"]
    finally:
        srv.get_exchange_client = orig  # type: ignore


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


def test_health_returns_503_when_config_read_fails(monkeypatch):
    import core.server as srv

    c = TestClient(app)

    def _boom():
        raise RuntimeError("config broken")

    monkeypatch.setattr(srv._AUTH, "get", _boom)

    r = c.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "error", "config_version": None, "config_hash": None}


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
            paper_submit(
                {
                    "symbol": "tTESTBTC:TESTUSD",
                    "side": "LONG",
                    "size": 0.003,
                    "type": "MARKET",
                }
            )
        )
        assert out.get("ok") is True and out.get("exchange") == "bitfinex"
        # Säkerhet: paper-trading ska acceptera giltig whitelist-symbol oförändrad.
        req = out.get("request") or {}
        assert req.get("symbol") == "tTESTBTC:TESTUSD"
    finally:
        srv.get_exchange_client = orig_get  # type: ignore


def test_paper_submit_invalid_symbol_returns_pinned_payload(monkeypatch):
    import asyncio

    from core.server import paper_submit

    out = asyncio.get_event_loop().run_until_complete(
        paper_submit({"symbol": "tBTCUSD", "side": "LONG", "size": 0.003, "type": "MARKET"})
    )

    assert out == {
        "ok": False,
        "error": "invalid_symbol",
        "requested_symbol": "tBTCUSD",
        "message": "symbol must be one of TEST_SPOT_WHITELIST",
    }


def test_debug_auth_masked():
    from core.server import debug_auth

    out = debug_auth()
    assert "rest_api_key" in out
    m = out["rest_api_key"]
    assert set(m.keys()) >= {"present", "length", "suffix"}
