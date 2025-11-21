"""
Smoke test för Optuna cache reuse fix (Alternativ B).

Kör optimizer två gånger med identisk konfiguration för att verifiera:
1. Första körningen skapar backtester och cache
2. Andra körningen återanvänder cache och loggar '[CACHE] Trial X reusing...'
3. Cache hit rate loggas korrekt
4. Inga 0.0-scores för cachade trials

Usage:
    python scripts/test_optuna_cache_reuse.py

Environment:
    GENESIS_FAST_WINDOW=1
    GENESIS_PRECOMPUTE_FEATURES=1
    GENESIS_RANDOM_SEED=42
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from core.optimizer.runner import run_optimizer  # noqa: E402


def main():
    """Run optimizer twice to test cache reuse."""
    # Use minimal test config for fast smoke test (3 trials, 10 days)
    config_path = Path("config/optimizer/cache_test_clean.yaml")

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("   Please ensure the config exists before running this test.")
        return 1

    print("=" * 80)
    print("OPTUNA CACHE REUSE SMOKE TEST")
    print("=" * 80)
    print()
    print("This test runs the optimizer twice with the same configuration:")
    print("  1. First run: Creates backtests and cache files")
    print("  2. Second run: Should reuse cache and log '[CACHE] Trial X reusing...'")
    print()
    print("Expected outcomes:")
    print("  ✓ First run shows '[Runner] Trial trial_XXX klar...' (new backtests)")
    print("  ✓ Second run shows '[CACHE] Trial X reusing cached score...'")
    print("  ✓ Cache stats show >0% hit rate in second run")
    print("  ✓ No 0.0 scores for cached trials")
    print()
    print("Starting first run automatically in 3 seconds...")
    time.sleep(3)

    # First run - creates cache
    print("\n" + "=" * 80)
    print("RUN 1: Initial run (creates cache)")
    print("=" * 80)
    try:
        run_optimizer(config_path)
        print("\n✅ First run completed successfully")
    except Exception as e:
        print(f"\n❌ First run failed: {e}")
        return 1

    print("\n" + "=" * 80)
    print("RUN 1 COMPLETE - Cache should now exist")
    print("=" * 80)
    print()
    print("Check the logs above for:")
    print("  - '[Runner] Trial trial_XXX klar...' messages (new backtests)")
    print("  - No '[CACHE]' messages expected in first run")
    print()
    print("Starting second run automatically in 3 seconds...")
    time.sleep(3)

    # Second run - should reuse cache
    print("\n" + "=" * 80)
    print("RUN 2: Cache reuse test")
    print("=" * 80)
    try:
        run_optimizer(config_path)
        print("\n✅ Second run completed successfully")
    except Exception as e:
        print(f"\n❌ Second run failed: {e}")
        return 1

    print("\n" + "=" * 80)
    print("RUN 2 COMPLETE - Verify cache reuse")
    print("=" * 80)
    print()
    print("✓ Check the logs above for:")
    print("  1. '[CACHE] Trial X reusing cached score Y.YY' messages")
    print("  2. '[CACHE STATS] N/M trials cached (X% hit rate)'")
    print("  3. Cache hit rate should be >50% for second run")
    print()
    print("✓ Verify in results/hparam_search/<run_id>/:")
    print("  1. trials.csv - no 0.0 scores")
    print("  2. best_trial.json - score > 0")
    print("  3. _cache/ directory contains .json files")
    print()
    print("If you see '[CACHE]' messages and cache hit rate >0%, the fix works! 🎉")
    return 0


if __name__ == "__main__":
    sys.exit(main())
