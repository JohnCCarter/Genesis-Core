"""
Tests for MCP Server functionality
"""

from __future__ import annotations

import pytest

from mcp_server.config import load_config
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
    result = await read_file("nonexistent_file.txt", config)
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
    """Test listing root directory."""
    result = await list_directory(".", config)
    assert result["success"] is True
    assert any(item["name"] == "src" for item in result["items"])


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

    # Blocked patterns
    is_safe, error = is_safe_path(".env", config)
    assert is_safe is False
    assert "blocked pattern" in error

    is_safe, error = is_safe_path("__pycache__/module.pyc", config)
    assert is_safe is False

    is_safe, error = is_safe_path(".git/config", config)
    assert is_safe is False


def test_load_config():
    """Test loading configuration."""
    config = load_config()
    assert config.server_name == "genesis-core"
    assert config.version == "1.0.0"
    assert config.features.file_operations is True
    assert config.features.code_execution is True
    assert config.features.git_integration is True
