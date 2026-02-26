from __future__ import annotations

import shutil
import subprocess

import pytest

from mcp_server.config import FeaturesConfig, MCPConfig, SecurityConfig
from mcp_server.tools import get_git_status


@pytest.mark.asyncio
async def test_get_git_status_apply_security_filters_hides_blocked_and_redacts_remote_url(
    monkeypatch,
) -> None:
    cfg = MCPConfig(
        security=SecurityConfig(
            allowed_paths=["src", "config"],
            blocked_patterns=[".env", "config/runtime.json"],
            execution_timeout_seconds=5,
            max_file_size_mb=1,
        ),
        features=FeaturesConfig(file_operations=True, code_execution=False, git_integration=True),
    )

    monkeypatch.setattr(shutil, "which", lambda _: "git")

    def _cp(args: list[str], stdout: str = "", stderr: str = "", returncode: int = 0):
        return subprocess.CompletedProcess(
            args=args, returncode=returncode, stdout=stdout, stderr=stderr
        )

    def fake_run(  # type: ignore[no-untyped-def]
        args,
        capture_output,
        text,
        check,
        timeout=None,
        stdin=None,
        env=None,
        **kwargs,
    ):
        cmd = list(args)[3:]

        if cmd[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return _cp(list(args), stdout="true\n")
        if cmd[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return _cp(list(args), stdout="main\n")
        if cmd[:2] == ["status", "--porcelain"]:
            return _cp(
                list(args),
                stdout="?? .env\n M src/core/pipeline.py\nA  config/runtime.json\n",
            )
        if cmd[:3] == ["config", "--get", "remote.origin.url"]:
            return _cp(list(args), stdout="https://user@github.com/org/repo.git\n")

        return _cp(list(args), returncode=1, stderr="unexpected")

    monkeypatch.setattr(subprocess, "run", fake_run)

    res = await get_git_status(cfg, apply_security_filters=True)
    assert res["success"] is True
    assert ".env" not in res["untracked_files"]
    assert "config/runtime.json" not in res["staged_files"]
    assert "src/core/pipeline.py" in res["modified_files"]
    assert res["remote_url"] == "https://github.com/org/repo.git"
