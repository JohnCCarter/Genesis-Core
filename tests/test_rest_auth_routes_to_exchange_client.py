from __future__ import annotations

import asyncio

import core.io.bitfinex.rest_auth as rest_auth


def test_sign_v2_delegates_to_exchange_client(monkeypatch) -> None:
    calls: list[tuple[str, dict]] = []

    class DummyEC:
        def _build_headers(self, endpoint: str, body: dict | None) -> dict[str, str]:  # noqa: D401
            calls.append((endpoint, dict(body or {})))
            return {"bfx-apikey": "k", "bfx-nonce": "1", "bfx-signature": "s"}

    monkeypatch.setattr(rest_auth, "get_exchange_client", lambda: DummyEC())

    out = rest_auth._sign_v2("auth/r/wallets", {"x": 1})
    assert out["bfx-apikey"] == "k"
    assert calls == [("auth/r/wallets", {"x": 1})]


def test_post_auth_routes_through_exchange_client_signed_request(monkeypatch) -> None:
    signed_calls: list[dict] = []

    class DummySettings:
        SYMBOL_MODE = "realistic"

    class DummyEC:
        async def signed_request(self, **kwargs):  # noqa: D401, ARG002
            signed_calls.append(dict(kwargs))
            return object()

    monkeypatch.setattr(rest_auth, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(rest_auth, "get_exchange_client", lambda: DummyEC())

    resp = asyncio.get_event_loop().run_until_complete(rest_auth.post_auth("auth/r/wallets", {}))
    assert resp is not None
    assert signed_calls == [
        {
            "method": "POST",
            "endpoint": "auth/r/wallets",
            "body": {},
            "timeout": 10,
        }
    ]
