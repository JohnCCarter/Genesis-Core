#!/usr/bin/env python3
"""
FAST vectorized feature precomputation.

Uses O(n) vectorized calculations instead of O(n²) per-sample approach.
Expected speedup: 25-50× faster!

Usage:
    python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 1h
    python scripts/precompute_features_fast.py --all
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.vectorized import calculate_all_features_vectorized, validate_features


def precompute_features_vectorized(symbol: str, timeframe: str, verbose: bool = True) -> dict:
    """
    Precompute features using vectorized operations.

    This is O(n) instead of O(n²)!
    """
    start_time = time.time()

    # Load candles
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    if not candles_path.exists():
        raise FileNotFoundError(f"Candles not found: {candles_path}")

    if verbose:
        print(f"[LOAD] {candles_path}")

    df = pd.read_parquet(candles_path)

    if verbose:
        print(f"[VECTORIZE] Computing features for {len(df):,} samples...")

    # === VECTORIZED COMPUTATION (O(n) complexity!) ===
    features_df = calculate_all_features_vectorized(df)

    # Add timestamp column
    features_df.insert(0, "timestamp", df["timestamp"])

    compute_time = time.time() - start_time

    if verbose:
        print(f"[COMPUTED] {len(features_df):,} samples in {compute_time:.2f}s")
        print(f"[SPEED] {len(features_df) / compute_time:.0f} samples/sec")

    # Validate features
    validation = validate_features(features_df)

    if verbose:
        print(f"[VALIDATE] {validation['feature_count']} features computed")
        print(
            f"[VALIDATE] {validation['valid_samples']:,}/{validation['total_samples']:,} valid samples"
        )
        if validation["nan_count"] > 0:
            print(f"[WARNING] {validation['nan_count']} NaN values found")
        if validation["inf_count"] > 0:
            print(f"[WARNING] {validation['inf_count']} Inf values found")

    # Save to disk
    features_dir = Path("data/features")
    features_dir.mkdir(parents=True, exist_ok=True)

    # Save to Feather (fast read)
    feather_path = features_dir / f"{symbol}_{timeframe}_features.feather"
    features_df.to_feather(feather_path)

    # Save to Parquet (backward compatibility)
    parquet_path = features_dir / f"{symbol}_{timeframe}_features.parquet"
    features_df.to_parquet(parquet_path, index=False)

    total_time = time.time() - start_time

    if verbose:
        print(f"[SAVED] {feather_path} ({len(features_df):,} rows, Feather)")
        print(f"[SAVED] {parquet_path} ({len(features_df):,} rows, Parquet)")
        print(f"\n[SUCCESS] Total time: {total_time:.2f}s")
        print(f"[SUCCESS] Average: {len(features_df) / total_time:.0f} samples/sec")

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "success",
        "samples": len(features_df),
        "features": validation["feature_count"],
        "compute_time_sec": compute_time,
        "total_time_sec": total_time,
        "samples_per_sec": len(features_df) / total_time,
        "output_feather": str(feather_path),
        "output_parquet": str(parquet_path),
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Fast vectorized feature precomputation")
    parser.add_argument("--symbol", type=str, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, help="Timeframe (e.g., 1h)")
    parser.add_argument("--all", action="store_true", help="Process all available candles")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    try:
        if args.all:
            # Process all parquet files
            candles_dir = Path("data/candles")
            if not candles_dir.exists():
                print("[ERROR] data/candles/ directory not found")
                return 1

            parquet_files = list(candles_dir.glob("*.parquet"))
            if not parquet_files:
                print("[ERROR] No parquet files found in data/candles/")
                return 1

            results = []
            for pf in parquet_files:
                stem = pf.stem
                parts = stem.rsplit("_", 1)
                if len(parts) != 2:
                    print(f"[SKIP] Invalid filename: {pf.name}")
                    continue

                symbol, timeframe = parts

                if not args.quiet:
                    print(f"\n{'='*60}")
                    print(f"Processing {symbol} {timeframe}")
                    print(f"{'='*60}")

                result = precompute_features_vectorized(symbol, timeframe, verbose=not args.quiet)
                results.append(result)

            # Summary
            if not args.quiet:
                print(f"\n{'='*60}")
                print("SUMMARY")
                print(f"{'='*60}")
                total_samples = sum(r["samples"] for r in results)
                total_time = sum(r["total_time_sec"] for r in results)
                print(f"Processed {len(results)} symbols")
                print(f"Total samples: {total_samples:,}")
                print(f"Total time: {total_time:.2f}s")
                print(f"Average speed: {total_samples / total_time:.0f} samples/sec")
                print(f"{'='*60}\n")

            return 0

        else:
            # Process single symbol
            if not args.symbol or not args.timeframe:
                parser.error("--symbol and --timeframe required (or use --all)")

            result = precompute_features_vectorized(
                args.symbol, args.timeframe, verbose=not args.quiet
            )

            return 0

    except KeyboardInterrupt:
        print("\n[CANCELLED] Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
