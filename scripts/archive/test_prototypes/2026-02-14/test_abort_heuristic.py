"""Smoke test for abort heuristic.

This is a manual script (not a pytest test) intended to validate that the optimizer's abort
heuristic behaves as expected.

Usage:
    python scripts/test_abort_heuristic.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def _bootstrap_src_on_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    return repo_root


_bootstrap_src_on_path()

from core.optimizer.runner import run_optimizer  # noqa: E402


def main() -> int:
    config_path = Path("config/optimizer/test_abort_heuristic.yaml")
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Create it (or point this script at an existing optimizer config) before running.")
        return 1

    print("=" * 80)
    print("ABORT HEURISTIC SMOKE TEST")
    print("=" * 80)
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    try:
        run_optimizer(config_path)
    except Exception as e:
        print(f"Run failed: {e}")
        return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
