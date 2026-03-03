from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts import run_skill


def test_run_skill_stable_vertical_slice_pass(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            "genesis_backtest_verify",
            "--manifest",
            "stable",
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "[SKILL] PASS" in proc.stdout


def test_run_skill_config_authority_lifecycle_check_pass(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            "config_authority_lifecycle_check",
            "--manifest",
            "dev",
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "[SKILL] PASS" in proc.stdout


def test_run_skill_shadow_error_rate_check_pass(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            "shadow_error_rate_check",
            "--manifest",
            "dev",
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "[SKILL] PASS" in proc.stdout


def test_run_skill_feature_parity_check_pass(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            "feature_parity_check",
            "--manifest",
            "dev",
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "[SKILL] PASS" in proc.stdout


def test_run_skill_ri_off_parity_artifact_check_pass(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_skill.py"

    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--skill",
            "ri_off_parity_artifact_check",
            "--manifest",
            "dev",
            "--dry-run",
            "--audit-file",
            str(tmp_path / "audit.jsonl"),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

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
