#!/usr/bin/env python3
"""
Precompute features v17 (including Fibonacci combinations) using the same
runtime pipeline (_extract_asof) to guarantee parity.
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root + src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))

from core.strategy.features_asof import extract_features_backtest  # noqa: E402


def precompute_features_v17(
    symbol: str,
    timeframe: str,
    *,
    verbose: bool = True,
    start_index: int | None = None,
    end_index: int | None = None,
    candles_file: Path | None = None,
) -> dict:
    """
    Precompute features v17 with Fibonacci combinations.

    Returns summary statistics.
    """
    start_time = time.time()

    # Load candle data (try two-layer structure first, fallback to legacy)
    candles_path = (
        Path(candles_file)
        if candles_file is not None
        else Path(f"data/curated/v1/candles/{symbol}_{timeframe}.parquet")
    )

    if not candles_path.exists():
        legacy_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
        if legacy_path.exists():
            candles_path = legacy_path
        else:
            raise FileNotFoundError(
                f"Candles not found:\n"
                f"  Expected curated: {candles_path}\n"
                f"Run: python scripts/fetch_historical.py --symbol {symbol} --timeframe {timeframe}"
            )

    if verbose:
        print(f"[LOAD] {candles_path}")

    df = pd.read_parquet(candles_path)

    if start_index is not None or end_index is not None:
        start = start_index or 0
        stop = end_index if end_index is not None else len(df)
        df = df.iloc[start:stop].reset_index(drop=True)
        if verbose:
            print(f"[SLICE] Using rows {start}:{stop} ({len(df)} samples)")

    if verbose:
        print(f"[RUNTIME] Computing features v17 for {len(df):,} samples...")

    candles = {
        "open": df["open"].tolist(),
        "high": df["high"].tolist(),
        "low": df["low"].tolist(),
        "close": df["close"].tolist(),
        "volume": df.get("volume", pd.Series([0.0] * len(df))).tolist(),
        "timestamp": df["timestamp"].tolist(),
    }

    rows: list[dict[str, float]] = []
    for asof_bar in range(len(df)):
        feats, _ = extract_features_backtest(candles, asof_bar, timeframe=timeframe, symbol=symbol)
        if not feats:
            continue
        feats["timestamp"] = candles["timestamp"][asof_bar]
        rows.append(feats)

    if not rows:
        raise RuntimeError("No features computed; insufficient bars for selected timeframe.")

    features_df = pd.DataFrame(rows)
    ordered_columns = ["timestamp"] + sorted(
        col for col in features_df.columns if col != "timestamp"
    )
    features_df = features_df.reindex(columns=ordered_columns)

    compute_time = time.time() - start_time

    if verbose:
        print(f"[COMPUTED] {len(features_df):,} samples in {compute_time:.2f}s")
        print(f"[SPEED] {len(features_df) / compute_time:.0f} samples/sec")
        print(f"[FEATURES] {len(features_df.columns)-1} features (v17)")

    # Validate features
    nan_count = features_df.isna().sum().sum()
    inf_count = np.isinf(features_df.select_dtypes(include=[float, int])).sum().sum()
    valid_samples = len(features_df) - features_df.isna().any(axis=1).sum()

    if verbose:
        print(f"[VALIDATE] {valid_samples:,}/{len(features_df):,} valid samples")
        if nan_count > 0:
            print(f"[WARNING] {nan_count} NaN values found")
        if inf_count > 0:
            print(f"[WARNING] {inf_count} Inf values found")

    # === SAVE FEATURES ===

    # Save as Feather (fast, for ML training)
    # Save features under archive/features/ (keep curated directory clean)
    features_dir = Path("data/archive/features")
    features_dir.mkdir(parents=True, exist_ok=True)

    feather_path = features_dir / f"{symbol}_{timeframe}_features_v17.feather"
    features_df.reset_index(drop=True).to_feather(feather_path)

    if verbose:
        print(f"[SAVED] Feather: {feather_path}")

    parquet_path = features_dir / f"{symbol}_{timeframe}_features_v17.parquet"
    features_df.to_parquet(parquet_path, index=False, compression="snappy")

    if verbose:
        print(f"[SAVED] Parquet: {parquet_path}")

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "samples": len(features_df),
        "features": len(features_df.columns) - 1,  # Exclude timestamp
        "valid_samples": valid_samples,
        "compute_time": compute_time,
        "samples_per_sec": len(features_df) / compute_time,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "version": "v17_fibonacci_combinations",
        "feature_columns": ordered_columns[1:],
    }


def main():
    parser = argparse.ArgumentParser(description="Precompute features v17 (Fibonacci combinations)")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe (1D, 6h, 3h, 1h, 30m)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--start-index", type=int, default=None, help="Optional start row index")
    parser.add_argument(
        "--end-index", type=int, default=None, help="Optional end row index (exclusive)"
    )
    parser.add_argument(
        "--candles-file", type=Path, default=None, help="Optional custom candles parquet"
    )
    args = parser.parse_args()

    verbose = not args.quiet

    print("=" * 80)
    print("PRECOMPUTE FEATURES v17 (FIBONACCI COMBINATIONS)")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print("=" * 80)
    print()

    try:
        summary = precompute_features_v17(
            args.symbol,
            args.timeframe,
            verbose=verbose,
            start_index=args.start_index,
            end_index=args.end_index,
            candles_file=args.candles_file,
        )

        if verbose:
            print()
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Samples: {summary['samples']:,}")
            print(f"Features: {summary['features']}")
            print(f"Valid: {summary['valid_samples']:,}/{summary['samples']:,}")
            print(f"Compute Time: {summary['compute_time']:.2f}s")
            print(f"Speed: {summary['samples_per_sec']:.0f} samples/sec")
            print(f"Version: {summary['version']}")
            print(f"Columns: {len(summary['feature_columns'])}")

            if summary["nan_count"] > 0 or summary["inf_count"] > 0:
                print("\n[WARNING] Quality issues detected:")
                print(f"  NaN: {summary['nan_count']}")
                print(f"  Inf: {summary['inf_count']}")

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import numpy as np

    sys.exit(main())
