"""
MCP Resource Handlers

Provides resources that can be accessed by AI assistants for context.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
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

        # Special-case: docs index
        if doc_path.strip() in {"*", ""}:
            docs_dir = project_root / "docs"
            items: list[dict[str, str]] = []

            if docs_dir.exists():
                for p in sorted(docs_dir.rglob("*.md")):
                    # Keep URIs relative to docs/ so get_documentation() can resolve them
                    rel = p.relative_to(docs_dir).as_posix()
                    items.append({"path": f"docs/{rel}", "uri": f"genesis://docs/{rel}"})

            # Common root docs
            for root_doc in ("README.md", "CHANGELOG.md", "AGENTS.md"):
                p = project_root / root_doc
                if p.exists():
                    items.append({"path": root_doc, "uri": f"genesis://docs/{root_doc}"})

            content_lines = ["# Project Documentation Index", ""]
            if not items:
                content_lines.append("(No documentation files found.)")
            else:
                for item in items:
                    content_lines.append(f"- {item['uri']}  ({item['path']})")

            logger.info("Successfully generated documentation index")
            return {
                "success": True,
                "uri": "genesis://docs/*",
                "content": "\n".join(content_lines),
                "type": "index",
                "items": items,
            }

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
        with open(full_path, encoding="utf-8") as f:
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

        project_root = get_project_root()

        git_exe = shutil.which("git")
        if not git_exe:
            return {"success": False, "error": "git executable not found on PATH"}

        # Git can be surprisingly slow on Windows (cold start / AV scanning). Allow a
        # slightly higher timeout while keeping an upper bound to maintain responsiveness.
        timeout_s = int(config.security.execution_timeout_seconds or 5)
        timeout_s = max(1, min(15, timeout_s))

        git_env = dict(os.environ)
        # Avoid any interactive prompts that can hang in stdio-hosted environments.
        git_env.setdefault("GIT_TERMINAL_PROMPT", "0")
        git_env.setdefault("GCM_INTERACTIVE", "Never")

        def _git(args: list[str], *, timeout: int = timeout_s) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [git_exe, "-C", str(project_root), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                stdin=subprocess.DEVNULL,
                env=git_env,
            )

        try:
            inside = _git(["rev-parse", "--is-inside-work-tree"])
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git rev-parse timed out"}
        if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
            return {"success": False, "error": "Not a git repository"}

        try:
            branch_res = _git(["rev-parse", "--abbrev-ref", "HEAD"])
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git branch query timed out"}
        current_branch = branch_res.stdout.strip() or "HEAD"

        untracked_included = True
        status_timed_out = False
        try:
            status_res = _git(["status", "--porcelain"])
        except subprocess.TimeoutExpired:
            # On large working trees, enumerating untracked files can be very slow on Windows.
            # Retry with untracked disabled to keep the MCP server responsive.
            logger.warning("git status timed out; retrying with --untracked-files=no")
            status_timed_out = True
            untracked_included = False
            try:
                status_res = _git(["status", "--porcelain", "--untracked-files=no"])
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "git status timed out (even with untracked disabled)",
                }

        if status_res.returncode != 0:
            return {"success": False, "error": "Unable to read git status"}

        modified_files: list[str] = []
        staged_files: list[str] = []
        untracked_files: list[str] = []
        for raw in status_res.stdout.splitlines():
            if len(raw) < 3:
                continue
            x, y = raw[0], raw[1]
            path = raw[3:].strip()
            if raw.startswith("??"):
                untracked_files.append(path)
                continue
            if x != " ":
                staged_files.append(path)
            if y != " ":
                modified_files.append(path)

        status_info = {
            "branch": current_branch,
            "is_dirty": bool(modified_files or staged_files or untracked_files),
            "modified_files": modified_files,
            "staged_files": staged_files,
            "untracked_files": untracked_files,
            "untracked_included": untracked_included,
            "status_timed_out": status_timed_out,
        }

        # Format as readable text
        content_lines = [
            f"Current Branch: {current_branch}",
            f"Status: {'Modified' if status_info['is_dirty'] else 'Clean'}",
            "",
        ]

        if not untracked_included:
            content_lines.append(
                "Note: Untracked files omitted for performance (git status timed out scanning untracked)."
            )
            content_lines.append("")

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
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                    config_files.append({"path": config_path, "exists": True})
                except Exception:
                    config_files.append(
                        {"path": config_path, "exists": True, "error": "Could not read"}
                    )
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
            status = "OK" if cfg["exists"] else "NOT FOUND"
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
