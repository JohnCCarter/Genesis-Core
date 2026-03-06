"""
MCP Tool Implementations

Provides all tools that can be called by AI assistants through the MCP protocol.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

from .config import MCPConfig, get_project_root
from .utils import is_safe_path, sanitize_code

logger = logging.getLogger(__name__)

GIT_WORKFLOW_BASE_BRANCH = "feature/composable-strategy-phase2"
GIT_WORKFLOW_TASK_BRANCH_PREFIX = "chatgpt/"
GIT_WORKFLOW_PROTECTED_BRANCHES = {
    GIT_WORKFLOW_BASE_BRANCH,
    "main",
    "master",
}
GIT_WORKFLOW_MUTATING_OPERATIONS = {
    "create_task_branch",
    "git_add",
    "git_commit",
    "git_push_task_branch",
    "create_pr",
}
GIT_WORKFLOW_SUPPORTED_OPERATIONS = {
    "create_task_branch",
    "git_status",
    "git_diff",
    "git_log",
    "git_add",
    "git_commit",
    "git_push_task_branch",
    "create_pr",
    "git_pull_ff_only",
}


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
        try:
            size_mb = path_obj.stat().st_size / (1024 * 1024)
            max_size = config.security.max_file_size_mb

            if size_mb > max_size:
                return {
                    "success": False,
                    "error": f"File size {size_mb:.2f}MB exceeds limit of {max_size}MB",
                }
        except Exception as e:
            logger.error(f"Error checking file size for {path_obj}: {e}")
            return {"success": False, "error": f"Error checking file size: {str(e)}"}

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

        try:
            max_lines_per_root = int(
                os.environ.get("GENESIS_MCP_STRUCTURE_MAX_LINES_PER_ROOT", "60")
            )
        except ValueError:
            max_lines_per_root = 60
        max_lines_per_root = max(20, min(400, max_lines_per_root))

        try:
            max_total_lines = int(os.environ.get("GENESIS_MCP_STRUCTURE_MAX_TOTAL_LINES", "800"))
        except ValueError:
            max_total_lines = 800
        max_total_lines = max(100, min(4000, max_total_lines))

        project_root = get_project_root()
        tree_lines = [str(project_root.name)]

        allowed_paths = config.security.allowed_paths or []
        if not allowed_paths:
            full_tree = format_tree_structure(project_root, "", max_depth=5)
            if len(full_tree) > max_total_lines:
                omitted = len(full_tree) - max_total_lines
                full_tree = full_tree[:max_total_lines]
                full_tree.append(f"... [truncated {omitted} lines]")
            tree_lines.extend(full_tree)
        else:
            allowed_roots: list[Path] = []
            for allowed in allowed_paths:
                try:
                    allowed_root = (project_root / allowed).resolve()
                    allowed_root.relative_to(project_root)
                    if allowed_root.exists():
                        allowed_roots.append(allowed_root)
                except Exception:
                    continue

            if not allowed_roots:
                structure = "\n".join(tree_lines)
                return {"success": True, "structure": structure, "root": str(project_root)}

            allowed_roots = sorted(set(allowed_roots))
            allowed_dir_roots = [p for p in allowed_roots if p.is_dir()]
            allowed_file_roots = [p for p in allowed_roots if p.is_file()]

            # Keep only top-most allowed directories (avoid duplicating nested roots).
            def _is_within(child: Path, parent: Path) -> bool:
                try:
                    child.relative_to(parent)
                    return True
                except Exception:
                    return False

            minimal_dir_roots: list[Path] = []
            for candidate in allowed_dir_roots:
                if any(
                    candidate != parent and _is_within(candidate, parent)
                    for parent in allowed_dir_roots
                ):
                    continue
                minimal_dir_roots.append(candidate)

            # Keep only allowed files not already covered by an allowed directory root.
            minimal_file_roots: list[Path] = []
            for f in allowed_file_roots:
                if any(_is_within(f, d) for d in minimal_dir_roots):
                    continue
                minimal_file_roots.append(f)

            display_roots: list[Path] = sorted(minimal_dir_roots + minimal_file_roots)

            for i, allowed_root in enumerate(display_roots):
                is_last = i == len(display_roots) - 1
                current_prefix = "└── " if is_last else "├── "
                rel = allowed_root.relative_to(project_root).as_posix()
                tree_lines.append(f"{current_prefix}{rel}")

                if allowed_root.is_dir():
                    extension = "    " if is_last else "│   "
                    # Reserve one level for the allowed root itself.
                    children = format_tree_structure(
                        allowed_root,
                        prefix=extension,
                        max_depth=4,
                        current_depth=0,
                    )
                    if len(children) > max_lines_per_root:
                        omitted = len(children) - max_lines_per_root
                        children = children[:max_lines_per_root]
                        children.append(f"{extension}... [truncated {omitted} lines]")
                    tree_lines.extend(children)

        if len(tree_lines) > max_total_lines:
            omitted = len(tree_lines) - max_total_lines
            tree_lines = tree_lines[:max_total_lines]
            tree_lines.append(f"... [truncated {omitted} lines]")

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
        truncated = False
        query_lower = query.lower()

        try:
            max_matches = int(os.environ.get("GENESIS_MCP_SEARCH_MAX_MATCHES", "200"))
        except ValueError:
            max_matches = 200
        max_matches = max(20, min(2000, max_matches))

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
            if len(matches) >= max_matches:
                truncated = True
                break

            # Skip files in blocked patterns
            is_safe, _ = is_safe_path(file_path, config)
            if not is_safe:
                continue

            relative_file = str(file_path.relative_to(project_root)).replace("\\", "/")
            if query_lower and query_lower in relative_file.lower():
                matches.append(
                    {
                        "file": relative_file,
                        "line": 0,
                        "content": "[path match]",
                    }
                )
                if len(matches) >= max_matches:
                    truncated = True
                    break

            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    if query_lower in line.lower():
                        matches.append(
                            {
                                "file": relative_file,
                                "line": line_num,
                                "content": line.strip(),
                            }
                        )
                        if len(matches) >= max_matches:
                            truncated = True
                            break

                if truncated:
                    break

            except (UnicodeDecodeError, PermissionError, OSError, ValueError):
                # Skip files that can't be read
                continue

        logger.info(
            "Search for '%s' found %d matches%s",
            query,
            len(matches),
            " (truncated)" if truncated else "",
        )
        return {
            "success": True,
            "query": query,
            "matches": matches,
            "count": len(matches),
            "truncated": truncated,
            "max_matches": max_matches,
        }

    except Exception as e:
        logger.error(f"Error searching code: {e}")
        return {"success": False, "error": f"Error searching code: {str(e)}"}


def _build_git_env() -> dict[str, str]:
    git_env = dict(os.environ)
    git_env.setdefault("GIT_TERMINAL_PROMPT", "0")
    git_env.setdefault("GCM_INTERACTIVE", "Never")
    return git_env


def _redact_remote_url(remote_url: str | None) -> str | None:
    if not remote_url or "://" not in remote_url:
        return remote_url

    try:
        parts = urlsplit(remote_url)
        netloc = parts.netloc
        if "@" in netloc:
            netloc = netloc.split("@", 1)[1]
            return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    except Exception:
        pass

    return remote_url


def _run_git_command(
    git_exe: str,
    *,
    project_root: Path,
    args: list[str],
    timeout_s: int,
    git_env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [git_exe, "-C", str(project_root), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_s,
        stdin=subprocess.DEVNULL,
        env=git_env,
    )


async def _run_git_command_async(
    git_exe: str,
    *,
    project_root: Path,
    args: list[str],
    timeout_s: int,
    git_env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return await asyncio.to_thread(
        _run_git_command,
        git_exe,
        project_root=project_root,
        args=args,
        timeout_s=timeout_s,
        git_env=git_env,
    )


def _git_repo_state(
    *,
    git_exe: str,
    project_root: Path,
    timeout_s: int,
    git_env: dict[str, str],
) -> dict[str, Any]:
    inside = _run_git_command(
        git_exe,
        project_root=project_root,
        args=["rev-parse", "--is-inside-work-tree"],
        timeout_s=timeout_s,
        git_env=git_env,
    )
    if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
        return {"success": False, "error": "Not a git repository"}

    branch_res = _run_git_command(
        git_exe,
        project_root=project_root,
        args=["rev-parse", "--abbrev-ref", "HEAD"],
        timeout_s=timeout_s,
        git_env=git_env,
    )
    if branch_res.returncode != 0:
        return {"success": False, "error": "Unable to resolve current git branch"}

    head_res = _run_git_command(
        git_exe,
        project_root=project_root,
        args=["rev-parse", "HEAD"],
        timeout_s=timeout_s,
        git_env=git_env,
    )
    if head_res.returncode != 0:
        return {"success": False, "error": "Unable to resolve HEAD commit"}

    remote_res = _run_git_command(
        git_exe,
        project_root=project_root,
        args=["config", "--get", "remote.origin.url"],
        timeout_s=timeout_s,
        git_env=git_env,
    )
    remote_url = _redact_remote_url(remote_res.stdout.strip() or None)

    return {
        "success": True,
        "branch": branch_res.stdout.strip() or "HEAD",
        "head_sha": head_res.stdout.strip(),
        "remote_url": remote_url,
    }


def _normalize_task_branch(
    *, task_slug: str | None, task_branch: str | None, date_utc: str | None
) -> str:
    if task_branch:
        return task_branch.strip()

    if not task_slug:
        raise ValueError("task_slug is required when task_branch is not provided")

    slug = re.sub(r"[^a-z0-9]+", "-", task_slug.strip().lower()).strip("-")
    if not slug:
        raise ValueError("task_slug must include at least one alphanumeric character")

    if date_utc:
        try:
            date_token = dt.datetime.strptime(date_utc, "%Y%m%d").strftime("%Y%m%d")
        except ValueError as exc:
            raise ValueError("date_utc must use YYYYMMDD format") from exc
    else:
        date_token = dt.datetime.now(dt.UTC).strftime("%Y%m%d")

    return f"{GIT_WORKFLOW_TASK_BRANCH_PREFIX}{date_token}-{slug}"


def _normalize_git_pathspecs(pathspecs: list[str] | str | None) -> list[str]:
    if not pathspecs:
        return ["."]

    if isinstance(pathspecs, str):
        pathspecs = [pathspecs]

    cleaned = [p.strip() for p in pathspecs if isinstance(p, str) and p.strip()]
    if not cleaned:
        return ["."]

    for pathspec in cleaned:
        if pathspec.startswith("-"):
            raise ValueError("pathspec entries must not begin with '-'")

    return cleaned


def _build_compare_url(remote_url: str | None, *, base_branch: str, head_branch: str) -> str | None:
    if not remote_url:
        return None

    remote = remote_url.strip()
    if remote.endswith(".git"):
        remote = remote[:-4]

    if remote.startswith("git@"):
        # Example: git@github.com:owner/repo
        try:
            host_and_path = remote.split("@", 1)[1]
            host, path = host_and_path.split(":", 1)
            web_base = f"https://{host}/{path}"
        except Exception:
            return None
    elif remote.startswith("https://") or remote.startswith("http://"):
        web_base = remote
    else:
        return None

    if not web_base:
        return None
    return (
        f"{web_base}/compare/"
        f"{quote(base_branch, safe='')}...{quote(head_branch, safe='')}?expand=1"
    )


async def get_git_status(
    config: MCPConfig, *, apply_security_filters: bool = False
) -> dict[str, Any]:
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

        timeout_s = max(
            1, min(15, max(1, min(30, int(config.security.execution_timeout_seconds or 5))))
        )
        git_env = _build_git_env()

        try:
            inside = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["rev-parse", "--is-inside-work-tree"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git rev-parse timed out"}
        if inside.returncode != 0 or inside.stdout.strip().lower() != "true":
            return {"success": False, "error": "Not a git repository"}

        try:
            branch_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["rev-parse", "--abbrev-ref", "HEAD"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git branch query timed out"}
        current_branch = branch_res.stdout.strip() or "HEAD"

        untracked_included = True
        status_timed_out = False
        try:
            status_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["status", "--porcelain"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
        except subprocess.TimeoutExpired:
            logger.warning("git status timed out; retrying with --untracked-files=no")
            status_timed_out = True
            untracked_included = False
            try:
                status_res = await _run_git_command_async(
                    git_exe,
                    project_root=project_root,
                    args=["status", "--porcelain", "--untracked-files=no"],
                    timeout_s=timeout_s,
                    git_env=git_env,
                )
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

        remote_url: str | None
        try:
            remote_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["config", "--get", "remote.origin.url"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            remote_url = remote_res.stdout.strip() or None
        except subprocess.TimeoutExpired:
            remote_url = None

        if apply_security_filters:

            def _filter_paths(paths: list[str]) -> list[str]:
                visible: list[str] = []
                for p in paths:
                    ok, _ = is_safe_path(p, config)
                    if ok:
                        visible.append(p)
                return visible

            modified_files = _filter_paths(modified_files)
            staged_files = _filter_paths(staged_files)
            untracked_files = _filter_paths(untracked_files)

        remote_url = _redact_remote_url(remote_url)

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


async def get_git_repo_state(config: MCPConfig) -> dict[str, Any]:
    """Return current git branch/HEAD metadata for confirmation binding."""

    try:
        if not config.features.git_integration:
            return {"success": False, "error": "Git integration is disabled"}

        git_exe = shutil.which("git")
        if not git_exe:
            return {"success": False, "error": "git executable not found on PATH"}

        state = await asyncio.to_thread(
            _git_repo_state,
            git_exe=git_exe,
            project_root=get_project_root(),
            timeout_s=max(1, min(30, int(config.security.execution_timeout_seconds or 5))),
            git_env=_build_git_env(),
        )
        return state
    except Exception as e:
        logger.error(f"Error getting git repo state: {e}")
        return {"success": False, "error": f"Error getting git repo state: {str(e)}"}


async def git_workflow_operation(
    operation: str,
    config: MCPConfig,
    *,
    dry_run: bool = False,
    task_slug: str | None = None,
    task_branch: str | None = None,
    date_utc: str | None = None,
    pathspecs: list[str] | str | None = None,
    commit_message: str | None = None,
    pr_title: str | None = None,
    pr_body: str | None = None,
    log_limit: int | None = None,
    diff_ref: str | None = None,
    base_branch: str = GIT_WORKFLOW_BASE_BRANCH,
) -> dict[str, Any]:
    """Execute constrained git operations for remote MCP task-branch workflow."""

    if not config.features.git_integration:
        return {"success": False, "error": "Git integration is disabled"}

    if operation not in GIT_WORKFLOW_SUPPORTED_OPERATIONS:
        return {
            "success": False,
            "error": (
                "Unsupported git operation. Allowed: "
                + ", ".join(sorted(GIT_WORKFLOW_SUPPORTED_OPERATIONS))
            ),
        }

    git_exe = shutil.which("git")
    if not git_exe:
        return {"success": False, "error": "git executable not found on PATH"}

    project_root = get_project_root()
    timeout_s = max(1, min(30, int(config.security.execution_timeout_seconds or 5)))
    git_env = _build_git_env()
    mutating = operation in GIT_WORKFLOW_MUTATING_OPERATIONS

    try:
        state = await asyncio.to_thread(
            _git_repo_state,
            git_exe=git_exe,
            project_root=project_root,
            timeout_s=timeout_s,
            git_env=git_env,
        )
        if not state.get("success"):
            return state

        current_branch = str(state.get("branch") or "HEAD")
        head_sha = str(state.get("head_sha") or "")
        remote_url = state.get("remote_url")

        preview_commands: list[list[str]] = []
        normalized_args: dict[str, Any] = {}

        if operation == "git_status":
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": [["git", "status", "--short", "--branch"]],
                    "normalized_args": {},
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }
            status = await get_git_status(config, apply_security_filters=True)
            status["operation"] = operation
            status["mutating"] = mutating
            return status

        if operation == "git_log":
            raw_limit = 20 if log_limit is None else int(log_limit)
            limit = max(1, min(200, raw_limit))
            normalized_args["log_limit"] = limit
            preview_commands.append(["git", "log", "--oneline", f"-n{limit}"])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            log_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["log", "--oneline", f"-n{limit}"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if log_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (log_res.stderr or log_res.stdout).strip() or "git log failed",
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "limit": limit,
                "log": log_res.stdout,
            }

        if operation == "git_diff":
            args = ["diff"]
            if diff_ref:
                args.append(diff_ref.strip())
                normalized_args["diff_ref"] = diff_ref.strip()
            else:
                normalized_args["diff_ref"] = None
            preview_commands.append(["git", *args])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            diff_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=args,
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if diff_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (diff_res.stderr or diff_res.stdout).strip() or "git diff failed",
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "diff": diff_res.stdout,
            }

        if operation == "create_task_branch":
            try:
                next_branch = _normalize_task_branch(
                    task_slug=task_slug,
                    task_branch=task_branch,
                    date_utc=date_utc,
                )
            except ValueError as exc:
                return {"success": False, "operation": operation, "error": str(exc)}

            if not next_branch.startswith(GIT_WORKFLOW_TASK_BRANCH_PREFIX):
                return {
                    "success": False,
                    "operation": operation,
                    "error": "Task branch must start with 'chatgpt/'",
                }

            if next_branch in GIT_WORKFLOW_PROTECTED_BRANCHES:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "Task branch name collides with protected branch",
                }

            normalized_args = {
                "task_branch": next_branch,
                "base_branch": base_branch,
            }
            preview_commands.extend(
                [
                    ["git", "fetch", "origin", "--prune"],
                    ["git", "checkout", "-b", next_branch, f"origin/{base_branch}"],
                ]
            )

            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            fetch_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["fetch", "origin", "--prune"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if fetch_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (fetch_res.stderr or fetch_res.stdout).strip() or "git fetch failed",
                }

            local_branch_check = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["show-ref", "--verify", "--quiet", f"refs/heads/{next_branch}"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if local_branch_check.returncode == 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Local branch already exists: {next_branch}",
                }

            remote_branch_check = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{next_branch}"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if remote_branch_check.returncode == 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Remote branch already exists: origin/{next_branch}",
                }

            base_check = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{base_branch}"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if base_check.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Base branch not found on origin: {base_branch}",
                }

            checkout_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["checkout", "-b", next_branch, f"origin/{base_branch}"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if checkout_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (checkout_res.stderr or checkout_res.stdout).strip()
                    or "git checkout -b failed",
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "task_branch": next_branch,
                "base_branch": base_branch,
                "message": f"Created and checked out {next_branch} from origin/{base_branch}",
            }

        if operation == "git_add":
            if not current_branch.startswith(GIT_WORKFLOW_TASK_BRANCH_PREFIX):
                return {
                    "success": False,
                    "operation": operation,
                    "error": "git_add is only allowed on chatgpt/* task branches",
                }

            normalized_pathspecs = _normalize_git_pathspecs(pathspecs)
            for pathspec in normalized_pathspecs:
                if pathspec in {".", "./"}:
                    continue
                is_safe, error = is_safe_path(pathspec, config)
                if not is_safe:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": f"Blocked pathspec '{pathspec}': {error}",
                    }

            normalized_args = {"pathspecs": normalized_pathspecs}
            preview_commands.append(["git", "add", "--", *normalized_pathspecs])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            add_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["add", "--", *normalized_pathspecs],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if add_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (add_res.stderr or add_res.stdout).strip() or "git add failed",
                }

            staged_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["diff", "--name-only", "--cached"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            staged_files = [
                line.strip()
                for line in staged_res.stdout.splitlines()
                if isinstance(line, str) and line.strip()
            ]

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "pathspecs": normalized_pathspecs,
                "staged_files": staged_files,
            }

        if operation == "git_commit":
            if not current_branch.startswith(GIT_WORKFLOW_TASK_BRANCH_PREFIX):
                return {
                    "success": False,
                    "operation": operation,
                    "error": "git_commit is only allowed on chatgpt/* task branches",
                }

            message = (commit_message or "").strip()
            if not message:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "commit_message is required for git_commit",
                }

            normalized_args = {"commit_message": message}
            preview_commands.append(["git", "commit", "-m", message])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            staged_quiet = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["diff", "--cached", "--quiet"],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if staged_quiet.returncode == 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "No staged changes to commit",
                }

            commit_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["commit", "-m", message],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if commit_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (commit_res.stderr or commit_res.stdout).strip()
                    or "git commit failed",
                }

            new_head = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["rev-parse", "HEAD"],
                timeout_s=timeout_s,
                git_env=git_env,
            )

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "branch": current_branch,
                "commit_sha": new_head.stdout.strip() if new_head.returncode == 0 else None,
                "output": commit_res.stdout,
            }

        if operation == "git_push_task_branch":
            if current_branch in GIT_WORKFLOW_PROTECTED_BRANCHES:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Direct push to protected branch is blocked: {current_branch}",
                }
            if not current_branch.startswith(GIT_WORKFLOW_TASK_BRANCH_PREFIX):
                return {
                    "success": False,
                    "operation": operation,
                    "error": "Push is only allowed from chatgpt/* task branches",
                }

            normalized_args = {"remote": "origin", "branch": current_branch}
            preview_commands.append(["git", "push", "-u", "origin", current_branch])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            push_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["push", "-u", "origin", current_branch],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if push_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (push_res.stderr or push_res.stdout).strip() or "git push failed",
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "branch": current_branch,
                "remote": "origin",
                "output": push_res.stdout,
            }

        if operation == "create_pr":
            if current_branch in GIT_WORKFLOW_PROTECTED_BRANCHES:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"PR source branch must not be protected: {current_branch}",
                }
            if not current_branch.startswith(GIT_WORKFLOW_TASK_BRANCH_PREFIX):
                return {
                    "success": False,
                    "operation": operation,
                    "error": "PR creation is only allowed from chatgpt/* task branches",
                }

            title = (pr_title or "").strip() or f"chore(mcp): {current_branch}"
            body = (pr_body or "").strip() or (
                "Automated change-set from Genesis-Core MCP workflow.\n\n"
                "Please review and merge if CI is green."
            )
            compare_url = _build_compare_url(
                remote_url,
                base_branch=base_branch,
                head_branch=current_branch,
            )

            normalized_args = {
                "base_branch": base_branch,
                "head_branch": current_branch,
                "title": title,
                "body": body,
            }
            preview_commands.append(
                [
                    "gh",
                    "pr",
                    "create",
                    "--base",
                    base_branch,
                    "--head",
                    current_branch,
                    "--title",
                    title,
                    "--body",
                    body,
                ]
            )
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": mutating,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                    "compare_url": compare_url,
                }

            gh_exe = shutil.which("gh")
            if gh_exe:
                pr_res = await asyncio.to_thread(
                    subprocess.run,
                    args=[
                        gh_exe,
                        "pr",
                        "create",
                        "--base",
                        base_branch,
                        "--head",
                        current_branch,
                        "--title",
                        title,
                        "--body",
                        body,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=timeout_s,
                    stdin=subprocess.DEVNULL,
                    env=git_env,
                    cwd=str(project_root),
                )
                if pr_res.returncode == 0:
                    return {
                        "success": True,
                        "operation": operation,
                        "mutating": mutating,
                        "created": True,
                        "base_branch": base_branch,
                        "head_branch": current_branch,
                        "pr_url": pr_res.stdout.strip() or None,
                        "output": pr_res.stdout,
                    }

                # gh is present but failed; keep a deterministic fallback.
                return {
                    "success": False,
                    "operation": operation,
                    "error": (pr_res.stderr or pr_res.stdout).strip() or "gh pr create failed",
                    "created": False,
                    "compare_url": compare_url,
                    "fallback": (
                        f"Open compare URL and create PR manually: {compare_url}"
                        if compare_url
                        else "Open GitHub and create PR manually from current task branch."
                    ),
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": mutating,
                "created": False,
                "compare_url": compare_url,
                "fallback": (
                    f"`gh` is not available. Create PR manually: {compare_url}"
                    if compare_url
                    else "`gh` is not available and compare URL could not be derived."
                ),
            }

        if operation == "git_pull_ff_only":
            normalized_args = {"remote": "origin", "branch": current_branch}
            preview_commands.append(["git", "pull", "--ff-only", "origin", current_branch])
            if dry_run:
                return {
                    "success": True,
                    "operation": operation,
                    "preview": True,
                    "mutating": False,
                    "commands": preview_commands,
                    "normalized_args": normalized_args,
                    "state": {
                        "branch": current_branch,
                        "head_sha": head_sha,
                    },
                }

            pull_res = await _run_git_command_async(
                git_exe,
                project_root=project_root,
                args=["pull", "--ff-only", "origin", current_branch],
                timeout_s=timeout_s,
                git_env=git_env,
            )
            if pull_res.returncode != 0:
                return {
                    "success": False,
                    "operation": operation,
                    "error": (pull_res.stderr or pull_res.stdout).strip()
                    or "git pull --ff-only failed",
                }

            return {
                "success": True,
                "operation": operation,
                "mutating": False,
                "output": pull_res.stdout,
            }

        return {"success": False, "operation": operation, "error": "Unsupported operation"}

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "operation": operation,
            "error": f"Command timed out after {timeout_s} seconds",
        }
    except Exception as e:
        logger.error(f"Error executing git workflow operation '{operation}': {e}")
        return {
            "success": False,
            "operation": operation,
            "error": f"Error executing git workflow operation: {str(e)}",
        }
