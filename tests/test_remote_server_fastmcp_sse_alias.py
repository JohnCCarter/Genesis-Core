from __future__ import annotations

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

import mcp_server.remote_server as rs


def test_fastmcp_mode_supports_sse_alias_get_and_post(monkeypatch):
    """Guard against regressions if FastMCP becomes available.

    OpenAI docs/examples commonly use server URLs ending in `/sse`. In Streamable HTTP
    mode, the endpoint is expected to support both POST (JSON-RPC) and optional GET
    (SSE stream). We ensure our FastMCP path provides `/sse` as an alias to `/mcp`.
    """

    inner_app = Starlette()

    async def mcp_endpoint(request):  # type: ignore[no-untyped-def]
        return PlainTextResponse("OK")

    inner_app.add_route("/mcp", mcp_endpoint, methods=["GET", "POST"])

    class FakeMcp:
        def streamable_http_app(self):  # type: ignore[no-untyped-def]
            return inner_app

    monkeypatch.setattr(rs, "_HAS_FASTMCP", True, raising=False)
    monkeypatch.setattr(rs, "mcp", FakeMcp(), raising=False)
    monkeypatch.setattr(rs, "REMOTE_TOKEN", "test-token", raising=False)
    monkeypatch.setattr(rs, "REMOTE_AUTH_REQUIRED", True, raising=False)

    app = rs._build_asgi_app()
    client = TestClient(app)

    headers = {"X-Genesis-MCP-Token": "test-token"}
    assert client.get("/sse", headers=headers).status_code == 200
    assert client.post("/sse", json={"jsonrpc": "2.0"}, headers=headers).status_code == 200
