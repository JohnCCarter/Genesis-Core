from __future__ import annotations

import pytest

from mcp_server.config import FeaturesConfig, MCPConfig, SecurityConfig
from mcp_server.tools import get_project_structure


@pytest.mark.asyncio
async def test_get_project_structure_respects_allowed_paths() -> None:
    cfg = MCPConfig(
        security=SecurityConfig(
            allowed_paths=["docs"],
            blocked_patterns=[".git", ".env"],
            max_file_size_mb=1,
            execution_timeout_seconds=5,
        ),
        features=FeaturesConfig(file_operations=True, code_execution=False, git_integration=False),
    )

    res = await get_project_structure(cfg)
    assert res["success"] is True
    assert "docs" in res["structure"]
    assert "src" not in res["structure"]


# End of file
