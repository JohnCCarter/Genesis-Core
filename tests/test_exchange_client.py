import pytest

from core.io.bitfinex.exchange_client import get_exchange_client


@pytest.mark.asyncio
async def test_build_and_request_smoke(monkeypatch):
    ec = get_exchange_client()

    class DummyResponse:
        def __init__(self, status_code: int, text: str = "{}"):
            self.status_code = status_code
            self._text = text

        def raise_for_status(self):
            if self.status_code >= 400:
                import httpx

                raise httpx.HTTPStatusError("err", request=None, response=self)

        @property
        def text(self):
            return self._text

    async def dummy_post(url, headers=None, content=None):  # noqa: ARG001
        return DummyResponse(200, "{}")

    class DummyClient:
        async def aclose(self):  # noqa: D401
            return None

        post = staticmethod(dummy_post)

    # Patch http client getter
    from core.io.bitfinex import exchange_client as mod

    orig_get = mod._get_http_client
    mod._HTTP_CLIENT = DummyClient()
    try:
        r = await ec.signed_request(method="POST", endpoint="auth/r/alerts", body={})
        assert isinstance(r, DummyResponse)
        assert r.status_code == 200
    finally:
        mod._HTTP_CLIENT = None
        mod._get_http_client = orig_get


@pytest.mark.asyncio
async def test_aclose_http_client_resets_global_client() -> None:
    from core.io.bitfinex import exchange_client as mod

    closed = {"ok": False}

    class DummyClient:
        async def aclose(self):  # noqa: D401
            closed["ok"] = True

    orig = mod._HTTP_CLIENT
    try:
        mod._HTTP_CLIENT = DummyClient()  # type: ignore[assignment]
        await mod.aclose_http_client()
        assert closed["ok"] is True
        assert mod._HTTP_CLIENT is None
    finally:
        mod._HTTP_CLIENT = orig
