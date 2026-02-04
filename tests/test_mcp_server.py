"""
Tests for MCP Server functionality
"""

from __future__ import annotations

import re

import pytest
from pydantic import AnyUrl, TypeAdapter

from mcp_server.config import MCPConfig, SecurityConfig, load_config
from mcp_server.tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)
from mcp_server.utils import is_safe_path


@pytest.mark.asyncio
async def test_read_resource_accepts_anyurl(config):
    """read_resource must tolerate pydantic AnyUrl (some MCP clients pass this type)."""
    from mcp_server.server import read_resource

    uri = TypeAdapter(AnyUrl).validate_python("genesis://docs/*")
    content = await read_resource(uri)
    assert "Project Documentation Index" in content


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config()


@pytest.mark.asyncio
async def test_read_file(config):
    """Test reading a file."""
    # Test reading an existing file
    result = await read_file("README.md", config)
    assert result["success"] is True
    assert "Genesis-Core" in result["content"]
    assert "path" in result


@pytest.mark.asyncio
async def test_read_file_not_exists(config):
    """Test reading a non-existent file."""
    # Use a path within an allowed root to ensure the error is about existence (not allowlisting).
    result = await read_file("src/nonexistent_file.txt", config)
    assert result["success"] is False
    assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_write_and_read_file(config):
    """Test writing and then reading a file."""
    test_content = "# Test File\n\nThis is a test."
    test_path = "tmp/test_mcp_write.md"

    # Write file
    write_result = await write_file(test_path, test_content, config)
    assert write_result["success"] is True

    # Read it back
    read_result = await read_file(test_path, config)
    assert read_result["success"] is True
    assert read_result["content"] == test_content


@pytest.mark.asyncio
async def test_list_directory(config):
    """Test listing directory contents."""
    result = await list_directory("src/core", config)
    assert result["success"] is True
    assert "items" in result
    assert result["count"] > 0
    assert any(item["name"] == "config" for item in result["items"])


@pytest.mark.asyncio
async def test_list_directory_root(config):
    """Test listing an allowed directory."""
    result = await list_directory("src", config)
    assert result["success"] is True
    assert any(item["name"] == "core" for item in result["items"])


@pytest.mark.asyncio
async def test_execute_python(config):
    """Test executing Python code."""
    code = "print('Hello, MCP!')\nprint(2 + 2)"
    result = await execute_python(code, config)
    assert result["success"] is True
    assert "Hello, MCP!" in result["output"]
    assert "4" in result["output"]


@pytest.mark.asyncio
async def test_execute_python_with_error(config):
    """Test executing Python code that raises an error."""
    code = "raise ValueError('Test error')"
    result = await execute_python(code, config)
    assert result["success"] is False
    assert "Test error" in result["error_output"]


@pytest.mark.asyncio
async def test_get_project_structure(config):
    """Test getting project structure."""
    result = await get_project_structure(config)
    assert result["success"] is True
    assert "structure" in result
    assert "src" in result["structure"]
    assert "Genesis-Core" in result["structure"]


@pytest.mark.asyncio
async def test_search_code(config):
    """Test searching code."""
    result = await search_code("def load_config", "*.py", config)
    assert result["success"] is True
    assert "matches" in result
    # Should find at least the definition in config.py
    assert any("config.py" in match["file"] for match in result["matches"])


@pytest.mark.asyncio
async def test_search_code_no_pattern(config):
    """Test searching code without file pattern."""
    result = await search_code("import", None, config)
    assert result["success"] is True
    assert result["count"] > 0


@pytest.mark.asyncio
async def test_get_git_status(config):
    """Test getting Git status."""
    result = await get_git_status(config)
    assert result["success"] is True
    assert "branch" in result
    assert "modified_files" in result
    assert "staged_files" in result
    assert "untracked_files" in result


def test_is_safe_path(config):
    """Test path validation."""
    # Safe paths
    is_safe, _ = is_safe_path("src/core/config/__init__.py", config)
    assert is_safe is True

    is_safe, _ = is_safe_path("README.md", config)
    assert is_safe is True

    # Blocked patterns (exercise within allowed roots)
    is_safe, error = is_safe_path("config/.env", config)
    assert is_safe is False
    assert "blocked pattern" in error

    is_safe, error = is_safe_path("src/__pycache__/module.pyc", config)
    assert is_safe is False
    assert "blocked pattern" in error

    # Outside allowed paths (also inside project root)
    is_safe, error = is_safe_path(".git/config", config)
    assert is_safe is False


def test_is_safe_path_enforces_allowed_paths():
    """Ensure allowed_paths restricts access even within project root."""
    restricted = MCPConfig(security=SecurityConfig(allowed_paths=["src"]))

    is_safe, _ = is_safe_path("src/core/config/__init__.py", restricted)
    assert is_safe is True

    is_safe, error = is_safe_path("README.md", restricted)
    assert is_safe is False
    assert "allowed_paths" in error


def test_load_config():
    """Test loading configuration."""
    config = load_config()
    assert config.server_name == "genesis-core"
    # Version can be bumped in config/mcp_settings.json; validate it's a semver-like string.
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:[-+].+)?", config.version)
    assert config.features.file_operations is True
    assert config.features.code_execution is True
    assert config.features.git_integration is True


def test_remote_token_auth_allows_when_unset(monkeypatch):
    """Remote token auth should be a no-op unless a token is configured."""
    import mcp_server.remote_server as remote

    monkeypatch.setattr(remote, "REMOTE_TOKEN", None)
    assert remote._is_authorized_remote_request(authorization=None, token_header=None) is True


def test_remote_token_auth_accepts_bearer_or_header(monkeypatch):
    """When configured, the token must match either Authorization Bearer or X-Genesis-MCP-Token."""
    import mcp_server.remote_server as remote

    monkeypatch.setattr(remote, "REMOTE_TOKEN", "s3cr3t")

    assert (
        remote._is_authorized_remote_request(authorization="Bearer s3cr3t", token_header=None)
        is True
    )
    assert remote._is_authorized_remote_request(authorization=None, token_header="s3cr3t") is True

    assert (
        remote._is_authorized_remote_request(authorization="Bearer wrong", token_header=None)
        is False
    )
    assert remote._is_authorized_remote_request(authorization=None, token_header="wrong") is False
    assert (
        remote._is_authorized_remote_request(authorization="Basic abc", token_header=None) is False
    )
