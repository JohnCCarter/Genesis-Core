"""
Precompute features from historical candle data.

Usage:
    python scripts/precompute_features.py --symbol tBTCUSD --timeframe 15m
    python scripts/precompute_features.py --all  # Process all available candles
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from tqdm import tqdm

from core.strategy.features import extract_features


def precompute_features_for_symbol(symbol: str, timeframe: str, verbose: bool = True) -> dict:
    """
    Precompute features for a single symbol/timeframe.

    Args:
        symbol: Symbol (e.g., 'tBTCUSD')
        timeframe: Timeframe (e.g., '15m', '1h')
        verbose: Show progress bar

    Returns:
        dict with metadata about the process
    """
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    features_path = Path("data/features") / f"{symbol}_{timeframe}_features.parquet"

    if not candles_path.exists():
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "error",
            "message": f"Candles file not found: {candles_path}",
        }

    # Load candles
    if verbose:
        print(f"[LOAD] {candles_path}")
    df = pd.read_parquet(candles_path)

    if df.empty:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "error",
            "message": "Empty candles dataframe",
        }

    # Extract features bar-by-bar (avoid lookahead bias)
    features_list = []

    iterator = range(len(df))
    if verbose:
        iterator = tqdm(iterator, desc=f"[COMPUTE] {symbol} {timeframe}")

    for i in iterator:
        # Use only data up to and including current bar
        candles_window = {
            "open": df["open"].iloc[: i + 1].tolist(),
            "high": df["high"].iloc[: i + 1].tolist(),
            "low": df["low"].iloc[: i + 1].tolist(),
            "close": df["close"].iloc[: i + 1].tolist(),
            "volume": df["volume"].iloc[: i + 1].tolist(),
        }

        # Extract features using existing pipeline logic
        feats, meta = extract_features(candles_window, now_index=i)

        # Store timestamp + features
        features_list.append(
            {
                "timestamp": df["timestamp"].iloc[i],
                **feats,
            }
        )

    # Convert to DataFrame
    features_df = pd.DataFrame(features_list)

    # Ensure features directory exists
    features_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to Parquet
    features_df.to_parquet(features_path, index=False)

    if verbose:
        print(f"[SAVED] {features_path} ({len(features_df)} rows)")

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "success",
        "candles_count": len(df),
        "features_count": len(features_df),
        "output_path": str(features_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Precompute features from historical candles")
    parser.add_argument("--symbol", type=str, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, help="Timeframe (e.g., 15m, 1h)")
    parser.add_argument("--all", action="store_true", help="Process all available candles")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    if args.all:
        # Find all parquet files in data/candles/
        candles_dir = Path("data/candles")
        if not candles_dir.exists():
            print("[ERROR] data/candles/ directory not found")
            sys.exit(1)

        parquet_files = list(candles_dir.glob("*.parquet"))
        if not parquet_files:
            print("[ERROR] No parquet files found in data/candles/")
            sys.exit(1)

        results = []
        for pf in parquet_files:
            # Parse filename: tBTCUSD_15m.parquet → symbol=tBTCUSD, timeframe=15m
            stem = pf.stem  # tBTCUSD_15m
            parts = stem.rsplit("_", 1)
            if len(parts) != 2:
                print(f"[SKIP] Invalid filename format: {pf.name}")
                continue

            symbol, timeframe = parts
            result = precompute_features_for_symbol(symbol, timeframe, verbose=not args.quiet)
            results.append(result)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        success_count = sum(1 for r in results if r["status"] == "success")
        print(
            f"Total: {len(results)}, Success: {success_count}, Failed: {len(results) - success_count}"
        )

        for r in results:
            if r["status"] == "success":
                print(f"[OK] {r['symbol']} {r['timeframe']}: {r['features_count']} features")
            else:
                print(f"[FAIL] {r['symbol']} {r['timeframe']}: {r['message']}")

    elif args.symbol and args.timeframe:
        result = precompute_features_for_symbol(args.symbol, args.timeframe, verbose=not args.quiet)

        if result["status"] == "success":
            print(f"\n[SUCCESS] Features saved to {result['output_path']}")
        else:
            print(f"\n[ERROR] {result['message']}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
