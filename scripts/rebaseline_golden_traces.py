#!/usr/bin/env python3
"""
Re-baseline golden trace snapshots after intentional logic changes.

This script generates new golden snapshots by running the actual strategy
code and saving the outputs. Use this ONLY after verifying that code changes
are intentional and correct.

Usage:
    # Re-baseline all golden traces
    python scripts/rebaseline_golden_traces.py --all

    # Re-baseline specific test
    python scripts/rebaseline_golden_traces.py --test test_param_to_feature_trace

    # Dry-run (show what would be updated without writing)
    python scripts/rebaseline_golden_traces.py --all --dry-run

Safety:
    - Always commit current code before re-baselining
    - Review generated snapshots before committing
    - Include git SHA and reason in snapshot metadata
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from core.backtest.metrics import calculate_metrics
from core.pipeline import GenesisPipeline
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features
from core.utils.optuna_helpers import set_global_seeds

SNAPSHOTS_DIR = REPO_ROOT / "tests" / "golden_traces" / "snapshots"


def get_git_sha() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()[:12]
    except Exception:
        return "unknown"


def rebaseline_param_to_feature(dry_run: bool = False) -> None:
    """Re-baseline Test 1: Parameter → Feature determinism."""
    print("\n[1/3] Re-baselining Parameter → Feature trace...")

    # Load champion params (if exists, otherwise use defaults)
    params_path = SNAPSHOTS_DIR / "golden_champion_params.json"
    if params_path.exists():
        with open(params_path) as f:
            champion_params = json.load(f)
    else:
        print(f"  WARNING: {params_path} not found. Using empty config.")
        champion_params = {}

    # Create frozen candles (100 bars of tBTCUSD 1h)
    # In production, this should be extracted from real frozen data
    print("  Note: Frozen candles should be created manually from data/raw/tBTCUSD_1h_frozen.parquet")
    print("  Skipping candles generation in this script.")

    # TODO: Extract features from frozen candles
    # For now, just create a placeholder
    features_snapshot = {
        "_baseline_meta": {
            "version": "v1",
            "git_sha": get_git_sha(),
            "date": datetime.now().isoformat(),
            "reason": "Initial baseline or manual update",
        },
        # Actual features would be extracted here
        "atr_14": 0.0,
        "ema_20": 0.0,
        "rsi_14": 0.0,
    }

    features_path = SNAPSHOTS_DIR / "golden_features_v1.json"

    if dry_run:
        print(f"  [DRY-RUN] Would write to: {features_path}")
    else:
        with open(features_path, "w") as f:
            json.dump(features_snapshot, f, indent=2)
        print(f"  ✓ Written: {features_path}")


def rebaseline_feature_to_decision(dry_run: bool = False) -> None:
    """Re-baseline Test 2: Feature → Decision determinism."""
    print("\n[2/3] Re-baselining Feature → Decision trace...")

    # Load golden features (must exist)
    features_path = SNAPSHOTS_DIR / "golden_features_v1.json"
    params_path = SNAPSHOTS_DIR / "golden_champion_params.json"

    if not features_path.exists() or not params_path.exists():
        print(f"  ERROR: Missing dependencies: {features_path} or {params_path}")
        return

    with open(features_path) as f:
        golden_features = json.load(f)
    with open(params_path) as f:
        champion_params = json.load(f)

    # Mock probability output
    probas = {"UP": 0.62, "DOWN": 0.38, "NEUTRAL": 0.15}

    # Compute confidence
    atr_pct = golden_features.get("atr_14", 100.0) / golden_features.get("close", 50000.0) * 100
    confidence = compute_confidence(
        probas=probas,
        atr_pct=atr_pct,
        spread_bp=1.0,
        volume_score=0.85,
        data_quality=1.0,
        config=champion_params,
    )

    # Make decision
    action, action_meta = decide(
        policy="backtest",
        probas=probas,
        confidence=confidence,
        regime="bull",
        state={},
        risk_ctx={"current_equity": 10000.0},
        cfg=champion_params,
    )

    decision_snapshot = {
        "_baseline_meta": {
            "version": "v1",
            "git_sha": get_git_sha(),
            "date": datetime.now().isoformat(),
            "reason": "Initial baseline or manual update",
        },
        "action": action,
        "size": action_meta.get("size"),
        "confidence": confidence["overall"],
        "reasons": action_meta.get("reasons", []),
        "blocked_by": action_meta.get("blocked_by"),
    }

    decision_path = SNAPSHOTS_DIR / "golden_decision_v1.json"

    if dry_run:
        print(f"  [DRY-RUN] Would write to: {decision_path}")
    else:
        with open(decision_path, "w") as f:
            json.dump(decision_snapshot, f, indent=2)
        print(f"  ✓ Written: {decision_path}")


def rebaseline_backtest_e2e(dry_run: bool = False) -> None:
    """Re-baseline Test 3: End-to-End backtest determinism."""
    print("\n[3/3] Re-baselining End-to-End Backtest trace...")

    params_path = SNAPSHOTS_DIR / "golden_champion_params.json"
    if not params_path.exists():
        print(f"  ERROR: Missing {params_path}")
        return

    with open(params_path) as f:
        champion_params = json.load(f)

    # Fixed seed
    set_global_seeds(42)

    # Create engine
    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)

    engine = pipeline.create_engine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2024-06-01",
        end_date="2024-08-01",
        capital=10000.0,
        commission=0.002,
        slippage=0.0005,
        warmup_bars=150,
        fast_window=True,
    )

    # Load data
    engine.load_data()

    # Run backtest
    results = engine.run(policy="backtest", configs=champion_params, verbose=False)

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Create snapshot
    backtest_snapshot = {
        "_baseline_meta": {
            "version": "v1",
            "git_sha": get_git_sha(),
            "date": datetime.now().isoformat(),
            "reason": "Initial baseline or manual update",
            "config": {
                "symbol": "tBTCUSD",
                "timeframe": "1h",
                "start": "2024-06-01",
                "end": "2024-08-01",
            },
        },
        "trades": results["trades"],
        "summary": results["summary"],
        "metrics": metrics,
    }

    backtest_path = SNAPSHOTS_DIR / "golden_backtest_v1.json"

    if dry_run:
        print(f"  [DRY-RUN] Would write to: {backtest_path}")
        print(f"  Trades: {len(results['trades'])}")
        print(f"  Final equity: {results['summary']['final_capital']:.2f}")
    else:
        with open(backtest_path, "w") as f:
            json.dump(backtest_snapshot, f, indent=2)
        print(f"  ✓ Written: {backtest_path}")
        print(f"  Trades: {len(results['trades'])}")
        print(f"  Final equity: {results['summary']['final_capital']:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Re-baseline golden trace snapshots")
    parser.add_argument(
        "--all", action="store_true", help="Re-baseline all golden traces"
    )
    parser.add_argument(
        "--test",
        choices=[
            "test_param_to_feature_trace",
            "test_feature_to_decision_trace",
            "test_backtest_e2e_trace",
        ],
        help="Re-baseline specific test",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be updated without writing"
    )

    args = parser.parse_args()

    if not args.all and not args.test:
        parser.error("Must specify --all or --test")

    # Ensure snapshots directory exists
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Check for champion params
    params_path = SNAPSHOTS_DIR / "golden_champion_params.json"
    if not params_path.exists():
        print(f"WARNING: {params_path} not found.")
        print("You should copy a known-good champion config there first:")
        print(f"  cp config/strategy/champions/tBTCUSD_1h.json {params_path}")
        print()

    # Run re-baseline operations
    if args.all or args.test == "test_param_to_feature_trace":
        rebaseline_param_to_feature(dry_run=args.dry_run)

    if args.all or args.test == "test_feature_to_decision_trace":
        rebaseline_feature_to_decision(dry_run=args.dry_run)

    if args.all or args.test == "test_backtest_e2e_trace":
        rebaseline_backtest_e2e(dry_run=args.dry_run)

    print("\n✓ Re-baseline complete!")
    if not args.dry_run:
        print("\nNext steps:")
        print("  1. Review generated snapshots in tests/golden_traces/snapshots/")
        print("  2. Run tests: pytest tests/golden_traces/ -v")
        print("  3. Commit snapshots with a descriptive message")


if __name__ == "__main__":
    main()
