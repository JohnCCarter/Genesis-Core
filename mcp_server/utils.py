"""
Utility functions for MCP server operations
"""

from __future__ import annotations

import fnmatch
import logging
import re
from pathlib import Path

from .config import MCPConfig, get_project_root

logger = logging.getLogger(__name__)


def is_safe_path(path: str | Path, config: MCPConfig) -> tuple[bool, str]:
    """
    Validate that a path is safe to access.

    Args:
        path: Path to validate
        config: MCP configuration with security settings

    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        # Convert to Path object
        path_obj = Path(path)

        # Resolve to absolute path
        if not path_obj.is_absolute():
            path_obj = (get_project_root() / path_obj).resolve()
        else:
            path_obj = path_obj.resolve()

        project_root = get_project_root()

        # Check if path is within project root
        try:
            path_obj.relative_to(project_root)
        except ValueError:
            return False, f"Path is outside project root: {path}"

        # Enforce allowed paths allowlist (relative to project root)
        allowed_paths = config.security.allowed_paths or []
        if allowed_paths:
            allowed_roots: list[Path] = []
            for allowed in allowed_paths:
                try:
                    allowed_root = (project_root / allowed).resolve()
                    # Only accept allowlist entries that are inside project root
                    allowed_root.relative_to(project_root)
                    allowed_roots.append(allowed_root)
                except Exception:
                    logger.warning(f"Ignoring invalid allowed_paths entry: {allowed!r}")

            if not allowed_roots:
                return False, "No valid allowed_paths configured"

            allowed = False
            for allowed_root in allowed_roots:
                try:
                    path_obj.relative_to(allowed_root)
                    allowed = True
                    break
                except ValueError:
                    continue

            if not allowed:
                return False, f"Path is not within allowed_paths: {path}"

        # Check against blocked patterns
        path_str = str(path_obj)
        for pattern in config.security.blocked_patterns:
            # Check if any part of the path matches blocked patterns
            if fnmatch.fnmatch(path_str, f"*{pattern}*") or fnmatch.fnmatch(path_obj.name, pattern):
                return False, f"Path matches blocked pattern '{pattern}': {path}"

        return True, ""

    except Exception as e:
        logger.error(f"Error validating path {path}: {e}")
        return False, f"Invalid path: {str(e)}"


def check_file_size(path: Path, config: MCPConfig) -> tuple[bool, str]:
    """
    Check if file size is within allowed limits.

    Args:
        path: Path to file
        config: MCP configuration with size limits

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not path.exists():
            return False, f"File does not exist: {path}"

        if not path.is_file():
            return False, f"Path is not a file: {path}"

        size_mb = path.stat().st_size / (1024 * 1024)
        max_size = config.security.max_file_size_mb

        if size_mb > max_size:
            return False, f"File size {size_mb:.2f}MB exceeds limit of {max_size}MB"

        return True, ""

    except Exception as e:
        logger.error(f"Error checking file size for {path}: {e}")
        return False, f"Error checking file size: {str(e)}"


def sanitize_code(code: str) -> str:
    """
    Detect potentially dangerous Python code patterns.

    NOTE: This function only logs warnings about dangerous patterns but does NOT
    prevent their execution. Code runs in an isolated subprocess with timeout,
    which provides the actual security boundary. This logging is for auditing purposes.

    The security model relies on:
    1. Subprocess isolation (separate process)
    2. Timeout enforcement (prevents infinite loops)
    3. Audit logging (tracks what was executed)

    Args:
        code: Python code to check

    Returns:
        Original code (unchanged)
    """
    # Detect potentially dangerous patterns for logging/auditing
    dangerous_patterns = [
        r"import\s+os\s*$",
        r"from\s+os\s+import",
        r"import\s+sys\s*$",
        r"from\s+sys\s+import",
        r"import\s+subprocess",
        r"from\s+subprocess\s+import",
        r"__import__",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.MULTILINE):
            logger.warning(f"Potentially dangerous code pattern detected (audit): {pattern}")

    return code


def format_tree_structure(
    directory: Path, prefix: str = "", max_depth: int = 5, current_depth: int = 0
) -> list[str]:
    """
    Generate a tree structure representation of a directory.

    Args:
        directory: Directory to traverse
        prefix: Prefix for formatting
        max_depth: Maximum depth to traverse
        current_depth: Current depth in recursion

    Returns:
        List of formatted lines representing the tree
    """
    if current_depth >= max_depth:
        return []

    lines = []
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for i, item in enumerate(items):
            # Skip hidden files and directories starting with .
            if item.name.startswith("."):
                continue

            # Skip common excluded directories
            if item.name in ["__pycache__", "node_modules", ".git"]:
                continue

            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir():
                extension = "    " if is_last else "│   "
                lines.extend(
                    format_tree_structure(item, prefix + extension, max_depth, current_depth + 1)
                )

    except PermissionError:
        lines.append(f"{prefix}[Permission Denied]")

    return lines


def setup_logging(config: MCPConfig) -> None:
    """
    Set up logging for the MCP server.

    Args:
        config: MCP configuration with logging settings
    """
    # Create logs directory if it doesn't exist
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(),  # Also log to console
        ],
    )

    logger.info(f"MCP Server logging initialized at {config.log_level} level")
