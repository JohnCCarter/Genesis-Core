"""
Integration tests for MCP Server end-to-end functionality
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
from mcp_server.tools import (
    execute_python,
    get_git_status,
    get_project_structure,
    list_directory,
    read_file,
    search_code,
    write_file,
)


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config()


@pytest.mark.asyncio
async def test_complete_workflow(config):
    """Test a complete workflow using multiple tools."""

    # 1. Check project structure
    structure_result = await get_project_structure(config)
    assert structure_result["success"] is True
    assert "src" in structure_result["structure"]

    # 2. Read main README
    readme_result = await read_file("README.md", config)
    assert readme_result["success"] is True
    assert "Genesis-Core" in readme_result["content"]

    # 3. List directory to find files
    list_result = await list_directory("mcp_server", config)
    assert list_result["success"] is True
    assert any(item["name"] == "server.py" for item in list_result["items"])

    # 4. Search for specific code
    search_result = await search_code("MCP Server", "*.py", config)
    assert search_result["success"] is True
    assert search_result["count"] > 0

    # 5. Check Git status
    git_result = await get_git_status(config)
    assert git_result["success"] is True
    assert "branch" in git_result

    # 6. Execute simple Python code
    code_result = await execute_python("print('Integration test success')", config)
    assert code_result["success"] is True
    assert "Integration test success" in code_result["output"]


@pytest.mark.asyncio
async def test_resource_workflow(config):
    """Test accessing all resources."""

    # 1. Get documentation resource
    doc_result = await get_documentation("README.md", config)
    assert doc_result["success"] is True
    assert doc_result["uri"] == "genesis://docs/README.md"

    # 2. Get structure resource
    structure_result = await get_structure_resource(config)
    assert structure_result["success"] is True
    assert structure_result["uri"] == "genesis://structure"

    # 3. Get Git status resource
    git_result = await get_git_status_resource(config)
    assert git_result["success"] is True
    assert git_result["uri"] == "genesis://git/status"

    # 4. Get config resource
    config_result = await get_config_resource(config)
    assert config_result["success"] is True
    assert config_result["uri"] == "genesis://config"


@pytest.mark.asyncio
async def test_file_operations_workflow(config):
    """Test file operations workflow."""

    test_file = "tmp/mcp_integration_test.txt"
    test_content = "MCP Integration Test\nThis file tests the complete workflow."

    # 1. Write a test file
    write_result = await write_file(test_file, test_content, config)
    assert write_result["success"] is True

    # 2. Read the file back
    read_result = await read_file(test_file, config)
    assert read_result["success"] is True
    assert read_result["content"] == test_content

    # 3. Search for content in the file
    search_result = await search_code("Integration Test", "*.txt", config)
    assert search_result["success"] is True
    # Should find our test file
    matches = [m for m in search_result["matches"] if test_file in m["file"]]
    assert len(matches) > 0


@pytest.mark.asyncio
async def test_security_workflow(config):
    """Test that security features work in a realistic workflow."""

    # 1. Try to read a blocked file
    env_result = await read_file(".env", config)
    assert env_result["success"] is False
    assert "blocked pattern" in env_result["error"]

    # 2. Try to access .git directory
    git_result = await read_file(".git/config", config)
    assert git_result["success"] is False

    # 3. Try to write to a safe location (should succeed)
    safe_result = await write_file("tmp/safe_test.txt", "Safe content", config)
    assert safe_result["success"] is True

    # 4. Verify we can list safe directories
    list_result = await list_directory("src", config)
    assert list_result["success"] is True


@pytest.mark.asyncio
async def test_code_execution_workflow(config):
    """Test code execution with various scenarios."""

    # 1. Simple calculation
    calc_result = await execute_python("result = 10 + 20\nprint(f'Result: {result}')", config)
    assert calc_result["success"] is True
    assert "Result: 30" in calc_result["output"]

    # 2. Multi-line code
    multiline_code = """
import math
for i in range(3):
    print(f'Square of {i}: {i**2}')
"""
    multiline_result = await execute_python(multiline_code, config)
    assert multiline_result["success"] is True
    assert "Square of 0: 0" in multiline_result["output"]

    # 3. Code with error
    error_result = await execute_python("1 / 0", config)
    assert error_result["success"] is False
    assert "ZeroDivisionError" in error_result["error_output"]
