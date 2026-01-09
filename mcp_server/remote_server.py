from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

from .config import load_config
from .tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)

# -----------------------------------------------------------------------------
# MCP server (remote / ChatGPT connector)
# -----------------------------------------------------------------------------

# Some environments (including ChatGPT linking) may block execution when a remote MCP server
# exposes high-privilege tools (write/exec). Default to a read-only safe mode unless explicitly
# disabled.
SAFE_REMOTE_MODE = os.environ.get("GENESIS_MCP_REMOTE_SAFE", "1") != "0"

# Some environments appear to block *any* tool that can access local files, even read-only.
# This mode exposes only extremely low-risk tools (e.g. ping) and connector stubs.
ULTRA_SAFE_REMOTE_MODE = os.environ.get("GENESIS_MCP_REMOTE_ULTRA_SAFE", "0") == "1"

mcp = FastMCP(
    "genesis-core",
    transport_security=TransportSecuritySettings(
        allowed_hosts=["*"],
        enable_dns_rebinding_protection=False,
    ),
)

# Reuse same config as stdio server
CONFIG = load_config()

# -----------------------------------------------------------------------------
# Native Genesis-Core tools
# -----------------------------------------------------------------------------


@mcp.tool()
async def ping_tool(**kwargs: Any) -> dict[str, Any]:
    """Minimal, low-risk connectivity probe."""
    return {
        "success": True,
        "pong": True,
        "safe_remote_mode": SAFE_REMOTE_MODE,
        "ultra_safe_remote_mode": ULTRA_SAFE_REMOTE_MODE,
    }


if not ULTRA_SAFE_REMOTE_MODE:

    @mcp.tool()
    async def read_file_tool(file_path: str, **kwargs: Any) -> dict[str, Any]:
        return await read_file(file_path, CONFIG)


if not SAFE_REMOTE_MODE:

    @mcp.tool()
    async def write_file_tool(file_path: str, content: str, **kwargs: Any) -> dict[str, Any]:
        return await write_file(file_path, content, CONFIG)


if not ULTRA_SAFE_REMOTE_MODE:

    @mcp.tool()
    async def list_directory_tool(directory_path: str = ".", **kwargs: Any) -> dict[str, Any]:
        return await list_directory(directory_path, CONFIG)


if not SAFE_REMOTE_MODE:

    @mcp.tool()
    async def execute_python_tool(code: str, **kwargs: Any) -> dict[str, Any]:
        return await execute_python(code, CONFIG)


if not ULTRA_SAFE_REMOTE_MODE:

    @mcp.tool()
    async def get_project_structure_tool(**kwargs: Any) -> dict[str, Any]:
        return await get_project_structure(CONFIG)


if not ULTRA_SAFE_REMOTE_MODE:

    @mcp.tool()
    async def search_code_tool(
        query: str,
        file_pattern: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return await search_code(query, file_pattern, CONFIG)


if not ULTRA_SAFE_REMOTE_MODE:

    @mcp.tool()
    async def get_git_status_tool(**kwargs: Any) -> dict[str, Any]:
        return await get_git_status(CONFIG)


# -----------------------------------------------------------------------------
# Connector / Deep research compatibility tools
# (REQUIRED by ChatGPT "Ny app" / MCP linking flow)
# -----------------------------------------------------------------------------


@mcp.tool()
async def search(
    query: str,
    file_pattern: str | None = None,
    **kwargs: Any,  # tolerera extra fält från klienten
) -> dict[str, Any]:
    """
    Connector-compatible search tool.
    Returns: {"results": [{"id", "title", "url"}]}
    """
    if ULTRA_SAFE_REMOTE_MODE:
        # Intentionally return no results in ultra-safe mode.
        return {"results": []}

    res = await search_code(query, file_pattern, CONFIG)
    if not res.get("success"):
        return {"results": []}

    matches = res.get("matches") or res.get("results") or []
    results: list[dict[str, str]] = []

    for hit in matches:
        path = hit.get("file") or hit.get("path") or hit.get("file_path")
        if not path:
            continue

        results.append(
            {
                "id": path,
                "title": path,
                "url": f"file://{path}",
            }
        )

    return {"results": results}


@mcp.tool()
async def fetch(
    id: str | None = None,
    ref: str | None = None,
    **kwargs: Any,  # tolerera extra fält
) -> dict[str, Any]:
    """
    Connector-compatible fetch tool.
    Accepts both `id` and `ref`.
    """
    path = id or ref
    if not path:
        return {
            "id": "",
            "title": "",
            "text": "",
            "url": "",
            "metadata": {},
        }

    if ULTRA_SAFE_REMOTE_MODE:
        # Intentionally return empty content in ultra-safe mode.
        text = ""
    else:
        res = await read_file(path, CONFIG)
        text = res.get("content", "") if res.get("success") else ""

    return {
        "id": path,
        "title": path,
        "text": text,
        "url": f"file://{path}",
        "metadata": {},
    }


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import logging

    import uvicorn
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import PlainTextResponse

    # Enable debug logging for troubleshooting connection drops
    logging.basicConfig(level=logging.DEBUG)

    # Streamable HTTP transport (ChatGPT remote MCP)
    # Explicitly use PORT env var if set, otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting MCP server on port {port}...")

    # Use uvicorn directly to control port.
    # IMPORTANT: ChatGPT's "Connect" flow expects the Streamable HTTP transport.
    # FastMCP exposes this as a Starlette app with the MCP endpoint at `/mcp`.
    app = mcp.streamable_http_app()

    # If tool execution is performed by the ChatGPT web client, CORS must allow cross-origin
    # requests. Without this, the browser can block calls with generic “security status” errors.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://chat.openai.com",
            "https://chatgpt.com",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    # Some clients treat the configured URL as a base URL and append `/mcp` automatically,
    # while others call the configured URL directly. In addition, users may paste `/sse` by habit.
    # To be resilient, add aliases that point to the same Streamable HTTP handler.
    mcp_route = next((r for r in app.routes if getattr(r, "path", None) == "/mcp"), None)
    mcp_endpoint = getattr(mcp_route, "endpoint", None)
    if mcp_endpoint is not None:
        # Allow posting to the root.
        app.add_route("/", mcp_endpoint, methods=["POST"])
        # Allow posting to /sse (common misconfiguration) and /sse/.
        app.add_route("/sse", mcp_endpoint, methods=["POST"])
        app.add_route("/sse/", mcp_endpoint, methods=["POST"])

    async def healthz(request):
        return PlainTextResponse("OK")

    app.add_route("/healthz", healthz, methods=["GET"])

    async def root(request):
        return PlainTextResponse("Genesis-Core MCP is running. Use POST /mcp")

    app.add_route("/", root, methods=["GET"])

    # Print routes for debugging (set GENESIS_MCP_DEBUG_ROUTES=1)
    if os.environ.get("GENESIS_MCP_DEBUG_ROUTES") == "1":
        print("Routes:")
        for route in app.routes:
            methods = getattr(route, "methods", None)
            print(f"  {route.path} [{methods}]")

    uvicorn.run(
        app,
        port=port,
        host=os.environ.get("GENESIS_MCP_BIND_HOST", "127.0.0.1"),
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="debug",
        timeout_keep_alive=300,
    )
