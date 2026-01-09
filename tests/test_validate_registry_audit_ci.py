from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import scripts.validate_registry as vr


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for audit CI validation tests",
)
def test_validate_registry_audit_single_commit_stable_change_allows_base_sha(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CI audit rule must support PRs where stable.json + audit entry are in same single commit.

    This happens in squash-import style PRs. The rule should then require:
    - action='break_glass_override'
    - commit_sha points to base_ref (not HEAD)
    - approved_by is present
    """

    repo = tmp_path
    _git(repo, "init")
    _git(repo, "checkout", "-b", "master")
    _git(repo, "config", "user.email", "ci@example.test")
    _git(repo, "config", "user.name", "CI")

    manifests = repo / "registry" / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    audit_dir = repo / "registry" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    stable_path = manifests / "stable.json"
    stable_path.write_text(
        '{"registry_version":1,"skills":[],"compacts":[]}',
        encoding="utf-8",
    )
    (manifests / "dev.json").write_text(
        '{"registry_version":1,"skills":[],"compacts":[]}',
        encoding="utf-8",
    )

    _git(repo, "add", "registry/manifests/stable.json", "registry/manifests/dev.json")
    _git(repo, "commit", "-m", "base")
    base_sha = _git(repo, "rev-parse", "HEAD")

    # Single commit that changes stable manifest and adds audit entry.
    stable_path.write_text(
        '{"registry_version":1,"skills":[{"id":"s1","version":"1.0.0"}],"compacts":[]}',
        encoding="utf-8",
    )

    entry = {
        "ts": "2026-01-09T00:00:00Z",
        "action": "break_glass_override",
        "actor": "ci",
        "commit_sha": base_sha,
        "items": [
            {
                "kind": "skill",
                "id": "s1",
                "version": "1.0.0",
                "from": "dev",
                "to": "stable",
            }
        ],
        "reason": "CI test: single-commit stable manifest change.",
        "approved_by": ["ci"],
    }

    (audit_dir / "break_glass.jsonl").write_text(
        json.dumps(entry, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    _git(repo, "add", "registry/manifests/stable.json", "registry/audit/break_glass.jsonl")
    _git(repo, "commit", "-m", "squash-style stable change")

    monkeypatch.setattr(vr, "_repo_root", lambda: repo)

    errors = vr._validate_audit_for_stable_change(base_ref=base_sha)
    assert errors == []
