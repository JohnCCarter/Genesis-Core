import pytest

from core.io.bitfinex.exchange_client import get_exchange_client


@pytest.mark.asyncio
async def test_build_and_request_smoke():
    ec = get_exchange_client()

    class DummyResponse:
        def __init__(self, status_code: int, text: str = "{}", json_payload=None):
            self.status_code = status_code
            self._text = text
            self._json_payload = json_payload

        def raise_for_status(self):
            if self.status_code >= 400:
                import httpx

                raise httpx.HTTPStatusError("err", request=None, response=self)

        @property
        def text(self):
            return self._text

        def json(self):
            if self._json_payload is not None:
                return self._json_payload
            import json

            return json.loads(self._text)

    async def dummy_post(url, headers=None, content=None, timeout=None):
        _ = (url, headers, content, timeout)
        return DummyResponse(200, "{}")

    class DummyClient:
        async def aclose(self):
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
        async def aclose(self):
            closed["ok"] = True

    orig = mod._HTTP_CLIENT
    try:
        mod._HTTP_CLIENT = DummyClient()  # type: ignore[assignment]
        await mod.aclose_http_client()
        assert closed["ok"] is True
        assert mod._HTTP_CLIENT is None
    finally:
        mod._HTTP_CLIENT = orig


@pytest.mark.asyncio
async def test_signed_request_retries_nonce_error_with_structured_payload(
    monkeypatch,
) -> None:
    from core.io.bitfinex import exchange_client as mod

    nonce_values = iter(["100", "101"])
    bump_calls: list[str] = []
    attempts = {"n": 0}

    class DummyResponse:
        def __init__(self, status_code: int, text: str = "{}", json_payload=None):
            self.status_code = status_code
            self._text = text
            self._json_payload = json_payload

        def raise_for_status(self):
            if self.status_code >= 400:
                import httpx

                raise httpx.HTTPStatusError("err", request=None, response=self)

        @property
        def text(self):
            return self._text

        def json(self):
            if self._json_payload is not None:
                return self._json_payload
            import json

            return json.loads(self._text)

    async def dummy_post(url, headers=None, content=None, timeout=None):
        _ = (url, headers, content, timeout)
        attempts["n"] += 1
        if attempts["n"] == 1:
            return DummyResponse(
                400,
                text='["error",10114,"nonce: small"]',
                json_payload=["error", 10114, "nonce: small"],
            )
        return DummyResponse(200, text="{}", json_payload={})

    class DummyClient:
        async def aclose(self):
            return None

        post = staticmethod(dummy_post)

    async def _no_sleep(_attempt: int = 1) -> None:
        return None

    orig = mod._HTTP_CLIENT
    monkeypatch.setattr(mod, "get_nonce", lambda _key: next(nonce_values))
    monkeypatch.setattr(
        mod,
        "bump_nonce",
        lambda key: bump_calls.append(key) or "999",
    )
    try:
        mod._HTTP_CLIENT = DummyClient()
        ec = mod.ExchangeClient()
        monkeypatch.setattr(ec, "_sleep_jitter", _no_sleep)
        resp = await ec.signed_request(method="POST", endpoint="auth/r/orders", body={})
        assert resp.status_code == 200
        assert attempts["n"] == 2
        assert len(bump_calls) == 1
    finally:
        mod._HTTP_CLIENT = orig


@pytest.mark.asyncio
async def test_signed_request_retries_retryable_statuses_up_to_third_attempt(
    monkeypatch,
) -> None:
    from core.io.bitfinex import exchange_client as mod

    nonce_values = iter(["200", "201", "202"])
    attempts = {"n": 0}

    class DummyResponse:
        def __init__(self, status_code: int, text: str = "{}", json_payload=None):
            self.status_code = status_code
            self._text = text
            self._json_payload = json_payload

        def raise_for_status(self):
            if self.status_code >= 400:
                import httpx

                raise httpx.HTTPStatusError("err", request=None, response=self)

        @property
        def text(self):
            return self._text

        def json(self):
            if self._json_payload is not None:
                return self._json_payload
            import json

            return json.loads(self._text)

    async def dummy_post(url, headers=None, content=None, timeout=None):
        _ = (url, headers, content, timeout)
        attempts["n"] += 1
        if attempts["n"] == 1:
            return DummyResponse(
                429,
                text='{"message":"rate limit"}',
                json_payload={"message": "rate limit"},
            )
        if attempts["n"] == 2:
            return DummyResponse(
                500,
                text='{"message":"temporary"}',
                json_payload={"message": "temporary"},
            )
        return DummyResponse(200, text="{}", json_payload={})

    class DummyClient:
        async def aclose(self):
            return None

        post = staticmethod(dummy_post)

    async def _no_sleep(_attempt: int = 1) -> None:
        return None

    orig = mod._HTTP_CLIENT
    monkeypatch.setattr(mod, "get_nonce", lambda _key: next(nonce_values))
    try:
        mod._HTTP_CLIENT = DummyClient()
        ec = mod.ExchangeClient()
        monkeypatch.setattr(ec, "_sleep_jitter", _no_sleep)
        resp = await ec.signed_request(method="POST", endpoint="auth/r/orders", body={})
        assert resp.status_code == 200
        assert attempts["n"] == 3
    finally:
        mod._HTTP_CLIENT = orig
