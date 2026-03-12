from __future__ import annotations

import pytest
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
    assert set(data.keys()) == {"result", "meta"}
    meta = data["meta"]
    assert isinstance(meta, dict)
    observability = meta.get("observability")
    assert isinstance(observability, dict)
    shadow_regime = observability.get("shadow_regime")
    assert isinstance(shadow_regime, dict)
    assert "authority_mode" in shadow_regime
    assert "authority_mode_source" in shadow_regime


def test_paper_whitelist_endpoint_returns_sorted_symbols():
    import core.server as srv

    c = TestClient(app)

    r = c.get("/paper/whitelist")

    assert r.status_code == 200
    assert r.json() == {"symbols": sorted(srv.TEST_SPOT_WHITELIST)}


def test_strategy_evaluate_delegates_with_current_defaults(monkeypatch):
    import core.server_strategy_api as route_mod

    captured = {}

    def _fake_evaluate_pipeline(candles, *, policy, configs, state):
        captured["candles"] = candles
        captured["policy"] = policy
        captured["configs"] = configs
        captured["state"] = state
        return {"action": "NONE"}, {"meta_source": "route_test"}

    monkeypatch.setattr(route_mod, "evaluate_pipeline", _fake_evaluate_pipeline)

    c = TestClient(app)
    payload = {
        "candles": {
            "open": [1, 2],
            "high": [2, 3],
            "low": [0.5, 1.5],
            "close": [1.5, 2.5],
            "volume": [10, 11],
        }
    }

    r = c.post("/strategy/evaluate", json=payload)

    assert r.status_code == 200
    assert r.json() == {
        "result": {"action": "NONE"},
        "meta": {"meta_source": "route_test"},
    }
    assert captured == {
        "candles": payload["candles"],
        "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
        "configs": {},
        "state": {},
    }


INVALID_CANDLES_RESPONSE = {
    "ok": False,
    "error": {
        "code": "INVALID_CANDLES",
        "message": (
            "candles must include non-empty equal-length " "open/high/low/close/volume arrays"
        ),
    },
}


@pytest.mark.parametrize(
    "payload",
    [
        {
            "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
            "configs": {},
            "state": {},
        },
        {
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
        },
        {
            "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
            "configs": {},
            "candles": "not-a-dict",
            "state": {},
        },
        {
            "policy": {"symbol": "tBTCUSD", "timeframe": "1m"},
            "configs": {},
            "candles": {
                "open": [1, 2],
                "high": [2, 3],
                "low": [0.5],
                "close": [1.5, 2.5],
                "volume": [10, 11],
            },
            "state": {},
        },
    ],
    ids=[
        "missing-candles",
        "empty-candle-lists",
        "invalid-candles-type",
        "mismatched-candle-lengths",
    ],
)
def test_evaluate_invalid_candles_variants_return_invalid_candles_error(payload):
    c = TestClient(app)

    r = c.post("/strategy/evaluate", json=payload)

    assert r.status_code == 200
    assert r.json() == INVALID_CANDLES_RESPONSE


def test_public_candles_endpoint_smoke():
    from core.server import public_candles as pc

    class DummyResp:
        def __init__(self):
            self._json = [[0, 1, 1.5, 2, 0.5, 10]]

        def raise_for_status(self):
            return None

        def json(self):
            return self._json

    def fake_get(_url, _params=None, _timeout=10):
        return DummyResp()

    class DummyEC:
        async def public_request(self, **_kwargs):
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


def test_auth_check_uses_helpers():
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


def test_paper_submit_monkeypatched():
    from core.server import paper_submit

    class DummyResp:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"status": "OK"}

    class DummyEC:
        async def signed_request(self, **_kwargs):
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


def test_paper_submit_invalid_symbol_returns_pinned_payload():
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
