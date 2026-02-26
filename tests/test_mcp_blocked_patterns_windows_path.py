from __future__ import annotations

from mcp_server.config import MCPConfig, SecurityConfig
from mcp_server.utils import is_safe_path


def test_blocked_patterns_match_forward_slash_relative_paths() -> None:
    cfg = MCPConfig(
        security=SecurityConfig(
            allowed_paths=["config"],
            blocked_patterns=["config/runtime.json"],
        )
    )

    ok, err = is_safe_path("config/runtime.json", cfg)
    assert ok is False
    assert "blocked pattern" in err.lower()


# End of file
