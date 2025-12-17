"""
MCP Server Configuration Management
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class SecurityConfig(BaseModel):
    """Security configuration for the MCP server."""

    allowed_paths: list[str] = Field(default_factory=lambda: ["."])
    blocked_patterns: list[str] = Field(
        default_factory=lambda: [
            ".git",
            "__pycache__",
            "*.pyc",
            "node_modules",
            ".env",
            ".nonce_tracker.json",
            "dev.overrides.local.json",
        ]
    )
    max_file_size_mb: int = 10
    execution_timeout_seconds: int = 30


class FeaturesConfig(BaseModel):
    """Feature flags for the MCP server."""

    file_operations: bool = True
    code_execution: bool = True
    git_integration: bool = True


class MCPConfig(BaseModel):
    """Main configuration for the MCP server."""

    server_name: str = "genesis-core"
    version: str = "1.0.0"
    log_level: str = "INFO"
    log_file: str = "logs/mcp_server.log"
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)


def load_config(config_path: str | Path | None = None) -> MCPConfig:
    """
    Load MCP server configuration from JSON file.

    Args:
        config_path: Path to configuration file. If None, uses default location.

    Returns:
        MCPConfig instance with loaded configuration.
    """
    if config_path is None:
        # Default to config/mcp_settings.json relative to project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "mcp_settings.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        # Return default config if file doesn't exist
        return MCPConfig()

    with open(config_path) as f:
        config_data = json.load(f)

    return MCPConfig(**config_data)


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root.
    """
    return Path(__file__).parent.parent.resolve()
