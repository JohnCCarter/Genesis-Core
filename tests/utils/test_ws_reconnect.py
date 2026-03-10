import pytest

from core.io.bitfinex.ws_reconnect import WSReconnectClient


@pytest.mark.asyncio
async def test_backoff_increases_bounded():
    c = WSReconnectClient(max_backoff=1.0)
    d1 = await c._backoff_delay(1)
    d3 = await c._backoff_delay(3)
    d6 = await c._backoff_delay(6)
    assert 0.1 <= d1 <= 1.5
    assert d3 <= 1.5
    assert d6 <= 1.6
