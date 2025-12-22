"""
Tests for MCP Server resource handlers
"""

from __future__ import annotations

import subprocess

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
async def test_get_documentation_index(config):
    """Reading genesis://docs/* should return an index, not crash or 'not found'."""
    result = await get_documentation("*", config)
    assert result["success"] is True
    assert result["uri"] == "genesis://docs/*"
    assert "genesis://docs/" in result["content"]
    assert result.get("type") == "index"


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
async def test_get_git_status_resource_fallback_timeout(monkeypatch, config):
    """If `git status --porcelain` is slow, we should fallback to skipping untracked."""

    def _cp(args: list[str], stdout: str = "", stderr: str = "", returncode: int = 0):
        return subprocess.CompletedProcess(
            args=args, returncode=returncode, stdout=stdout, stderr=stderr
        )

    def fake_run(args, capture_output, text, check, timeout=None, **kwargs):  # type: ignore[no-untyped-def]
        # args is like: ["git", "-C", <root>, ...]
        cmd = list(args)[3:]

        if cmd[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return _cp(list(args), stdout="true\n")
        if cmd[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return _cp(list(args), stdout="Phase-7e\n")
        if cmd[:2] == ["status", "--porcelain"]:
            if "--untracked-files=no" not in cmd:
                raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)
            return _cp(list(args), stdout=" M README.md\n")

        return _cp(list(args), returncode=1, stderr="unexpected")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = await get_git_status_resource(config)
    assert result["success"] is True
    assert result["data"]["untracked_included"] is False
    assert result["data"]["status_timed_out"] is True
    assert "Untracked files omitted" in result["content"]


@pytest.mark.asyncio
async def test_get_config_resource(config):
    """Test getting configuration resource."""
    result = await get_config_resource(config)
    assert result["success"] is True
    assert result["uri"] == "genesis://config"
    assert "Genesis-Core Configuration" in result["content"]
    assert "pyproject.toml" in result["content"]
    assert "config_files" in result
