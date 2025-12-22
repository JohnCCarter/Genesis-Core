"""
MCP Tool Implementations

Provides all tools that can be called by AI assistants through the MCP protocol.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import MCPConfig, get_project_root
from .utils import check_file_size, is_safe_path, sanitize_code

logger = logging.getLogger(__name__)


async def read_file(file_path: str, config: MCPConfig) -> dict[str, Any]:
    """
    Read the contents of a file in the project.

    Args:
        file_path: Path to the file to read
        config: MCP configuration

    Returns:
        Dictionary with file contents or error information
    """
    try:
        # Validate path
        is_safe, error_msg = is_safe_path(file_path, config)
        if not is_safe:
            logger.warning(f"Unsafe path access attempt: {file_path}")
            return {"success": False, "error": error_msg}

        # Convert to absolute path
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = get_project_root() / path_obj

        # Check if file exists
        if not path_obj.exists():
            return {"success": False, "error": f"File does not exist: {file_path}"}

        if not path_obj.is_file():
            return {"success": False, "error": f"Path is not a file: {file_path}"}

        # Check file size
        is_valid_size, size_error = check_file_size(path_obj, config)
        if not is_valid_size:
            return {"success": False, "error": size_error}

        # Read file content (no external deps; avoid aiofiles requirement)
        content = await asyncio.to_thread(path_obj.read_text, encoding="utf-8")

        logger.info(f"Successfully read file: {file_path}")
        return {"success": True, "content": content, "path": str(path_obj)}

    except UnicodeDecodeError:
        return {"success": False, "error": f"File is not a text file: {file_path}"}
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {"success": False, "error": f"Error reading file: {str(e)}"}


async def write_file(file_path: str, content: str, config: MCPConfig) -> dict[str, Any]:
    """
    Write or update a file in the project.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        config: MCP configuration

    Returns:
        Dictionary with success status or error information
    """
    try:
        # Validate path
        is_safe, error_msg = is_safe_path(file_path, config)
        if not is_safe:
            logger.warning(f"Unsafe path write attempt: {file_path}")
            return {"success": False, "error": error_msg}

        # Convert to absolute path
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = get_project_root() / path_obj

        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write file content (no external deps; avoid aiofiles requirement)
        await asyncio.to_thread(path_obj.write_text, content, encoding="utf-8")

        logger.info(f"Successfully wrote file: {file_path}")
        return {
            "success": True,
            "message": f"File written successfully: {file_path}",
            "path": str(path_obj),
        }

    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return {"success": False, "error": f"Error writing file: {str(e)}"}


async def list_directory(directory_path: str, config: MCPConfig) -> dict[str, Any]:
    """
    List files and directories in the specified path.

    Args:
        directory_path: Path to the directory to list (default: ".")
        config: MCP configuration

    Returns:
        Dictionary with directory contents or error information
    """
    try:
        # Default to current directory if not specified
        if not directory_path or directory_path == ".":
            directory_path = "."

        # Validate path
        is_safe, error_msg = is_safe_path(directory_path, config)
        if not is_safe:
            logger.warning(f"Unsafe directory access attempt: {directory_path}")
            return {"success": False, "error": error_msg}

        # Convert to absolute path
        path_obj = Path(directory_path)
        if not path_obj.is_absolute():
            path_obj = get_project_root() / path_obj

        # Check if directory exists
        if not path_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {directory_path}"}

        if not path_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory_path}"}

        # List directory contents
        items = []
        for item in sorted(path_obj.iterdir()):
            # Skip hidden files unless explicitly requested
            if item.name.startswith("."):
                continue

            item_info = {
                "name": item.name,
                "path": str(item.relative_to(get_project_root())),
                "type": "directory" if item.is_dir() else "file",
            }

            # Add size for files
            if item.is_file():
                try:
                    item_info["size"] = item.stat().st_size
                except Exception:
                    item_info["size"] = None

            items.append(item_info)

        logger.info(f"Successfully listed directory: {directory_path}")
        return {
            "success": True,
            "path": str(path_obj.relative_to(get_project_root())),
            "items": items,
            "count": len(items),
        }

    except Exception as e:
        logger.error(f"Error listing directory {directory_path}: {e}")
        return {"success": False, "error": f"Error listing directory: {str(e)}"}


async def execute_python(code: str, config: MCPConfig) -> dict[str, Any]:
    """
    Execute Python code in a safe environment.

    Args:
        code: Python code to execute
        config: MCP configuration with execution timeout

    Returns:
        Dictionary with execution result or error information
    """
    try:
        if not config.features.code_execution:
            return {"success": False, "error": "Code execution is disabled"}

        # Sanitize code
        sanitized_code = sanitize_code(code)

        # Execute code in a subprocess with timeout
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            sanitized_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(get_project_root()),
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=config.security.execution_timeout_seconds
            )

            stdout_text = stdout.decode("utf-8") if stdout else ""
            stderr_text = stderr.decode("utf-8") if stderr else ""

            if process.returncode == 0:
                logger.info("Successfully executed Python code")
                return {
                    "success": True,
                    "output": stdout_text,
                    "error_output": stderr_text if stderr_text else None,
                    "return_code": process.returncode,
                }
            else:
                logger.warning(f"Python code execution failed with code {process.returncode}")
                return {
                    "success": False,
                    "error": f"Execution failed with return code {process.returncode}",
                    "output": stdout_text,
                    "error_output": stderr_text,
                    "return_code": process.returncode,
                }

        except TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "error": f"Execution timed out after {config.security.execution_timeout_seconds} seconds",
            }

    except Exception as e:
        logger.error(f"Error executing Python code: {e}")
        return {"success": False, "error": f"Error executing code: {str(e)}"}


async def get_project_structure(config: MCPConfig) -> dict[str, Any]:
    """
    Get the project structure as a tree.

    Args:
        config: MCP configuration

    Returns:
        Dictionary with project structure or error information
    """
    try:
        from .utils import format_tree_structure

        project_root = get_project_root()
        tree_lines = [str(project_root.name)]
        tree_lines.extend(format_tree_structure(project_root, "", max_depth=5))

        structure = "\n".join(tree_lines)

        logger.info("Successfully generated project structure")
        return {"success": True, "structure": structure, "root": str(project_root)}

    except Exception as e:
        logger.error(f"Error generating project structure: {e}")
        return {"success": False, "error": f"Error generating structure: {str(e)}"}


async def search_code(query: str, file_pattern: str | None, config: MCPConfig) -> dict[str, Any]:
    """
    Search for code in the project.

    Args:
        query: Search query string
        file_pattern: Optional file pattern to filter (e.g., "*.py")
        config: MCP configuration

    Returns:
        Dictionary with search results or error information
    """
    try:
        project_root = get_project_root()
        matches = []

        excluded_dirs = {
            ".git",
            ".venv",
            "__pycache__",
            "archive",
            "cache",
            "data",
            "logs",
            "reports",
            "results",
        }

        # Determine which files to search
        import fnmatch

        files: list[Path] = []
        pattern = file_pattern or "*.py"
        for f in project_root.rglob(pattern):
            try:
                if excluded_dirs.intersection(f.parts):
                    continue
                if not f.is_file():
                    continue
                if file_pattern and not fnmatch.fnmatch(f.name, file_pattern):
                    continue
                files.append(f)
            except OSError:
                # Some files (e.g. within broken/locked environments) can raise on stat.
                continue

        # Search in files
        for file_path in files:
            # Skip files in blocked patterns
            is_safe, _ = is_safe_path(file_path, config)
            if not is_safe:
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    if query.lower() in line.lower():
                        matches.append(
                            {
                                "file": str(file_path.relative_to(project_root)).replace("\\", "/"),
                                "line": line_num,
                                "content": line.strip(),
                            }
                        )

            except (UnicodeDecodeError, PermissionError, OSError, ValueError):
                # Skip files that can't be read
                continue

        logger.info(f"Search for '{query}' found {len(matches)} matches")
        return {"success": True, "query": query, "matches": matches, "count": len(matches)}

    except Exception as e:
        logger.error(f"Error searching code: {e}")
        return {"success": False, "error": f"Error searching code: {str(e)}"}


async def get_git_status(config: MCPConfig) -> dict[str, Any]:
    """
    Get Git status information for the project.

    Args:
        config: MCP configuration

    Returns:
        Dictionary with Git status or error information
    """
    try:
        if not config.features.git_integration:
            return {"success": False, "error": "Git integration is disabled"}

        project_root = get_project_root()

        git_exe = shutil.which("git")
        if not git_exe:
            return {"success": False, "error": "git executable not found on PATH"}

        timeout_s = min(5, int(config.security.execution_timeout_seconds or 5))

        def _git(args: list[str], *, timeout: int = timeout_s) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [git_exe, "-C", str(project_root), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )

        inside = _git(["rev-parse", "--is-inside-work-tree"])
        if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
            return {"success": False, "error": "Not a git repository"}

        branch_res = _git(["rev-parse", "--abbrev-ref", "HEAD"])
        current_branch = branch_res.stdout.strip() or "HEAD"

        untracked_included = True
        status_timed_out = False
        try:
            status_res = _git(["status", "--porcelain"])
        except subprocess.TimeoutExpired:
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

        remote_res = _git(["config", "--get", "remote.origin.url"])
        remote_url = remote_res.stdout.strip() or None

        is_dirty = bool(modified_files or staged_files or untracked_files)

        logger.info("Successfully retrieved Git status")
        return {
            "success": True,
            "branch": current_branch,
            "modified_files": modified_files,
            "staged_files": staged_files,
            "untracked_files": untracked_files,
            "remote_url": remote_url,
            "is_dirty": is_dirty,
            "untracked_included": untracked_included,
            "status_timed_out": status_timed_out,
        }

    except Exception as e:
        logger.error(f"Error getting Git status: {e}")
        return {"success": False, "error": f"Error getting Git status: {str(e)}"}
