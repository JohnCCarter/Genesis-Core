from __future__ import annotations

import importlib


def _reload_remote_server(monkeypatch, *, token: str | None, allow_unauth: bool | None):
    if token is None:
        monkeypatch.delenv("GENESIS_MCP_REMOTE_TOKEN", raising=False)
    else:
        monkeypatch.setenv("GENESIS_MCP_REMOTE_TOKEN", token)

    if allow_unauth is None:
        monkeypatch.delenv("GENESIS_MCP_REMOTE_ALLOW_UNAUTH", raising=False)
    else:
        monkeypatch.setenv("GENESIS_MCP_REMOTE_ALLOW_UNAUTH", "1" if allow_unauth else "0")

    import mcp_server.remote_server as remote_server

    return importlib.reload(remote_server)


def test_remote_auth_required_by_default(monkeypatch) -> None:
    remote_server = _reload_remote_server(monkeypatch, token=None, allow_unauth=None)
    assert remote_server.REMOTE_AUTH_REQUIRED is True
    assert (
        remote_server._is_authorized_remote_request(authorization=None, token_header=None) is False
    )

    # Restore module globals for other tests.
    _reload_remote_server(monkeypatch, token=None, allow_unauth=None)


def test_remote_auth_allows_explicit_unauth_override(monkeypatch) -> None:
    remote_server = _reload_remote_server(monkeypatch, token=None, allow_unauth=True)
    assert remote_server.REMOTE_AUTH_REQUIRED is False
    assert (
        remote_server._is_authorized_remote_request(authorization=None, token_header=None) is True
    )

    # Restore module globals for other tests.
    _reload_remote_server(monkeypatch, token=None, allow_unauth=None)


def test_remote_auth_accepts_bearer_and_token_header(monkeypatch) -> None:
    remote_server = _reload_remote_server(monkeypatch, token="test-secret", allow_unauth=True)

    # If a token is configured, auth must remain required even if allow_unauth is set.
    assert remote_server.REMOTE_AUTH_REQUIRED is True

    assert (
        remote_server._is_authorized_remote_request(authorization=None, token_header=None) is False
    )

    assert (
        remote_server._is_authorized_remote_request(
            authorization="Bearer test-secret",
            token_header=None,
        )
        is True
    )

    assert (
        remote_server._is_authorized_remote_request(
            authorization=None,
            token_header="test-secret",
        )
        is True
    )

    assert (
        remote_server._is_authorized_remote_request(
            authorization="Bearer wrong",
            token_header=None,
        )
        is False
    )

    # Restore module globals for other tests.
    _reload_remote_server(monkeypatch, token=None, allow_unauth=None)
