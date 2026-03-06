import pytest

from core.io.bitfinex.ws_public import one_message_ticker


@pytest.mark.asyncio
async def test_ws_public_timeout():
    class DummyWS:
        async def recv(self):
            import asyncio

            await asyncio.sleep(0.2)
            return "{}"

        async def __aenter__(self):
            return self

        async def __aexit__(self, _exc_type, _exc, _tb):
            return False

        async def send(self, _):
            return None

    import core.io.bitfinex.ws_public as mod

    orig_connect = mod.websockets.connect

    def fake_connect(*_args, **_kwargs):
        return DummyWS()

    mod.websockets.connect = fake_connect  # type: ignore
    try:
        out = await one_message_ticker(timeout=0.1)
        assert out["ok"] is False and out["error"] == "timeout"
    finally:
        mod.websockets.connect = orig_connect  # type: ignore
