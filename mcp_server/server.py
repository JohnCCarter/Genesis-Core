"""
Genesis-Core MCP Server

Main server implementation using the Model Context Protocol.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, cast

from pydantic import AnyUrl

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, Tool
except Exception:  # pragma: no cover - fallback for environments without mcp installed

    @dataclass
    class Tool:
        name: str
        description: str
        inputSchema: dict[str, Any]

    @dataclass
    class Resource:
        uri: Any
        name: str
        description: str
        mimeType: str

    @dataclass
    class TextContent:
        type: str
        text: str

    class Server:  # type: ignore[override]
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def list_tools(self):
            def _decorator(fn):
                return fn

            return _decorator

        def call_tool(self):
            def _decorator(fn):
                return fn

            return _decorator

        def list_resources(self):
            def _decorator(fn):
                return fn

            return _decorator

        def read_resource(self):
            def _decorator(fn):
                return fn

            return _decorator

        def create_initialization_options(self) -> dict[str, Any]:
            return {}

        async def run(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("MCP SDK is not installed")

    @asynccontextmanager
    async def stdio_server():
        raise RuntimeError("MCP SDK is not installed")
        yield (None, None)


from mcp_server.config import load_config
from mcp_server.resources import (
    get_config_resource,
    get_documentation,
    get_git_status_resource,
    get_structure_resource,
)
from mcp_server.tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)
from mcp_server.trading_tools import (
    append_decision_log,
    read_account_state,
    read_candles,
    read_decision_log,
    run_strategy,
    submit_paper_order,
)
from mcp_server.utils import safe_args_for_logging, setup_logging

logger = logging.getLogger(__name__)

# Global configuration
config = load_config()

# Initialize MCP server
app = Server("genesis-core")


def _ensure_utf8_stdio() -> None:
    """Best-effort: ensure stdio streams can emit non-ASCII on Windows.

    VS Code (and some host processes) may start Python with a legacy console encoding
    (e.g. cp1252). The MCP stdio transport writes JSON responses to stdout; if that JSON
    contains non-ASCII (docs, box-drawing tree glyphs, etc.), writing can crash with
    UnicodeEncodeError and bring the server down.

    We defensively reconfigure stdout/stderr to UTF-8 when possible.
    """

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue

        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue

        try:
            reconfigure(encoding="utf-8", errors="strict")
        except Exception:
            # If the host/capture layer does not support reconfigure, avoid crashing.
            continue


# Tool definitions
TOOLS = [
    Tool(
        name="read_file",
        description="Read the contents of a file in the project. Returns the file content as a string.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (relative to project root)",
                }
            },
            "required": ["file_path"],
        },
    ),
    Tool(
        name="write_file",
        description="Write or update a file in the project. Creates parent directories if needed.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write (relative to project root)",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["file_path", "content"],
        },
    ),
    Tool(
        name="list_directory",
        description="List files and directories in the specified path. Returns file/directory names with metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list (default: current directory)",
                    "default": ".",
                }
            },
        },
    ),
    Tool(
        name="execute_python",
        description="Execute Python code in a safe environment with timeout. Use for testing code snippets or running analyses.",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                }
            },
            "required": ["code"],
        },
    ),
    Tool(
        name="get_project_structure",
        description="Get the project structure as a tree. Shows directory hierarchy up to 5 levels deep.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="search_code",
        description="Search for code in the project. Returns matching lines with file paths and line numbers.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Optional file pattern to filter (e.g., '*.py', '*.md')",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_git_status",
        description="Get Git status information including current branch, modified files, staged files, and untracked files.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="read_account_state",
        description="Read Bitfinex wallets, positions, and open orders. Returns empty lists if API keys are missing.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="read_candles",
        description="Fetch normalised OHLCV candles from Bitfinex public API. Allowed timeframes: 1m,5m,15m,30m,1h,3h,6h,12h,1D,1W,14D,1M.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "default": "tBTCUSD"},
                "timeframe": {"type": "string", "default": "1h"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 300},
            },
            "required": ["symbol", "timeframe"],
        },
    ),
    Tool(
        name="run_strategy",
        description="Run the nested top-down Fibonacci strategy. Pulls HTF+LTF candles (or accepts pre-fetched), produces a deterministic decision record, and appends to the audit log when persist=true.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "trend_tf": {"type": "string", "default": "6h"},
                "entry_tf": {"type": "string", "default": "1h"},
                "params": {"type": "object"},
                "risk_state": {"type": "object"},
                "risk_pct": {"type": "number", "default": 0.01},
                "persist": {"type": "boolean", "default": True},
                "candle_limit": {"type": "integer", "minimum": 60, "maximum": 1000, "default": 300},
                "htf_candles": {"type": "object"},
                "ltf_candles": {"type": "object"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="submit_paper_order",
        description="Submit a paper order to Bitfinex. When decision_id is supplied, refuses to submit if that decision's risk_check.passed=false unless force=true.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "side": {"type": "string", "enum": ["LONG", "SHORT"]},
                "size": {"type": "number"},
                "type": {"type": "string", "enum": ["MARKET", "LIMIT"], "default": "MARKET"},
                "price": {"type": "number"},
                "decision_id": {"type": "string"},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["symbol", "side", "size"],
        },
    ),
    Tool(
        name="read_decision_log",
        description="Read recent agent decision records from logs/agent_decisions.jsonl, optionally filtered by symbol or decision_id.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "decision_id": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 50},
            },
        },
    ),
    Tool(
        name="append_decision_log",
        description="Append a DecisionRecord-shaped dict to logs/agent_decisions.jsonl (used for human review markers).",
        inputSchema={
            "type": "object",
            "properties": {"record": {"type": "object"}},
            "required": ["record"],
        },
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls from the MCP client.

    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool

    Returns:
        List of TextContent with the tool result
    """
    try:
        logger.info(f"Tool called: {name} with arguments: {safe_args_for_logging(name, arguments)}")

        # Route to appropriate tool handler
        if name == "read_file":
            result = await read_file(arguments.get("file_path", ""), config)
        elif name == "write_file":
            result = await write_file(
                arguments.get("file_path", ""), arguments.get("content", ""), config
            )
        elif name == "list_directory":
            result = await list_directory(arguments.get("directory_path", "."), config)
        elif name == "execute_python":
            result = await execute_python(arguments.get("code", ""), config)
        elif name == "get_project_structure":
            result = await get_project_structure(config)
        elif name == "search_code":
            result = await search_code(
                arguments.get("query", ""), arguments.get("file_pattern"), config
            )
        elif name == "get_git_status":
            result = await get_git_status(config)
        elif name == "read_account_state":
            result = await read_account_state(config)
        elif name == "read_candles":
            result = await read_candles(
                arguments.get("symbol", "tBTCUSD"),
                arguments.get("timeframe", "1h"),
                int(arguments.get("limit", 300) or 300),
                config,
            )
        elif name == "run_strategy":
            result = await run_strategy(
                arguments.get("symbol", ""),
                arguments.get("trend_tf", "6h"),
                arguments.get("entry_tf", "1h"),
                config,
                htf_candles=arguments.get("htf_candles"),
                ltf_candles=arguments.get("ltf_candles"),
                params=arguments.get("params"),
                risk_state=arguments.get("risk_state"),
                risk_pct=float(arguments.get("risk_pct", 0.01) or 0.01),
                persist=bool(arguments.get("persist", True)),
                candle_limit=int(arguments.get("candle_limit", 300) or 300),
            )
        elif name == "submit_paper_order":
            result = await submit_paper_order(
                arguments.get("symbol", ""),
                arguments.get("side", ""),
                float(arguments.get("size", 0) or 0),
                config,
                type=str(arguments.get("type", "MARKET")),
                price=arguments.get("price"),
                decision_id=arguments.get("decision_id"),
                force=bool(arguments.get("force", False)),
            )
        elif name == "read_decision_log":
            result = await read_decision_log(
                config,
                symbol=arguments.get("symbol"),
                decision_id=arguments.get("decision_id"),
                limit=int(arguments.get("limit", 50) or 50),
            )
        elif name == "append_decision_log":
            result = await append_decision_log(arguments.get("record", {}), config)
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}

        # Format result as TextContent
        result_text = json.dumps(result, indent=2)
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        error_result = {"success": False, "error": f"Tool execution error: {str(e)}"}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


# Resource definitions
RESOURCES = [
    Resource(
        uri=cast(AnyUrl, "genesis://docs/*"),
        name="Project Documentation",
        description="Access project documentation files",
        mimeType="text/markdown",
    ),
    Resource(
        uri=cast(AnyUrl, "genesis://structure"),
        name="Project Structure",
        description="Project directory structure as a tree",
        mimeType="text/plain",
    ),
    Resource(
        uri=cast(AnyUrl, "genesis://git/status"),
        name="Git Status",
        description="Current Git repository status",
        mimeType="text/plain",
    ),
    Resource(
        uri=cast(AnyUrl, "genesis://config"),
        name="Configuration",
        description="Project configuration information",
        mimeType="text/plain",
    ),
]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available resources."""
    return RESOURCES


@app.read_resource()
async def read_resource(uri: Any) -> str:
    """
    Handle resource read requests.

    Args:
        uri: URI of the resource to read

    Returns:
        Resource content as string
    """
    try:
        uri_str = str(uri)
        logger.info(f"Resource requested: {uri_str}")
        # Route to appropriate resource handler
        if uri_str.startswith("genesis://docs/"):
            doc_path = uri_str.replace("genesis://docs/", "")
            result = await get_documentation(doc_path, config)
        elif uri_str == "genesis://structure":
            result = await get_structure_resource(config)
        elif uri_str == "genesis://git/status":
            result = await get_git_status_resource(config)
        elif uri_str == "genesis://config":
            result = await get_config_resource(config)
        else:
            result = {"success": False, "error": f"Unknown resource URI: {uri_str}"}

        if result.get("success"):
            return result.get("content", json.dumps(result, indent=2))
        else:
            return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return json.dumps({"success": False, "error": f"Resource error: {str(e)}"}, indent=2)


async def main():
    """Main entry point for the MCP server."""
    _ensure_utf8_stdio()
    # Setup logging
    setup_logging(config)

    logger.info("=" * 60)
    logger.info(f"Genesis-Core MCP Server v{config.version}")
    logger.info("=" * 60)
    logger.info(f"Server Name: {config.server_name}")
    logger.info(f"Log Level: {config.log_level}")
    logger.info("Features Enabled:")
    logger.info(f"  - File Operations: {config.features.file_operations}")
    logger.info(f"  - Code Execution: {config.features.code_execution}")
    logger.info(f"  - Git Integration: {config.features.git_integration}")
    logger.info("=" * 60)

    # Start the server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server started and ready for connections")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
