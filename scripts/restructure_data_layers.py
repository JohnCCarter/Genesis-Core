#!/usr/bin/env python3
"""
Restructure data directory into Two-Layer Architecture:
  Raw Lake (immutable) + Curated Gold (validated, versioned)

Usage:
    python scripts/restructure_data_layers.py --dry-run
    python scripts/restructure_data_layers.py --execute
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


def create_two_layer_structure(dry_run: bool = True):
    """
    Migrate existing data to two-layer architecture.

    Structure:
        data/
        ├── raw/              # Raw Lake (immutable, timestamped)
        │   └── bitfinex/
        │       └── candles/
        │           └── {symbol}_{timeframe}_{YYYY-MM-DD}.parquet
        ├── curated/          # Gold Layer (validated, versioned)
        │   └── v1/
        │       ├── candles/
        │       │   └── {symbol}_{timeframe}.parquet
        │       └── features/
        │           └── {symbol}_{timeframe}_features.feather (+ .parquet backup)
        └── metadata/
            └── curated/
                └── {symbol}_{timeframe}_v1.json

    Note:
      - Raw candles: Parquet (compression, long-term storage)
      - Curated features: Feather primary + Parquet backup (2× faster reads)
    """
    base_dir = Path("data")

    # Define new structure
    raw_dir = base_dir / "raw" / "bitfinex" / "candles"
    curated_dir = base_dir / "curated" / "v1" / "candles"
    metadata_curated = base_dir / "metadata" / "curated"

    if not dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)
        curated_dir.mkdir(parents=True, exist_ok=True)
        metadata_curated.mkdir(parents=True, exist_ok=True)

    # Find existing candles
    candles_dir = base_dir / "candles"
    if not candles_dir.exists():
        print("No existing candles directory found.")
        return

    parquet_files = list(candles_dir.glob("*.parquet"))

    if not parquet_files:
        print("No parquet files found in data/candles/")
        return

    print(f"Found {len(parquet_files)} candle files to migrate\n")

    fetch_date = datetime.now().strftime("%Y-%m-%d")

    for parquet_file in parquet_files:
        symbol_timeframe = parquet_file.stem  # e.g., "tBTCUSD_1h"

        print(f"Processing: {symbol_timeframe}")

        # Load data
        df = pd.read_parquet(parquet_file)

        # 1. Copy to Raw Lake (immutable, timestamped)
        raw_filename = f"{symbol_timeframe}_{fetch_date}.parquet"
        raw_path = raw_dir / raw_filename

        if dry_run:
            print(f"  [DRY-RUN] Would copy to: {raw_path}")
        else:
            df.to_parquet(raw_path, index=False, compression="snappy")
            print(f"  ✅ Raw: {raw_path}")

        # 2. Validate and create Curated version
        validation_results = validate_candles(df, symbol_timeframe)

        if validation_results["valid"]:
            # Candles: Parquet only (raw OHLCV data)
            curated_path = curated_dir / f"{symbol_timeframe}.parquet"

            if dry_run:
                print(f"  [DRY-RUN] Would create curated: {curated_path}")
            else:
                df.to_parquet(curated_path, index=False, compression="snappy")
                print(f"  ✅ Curated: {curated_path}")

            # Note: Features would be saved as Feather+Parquet in features/ subdirectory
            # (handled by precompute_features_v17.py)

            # 3. Create metadata
            metadata = {
                "dataset_version": "v1",
                "symbol_timeframe": symbol_timeframe,
                "source": "bitfinex_public_api",
                "raw_file": str(raw_filename),
                "curated_at": datetime.now().isoformat(),
                "fetch_date": fetch_date,
                "total_candles": len(df),
                "start_date": (
                    df["timestamp"].min().isoformat() if "timestamp" in df.columns else None
                ),
                "end_date": (
                    df["timestamp"].max().isoformat() if "timestamp" in df.columns else None
                ),
                "validation": validation_results,
                "adjustments": [],
                "quality_score": validation_results.get("quality_score", 1.0),
            }

            metadata_path = metadata_curated / f"{symbol_timeframe}_v1.json"

            if dry_run:
                print(f"  [DRY-RUN] Would create metadata: {metadata_path}")
                print(f"    Quality: {metadata['quality_score']:.2%}")
            else:
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                print(f"  ✅ Metadata: {metadata_path}")
        else:
            print(f"  ⚠️  Validation failed: {validation_results['issues']}")

        print()

    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Raw Lake: {raw_dir}")
    print(f"Curated: {curated_dir}")
    print(f"Metadata: {metadata_curated}")

    if dry_run:
        print("\n⚠️  DRY RUN - No files were modified")
        print("Run with --execute to apply changes")


def validate_candles(df: pd.DataFrame, symbol_timeframe: str) -> dict:
    """
    Validate candle data quality.

    Returns:
        dict with 'valid' flag and quality metrics
    """
    issues = []

    # Check required columns
    required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")
        return {"valid": False, "issues": issues}

    # Check for NaN
    nan_count = df[required_cols].isna().sum().sum()
    if nan_count > 0:
        issues.append(f"NaN values: {nan_count}")

    # Check OHLC logic (high >= low, high >= open/close, low <= open/close)
    invalid_ohlc = (
        (df["high"] < df["low"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
    ).sum()

    if invalid_ohlc > 0:
        issues.append(f"Invalid OHLC logic: {invalid_ohlc} bars")

    # Check for gaps (basic check - could be improved with timeframe-aware logic)
    if "timestamp" in df.columns:
        # Check if sorted (simplified validation)
        if not df["timestamp"].is_monotonic_increasing:
            issues.append("Timestamps not monotonic increasing")

    # Quality score
    total_bars = len(df)
    problem_bars = nan_count + invalid_ohlc
    quality_score = 1.0 - (problem_bars / total_bars) if total_bars > 0 else 0.0

    valid = quality_score >= 0.95  # 95% quality threshold

    return {
        "valid": valid,
        "quality_score": quality_score,
        "total_bars": total_bars,
        "nan_count": int(nan_count),
        "invalid_ohlc": int(invalid_ohlc),
        "issues": issues if issues else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Migrate data to two-layer architecture")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the migration",
    )

    args = parser.parse_args()

    # --execute overrides --dry-run
    dry_run = not args.execute

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60 + "\n")

    create_two_layer_structure(dry_run=dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
