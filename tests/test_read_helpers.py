import pytest

from core.io.bitfinex import read_helpers as rh


@pytest.mark.asyncio
async def test_helpers_smoke():
    class DummyResp:
        def __init__(self):
            self.text = "[]"

        def json(self):
            return []

    from core.io.bitfinex import exchange_client as mod

    orig_get = mod.get_exchange_client

    class DummyEC:
        async def signed_request(self, **_kwargs):
            return DummyResp()

    def fake_get_ec():
        return DummyEC()

    # Patch symbol i read_helpers så anropet använder DummyEC
    rh.get_exchange_client = fake_get_ec
    try:
        w = await rh.get_wallets()
        p = await rh.get_positions()
        assert isinstance(w, list) and isinstance(p, list)
    finally:
        rh.get_exchange_client = orig_get
