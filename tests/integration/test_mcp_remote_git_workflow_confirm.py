from __future__ import annotations

import pytest

import mcp_server.remote_server as remote


@pytest.fixture(autouse=True)
def _reset_confirm_store() -> None:
    remote._CONFIRM_TOKEN_STORE.clear()


@pytest.mark.asyncio
async def test_mutating_git_workflow_requires_preview_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_git_workflow_operation(  # type: ignore[no-untyped-def]
        operation,
        config,
        *,
        dry_run=False,
        **kwargs,
    ):
        _ = config
        if dry_run:
            return {
                "success": True,
                "operation": operation,
                "preview": True,
                "mutating": operation in remote.GIT_WORKFLOW_MUTATING_OPERATIONS,
                "normalized_args": {"commit_message": kwargs.get("commit_message")},
                "state": {"branch": "chatgpt/20260219-test", "head_sha": "abc123"},
            }
        return {"success": True, "operation": operation, "executed": True}

    monkeypatch.setattr(remote, "git_workflow_operation", fake_git_workflow_operation)

    missing = await remote._dispatch_git_workflow(
        operation="git_commit",
        preview=False,
        confirm_token=None,
        commit_message="test commit",
    )
    assert missing["success"] is False
    assert "preview=true" in missing["error"]

    preview = await remote._dispatch_git_workflow(
        operation="git_commit",
        preview=True,
        confirm_token=None,
        commit_message="test commit",
    )
    assert preview["success"] is True
    assert preview["confirmation_required"] is True
    token = preview["confirm_token"]
    assert isinstance(token, str) and token

    execute = await remote._dispatch_git_workflow(
        operation="git_commit",
        preview=False,
        confirm_token=token,
        commit_message="test commit",
    )
    assert execute["success"] is True
    assert execute["executed"] is True

    reused = await remote._dispatch_git_workflow(
        operation="git_commit",
        preview=False,
        confirm_token=token,
        commit_message="test commit",
    )
    assert reused["success"] is False
    assert "Invalid or expired" in reused["error"]


@pytest.mark.asyncio
async def test_non_mutating_git_workflow_runs_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_git_workflow_operation(  # type: ignore[no-untyped-def]
        operation,
        config,
        *,
        dry_run=False,
        **_kwargs,
    ):
        _ = config
        if dry_run:
            return {
                "success": True,
                "operation": operation,
                "preview": True,
                "mutating": operation in remote.GIT_WORKFLOW_MUTATING_OPERATIONS,
                "normalized_args": {},
                "state": {"branch": "chatgpt/20260219-test", "head_sha": "abc123"},
            }
        return {"success": True, "operation": operation, "status": "ok"}

    monkeypatch.setattr(remote, "git_workflow_operation", fake_git_workflow_operation)

    result = await remote._dispatch_git_workflow(
        operation="git_status",
        preview=False,
        confirm_token=None,
    )
    assert result["success"] is True
    assert result["status"] == "ok"
