import pytest

from core.io.bitfinex.ws_public import one_message_ticker


@pytest.mark.asyncio
async def test_ws_public_timeout(monkeypatch):
    class DummyWS:
        async def recv(self):  # noqa: D401
            import asyncio

            await asyncio.sleep(0.2)
            return "{}"

        async def __aenter__(self):  # noqa: D401
            return self

        async def __aexit__(self, exc_type, exc, tb):  # noqa: D401, ARG002
            return False

        async def send(self, _):  # noqa: D401, ARG002
            return None

    import core.io.bitfinex.ws_public as mod

    orig_connect = mod.websockets.connect

    def fake_connect(*args, **kwargs):  # noqa: D401, ARG002
        return DummyWS()

    mod.websockets.connect = fake_connect  # type: ignore
    try:
        out = await one_message_ticker(timeout=0.1)
        assert out["ok"] is False and out["error"] == "timeout"
    finally:
        mod.websockets.connect = orig_connect  # type: ignore
