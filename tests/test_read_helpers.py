import pytest

from core.io.bitfinex import read_helpers as rh


@pytest.mark.asyncio
async def test_helpers_smoke():
    calls = []

    class DummyResp:
        def __init__(self):
            self.text = "[]"

        def json(self):
            return []

    from core.io.bitfinex import exchange_client as mod

    orig_get = mod.get_exchange_client

    class DummyEC:
        async def signed_request(self, **kwargs):
            calls.append(kwargs)
            return DummyResp()

    def fake_get_ec():
        return DummyEC()

    # Patch symbol i read_helpers så anropet använder DummyEC
    rh.get_exchange_client = fake_get_ec
    try:
        w = await rh.get_wallets()
        p = await rh.get_positions()
        o = await rh.get_orders()
        assert isinstance(w, list) and isinstance(p, list) and isinstance(o, list)
        assert [c.get("endpoint") for c in calls] == [
            "auth/r/wallets",
            "auth/r/positions",
            "auth/r/orders",
        ]
        assert all(c.get("method") == "POST" for c in calls)
        assert all(c.get("body") == {} for c in calls)
    finally:
        rh.get_exchange_client = orig_get


@pytest.mark.asyncio
async def test_helper_fallback_to_json_loads_text_payload():
    class DummyResp:
        def __init__(self):
            self.text = '{"ok": true}'

        def json(self):
            raise ValueError("no json method decode")

    from core.io.bitfinex import exchange_client as mod

    orig_get = mod.get_exchange_client

    class DummyEC:
        async def signed_request(self, **_kwargs):
            return DummyResp()

    def fake_get_ec():
        return DummyEC()

    rh.get_exchange_client = fake_get_ec
    try:
        payload = await rh.get_wallets()
        assert payload == {"ok": True}
    finally:
        rh.get_exchange_client = orig_get


@pytest.mark.asyncio
async def test_helper_fallback_to_raw_text_when_json_decode_fails():
    class DummyResp:
        def __init__(self):
            self.text = "not-json"

        def json(self):
            raise ValueError("no json method decode")

    from core.io.bitfinex import exchange_client as mod

    orig_get = mod.get_exchange_client

    class DummyEC:
        async def signed_request(self, **_kwargs):
            return DummyResp()

    def fake_get_ec():
        return DummyEC()

    rh.get_exchange_client = fake_get_ec
    try:
        payload = await rh.get_positions()
        assert payload == "not-json"
    finally:
        rh.get_exchange_client = orig_get
