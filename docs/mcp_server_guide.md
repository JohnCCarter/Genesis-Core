# Genesis-Core MCP Server Guide

This guide covers the Model Context Protocol (MCP) server implementation for Genesis-Core, enabling seamless integration with VSCode, GitHub Copilot, and other AI coding assistants.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [VSCode Configuration](#vscode-configuration)
- [Available Tools](#available-tools)
- [Available Resources](#available-resources)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Security](#security)

## Overview

The Genesis-Core MCP server provides a bridge between AI coding assistants and the Genesis-Core codebase. It exposes project functionality through a standardized protocol, allowing AI assistants to:

- Read and write files in the project
- Execute Python code safely
- Navigate the project structure
- Search through code
- Access Git status and history
- Read project documentation

### Key Features

- ✅ **7 Powerful Tools** for file operations, code execution, and project navigation
- ✅ **4 Resource Types** for accessing documentation, structure, Git info, and configuration
- ✅ **Security First** with path validation, size limits, and execution timeouts
- ✅ **Async/Await** for efficient I/O operations
- ✅ **Comprehensive Logging** of all operations
- ✅ **VSCode Integration** with simple JSON configuration

## Installation

### 1. Install Dependencies

The MCP server requires additional Python packages. Install them with:

```bash
pip install -e ".[mcp]"
```

Or install packages individually:

```bash
pip install mcp>=0.9.0 aiofiles>=23.0.0 gitpython>=3.1.0
```

### 2. Verify Installation

Test that the MCP server can start:

```bash
python -m mcp_server.server
```

You should see output like:

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

## VSCode Configuration

### 1. Enable MCP Support

Ensure you have VSCode with MCP support enabled. The MCP integration is available in:
- GitHub Copilot with MCP support
- Claude for VSCode
- Other MCP-compatible extensions

### 2. Configure MCP Server

The `.vscode/mcp.json` file has already been created with the following configuration:

```json
{
  "mcpServers": {
    "genesis-core": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {}
    }
  }
}
```

### 3. Activate in VSCode

1. Open VSCode in the Genesis-Core project directory
2. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Search for "MCP: Connect to Server"
4. Select "genesis-core" from the list

The server will start automatically and connect to your AI assistant.

## Available Tools

The MCP server provides 7 tools that AI assistants can call:

### 1. read_file

Read the contents of a file in the project.

**Input:**
- `file_path` (string, required): Path to the file relative to project root

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `content` (string): File contents (if successful)
- `path` (string): Absolute path to the file
- `error` (string): Error message (if failed)

**Example:**
```json
{
  "file_path": "src/core/config/__init__.py"
}
```

### 2. write_file

Write or update a file in the project.

**Input:**
- `file_path` (string, required): Path to the file relative to project root
- `content` (string, required): Content to write to the file

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `message` (string): Success message
- `path` (string): Absolute path to the file
- `error` (string): Error message (if failed)

**Example:**
```json
{
  "file_path": "new_module/helper.py",
  "content": "def helper_function():\n    pass\n"
}
```

### 3. list_directory

List files and directories in a specified path.

**Input:**
- `directory_path` (string, optional, default="."): Path to directory

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `path` (string): Directory path
- `items` (array): List of files/directories with metadata
  - `name` (string): Item name
  - `path` (string): Relative path
  - `type` (string): "file" or "directory"
  - `size` (number): Size in bytes (files only)
- `count` (number): Total number of items
- `error` (string): Error message (if failed)

**Example:**
```json
{
  "directory_path": "src/core"
}
```

### 4. execute_python

Execute Python code in a safe environment with timeout.

**Input:**
- `code` (string, required): Python code to execute

**Returns:**
- `success` (boolean): Whether the execution succeeded
- `output` (string): Standard output from execution
- `error_output` (string): Standard error from execution
- `return_code` (number): Process return code
- `error` (string): Error message (if failed)

**Example:**
```json
{
  "code": "print('Hello from MCP!')\nfor i in range(5):\n    print(f'Count: {i}')"
}
```

**Security Notes:**
- Code execution has a 30-second timeout
- Runs in a subprocess isolated from the server
- Some dangerous operations are logged as warnings

### 5. get_project_structure

Get the project structure as a tree representation.

**Input:** None (empty object)

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `structure` (string): Tree representation of project
- `root` (string): Project root path
- `error` (string): Error message (if failed)

**Example:**
```json
{}
```

### 6. search_code

Search for code in the project.

**Input:**
- `query` (string, required): Search query string
- `file_pattern` (string, optional): File pattern to filter (e.g., "*.py", "*.md")

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `query` (string): The search query used
- `matches` (array): List of matches
  - `file` (string): File path
  - `line` (number): Line number
  - `content` (string): Matched line content
- `count` (number): Total number of matches
- `error` (string): Error message (if failed)

**Example:**
```json
{
  "query": "def backtest",
  "file_pattern": "*.py"
}
```

### 7. get_git_status

Get Git status information for the project.

**Input:** None (empty object)

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `branch` (string): Current branch name
- `modified_files` (array): List of modified files
- `staged_files` (array): List of staged files
- `untracked_files` (array): List of untracked files
- `remote_url` (string): Remote repository URL
- `is_dirty` (boolean): Whether the repository has uncommitted changes
- `error` (string): Error message (if failed)

**Example:**
```json
{}
```

## Available Resources

Resources provide context that AI assistants can read. They use URI-based access:

### 1. Project Documentation

**URI Pattern:** `genesis://docs/{path}`

Access project documentation files.

**Examples:**
- `genesis://docs/README.md` - Main README
- `genesis://docs/mcp_server_guide.md` - This guide
- `genesis://docs/performance/PERFORMANCE_GUIDE.md` - Performance documentation

### 2. Project Structure

**URI:** `genesis://structure`

Get the project directory structure as a tree (up to 5 levels deep).

### 3. Git Status

**URI:** `genesis://git/status`

Get the current Git repository status in a readable format.

### 4. Configuration

**URI:** `genesis://config`

Get project configuration information including:
- Available config files
- MCP server settings
- Feature flags

## Usage Examples

### Example 1: Reading a Configuration File

**AI Assistant Prompt:**
```
Read the MCP server configuration file
```

**Tool Call:**
```json
{
  "tool": "read_file",
  "arguments": {
    "file_path": "config/mcp_settings.json"
  }
}
```

### Example 2: Creating a New Module

**AI Assistant Prompt:**
```
Create a new module at utils/string_helpers.py with common string utilities
```

**Tool Call:**
```json
{
  "tool": "write_file",
  "arguments": {
    "file_path": "utils/string_helpers.py",
    "content": "\"\"\"String utility functions\"\"\"\n\ndef capitalize_words(text: str) -> str:\n    \"\"\"Capitalize each word in the string.\"\"\"\n    return ' '.join(word.capitalize() for word in text.split())\n"
  }
}
```

### Example 3: Searching for Functions

**AI Assistant Prompt:**
```
Find all functions that deal with backtesting
```

**Tool Call:**
```json
{
  "tool": "search_code",
  "arguments": {
    "query": "def backtest",
    "file_pattern": "*.py"
  }
}
```

### Example 4: Running a Quick Analysis

**AI Assistant Prompt:**
```
Calculate the average file size in the src/core directory
```

**Tool Call Sequence:**
1. `list_directory` to get file information
2. `execute_python` to calculate average:

```json
{
  "tool": "execute_python",
  "arguments": {
    "code": "sizes = [1024, 2048, 4096, 8192]\navg = sum(sizes) / len(sizes)\nprint(f'Average size: {avg} bytes')"
  }
}
```

### Example 5: Checking Git Status Before Commit

**AI Assistant Prompt:**
```
What files have been modified?
```

**Tool Call:**
```json
{
  "tool": "get_git_status",
  "arguments": {}
}
```

## Troubleshooting

### Server Won't Start

**Problem:** `python -m mcp_server.server` fails

**Solutions:**
1. Check that dependencies are installed: `pip install -e ".[mcp]"`
2. Verify Python version is 3.11+: `python --version`
3. Check logs at `logs/mcp_server.log`

### VSCode Can't Connect

**Problem:** VSCode shows "Failed to connect to MCP server"

**Solutions:**
1. Verify `.vscode/mcp.json` exists and is properly formatted
2. Check that Python is in your PATH
3. Try running the server manually to see error messages
4. Restart VSCode

### Path Access Denied

**Problem:** Tool returns "Path is outside project root" or "Path matches blocked pattern"

**Solutions:**
1. Check that the path is relative to project root
2. Verify the file isn't in a blocked directory (`.git`, `__pycache__`, etc.)
3. Review `config/mcp_settings.json` security settings

### Code Execution Timeout

**Problem:** `execute_python` returns "Execution timed out"

**Solutions:**
1. Simplify the code to run faster
2. Increase timeout in `config/mcp_settings.json` (default: 30 seconds)
3. Consider running long operations outside the MCP server

### File Size Limit Exceeded

**Problem:** "File size exceeds limit"

**Solutions:**
1. Adjust `max_file_size_mb` in `config/mcp_settings.json` (default: 10MB)
2. Use streaming for large files
3. Compress or split large files

## Architecture

### Component Overview

```
mcp_server/
├── __init__.py        # Package initialization
├── server.py          # Main MCP server with protocol handling
├── tools.py           # Tool implementations (7 tools)
├── resources.py       # Resource handlers (4 resource types)
├── config.py          # Configuration management
└── utils.py           # Security, validation, and helpers
```

### Data Flow

```
AI Assistant → VSCode → MCP Server → Tools/Resources → Project Files
                  ↑                        ↓
                  └────── Results ─────────┘
```

### Key Design Decisions

1. **Async/Await Throughout**: All I/O operations use `asyncio` for efficiency
2. **Security by Default**: Path validation and access control on every operation
3. **Structured Logging**: All operations logged with timestamps and context
4. **Configuration-Driven**: Behavior controlled via JSON configuration
5. **Error Resilience**: Comprehensive error handling with graceful degradation

### Technology Stack

- **MCP Protocol**: Model Context Protocol for AI assistant integration
- **Python 3.11+**: Modern Python with type hints
- **asyncio**: Asynchronous I/O operations
- **aiofiles**: Async file operations
- **GitPython**: Git repository integration
- **Pydantic**: Configuration validation

## Security

### Path Security

The server implements multiple layers of path validation:

1. **Project Root Restriction**: All paths must be within the project directory
2. **Blocked Patterns**: Certain directories and files are blocked:
   - `.git` (Git internals)
   - `__pycache__` (Python cache)
   - `*.pyc` (Compiled Python)
   - `node_modules` (Node.js packages)
   - `.env` (Environment variables)
   - `.nonce_tracker.json` (Sensitive data)
   - `dev.overrides.local.json` (Local overrides)

3. **Path Traversal Prevention**: Resolves and validates all paths to prevent `../` attacks

### Code Execution Security

When using `execute_python`:

1. **Subprocess Isolation**: Code runs in a separate process
2. **Timeout Protection**: 30-second default timeout (configurable)
3. **Pattern Detection**: Dangerous patterns are logged
4. **Working Directory**: Runs in project root, not server directory

### File Operation Security

1. **Size Limits**: Files limited to 10MB by default (configurable)
2. **Encoding Validation**: Only UTF-8 text files are supported
3. **Permission Checks**: Validates file permissions before operations

### Logging and Auditing

All operations are logged to `logs/mcp_server.log`:
- Timestamp of operation
- Tool/resource accessed
- Parameters provided
- Success/failure status
- Error messages

### Configuration

Security settings in `config/mcp_settings.json`:

```json
{
  "security": {
    "allowed_paths": ["."],
    "blocked_patterns": ["...", "..."],
    "max_file_size_mb": 10,
    "execution_timeout_seconds": 30
  }
}
```

### Best Practices

1. **Review Generated Code**: Always review code written by AI assistants
2. **Monitor Logs**: Check `logs/mcp_server.log` for suspicious activity
3. **Limit Scope**: Don't give AI assistants access to sensitive files
4. **Use Version Control**: Commit often so you can revert AI changes
5. **Test in Isolation**: Test AI-generated code before deploying

## Advanced Configuration

### Custom Security Settings

Edit `config/mcp_settings.json` to customize security:

```json
{
  "security": {
    "allowed_paths": [".", "tests"],
    "blocked_patterns": [".git", "*.pyc", "secrets/"],
    "max_file_size_mb": 20,
    "execution_timeout_seconds": 60
  }
}
```

### Feature Flags

Disable features if not needed:

```json
{
  "features": {
    "file_operations": true,
    "code_execution": false,  // Disable code execution
    "git_integration": true
  }
}
```

### Custom Log Level

Adjust logging verbosity:

```json
{
  "log_level": "DEBUG"  // Options: DEBUG, INFO, WARNING, ERROR
}
```

## Contributing

To extend the MCP server:

1. **Add New Tools**: Define in `tools.py` and register in `server.py`
2. **Add New Resources**: Define in `resources.py` and register in `server.py`
3. **Update Documentation**: Document new features in this guide
4. **Add Tests**: Create tests for new functionality

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs at `logs/mcp_server.log`
3. Open an issue on the Genesis-Core repository
4. Consult the [MCP Documentation](https://modelcontextprotocol.io/)

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP SDK Documentation](https://modelcontextprotocol.io/docs/sdk/python)
- [Genesis-Core Documentation](../README.md)
