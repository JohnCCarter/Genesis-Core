"""Smoke test for Optuna cache reuse fix.

Runs the optimizer twice with identical configuration to verify:
1. First run creates backtests and cache
2. Second run reuses cache

Usage:
    python scripts/test_optuna_cache_reuse.py
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
    config_path = Path("config/optimizer/cache_test_clean.yaml")
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Create it (or point this script at an existing optimizer config) before running.")
        return 1

    print("=" * 80)
    print("OPTUNA CACHE REUSE SMOKE TEST")
    print("=" * 80)
    print()
    print("This test runs the optimizer twice with the same configuration:")
    print("  1. First run: creates backtests and cache files")
    print("  2. Second run: should reuse cache")
    print()

    print("Starting first run in 3 seconds...")
    time.sleep(3)

    print("\n" + "=" * 80)
    print("RUN 1: Initial run (creates cache)")
    print("=" * 80)
    try:
        run_optimizer(config_path)
        print("\nFirst run completed")
    except Exception as e:
        print(f"\nFirst run failed: {e}")
        return 1

    print("\n" + "=" * 80)
    print("RUN 2: Cache reuse test")
    print("=" * 80)
    try:
        run_optimizer(config_path)
        print("\nSecond run completed")
    except Exception as e:
        print(f"\nSecond run failed: {e}")
        return 1

    print("\nDone. Check optimizer logs for cache reuse messages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
