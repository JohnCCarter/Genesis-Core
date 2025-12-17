"""
MCP Resource Handlers

Provides resources that can be accessed by AI assistants for context.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .config import MCPConfig, get_project_root
from .utils import format_tree_structure, is_safe_path

logger = logging.getLogger(__name__)


async def get_documentation(doc_path: str, config: MCPConfig) -> dict[str, Any]:
    """
    Get project documentation.

    Args:
        doc_path: Path to documentation file relative to docs/ or root
        config: MCP configuration

    Returns:
        Dictionary with documentation content or error information
    """
    try:
        project_root = get_project_root()

        # Try to resolve the path
        if doc_path.startswith("/"):
            doc_path = doc_path[1:]

        # Look in docs directory first
        docs_dir = project_root / "docs"
        full_path = docs_dir / doc_path

        # If not found in docs, try root
        if not full_path.exists():
            full_path = project_root / doc_path

        if not full_path.exists():
            return {"success": False, "error": f"Documentation not found: {doc_path}"}

        # Validate path safety
        is_safe, error_msg = is_safe_path(full_path, config)
        if not is_safe:
            return {"success": False, "error": error_msg}

        # Read documentation
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        logger.info(f"Successfully retrieved documentation: {doc_path}")
        return {
            "success": True,
            "uri": f"genesis://docs/{doc_path}",
            "content": content,
            "path": str(full_path.relative_to(project_root)),
        }

    except Exception as e:
        logger.error(f"Error retrieving documentation {doc_path}: {e}")
        return {"success": False, "error": f"Error retrieving documentation: {str(e)}"}


async def get_structure_resource(config: MCPConfig) -> dict[str, Any]:
    """
    Get project structure as a resource.

    Args:
        config: MCP configuration

    Returns:
        Dictionary with project structure
    """
    try:
        project_root = get_project_root()
        tree_lines = [str(project_root.name)]
        tree_lines.extend(format_tree_structure(project_root, "", max_depth=5))

        structure = "\n".join(tree_lines)

        logger.info("Successfully generated structure resource")
        return {
            "success": True,
            "uri": "genesis://structure",
            "content": structure,
            "type": "tree",
        }

    except Exception as e:
        logger.error(f"Error generating structure resource: {e}")
        return {"success": False, "error": f"Error generating structure: {str(e)}"}


async def get_git_status_resource(config: MCPConfig) -> dict[str, Any]:
    """
    Get Git status as a resource.

    Args:
        config: MCP configuration

    Returns:
        Dictionary with Git status information
    """
    try:
        if not config.features.git_integration:
            return {"success": False, "error": "Git integration is disabled"}

        try:
            import git
        except ImportError:
            return {"success": False, "error": "GitPython not installed"}

        project_root = get_project_root()

        try:
            repo = git.Repo(project_root)
        except git.exc.InvalidGitRepositoryError:
            return {"success": False, "error": "Not a git repository"}

        # Get current branch
        current_branch = repo.active_branch.name if not repo.head.is_detached else "HEAD"

        # Get status information
        status_info = {
            "branch": current_branch,
            "is_dirty": repo.is_dirty(),
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
            "untracked_files": repo.untracked_files,
        }

        # Format as readable text
        content_lines = [
            f"Current Branch: {current_branch}",
            f"Status: {'Modified' if repo.is_dirty() else 'Clean'}",
            "",
        ]

        if status_info["modified_files"]:
            content_lines.append("Modified Files:")
            for f in status_info["modified_files"]:
                content_lines.append(f"  - {f}")
            content_lines.append("")

        if status_info["staged_files"]:
            content_lines.append("Staged Files:")
            for f in status_info["staged_files"]:
                content_lines.append(f"  - {f}")
            content_lines.append("")

        if status_info["untracked_files"]:
            content_lines.append("Untracked Files:")
            for f in status_info["untracked_files"]:
                content_lines.append(f"  - {f}")

        content = "\n".join(content_lines)

        logger.info("Successfully generated Git status resource")
        return {
            "success": True,
            "uri": "genesis://git/status",
            "content": content,
            "data": status_info,
        }

    except Exception as e:
        logger.error(f"Error generating Git status resource: {e}")
        return {"success": False, "error": f"Error getting Git status: {str(e)}"}


async def get_config_resource(config: MCPConfig) -> dict[str, Any]:
    """
    Get configuration as a resource.

    Args:
        config: MCP configuration

    Returns:
        Dictionary with configuration information
    """
    try:
        project_root = get_project_root()

        # Read main configuration files
        config_files = []

        # Check for various config files
        config_paths = [
            "pyproject.toml",
            "config/runtime.seed.json",
            "config/mcp_settings.json",
        ]

        for config_path in config_paths:
            full_path = project_root / config_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    config_files.append({"path": config_path, "exists": True})
                except Exception:
                    config_files.append({"path": config_path, "exists": True, "error": "Could not read"})
            else:
                config_files.append({"path": config_path, "exists": False})

        # Format as readable text
        content_lines = [
            "Genesis-Core Configuration",
            "=" * 50,
            "",
            "Available Configuration Files:",
            "",
        ]

        for cfg in config_files:
            status = "✓" if cfg["exists"] else "✗"
            content_lines.append(f"{status} {cfg['path']}")

        content_lines.extend(
            [
                "",
                "MCP Server Configuration:",
                f"  Server Name: {config.server_name}",
                f"  Version: {config.version}",
                f"  Log Level: {config.log_level}",
                f"  File Operations: {'Enabled' if config.features.file_operations else 'Disabled'}",
                f"  Code Execution: {'Enabled' if config.features.code_execution else 'Disabled'}",
                f"  Git Integration: {'Enabled' if config.features.git_integration else 'Disabled'}",
            ]
        )

        content = "\n".join(content_lines)

        logger.info("Successfully generated configuration resource")
        return {
            "success": True,
            "uri": "genesis://config",
            "content": content,
            "config_files": config_files,
        }

    except Exception as e:
        logger.error(f"Error generating configuration resource: {e}")
        return {"success": False, "error": f"Error getting configuration: {str(e)}"}
