from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts import run_skill


def _run_skill_dry_run(
    tmp_path: Path, *, skill: str, manifest: str
) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            skill,
            "--manifest",
            manifest,
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("skill", "manifest"),
    [
        ("genesis_backtest_verify", "stable"),
        ("config_authority_lifecycle_check", "dev"),
        ("shadow_error_rate_check", "dev"),
        ("feature_parity_check", "dev"),
        ("ri_off_parity_artifact_check", "dev"),
    ],
)
def test_run_skill_vertical_slice_pass(tmp_path: Path, skill: str, manifest: str) -> None:
    proc = _run_skill_dry_run(tmp_path, skill=skill, manifest=manifest)

    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "[SKILL] PASS" in proc.stdout


def test_validate_pytest_selectors_args_rejects_invalid_selectors() -> None:
    ok, detail, selectors, pytest_args = run_skill._validate_pytest_selectors_args(
        {"selectors": []}
    )

    assert ok is False
    assert detail == {"reason": "invalid_selectors"}
    assert selectors == []
    assert pytest_args == []


def test_validate_pytest_selectors_args_rejects_invalid_pytest_args() -> None:
    ok, detail, selectors, pytest_args = run_skill._validate_pytest_selectors_args(
        {
            "selectors": [
                "tests/test_config_ssot.py::test_regime_unified_alias_non_dict_is_rejected"
            ],
            "pytest_args": ["-k", 1],
        }
    )

    assert ok is False
    assert detail == {"reason": "invalid_pytest_args"}
    assert selectors == []
    assert pytest_args == []
