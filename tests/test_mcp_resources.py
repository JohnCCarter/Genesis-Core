"""
Tests for MCP Server resource handlers
"""

from __future__ import annotations

import pytest

from mcp_server.config import load_config
from mcp_server.resources import (
    get_config_resource,
    get_documentation,
    get_git_status_resource,
    get_structure_resource,
)


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config()


@pytest.mark.asyncio
async def test_get_documentation(config):
    """Test getting documentation resource."""
    result = await get_documentation("README.md", config)
    assert result["success"] is True
    assert "Genesis-Core" in result["content"]
    assert result["uri"] == "genesis://docs/README.md"


@pytest.mark.asyncio
async def test_get_documentation_in_docs_dir(config):
    """Test getting documentation from docs directory."""
    result = await get_documentation("mcp_server_guide.md", config)
    assert result["success"] is True
    assert "Genesis-Core MCP Server Guide" in result["content"]


@pytest.mark.asyncio
async def test_get_documentation_not_found(config):
    """Test getting non-existent documentation."""
    result = await get_documentation("nonexistent.md", config)
    assert result["success"] is False
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_get_structure_resource(config):
    """Test getting project structure resource."""
    result = await get_structure_resource(config)
    assert result["success"] is True
    assert result["uri"] == "genesis://structure"
    assert "src" in result["content"]
    assert result["type"] == "tree"


@pytest.mark.asyncio
async def test_get_git_status_resource(config):
    """Test getting Git status resource."""
    result = await get_git_status_resource(config)
    assert result["success"] is True
    assert result["uri"] == "genesis://git/status"
    assert "Current Branch:" in result["content"]
    assert "data" in result


@pytest.mark.asyncio
async def test_get_config_resource(config):
    """Test getting configuration resource."""
    result = await get_config_resource(config)
    assert result["success"] is True
    assert result["uri"] == "genesis://config"
    assert "Genesis-Core Configuration" in result["content"]
    assert "pyproject.toml" in result["content"]
    assert "config_files" in result
