from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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
