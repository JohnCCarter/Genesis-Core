#!/usr/bin/env python3
"""
Quick Optuna smoke test for determinism verification.
Runs a minimal optimization with fixed parameters.
"""

import sys
from pathlib import Path


def _find_repo_root() -> Path:
    """Find repository root from current file location."""

    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    return Path(__file__).resolve().parent.parent


# Add src to path
src_path = _find_repo_root() / "src"
sys.path.insert(0, str(src_path))

from core.optimizer.runner import run_optimizer  # noqa: E402

if __name__ == "__main__":
    config_path = Path("config/optimizer/determinism_smoke_test.yaml")
    print(f"[SMOKE] Running determinism test with config: {config_path}")
    run_optimizer(config_path)
    print("[SMOKE] Test complete!")
