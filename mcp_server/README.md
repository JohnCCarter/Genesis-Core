# Genesis-Core MCP Server

Model Context Protocol (MCP) server for Genesis-Core, enabling AI coding assistants to interact with the project.

## Quick Start

### Installation

```bash
# Install MCP dependencies
pip install -e ".[mcp]"
```

### Running the Server

```bash
# Start the MCP server (stdio transport for VS Code MCP clients)
python -m mcp_server.server
```

### Running the Remote HTTP Server (ChatGPT Connector)

For ChatGPT “Connect to MCP” / remote linking you should run the HTTP server:

```bash
# Start the MCP server (Streamable HTTP transport)
# The MCP endpoint is POST /mcp
$env:PORT=3333
$env:GENESIS_MCP_REMOTE_SAFE=1
python -m mcp_server.remote_server
```

Environment variables:

- `PORT` (default: 8000) — set this to match your tunnel/forwarding target (e.g. 3333).
- `GENESIS_MCP_REMOTE_SAFE` (default: 1) — read-only mode (no write/execute tools).
- `GENESIS_MCP_REMOTE_ULTRA_SAFE` (default: 0) — exposes only `ping_tool` + connector stubs.
- `GENESIS_MCP_DEBUG_ROUTES` (default: 0) — prints registered routes on startup.

Remote endpoints:

- `GET /healthz` — returns `OK` (basic reachability check)
- `POST /mcp` — MCP endpoint used by ChatGPT connector

> Note: The server also registers some compatibility aliases (e.g. `/` and `/sse`) for POST in
> certain connector setups, but you should prefer `/mcp`.

Reverse-proxy / port-forwarding note:

- If you expose this server outside localhost, use a reverse proxy / tunnel of your choice.
- Ensure the public URL routes to the same local `PORT` that `mcp_server.remote_server` binds.
- Treat any public MCP URL as sensitive; prefer `GENESIS_MCP_REMOTE_SAFE=1`.

End-to-end checklist (ChatGPT “Connect to MCP”):

1. Verify reachability: open `https://<your-hostname>/healthz` and confirm it returns `OK`.
2. In ChatGPT, connect to the MCP server using the base URL and ensure it targets `POST /mcp`.
3. Run a simple tool call (e.g. `ping_tool`) to confirm the full request/response flow.

You should see:

```
============================================================
Genesis-Core MCP Server v1.0.0
============================================================
Server Name: genesis-core
Log Level: INFO
Features Enabled:
  - File Operations: True
  - Code Execution: True
  - Git Integration: True
============================================================
MCP Server started and ready for connections
```

Security notes:

- If the server is exposed on the public Internet, treat the URL as a secret.
- Prefer `GENESIS_MCP_REMOTE_SAFE=1` for read-only operation.
- When you do not actively need project tools, consider `GENESIS_MCP_REMOTE_ULTRA_SAFE=1`.
- Reduce `allowed_paths` in `config/mcp_settings.json` to the minimum required (avoid `"."` if
  you only need a subset like `docs/`).

“Private” access:

There is no UI toggle that makes an MCP server truly private per user. If you need “only me”
access for ChatGPT connector usage, you typically implement OAuth 2.1 (Auth Code + PKCE + token
verification) and enforce it on the MCP endpoint.

### VSCode Integration

1. Ensure `.vscode/mcp.json` exists (already created)
2. Open VSCode in the Genesis-Core directory
3. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
4. Search for "MCP: Connect to Server"
5. Select "genesis-core"

The server will start automatically and AI assistants can now interact with your project!

## Available Tools

The stdio server (`python -m mcp_server.server`) exposes tools with these names:

- **read_file** - Read file contents
- **write_file** - Write/update files
- **list_directory** - List files and directories
- **execute_python** - Execute Python code safely
- **get_project_structure** - Get project tree structure
- **search_code** - Search for code in the project
- **get_git_status** - Get Git repository status

The remote HTTP server (`python -m mcp_server.remote_server`) uses FastMCP and exposes the same
capabilities but with `*_tool` suffixes (e.g. `read_file_tool`, `list_directory_tool`). It also
includes connector-compatible `search` and `fetch` helpers.

## Available Resources

- `genesis://docs/{path}` - Project documentation
- `genesis://structure` - Project directory structure
- `genesis://git/status` - Git status information
- `genesis://config` - Configuration information

## Configuration

Edit `config/mcp_settings.json` to customize:

- Security settings (allowed paths, blocked patterns)
- File size limits
- Code execution timeouts
- Feature flags
- Log levels

## Testing

```bash
# Run MCP server tests
pytest tests/test_mcp_server.py tests/test_mcp_resources.py -v
```

## Documentation

See [`docs/mcp_server_guide.md`](../docs/mcp_server_guide.md) for complete documentation including:

- Detailed tool descriptions with examples
- Security features and best practices
- Troubleshooting guide
- Architecture overview
- Advanced configuration

## Security

The MCP server includes multiple security features:

- Path validation (prevents directory traversal)
- Blocked patterns (`.git`, `__pycache__`, `.env`, etc.)
- File size limits (default: 10MB)
- Code execution timeouts (default: 30 seconds)
- Comprehensive logging of all operations

## Logs

All operations are logged to `logs/mcp_server.log` with timestamps and detailed information.

## Support

For issues or questions, see the [full documentation](../docs/mcp_server_guide.md) or check the logs at `logs/mcp_server.log`.
