#!/usr/bin/env python3
"""
Validate that vectorized feature computation gives same results as per-sample.

Critical test to ensure our 27,734× speedup didn't introduce errors!

Usage:
    python scripts/validate_vectorized_features.py --symbol tBTCUSD --timeframe 1h --samples 100
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.vectorized import calculate_all_features_vectorized
from core.strategy.features_asof import extract_features_backtest


def compute_per_sample_features(df: pd.DataFrame, max_samples: int = 100) -> pd.DataFrame:
    """
    Compute features using ORIGINAL per-sample method (slow but verified correct).

    This is the ground truth!
    """
    features_list = []

    # Only test last N samples to save time
    start_idx = max(0, len(df) - max_samples)

    print(f"[PER-SAMPLE] Computing features for {max_samples} samples (slow method)...")

    for i in range(start_idx, len(df)):
        # Use only data up to current bar
        candles_window = {
            "open": df["open"].iloc[: i + 1].tolist(),
            "high": df["high"].iloc[: i + 1].tolist(),
            "low": df["low"].iloc[: i + 1].tolist(),
            "close": df["close"].iloc[: i + 1].tolist(),
            "volume": df["volume"].iloc[: i + 1].tolist(),
        }

        # Extract features AS OF bar i (uses bars [0:i] inclusive)
        feats, meta = extract_features_backtest(candles_window, asof_bar=i)

        # Invariant check
        assert meta["asof_bar"] == i, f"Expected asof_bar={i}, got {meta['asof_bar']}"

        features_list.append(
            {
                "timestamp": df["timestamp"].iloc[i],
                **feats,
            }
        )

    return pd.DataFrame(features_list)


def compare_features(
    per_sample_df: pd.DataFrame,
    vectorized_df: pd.DataFrame,
    tolerance: float = 1e-6,
) -> dict:
    """
    Compare per-sample vs vectorized features.

    Returns validation results with differences.
    """
    # Align dataframes by timestamp
    merged = per_sample_df.merge(
        vectorized_df,
        on="timestamp",
        suffixes=("_per_sample", "_vectorized"),
    )

    if len(merged) == 0:
        return {"status": "error", "message": "No matching timestamps!"}

    print(f"\n[COMPARE] Comparing {len(merged)} samples...")

    # Get feature columns (excluding timestamp)
    per_sample_cols = [col for col in per_sample_df.columns if col != "timestamp"]

    results = {
        "total_samples": len(merged),
        "features_tested": len(per_sample_cols),
        "features": {},
        "summary": {},
    }

    all_diffs = []
    max_diff_overall = 0
    worst_feature = None

    for feat in per_sample_cols:
        col_per_sample = f"{feat}_per_sample"
        col_vectorized = f"{feat}_vectorized"

        if col_per_sample not in merged.columns or col_vectorized not in merged.columns:
            print(f"[WARNING] Feature '{feat}' missing in one method!")
            continue

        # Calculate differences
        diff = np.abs(merged[col_per_sample] - merged[col_vectorized])

        max_diff = diff.max()
        mean_diff = diff.mean()
        median_diff = diff.median()

        all_diffs.extend(diff.tolist())

        # Check if within tolerance
        within_tolerance = (diff <= tolerance).all()

        results["features"][feat] = {
            "max_diff": float(max_diff),
            "mean_diff": float(mean_diff),
            "median_diff": float(median_diff),
            "within_tolerance": bool(within_tolerance),
            "tolerance": tolerance,
        }

        if max_diff > max_diff_overall:
            max_diff_overall = max_diff
            worst_feature = feat

        # Print status
        status = "[OK]" if within_tolerance else "[DIFF]"
        print(f"  {feat:<30} {status} max_diff={max_diff:.2e}, mean={mean_diff:.2e}")

    # Overall summary
    all_within_tolerance = all(f["within_tolerance"] for f in results["features"].values())

    results["summary"] = {
        "all_within_tolerance": bool(all_within_tolerance),
        "max_diff_overall": float(max_diff_overall),
        "worst_feature": worst_feature,
        "tolerance": tolerance,
    }

    return results


def print_summary(results: dict):
    """Print validation summary."""
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    summary = results["summary"]

    print(f"\nSamples tested:  {results['total_samples']}")
    print(f"Features tested: {results['features_tested']}")
    print(f"Tolerance:       {summary['tolerance']:.2e}")

    print(f"\nMax difference:  {summary['max_diff_overall']:.2e}")
    print(f"Worst feature:   {summary['worst_feature']}")

    if summary["all_within_tolerance"]:
        print("\n[SUCCESS] All features within tolerance!")
        print("[OK] Vectorized computation is VALIDATED!")
    else:
        print("\n[WARNING] Some features differ beyond tolerance!")
        print("[ALERT] Review vectorized implementation!")

        # Show features with issues
        print("\nFeatures with differences:")
        for feat, stats in results["features"].items():
            if not stats["within_tolerance"]:
                print(f"  - {feat}: max_diff={stats['max_diff']:.2e}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate vectorized features")
    parser.add_argument("--symbol", required=True, help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of samples to test (default: 100, set higher for thorough test)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="Tolerance for numerical differences (default: 1e-6)",
    )

    args = parser.parse_args()

    try:
        print("\n" + "=" * 80)
        print("VECTORIZED FEATURES VALIDATION")
        print("=" * 80)
        print(f"Symbol:    {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Samples:   {args.samples} (last N samples)")
        print(f"Tolerance: {args.tolerance:.2e}")

        # Load candles
        print("\n[LOAD] Loading candles...")
        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)

        # Method 1: Per-sample (GROUND TRUTH)
        per_sample_df = compute_per_sample_features(candles_df, args.samples)

        # Method 2: Vectorized (FAST)
        print("\n[VECTORIZED] Computing features (fast method)...")
        vectorized_df = calculate_all_features_vectorized(candles_df)
        vectorized_df.insert(0, "timestamp", candles_df["timestamp"])

        # Take only last N samples for comparison
        vectorized_df = vectorized_df.tail(args.samples)

        print(f"[VECTORIZED] Computed {len(vectorized_df)} samples")

        # Compare
        print("\n[VALIDATE] Comparing methods...")
        results = compare_features(per_sample_df, vectorized_df, args.tolerance)

        # Print summary
        print_summary(results)

        # Return exit code
        if results["summary"]["all_within_tolerance"]:
            print("\n" + "=" * 80)
            print("[SUCCESS] Vectorized features VALIDATED!")
            print("=" * 80 + "\n")
            return 0
        else:
            print("\n" + "=" * 80)
            print("[FAILED] Vectorized features have ERRORS!")
            print("=" * 80 + "\n")
            return 1

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
