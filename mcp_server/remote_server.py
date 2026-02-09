from __future__ import annotations

import hmac
import importlib
import json
import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Optional dependency. Keep type information when available without
    # requiring the package to exist in all dev environments.
    from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]  # noqa: F401
    from mcp.server.fastmcp.server import (  # type: ignore[import-not-found]
        TransportSecuritySettings,  # noqa: F401
    )


from .config import get_project_root, load_config
from .tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)


def _load_mcp_symbols() -> tuple[type[Any] | None, type[Any] | None]:
    """Best-effort import of MCP FastMCP + TransportSecuritySettings.

    This module is sometimes imported in environments where `mcp` isn't installed.
    We avoid hard imports to prevent editor/type-checker `reportMissingImports`.
    """

    try:
        fastmcp_mod = importlib.import_module("mcp.server.fastmcp")

        try:
            fastmcp_cls = fastmcp_mod.FastMCP
        except AttributeError:
            return None, None

        # TransportSecuritySettings has moved between MCP versions.
        try:
            tss_cls = fastmcp_mod.TransportSecuritySettings
        except AttributeError:
            tss_cls = None

        if tss_cls is None:
            server_mod = importlib.import_module("mcp.server.fastmcp.server")
            try:
                tss_cls = server_mod.TransportSecuritySettings
            except AttributeError:
                tss_cls = None

        return fastmcp_cls, tss_cls
    except Exception:
        return None, None


_FastMCP, _TransportSecuritySettings = _load_mcp_symbols()


class _MCPStub:
    """Fallback when `mcp` isn't installed.

    Allows this module to be imported (decorators become no-ops), but
    prevents starting the server without the required dependency.
    """

    def tool(self, *args: Any, **kwargs: Any):
        def _decorator(fn):
            return fn

        return _decorator

    def streamable_http_app(self, *args: Any, **kwargs: Any):
        raise RuntimeError(
            "FastMCP/streamable HTTP transport is unavailable in this environment. "
            "Use the SSE fallback (GET /sse + POST /mcp) or install a newer `mcp` version."
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

# Optional shared-secret guard for remote usage.
# Only enforced when a non-empty token is set.
REMOTE_TOKEN = (os.environ.get("GENESIS_MCP_REMOTE_TOKEN") or "").strip() or None

# Secure-by-default: remote requests must be authorized unless explicitly overridden.
# NOTE: If a token is configured, authorization is always required.
ALLOW_UNAUTH_REMOTE = (os.environ.get("GENESIS_MCP_REMOTE_ALLOW_UNAUTH") or "").strip() == "1"
REMOTE_AUTH_REQUIRED = REMOTE_TOKEN is not None or not ALLOW_UNAUTH_REMOTE


def _load_privacy_policy_text() -> str:
    """Load privacy policy text from docs, with a safe fallback."""

    # Canonical location (docs were reorganized into category subfolders).
    # Keep a legacy fallback for older checkouts.
    policy_paths = [
        get_project_root() / "docs" / "mcp" / "privacy-policy.md",
        get_project_root() / "docs" / "privacy-policy.md",
    ]

    for policy_path in policy_paths:
        try:
            return policy_path.read_text(encoding="utf-8")
        except Exception:
            continue

    return "Privacy policy not found."


_HAS_FASTMCP = _FastMCP is not None and _TransportSecuritySettings is not None

if _HAS_FASTMCP:
    assert _FastMCP is not None
    assert _TransportSecuritySettings is not None
    mcp = _FastMCP(
        "genesis-core",
        transport_security=_TransportSecuritySettings(
            allowed_hosts=["*"],
            enable_dns_rebinding_protection=False,
        ),
    )
else:
    mcp = _MCPStub()

# Reuse same config as stdio server
CONFIG = load_config()

# JSON-RPC 2.0 standard error codes.
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INTERNAL_ERROR = -32603

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
        return await get_git_status(CONFIG, apply_security_filters=True)


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


def _is_authorized_remote_request(*, authorization: str | None, token_header: str | None) -> bool:
    """Validate remote auth headers against REMOTE_TOKEN.

    Accepted forms:
    - Authorization: Bearer <token>
    - X-Genesis-MCP-Token: <token>

    If remote auth is disabled (explicit override), all requests are authorized.
    Otherwise, requests are authorized only when they present a valid token.
    """

    if not REMOTE_AUTH_REQUIRED:
        return True

    if REMOTE_TOKEN is None:
        return False

    presented: str | None = None
    if authorization:
        auth = authorization.strip()
        if auth.lower().startswith("bearer "):
            presented = auth[7:].strip()

    if not presented and token_header:
        presented = token_header.strip()

    if not presented:
        return False

    return hmac.compare_digest(presented, REMOTE_TOKEN)


def _wrap_sse_send_for_proxy(*, send, pad_bytes: bytes):
    """Wrap an ASGI `send` callable to reduce proxy buffering issues for SSE.

    Some reverse proxies (including certain tunnel/proxy stacks) may buffer very
    small initial chunks, causing clients to receive the SSE headers but not the
    first event (MCP's required `endpoint` event) promptly.

    We mitigate this by:
    1) Ensuring cache/transform buffering headers are present.
    2) Appending a harmless SSE comment padding to the first non-empty body chunk.

    The padding is appended (not prepended) so the first SSE event remains the
    `endpoint` event as required by legacy HTTP+SSE clients.
    """

    injected = False

    async def _send(message):
        nonlocal injected

        msg_type = message.get("type")

        if msg_type == "http.response.start":
            headers = list(message.get("headers") or [])

            def _has_header(name_lower: bytes) -> bool:
                return any(k.lower() == name_lower for k, _ in headers)

            # Avoid buffering/transforms on SSE streams.
            if not _has_header(b"cache-control"):
                headers.append((b"cache-control", b"no-cache, no-transform"))
            if not _has_header(b"x-accel-buffering"):
                headers.append((b"x-accel-buffering", b"no"))

            message = dict(message)
            message["headers"] = headers

        elif msg_type == "http.response.body" and not injected:
            body = message.get("body") or b""
            if body:
                message = dict(message)
                message["body"] = body + pad_bytes
                injected = True

        await send(message)

    return _send


def _build_sse_app():
    """Build an SSE-based MCP HTTP server for older `mcp` versions (e.g. 0.9.x).

    Endpoints:
    - GET /sse: establishes an SSE connection and yields the POST endpoint.
    - POST /mcp: client messages (requires session_id query param from /sse).
    - GET /healthz: health probe.

    Notes:
    - This is a compatibility path when `mcp.server.fastmcp` isn't available.
    - Tool surface is gated by SAFE_REMOTE_MODE / ULTRA_SAFE_REMOTE_MODE.
    """

    from urllib.parse import parse_qs
    from uuid import uuid4

    import mcp.types as mcp_types
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    from mcp.types import TextContent, Tool
    from starlette.middleware.cors import CORSMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, PlainTextResponse, Response

    logger = logging.getLogger(__name__)

    server = Server("genesis-core")

    def _safe_args_for_logging(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        safe: dict[str, Any] = dict(args or {})
        if tool_name in {"write_file", "execute_python"}:
            if "content" in safe:
                content = safe.get("content")
                safe["content"] = (
                    f"<redacted len={len(content) if isinstance(content, str) else 'n/a'}>"
                )
            if "code" in safe:
                code = safe.get("code")
                safe["code"] = f"<redacted len={len(code) if isinstance(code, str) else 'n/a'}>"
        return safe

    tools: list[Tool] = [
        Tool(
            name="ping",
            description="Minimal connectivity probe.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="search",
            description="Connector-compatible search tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "file_pattern": {"type": "string"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="fetch",
            description="Connector-compatible fetch tool (reads file content when allowed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "ref": {"type": "string"},
                },
            },
        ),
    ]

    if not ULTRA_SAFE_REMOTE_MODE:
        tools.extend(
            [
                Tool(
                    name="read_file",
                    description="Read file contents.",
                    inputSchema={
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                ),
                Tool(
                    name="list_directory",
                    description="List directory contents.",
                    inputSchema={
                        "type": "object",
                        "properties": {"directory_path": {"type": "string", "default": "."}},
                    },
                ),
                Tool(
                    name="get_project_structure",
                    description="Project tree (up to depth limits).",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="search_code",
                    description="Search code in project.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "file_pattern": {"type": "string"},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_git_status",
                    description="Git status summary.",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]
        )

    if not SAFE_REMOTE_MODE:
        tools.extend(
            [
                Tool(
                    name="write_file",
                    description="Write/update a file.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["file_path", "content"],
                    },
                ),
                Tool(
                    name="execute_python",
                    description="Execute Python code (high-privilege).",
                    inputSchema={
                        "type": "object",
                        "properties": {"code": {"type": "string"}},
                        "required": ["code"],
                    },
                ),
            ]
        )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            logger.info(f"Tool called: {name} args={_safe_args_for_logging(name, arguments)}")

            if name == "ping":
                result = {
                    "success": True,
                    "pong": True,
                    "safe_remote_mode": SAFE_REMOTE_MODE,
                    "ultra_safe_remote_mode": ULTRA_SAFE_REMOTE_MODE,
                }
            elif name == "search":
                result = await search(
                    query=str(arguments.get("query", "")),
                    file_pattern=arguments.get("file_pattern"),
                )
            elif name == "fetch":
                result = await fetch(id=arguments.get("id"), ref=arguments.get("ref"))
            elif ULTRA_SAFE_REMOTE_MODE:
                result = {"success": False, "error": "ULTRA_SAFE_REMOTE_MODE blocks this tool"}
            elif name == "read_file":
                result = await read_file(str(arguments.get("file_path", "")), CONFIG)
            elif name == "list_directory":
                result = await list_directory(str(arguments.get("directory_path", ".")), CONFIG)
            elif name == "get_project_structure":
                result = await get_project_structure(CONFIG)
            elif name == "search_code":
                result = await search_code(
                    str(arguments.get("query", "")),
                    arguments.get("file_pattern"),
                    CONFIG,
                )
            elif name == "get_git_status":
                result = await get_git_status(CONFIG, apply_security_filters=True)
            elif SAFE_REMOTE_MODE:
                result = {"success": False, "error": "SAFE_REMOTE_MODE blocks this tool"}
            elif name == "write_file":
                result = await write_file(
                    str(arguments.get("file_path", "")),
                    str(arguments.get("content", "")),
                    CONFIG,
                )
            elif name == "execute_python":
                result = await execute_python(str(arguments.get("code", "")), CONFIG)
            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [
                TextContent(
                    type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2)
                )
            ]

    transport = SseServerTransport(endpoint="/mcp")

    async def sse_asgi(scope, receive, send):
        # Some proxies buffer very small initial SSE bodies. Appending a modest padding
        # to the first chunk improves interoperability without altering semantics.
        pad = (":" + (" " * 2048) + "\n\n").encode("utf-8")
        send_wrapped = _wrap_sse_send_for_proxy(send=send, pad_bytes=pad)

        async with transport.connect_sse(scope, receive, send_wrapped) as (
            read_stream,
            write_stream,
        ):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    def _tool_list_payload() -> list[dict[str, Any]]:
        return [t.model_dump(by_alias=True, exclude_none=True) for t in tools]

    async def _handle_streamable_http_post(scope, receive, send) -> None:
        """Handle a single JSON-RPC message over HTTP POST (application/json).

        This is a pragmatic fallback for environments where long-lived SSE streams
        are unreliable through certain proxies/tunnels.
        """

        if REMOTE_AUTH_REQUIRED:
            # Avoid reading/consuming request body before auth.
            for k, v in scope.get("headers") or []:
                if k.lower() == b"authorization":
                    auth_header = v.decode("utf-8", errors="ignore")
                    break
            else:
                auth_header = None

            for k, v in scope.get("headers") or []:
                if k.lower() == b"x-genesis-mcp-token":
                    token_header = v.decode("utf-8", errors="ignore")
                    break
            else:
                token_header = None

            if not _is_authorized_remote_request(
                authorization=auth_header,
                token_header=token_header,
            ):
                await Response("Unauthorized", status_code=401)(scope, receive, send)
                return

        request = Request(scope, receive)
        try:
            payload = await request.json()
        except Exception:
            await Response("Invalid JSON", status_code=400)(scope, receive, send)
            return

        try:
            msg = mcp_types.JSONRPCMessage.model_validate(payload)
        except Exception:
            await Response("Invalid JSON-RPC message", status_code=400)(scope, receive, send)
            return

        root = msg.root

        # Notifications/responses: accept without a body.
        if isinstance(root, mcp_types.JSONRPCNotification) or isinstance(
            root, mcp_types.JSONRPCResponse
        ):
            await Response(status_code=202)(scope, receive, send)
            return

        if isinstance(root, mcp_types.JSONRPCError):
            await Response(status_code=202)(scope, receive, send)
            return

        if not isinstance(root, mcp_types.JSONRPCRequest):
            await Response("Unsupported message", status_code=400)(scope, receive, send)
            return

        method = root.method
        req_id = root.id
        params = root.params or {}

        def _err(code: int, message: str) -> dict[str, Any]:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

        try:
            if method == "initialize":
                # Generate a session id for clients that want to reuse it, but we do
                # not require it for subsequent calls in this fallback.
                session_id = request.headers.get("mcp-session-id") or uuid4().hex

                result = {
                    "protocolVersion": getattr(mcp_types, "LATEST_PROTOCOL_VERSION", "2024-11-05"),
                    "capabilities": server.create_initialization_options().capabilities.model_dump(
                        by_alias=True, exclude_none=True
                    ),
                    "serverInfo": {
                        "name": "genesis-core",
                        "version": "unknown",
                    },
                }

                return await JSONResponse(
                    {"jsonrpc": "2.0", "id": req_id, "result": result},
                    headers={"Mcp-Session-Id": session_id},
                )(scope, receive, send)

            if method == "tools/list":
                result = {"tools": _tool_list_payload()}
                return await JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})(
                    scope, receive, send
                )

            if method == "tools/call":
                tool_name = str(params.get("name", ""))
                arguments = params.get("arguments") or {}
                if not isinstance(arguments, dict):
                    return await JSONResponse(
                        _err(JSONRPC_INVALID_PARAMS, "arguments must be an object")
                    )(scope, receive, send)

                # Reuse the same tool dispatch as the legacy path.
                out = await call_tool(tool_name, arguments)
                parts: list[str] = []
                for item in out or []:
                    if isinstance(item, TextContent):
                        parts.append(item.text)
                    else:
                        try:
                            parts.append(
                                json.dumps(item.model_dump(by_alias=True, exclude_none=True))
                            )
                        except Exception:
                            parts.append(str(item))

                tool_text = "\n".join(parts)

                result = {"content": [{"type": "text", "text": tool_text}], "isError": False}
                return await JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})(
                    scope, receive, send
                )

            if method == "ping":
                return await JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {}})(
                    scope, receive, send
                )

            return await JSONResponse(_err(JSONRPC_METHOD_NOT_FOUND, f"Unknown method: {method}"))(
                scope, receive, send
            )
        except Exception as e:
            return await JSONResponse(_err(JSONRPC_INTERNAL_ERROR, str(e)))(scope, receive, send)

    healthz_resp = PlainTextResponse("OK")
    privacy_resp = PlainTextResponse(_load_privacy_policy_text())
    root_resp = PlainTextResponse(
        "Genesis-Core MCP server is running. Use POST /mcp (streamable HTTP) or GET /sse (legacy SSE)."
    )

    async def asgi_app(scope, receive, send):
        # Minimal ASGI router to avoid Starlette redirect_slashes and request/response
        # adaptation issues with MCP's ASGI callables.
        if scope.get("type") != "http":
            return

        path = str(scope.get("path") or "")
        normalized = path.rstrip("/")

        method = scope.get("method")

        if REMOTE_AUTH_REQUIRED and normalized not in {"/healthz", "/privacy-policy"}:
            auth_header = None
            token_header = None
            for k, v in scope.get("headers") or []:
                lk = k.lower()
                if lk == b"authorization":
                    auth_header = v.decode("utf-8", errors="ignore")
                elif lk == b"x-genesis-mcp-token":
                    token_header = v.decode("utf-8", errors="ignore")
            if not _is_authorized_remote_request(
                authorization=auth_header,
                token_header=token_header,
            ):
                await PlainTextResponse("Unauthorized", status_code=401)(scope, receive, send)
                return

        def _query_has_session_id() -> bool:
            # Legacy HTTP+SSE transport uses session_id in query string.
            qs = parse_qs((scope.get("query_string") or b"").decode("utf-8", errors="ignore"))
            return bool(qs.get("session_id"))

        async def _handle_mcp_post_alias() -> None:
            if _query_has_session_id():
                await transport.handle_post_message(scope, receive, send)
                return
            # Streamable HTTP fallback (single POST endpoint returning application/json).
            await _handle_streamable_http_post(scope, receive, send)
            return

        if normalized == "/sse":
            if method in {"GET", "HEAD"}:
                await sse_asgi(scope, receive, send)
                return
            if method == "POST":
                # Some clients misconfigure the base URL and post to /sse.
                await _handle_mcp_post_alias()
                return
            await PlainTextResponse("Method Not Allowed", status_code=405)(scope, receive, send)
            return

        if normalized == "/messages":
            if method != "POST":
                await PlainTextResponse("Method Not Allowed", status_code=405)(scope, receive, send)
                return
            await transport.handle_post_message(scope, receive, send)
            return

        if normalized == "/mcp":
            if method in {"GET", "HEAD"}:
                # Some clients/proxies probe the MCP endpoint with GET.
                # If the client explicitly requests SSE, provide the legacy SSE transport here.
                accept = b""
                for k, v in scope.get("headers") or []:
                    if k.lower() == b"accept":
                        accept = v
                        break

                if b"text/event-stream" in accept.lower():
                    await sse_asgi(scope, receive, send)
                    return

                await PlainTextResponse(
                    "MCP endpoint. Use POST /mcp (application/json). For legacy SSE use GET /sse.",
                    status_code=200,
                )(scope, receive, send)
                return

            if method != "POST":
                await PlainTextResponse("Method Not Allowed", status_code=405)(scope, receive, send)
                return

            await _handle_mcp_post_alias()
            return

        if normalized == "/healthz":
            await healthz_resp(scope, receive, send)
            return

        if normalized == "/privacy-policy":
            await privacy_resp(scope, receive, send)
            return

        if normalized == "":
            if method in {"GET", "HEAD"}:
                await root_resp(scope, receive, send)
                return
            if method == "POST":
                # Some clients treat the configured URL as the MCP endpoint directly.
                await _handle_mcp_post_alias()
                return
            await PlainTextResponse("Method Not Allowed", status_code=405)(scope, receive, send)
            return

        await PlainTextResponse("Not Found", status_code=404)(scope, receive, send)

    return CORSMiddleware(
        asgi_app,
        allow_origins=[
            "https://chat.openai.com",
            "https://chatgpt.com",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )


def _build_asgi_app():
    """Build the best available HTTP app for remote MCP.

    Prefer FastMCP streamable HTTP when available; otherwise fall back to SSE.
    """

    if not _HAS_FASTMCP:
        return _build_sse_app()

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import PlainTextResponse

    app = mcp.streamable_http_app()

    if REMOTE_AUTH_REQUIRED:

        class _RemoteTokenMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                if request.url.path in {"/healthz", "/privacy-policy"}:
                    return await call_next(request)

                if not _is_authorized_remote_request(
                    authorization=request.headers.get("authorization"),
                    token_header=request.headers.get("x-genesis-mcp-token"),
                ):
                    return PlainTextResponse("Unauthorized", status_code=401)

                return await call_next(request)

        app.add_middleware(_RemoteTokenMiddleware)

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

    mcp_route = next((r for r in app.routes if getattr(r, "path", None) == "/mcp"), None)
    mcp_endpoint = getattr(mcp_route, "endpoint", None)
    if mcp_endpoint is not None:
        app.add_route("/", mcp_endpoint, methods=["POST"])
        sse_alias_methods = ["POST"]
        try:
            route_methods = getattr(mcp_route, "methods", None)
            if route_methods and "GET" in route_methods:
                sse_alias_methods = ["GET", "POST"]
        except Exception:
            # Best-effort only; if we can't introspect methods, keep POST alias.
            pass

        app.add_route("/sse", mcp_endpoint, methods=sse_alias_methods)
        app.add_route("/sse/", mcp_endpoint, methods=sse_alias_methods)

    async def healthz(request):
        return PlainTextResponse("OK")

    app.add_route("/healthz", healthz, methods=["GET"])

    async def privacy_policy(request):
        return PlainTextResponse(_load_privacy_policy_text())

    app.add_route("/privacy-policy", privacy_policy, methods=["GET"])

    async def root(request):
        return PlainTextResponse("Genesis-Core MCP is running. Use POST /mcp")

    app.add_route("/", root, methods=["GET"])

    return app


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    # Enable debug logging for troubleshooting connection drops
    logging.basicConfig(level=logging.DEBUG)

    # Streamable HTTP transport (ChatGPT remote MCP)
    # Prefer a dedicated MCP port variable to avoid clashing with FastAPI's PORT.
    # Backward-compatible fallback: PORT (common convention in hosting platforms).
    port_raw = (
        os.environ.get("GENESIS_MCP_PORT") or os.environ.get("MCP_PORT") or os.environ.get("PORT")
    )
    try:
        port = int(port_raw) if port_raw else 8000
    except ValueError:
        port = 8000
    print(f"Starting MCP server on port {port}...")

    # Build best available transport app (FastMCP streamable HTTP or SSE fallback).
    app = _build_asgi_app()

    # Print routes for debugging (set GENESIS_MCP_DEBUG_ROUTES=1)
    if os.environ.get("GENESIS_MCP_DEBUG_ROUTES") == "1":
        print("Routes:")
        routes = getattr(app, "routes", None)
        if routes is None:
            # Middleware-wrapped apps (e.g. CORSMiddleware) may not expose `.routes`.
            print("  /sse  [GET]")
            print("  /mcp  [POST]")
            print("  /messages  [POST]")
            print("  /healthz  [GET]")
            print("  /  [GET]")
        else:
            for route in routes:
                methods = getattr(route, "methods", None)
                path = getattr(route, "path", "<unknown>")
                print(f"  {path} [{methods}]")

    uvicorn.run(
        app,
        port=port,
        host=os.environ.get("GENESIS_MCP_BIND_HOST", "127.0.0.1"),
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="debug",
        timeout_keep_alive=300,
    )
