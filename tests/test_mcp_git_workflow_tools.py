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
@pytest.mark.parametrize(
    ("input_limit", "expected_limit"),
    [
        (None, 20),
        (0, 1),
        (201, 200),
        (20, 20),
    ],
)
async def test_git_log_dry_run_normalizes_log_limit(
    git_repo: Path, input_limit: int | None, expected_limit: int
) -> None:
    config = _test_config()

    result = await git_workflow_operation(
        "git_log",
        config,
        dry_run=True,
        log_limit=input_limit,
    )

    assert result["success"] is True
    assert result["preview"] is True
    assert result["normalized_args"]["log_limit"] == expected_limit
    assert result["commands"][0] == ["git", "log", "--oneline", f"-n{expected_limit}"]


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


@pytest.mark.asyncio
async def test_create_pr_with_gh_uses_thread_boundary(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _test_config()

    create_branch = await git_workflow_operation(
        "create_task_branch",
        config,
        dry_run=False,
        task_slug="pr-thread-boundary",
        date_utc="20260219",
    )
    assert create_branch["success"] is True

    _git(git_repo, "remote", "set-url", "origin", "https://github.com/JohnCCarter/Genesis-Core.git")

    thread_funcs: list[object] = []

    async def fake_to_thread(func, *args, **kwargs):  # type: ignore[no-untyped-def]
        thread_funcs.append(func)
        return func(*args, **kwargs)

    real_which = shutil.which
    real_run = subprocess.run

    def fake_which(name: str) -> str | None:
        if name == "gh":
            return "gh"
        return real_which(name)

    def fake_run(args, capture_output, text, check, timeout=None, **kwargs):  # type: ignore[no-untyped-def]
        cmd = list(args)
        if cmd and cmd[0] == "gh":
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="https://example.invalid/pr/1\n",
                stderr="",
            )
        return real_run(
            args,
            capture_output=capture_output,
            text=text,
            check=check,
            timeout=timeout,
            **kwargs,
        )

    monkeypatch.setattr(tools_mod.asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(tools_mod.shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)

    res = await git_workflow_operation(
        "create_pr",
        config,
        dry_run=False,
        pr_title="chore: async boundary",
        pr_body="body",
    )

    assert res["success"] is True
    assert res["created"] is True
    assert res["pr_url"] == "https://example.invalid/pr/1"
    assert any(func is fake_run for func in thread_funcs)
