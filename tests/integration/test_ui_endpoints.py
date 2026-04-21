from __future__ import annotations

import importlib

import httpx
import pytest
from fastapi.testclient import TestClient

from core.server import app


def test_ui_get_and_evaluate_post():
    import core.api.ui as ui_api
    import core.server as srv

    c = TestClient(app)
    r = c.get("/ui")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "Minimal test" in r.text
    assert srv.ui_page is ui_api.ui_page
    assert r.text == srv.ui_page() == ui_api.ui_page()

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
    assert "scpe_ri_v1" not in observability


def test_ui_strategy_evaluate_emits_ri_runtime_observability_only_with_opt_in():
    c = TestClient(app)

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
        "state": {"observability": {"scpe_ri_v1": True}},
    }

    response = c.post("/strategy/evaluate", json=payload)

    assert response.status_code == 200
    data = response.json()
    observability = data["meta"]["observability"]
    assert observability["scpe_ri_v1"] == {
        "family_tag": "ri",
        "lane": "runtime_observability",
        "observational_only": True,
        "decision_input": False,
        "enabled_via": "state.observability.scpe_ri_v1",
        "authority_mode": observability["shadow_regime"]["authority_mode"],
        "authority_mode_source": observability["shadow_regime"]["authority_mode_source"],
        "authoritative_regime": observability["shadow_regime"]["authority"],
        "shadow_regime": observability["shadow_regime"]["shadow"],
        "regime_mismatch": observability["shadow_regime"]["mismatch"],
    }


def test_ui_route_server_and_canonical_identity():
    import core.api.ui as ui_api
    import core.server as srv

    assert srv.ui_page is ui_api.ui_page
    assert srv.ui_router is ui_api.router
    ui_routes = [route for route in srv.app.routes if getattr(route, "path", None) == "/ui"]
    assert len(ui_routes) == 1


@pytest.mark.parametrize(
    "module_name",
    [
        "core.server_account_api",
        "core.server_config_api",
        "core.server_info_api",
        "core.server_models_api",
        "core.server_paper_api",
        "core.server_public_api",
        "core.server_status_api",
        "core.server_strategy_api",
        "core.server_ui_api",
    ],
)
def test_legacy_server_api_modules_are_not_importable_after_retirement(module_name):
    import sys

    sys.modules.pop(module_name, None)

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


def test_paper_whitelist_endpoint_returns_sorted_symbols():
    import core.server as srv

    c = TestClient(app)

    r = c.get("/paper/whitelist")

    assert r.status_code == 200
    assert r.json() == {"symbols": sorted(srv.TEST_SPOT_WHITELIST)}


def test_strategy_evaluate_delegates_with_current_defaults(monkeypatch):
    import core.api.strategy as route_mod

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
            calls.append(_kwargs)
            return fake_get("unused")

    import asyncio

    import core.api.public as public_api
    import core.server as srv

    calls = []
    orig = srv.get_exchange_client
    original_cache = dict(srv._CANDLES_CACHE)
    srv.get_exchange_client = lambda: DummyEC()  # type: ignore
    try:
        srv._CANDLES_CACHE.clear()
        c = TestClient(app)
        out = asyncio.get_event_loop().run_until_complete(
            pc(symbol="tBTCUSD", timeframe="1m", limit=1001)
        )
        route = c.get(
            "/public/candles",
            params={"symbol": "tBTCUSD", "timeframe": "1m", "limit": 1001},
        )

        assert route.status_code == 200
        assert out == route.json()
        assert set(out.keys()) == {"open", "high", "low", "close", "volume"}
        assert out["open"] and out["close"]
        assert srv.public_candles is public_api.public_candles
        assert srv.public_router is public_api.router
        assert srv._CANDLES_CACHE is public_api._CANDLES_CACHE
        assert srv._CANDLES_TTL == public_api._CANDLES_TTL
        assert "tBTCUSD:1m:1001" in srv._CANDLES_CACHE
        assert len(calls) == 1
        assert calls[0]["params"] == {"limit": 1000, "sort": 1}
        candle_routes = [
            route for route in srv.app.routes if getattr(route, "path", None) == "/public/candles"
        ]
        assert len(candle_routes) == 1
    finally:
        srv._CANDLES_CACHE.clear()
        srv._CANDLES_CACHE.update(original_cache)
        srv.get_exchange_client = orig  # type: ignore


def test_auth_check_uses_helpers():
    from core.server import auth_check

    async def fake_wallets():
        return []

    async def fake_positions():
        return []

    import core.api.account as account_api
    import core.server as srv

    orig_wh = srv.bfx_read.get_wallets
    orig_ph = srv.bfx_read.get_positions
    srv.bfx_read.get_wallets = fake_wallets  # type: ignore
    srv.bfx_read.get_positions = fake_positions  # type: ignore
    try:
        import asyncio

        c = TestClient(app)

        direct_json = asyncio.get_event_loop().run_until_complete(auth_check())
        route_json = c.get("/auth/check").json()

        assert direct_json == route_json == {"ok": True, "wallets": 0, "positions": 0}
        assert srv.auth_check is account_api.auth_check
    finally:
        srv.bfx_read.get_wallets = orig_wh  # type: ignore
        srv.bfx_read.get_positions = orig_ph  # type: ignore


def test_account_route_and_cache_use_canonical_module():
    import core.api.account as account_api
    import core.server as srv

    assert srv.auth_check is account_api.auth_check
    assert srv.account_wallets is account_api.account_wallets
    assert srv.account_positions is account_api.account_positions
    assert srv.account_orders is account_api.account_orders
    assert srv.account_router is account_api.router
    assert srv._ACCOUNT_CACHE is account_api._ACCOUNT_CACHE
    assert srv._ACCOUNT_TTL == account_api._ACCOUNT_TTL


def test_runtime_endpoints_exist():
    from core.server import app

    c = TestClient(app)
    r = c.get("/config/runtime")
    assert r.status_code == 200


def test_models_reload_route_and_delegation_parity(monkeypatch):
    import core.api.models as models_api
    import core.server as srv

    calls = []

    def _fake_clear_cache(self):
        calls.append("clear")

    monkeypatch.setattr(models_api.ModelRegistry, "clear_cache", _fake_clear_cache)

    c = TestClient(app)

    route_response = c.post("/models/reload")
    direct_json = srv.reload_models()

    assert route_response.status_code == 200
    assert srv.reload_models is models_api.reload_models
    assert route_response.json() == direct_json == {"ok": True, "message": "Model cache cleared"}
    assert calls == ["clear", "clear"]


def test_health_returns_503_when_config_read_fails(monkeypatch):
    import core.server as srv

    c = TestClient(app)

    def _boom():
        raise RuntimeError("config broken")

    monkeypatch.setattr(srv._AUTH, "get", _boom)

    r = c.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "error", "config_version": None, "config_hash": None}


def test_health_shared_auth_uses_canonical_module():
    import core.api.status as status_api
    import core.server as srv

    assert srv._AUTH is status_api._AUTH


def test_paper_submit_monkeypatched():
    from core.server import paper_submit

    class DummyResp:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"status": "OK"}

    class DummyEC:
        async def signed_request(self, **_kwargs):
            calls.append(_kwargs)
            return DummyResp()

    import core.api.paper as paper_api
    import core.server as srv

    calls = []
    orig_get = srv.get_exchange_client
    srv.get_exchange_client = lambda: DummyEC()  # type: ignore
    try:
        import asyncio

        c = TestClient(app)
        payload = {
            "symbol": "tTESTBTC:TESTUSD",
            "side": "LONG",
            "size": 0.003,
            "type": "MARKET",
        }

        out = asyncio.get_event_loop().run_until_complete(paper_submit(payload))
        route = c.post("/paper/submit", json=payload)

        assert route.status_code == 200
        assert out == route.json()
        assert out.get("ok") is True and out.get("exchange") == "bitfinex"
        # Säkerhet: paper-trading ska acceptera giltig whitelist-symbol oförändrad.
        req = out.get("request") or {}
        assert req.get("symbol") == "tTESTBTC:TESTUSD"
        assert srv.paper_submit is paper_api.paper_submit
        assert srv.paper_router is paper_api.router
        paper_submit_routes = [
            route for route in srv.app.routes if getattr(route, "path", None) == "/paper/submit"
        ]
        assert len(paper_submit_routes) == 1
        assert calls == [
            {
                "method": "POST",
                "endpoint": "auth/w/order/submit",
                "body": req,
            },
            {
                "method": "POST",
                "endpoint": "auth/w/order/submit",
                "body": req,
            },
        ]
    finally:
        srv.get_exchange_client = orig_get  # type: ignore


def test_paper_estimate_route_and_canonical_module_parity(monkeypatch):
    import asyncio

    import core.api.paper as paper_api
    import core.server as srv

    class DummySettings:
        BITFINEX_API_KEY = "key"  # pragma: allowlist secret
        BITFINEX_API_SECRET = "secret"  # pragma: allowlist secret

    class DummyResp:
        def json(self):
            return [0, 0, 0, 0, 0, 0, 50.0]

    class DummyEC:
        async def public_request(self, **kwargs):
            calls.append(kwargs)
            return DummyResp()

    async def fake_wallets():
        return [
            ["exchange", "USD", 0, 0, 250.0],
            ["exchange", "ETH", 0, 0, 7.0],
        ]

    calls = []
    monkeypatch.setattr(srv, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(srv.bfx_read, "get_wallets", fake_wallets)
    monkeypatch.setattr(srv, "get_exchange_client", lambda: DummyEC())
    monkeypatch.setattr(srv, "MIN_ORDER_SIZE", {"tTESTBTC:TESTUSD": 2.5})
    monkeypatch.setattr(srv, "MIN_ORDER_MARGIN", 0.2)
    monkeypatch.setattr(srv, "_real_from_test", lambda _sym: "tFAKEUSD")
    monkeypatch.setattr(srv, "_base_ccy_from_test", lambda _sym: "ETH")

    c = TestClient(app)
    direct_json = asyncio.get_event_loop().run_until_complete(srv.paper_estimate(symbol="tNOPE"))
    route = c.get("/paper/estimate", params={"symbol": "tNOPE"})

    assert route.status_code == 200
    assert srv.paper_estimate is paper_api.paper_estimate
    assert srv.paper_router is paper_api.router
    assert direct_json == route.json()
    assert direct_json == {
        "symbol": "tTESTBTC:TESTUSD",
        "required_min": 2.5,
        "min_with_margin": 3.0,
        "usd_available": 250.0,
        "base_available": 7.0,
        "last_price": 50.0,
        "est_max_size": 5.0,
    }
    assert calls == [
        {
            "method": "GET",
            "endpoint": "ticker/tFAKEUSD",
            "timeout": 5,
        },
        {
            "method": "GET",
            "endpoint": "ticker/tFAKEUSD",
            "timeout": 5,
        },
    ]
    paper_estimate_routes = [
        route for route in srv.app.routes if getattr(route, "path", None) == "/paper/estimate"
    ]
    assert len(paper_estimate_routes) == 1


def test_paper_estimate_without_credentials_skips_wallet_lookup(monkeypatch):
    import asyncio

    import core.server as srv

    class DummySettings:
        BITFINEX_API_KEY = ""  # pragma: allowlist secret
        BITFINEX_API_SECRET = ""  # pragma: allowlist secret

    class DummyResp:
        def json(self):
            return [0, 0, 0, 0, 0, 0, 20.0]

    class DummyEC:
        async def public_request(self, **_kwargs):
            return DummyResp()

    async def unexpected_wallets():
        raise AssertionError("wallet lookup should be skipped without credentials")

    monkeypatch.setattr(srv, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(srv.bfx_read, "get_wallets", unexpected_wallets)
    monkeypatch.setattr(srv, "get_exchange_client", lambda: DummyEC())

    direct_json = asyncio.get_event_loop().run_until_complete(
        srv.paper_estimate(symbol="tTESTBTC:TESTUSD")
    )

    assert direct_json["symbol"] == "tTESTBTC:TESTUSD"
    assert direct_json["required_min"] == 0.001
    assert direct_json["min_with_margin"] == pytest.approx(0.00105)
    assert direct_json["usd_available"] is None
    assert direct_json["base_available"] is None
    assert direct_json["last_price"] == 20.0
    assert direct_json["est_max_size"] is None


def test_paper_submit_invalid_symbol_returns_pinned_payload():
    import asyncio

    from core.server import app as srv_app
    from core.server import paper_submit

    c = TestClient(srv_app)
    payload = {"symbol": "tBTCUSD", "side": "LONG", "size": 0.003, "type": "MARKET"}

    out = asyncio.get_event_loop().run_until_complete(paper_submit(payload))
    route = c.post("/paper/submit", json=payload)

    expected = {
        "ok": False,
        "error": "invalid_symbol",
        "requested_symbol": "tBTCUSD",
        "message": "symbol must be one of TEST_SPOT_WHITELIST",
    }
    assert out == route.json() == expected


@pytest.mark.parametrize(
    "payload",
    [
        {"symbol": "tTESTBTC:TESTUSD", "side": "NONE", "size": 1.0, "type": "MARKET"},
        {"symbol": "tTESTBTC:TESTUSD", "side": "LONG", "size": 0.0, "type": "MARKET"},
    ],
    ids=["invalid-side", "invalid-size"],
)
def test_paper_submit_invalid_action_or_size_route_parity(payload):
    import asyncio

    import core.server as srv

    c = TestClient(app)
    direct_json = asyncio.get_event_loop().run_until_complete(srv.paper_submit(payload))
    route = c.post("/paper/submit", json=payload)

    assert route.status_code == 200
    assert direct_json == route.json() == {"ok": False, "error": "invalid_action_or_size"}


def test_paper_submit_wallet_cap_uses_shared_helpers(monkeypatch):
    import asyncio

    import core.server as srv

    class DummySettings:
        WALLET_CAP_ENABLED = 1
        BITFINEX_API_KEY = "key"  # pragma: allowlist secret
        BITFINEX_API_SECRET = "secret"  # pragma: allowlist secret

    class DummyResp:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload

        def json(self):
            return self._payload

    class DummyEC:
        async def public_request(self, **kwargs):
            ticker_calls.append(kwargs)
            return DummyResp([0, 0, 0, 0, 0, 0, 5.0])

        async def signed_request(self, **kwargs):
            signed_calls.append(kwargs)
            return DummyResp({"status": "OK"})

    async def fake_wallets():
        return [
            ["exchange", "USD", 0, 0, 20.0],
            ["exchange", "ETH", 0, 0, 3.0],
        ]

    ticker_calls = []
    signed_calls = []
    monkeypatch.setattr(srv, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(srv.bfx_read, "get_wallets", fake_wallets)
    monkeypatch.setattr(srv, "get_exchange_client", lambda: DummyEC())
    monkeypatch.setattr(srv, "MIN_ORDER_SIZE", {"tTESTBTC:TESTUSD": 1.0})
    monkeypatch.setattr(srv, "MIN_ORDER_MARGIN", 0.1)
    monkeypatch.setattr(srv, "_real_from_test", lambda _sym: "tFAKEUSD")
    monkeypatch.setattr(srv, "_base_ccy_from_test", lambda _sym: "ETH")

    long_out = asyncio.get_event_loop().run_until_complete(
        srv.paper_submit(
            {
                "symbol": "tTESTBTC:TESTUSD",
                "side": "LONG",
                "size": 10.0,
                "type": "MARKET",
            }
        )
    )
    short_out = asyncio.get_event_loop().run_until_complete(
        srv.paper_submit(
            {
                "symbol": "tTESTBTC:TESTUSD",
                "side": "SHORT",
                "size": 10.0,
                "type": "MARKET",
            }
        )
    )

    assert long_out["ok"] is True
    assert long_out["meta"]["wallet_clamped"] is True
    assert long_out["meta"]["size_after"] == 4.0
    assert short_out["ok"] is True
    assert short_out["meta"]["wallet_clamped"] is True
    assert short_out["meta"]["size_after"] == 3.0
    assert ticker_calls == [
        {
            "method": "GET",
            "endpoint": "ticker/tFAKEUSD",
            "timeout": 5,
        }
    ]
    assert signed_calls[0]["body"]["amount"] == "4.0"
    assert signed_calls[1]["body"]["amount"] == "-3.0"


def test_paper_submit_http_status_error_shape(monkeypatch):
    import asyncio

    import core.server as srv

    class DummyEC:
        async def signed_request(self, **_kwargs):
            request = httpx.Request("POST", "https://example.test/auth/w/order/submit")
            response = httpx.Response(429, request=request, text="rate limited")
            raise httpx.HTTPStatusError("boom", request=request, response=response)

    monkeypatch.setattr(srv, "get_exchange_client", lambda: DummyEC())

    c = TestClient(app)
    payload = {"symbol": "tTESTBTC:TESTUSD", "side": "LONG", "size": 1.0, "type": "MARKET"}
    direct_json = asyncio.get_event_loop().run_until_complete(srv.paper_submit(payload))
    route_json = c.post("/paper/submit", json=payload).json()

    for data in (direct_json, route_json):
        assert data["ok"] is False
        assert data["error"] == "bitfinex_http_error"
        assert data["status"] == 429
        assert isinstance(data["error_id"], str)
        assert len(data["error_id"]) == 12


def test_paper_submit_internal_error_shape(monkeypatch):
    import asyncio

    import core.server as srv

    class DummyEC:
        async def signed_request(self, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(srv, "get_exchange_client", lambda: DummyEC())

    c = TestClient(app)
    payload = {"symbol": "tTESTBTC:TESTUSD", "side": "LONG", "size": 1.0, "type": "MARKET"}
    direct_json = asyncio.get_event_loop().run_until_complete(srv.paper_submit(payload))
    route_json = c.post("/paper/submit", json=payload).json()

    for data in (direct_json, route_json):
        assert data["ok"] is False
        assert data["error"] == "internal_error"
        assert isinstance(data["error_id"], str)
        assert len(data["error_id"]) == 12
        assert "status" not in data


def test_debug_auth_masked():
    from core.server import debug_auth

    out = debug_auth()
    assert "rest_api_key" in out
    m = out["rest_api_key"]
    assert set(m.keys()) >= {"present", "length", "suffix"}


def test_debug_auth_route_matches_direct_function(monkeypatch):
    import core.api.status as status_api
    import core.server as srv

    class DummySettings:
        BITFINEX_API_KEY = "abcd1234"  # pragma: allowlist secret

    monkeypatch.setattr(status_api, "get_settings", lambda: DummySettings())

    c = TestClient(app)

    route_json = c.get("/debug/auth").json()
    direct_json = srv.debug_auth()

    assert (
        route_json
        == direct_json
        == {"rest_api_key": {"present": True, "length": 8, "suffix": "1234"}}
    )
