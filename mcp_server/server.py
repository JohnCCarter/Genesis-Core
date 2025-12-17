"""
Genesis-Core MCP Server

Main server implementation using the Model Context Protocol.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from .config import load_config
from .resources import (
    get_config_resource,
    get_documentation,
    get_git_status_resource,
    get_structure_resource,
)
from .tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)

# Global configuration
config = load_config()

# Initialize MCP server
app = Server("genesis-core")


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
        logger.info(f"Tool called: {name} with arguments: {arguments}")

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
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}

        # Format result as TextContent
        import json

        result_text = json.dumps(result, indent=2)
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        import json

        error_result = {"success": False, "error": f"Tool execution error: {str(e)}"}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


# Resource definitions
RESOURCES = [
    Resource(
        uri="genesis://docs/*",
        name="Project Documentation",
        description="Access project documentation files",
        mimeType="text/markdown",
    ),
    Resource(
        uri="genesis://structure",
        name="Project Structure",
        description="Project directory structure as a tree",
        mimeType="text/plain",
    ),
    Resource(
        uri="genesis://git/status",
        name="Git Status",
        description="Current Git repository status",
        mimeType="text/plain",
    ),
    Resource(
        uri="genesis://config",
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
async def read_resource(uri: str) -> str:
    """
    Handle resource read requests.

    Args:
        uri: URI of the resource to read

    Returns:
        Resource content as string
    """
    try:
        logger.info(f"Resource requested: {uri}")

        import json

        # Route to appropriate resource handler
        if uri.startswith("genesis://docs/"):
            doc_path = uri.replace("genesis://docs/", "")
            result = await get_documentation(doc_path, config)
        elif uri == "genesis://structure":
            result = await get_structure_resource(config)
        elif uri == "genesis://git/status":
            result = await get_git_status_resource(config)
        elif uri == "genesis://config":
            result = await get_config_resource(config)
        else:
            result = {"success": False, "error": f"Unknown resource URI: {uri}"}

        if result.get("success"):
            return result.get("content", json.dumps(result, indent=2))
        else:
            return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        import json

        return json.dumps({"success": False, "error": f"Resource error: {str(e)}"}, indent=2)


async def main():
    """Main entry point for the MCP server."""
    # Setup logging
    setup_logging(config)

    logger.info("=" * 60)
    logger.info(f"Genesis-Core MCP Server v{config.version}")
    logger.info("=" * 60)
    logger.info(f"Server Name: {config.server_name}")
    logger.info(f"Log Level: {config.log_level}")
    logger.info(f"Features Enabled:")
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
