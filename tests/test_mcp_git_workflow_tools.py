from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

import mcp_server.tools as tools_mod
from mcp_server.config import FeaturesConfig, MCPConfig, SecurityConfig
from mcp_server.tools import git_workflow_operation


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=check,
    )


def _test_config() -> MCPConfig:
    return MCPConfig(
        security=SecurityConfig(
            allowed_paths=["."],
            blocked_patterns=[".git", "__pycache__", "*.pyc", ".env"],
            execution_timeout_seconds=15,
            max_file_size_mb=10,
        ),
        features=FeaturesConfig(file_operations=True, code_execution=False, git_integration=True),
    )


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    origin = tmp_path / "origin.git"
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    _git(tmp_path, "init", "--bare", str(origin))
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")

    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "seed")
    _git(repo, "checkout", "-b", "feature/composable-strategy-phase2")
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-u", "origin", "feature/composable-strategy-phase2")

    monkeypatch.setattr(tools_mod, "get_project_root", lambda: repo)
    return repo


@pytest.mark.asyncio
async def test_create_task_branch_from_base_branch(git_repo: Path) -> None:
    config = _test_config()

    preview = await git_workflow_operation(
        "create_task_branch",
        config,
        dry_run=True,
        task_slug="Fix MCP Git Flow",
        date_utc="20260219",
    )
    assert preview["success"] is True
    assert preview["preview"] is True
    assert preview["normalized_args"]["task_branch"] == "chatgpt/20260219-fix-mcp-git-flow"

    execute = await git_workflow_operation(
        "create_task_branch",
        config,
        dry_run=False,
        task_slug="Fix MCP Git Flow",
        date_utc="20260219",
    )
    assert execute["success"] is True
    assert execute["task_branch"] == "chatgpt/20260219-fix-mcp-git-flow"

    current = _git(git_repo, "branch", "--show-current")
    assert current.stdout.strip() == "chatgpt/20260219-fix-mcp-git-flow"


@pytest.mark.asyncio
async def test_push_to_protected_branch_is_blocked(git_repo: Path) -> None:
    config = _test_config()
    _git(git_repo, "checkout", "feature/composable-strategy-phase2")

    result = await git_workflow_operation("git_push_task_branch", config, dry_run=False)
    assert result["success"] is False
    assert "protected branch" in result["error"]


@pytest.mark.asyncio
async def test_add_commit_push_task_branch_flow(git_repo: Path) -> None:
    config = _test_config()

    create_branch = await git_workflow_operation(
        "create_task_branch",
        config,
        dry_run=False,
        task_slug="pipeline-cleanup",
        date_utc="20260219",
    )
    assert create_branch["success"] is True
    task_branch = create_branch["task_branch"]

    (git_repo / "tmp_change.txt").write_text("hello\n", encoding="utf-8")

    add_res = await git_workflow_operation(
        "git_add",
        config,
        dry_run=False,
        pathspecs=["tmp_change.txt"],
    )
    assert add_res["success"] is True
    assert "tmp_change.txt" in add_res["staged_files"]

    commit_res = await git_workflow_operation(
        "git_commit",
        config,
        dry_run=False,
        commit_message="chore: add tmp change",
    )
    assert commit_res["success"] is True
    assert commit_res["commit_sha"]

    push_res = await git_workflow_operation("git_push_task_branch", config, dry_run=False)
    assert push_res["success"] is True
    assert push_res["branch"] == task_branch

    ls_remote = _git(git_repo, "ls-remote", "--heads", "origin", task_branch)
    assert task_branch in ls_remote.stdout


@pytest.mark.asyncio
async def test_create_pr_falls_back_without_gh(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _test_config()

    create_branch = await git_workflow_operation(
        "create_task_branch",
        config,
        dry_run=False,
        task_slug="pr-fallback",
        date_utc="20260219",
    )
    assert create_branch["success"] is True

    # Derive deterministic compare URL for fallback message.
    _git(git_repo, "remote", "set-url", "origin", "https://github.com/JohnCCarter/Genesis-Core.git")

    real_which = shutil.which

    def fake_which(name: str) -> str | None:
        if name == "gh":
            return None
        return real_which(name)

    monkeypatch.setattr(tools_mod.shutil, "which", fake_which)

    res = await git_workflow_operation(
        "create_pr",
        config,
        dry_run=False,
        pr_title="chore: test",
        pr_body="body",
    )
    assert res["success"] is True
    assert res["created"] is False
    assert "compare_url" in res
    assert "feature%2Fcomposable-strategy-phase2" in (res["compare_url"] or "")
