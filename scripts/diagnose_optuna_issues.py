#!/usr/bin/env python3
"""Diagnostic script to understand Optuna duplicate and zero-trade issues."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import sys


def load_trial(trial_path: Path) -> dict[str, Any] | None:
    """Load a trial JSON file."""
    try:
        return json.loads(trial_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def diagnose_run(run_dir: Path) -> dict[str, Any]:
    """Diagnose a single optimizer run."""
    trial_files = sorted(run_dir.glob("trial_*.json"))
    
    if not trial_files:
        return {"error": "No trial files found", "run_dir": str(run_dir)}
    
    # Counters
    total_trials = len(trial_files)
    skipped_trials = 0
    duplicate_trials = 0
    error_trials = 0
    zero_trade_trials = 0
    valid_trials = 0
    
    # Parameter tracking
    param_signatures = []
    param_counts = Counter()
    
    # Score tracking
    scores = []
    
    # Zero trade details
    zero_trade_details = []
    
    # Duplicate details
    duplicate_details = []
    
    for trial_path in trial_files:
        trial = load_trial(trial_path)
        if not trial:
            continue
            
        # Track parameters
        params = trial.get("parameters", {})
        param_str = json.dumps(params, sort_keys=True)
        param_signatures.append(param_str)
        param_counts[param_str] += 1
        
        # Check status
        if trial.get("skipped"):
            skipped_trials += 1
            reason = trial.get("reason", "unknown")
            if reason == "duplicate_within_run":
                duplicate_trials += 1
                duplicate_details.append({
                    "trial_id": trial.get("trial_id"),
                    "reason": reason,
                    "params": params,
                })
            continue
            
        if trial.get("error"):
            error_trials += 1
            continue
        
        # Check for zero trades
        score_block = trial.get("score", {})
        metrics = score_block.get("metrics", {})
        num_trades = metrics.get("num_trades", 0)
        
        if num_trades == 0:
            zero_trade_trials += 1
            zero_trade_details.append({
                "trial_id": trial.get("trial_id"),
                "params": params,
                "score": score_block.get("score"),
                "hard_failures": score_block.get("hard_failures", []),
            })
        else:
            valid_trials += 1
            scores.append(score_block.get("score", 0.0))
    
    # Find most common parameters
    most_common_params = param_counts.most_common(5)
    
    # Detect duplicate parameter sets
    duplicate_param_sets = [(params, count) for params, count in param_counts.items() if count > 1]
    
    return {
        "run_dir": str(run_dir),
        "summary": {
            "total_trials": total_trials,
            "skipped_trials": skipped_trials,
            "duplicate_trials": duplicate_trials,
            "error_trials": error_trials,
            "zero_trade_trials": zero_trade_trials,
            "valid_trials": valid_trials,
        },
        "duplicates": {
            "count": len(duplicate_param_sets),
            "examples": duplicate_details[:5],
            "most_common": [
                {
                    "count": count,
                    "params": json.loads(params)
                }
                for params, count in most_common_params[:3]
            ]
        },
        "zero_trades": {
            "count": zero_trade_trials,
            "examples": zero_trade_details[:5],
        },
        "valid": {
            "count": valid_trials,
            "scores": {
                "min": min(scores) if scores else None,
                "max": max(scores) if scores else None,
                "avg": sum(scores) / len(scores) if scores else None,
            }
        }
    }


def print_diagnosis(diagnosis: dict[str, Any]) -> None:
    """Pretty print diagnosis results."""
    print("\n" + "="*80)
    print(f"DIAGNOSIS: {diagnosis['run_dir']}")
    print("="*80)
    
    if "error" in diagnosis:
        print(f"ERROR: {diagnosis['error']}")
        return
    
    summary = diagnosis["summary"]
    print("\nSUMMARY:")
    print(f"  Total trials:      {summary['total_trials']}")
    print(f"  Skipped:           {summary['skipped_trials']} ({summary['skipped_trials']/summary['total_trials']*100:.1f}%)")
    print(f"  - Duplicates:      {summary['duplicate_trials']}")
    print(f"  Errors:            {summary['error_trials']}")
    print(f"  Zero trades:       {summary['zero_trade_trials']}")
    print(f"  Valid (>0 trades): {summary['valid_trials']}")
    
    # Duplicate analysis
    duplicates = diagnosis["duplicates"]
    print(f"\nDUPLICATE ANALYSIS:")
    print(f"  Unique param sets appearing >1 time: {duplicates['count']}")
    
    if duplicates["most_common"]:
        print(f"\n  Most common parameter combinations:")
        for i, item in enumerate(duplicates["most_common"], 1):
            print(f"    {i}. Appeared {item['count']} times")
            print(f"       Sample params: {json.dumps(item['params'], indent=8)[:200]}...")
    
    if duplicates["examples"]:
        print(f"\n  Duplicate trial examples:")
        for ex in duplicates["examples"]:
            print(f"    - {ex['trial_id']}: {ex['reason']}")
    
    # Zero trade analysis
    zero_trades = diagnosis["zero_trades"]
    if zero_trades["count"] > 0:
        print(f"\nZERO TRADE ANALYSIS:")
        print(f"  Trials with 0 trades: {zero_trades['count']}")
        if zero_trades["examples"]:
            print(f"\n  Examples:")
            for ex in zero_trades["examples"]:
                print(f"    - {ex['trial_id']}: score={ex['score']}")
                if ex.get("hard_failures"):
                    print(f"      Hard failures: {ex['hard_failures']}")
                # Show key parameters that might cause zero trades
                params = ex.get("params", {})
                print(f"      Key params:")
                for key in ["thresholds", "htf_fib", "ltf_fib", "multi_timeframe"]:
                    if key in params:
                        print(f"        {key}: {json.dumps(params[key], indent=10)[:150]}...")
    
    # Valid trial analysis
    valid = diagnosis["valid"]
    if valid["count"] > 0:
        print(f"\nVALID TRIALS:")
        print(f"  Count: {valid['count']}")
        scores = valid["scores"]
        if scores["min"] is not None:
            print(f"  Score range: {scores['min']:.2f} to {scores['max']:.2f}")
            print(f"  Average: {scores['avg']:.2f}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python diagnose_optuna_issues.py <run_dir_or_run_id>")
        print("\nExample:")
        print("  python diagnose_optuna_issues.py run_20251103_110227")
        print("  python diagnose_optuna_issues.py results/hparam_search/run_20251103_110227")
        sys.exit(1)
    
    run_path = sys.argv[1]
    run_dir = Path(run_path)
    
    # If just the run_id is given, prepend the results path
    if not run_dir.exists():
        run_dir = Path(__file__).parent.parent / "results" / "hparam_search" / run_path
    
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)
    
    diagnosis = diagnose_run(run_dir)
    print_diagnosis(diagnosis)
    
    # Skip recommendations if there's an error
    if "error" in diagnosis:
        print("\nℹ️  No trials to analyze. This may be a fresh/incomplete run.")
        return
    
    # Print recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    
    summary = diagnosis["summary"]
    duplicates = diagnosis["duplicates"]
    zero_trades = diagnosis["zero_trades"]
    
    if duplicates["count"] > 0:
        print("\n⚠️  DUPLICATE ISSUES DETECTED:")
        print("  - Optuna is suggesting the same parameters repeatedly")
        print("  - This happens when:")
        print("    1. Search space is too narrow (increase ranges)")
        print("    2. TPE sampler degenerates (increase n_startup_trials)")
        print("    3. Float step size causes rounding to same values")
        print("  - Solutions:")
        print("    - Widen search space ranges")
        print("    - Increase n_startup_trials (e.g., 25+)")
        print("    - Reduce float step sizes or remove them")
        print("    - Use multivariate=true and constant_liar=true in TPE")
    
    if zero_trades["count"] > summary["total_trials"] * 0.5:
        print("\n⚠️  EXCESSIVE ZERO-TRADE TRIALS DETECTED:")
        print("  - >50% of trials produce no trades")
        print("  - This happens when:")
        print("    1. Entry confidence thresholds too high")
        print("    2. Fibonacci gates too strict")
        print("    3. Multi-timeframe gates blocking all signals")
        print("  - Solutions:")
        print("    - Lower entry_conf_overall threshold (try 0.25-0.35)")
        print("    - Widen fibonacci tolerance_atr ranges")
        print("    - Allow LTF override when HTF blocks")
        print("    - Check that champion parameters are in search space")
    
    if summary["valid_trials"] < 3:
        print("\n⚠️  TOO FEW VALID TRIALS:")
        print("  - Need at least 3-5 valid trials for meaningful optimization")
        print("  - Run a smoke test first (2-5 trials) to verify search space")
        print("  - Use grid search initially to find viable regions")


if __name__ == "__main__":
    main()
