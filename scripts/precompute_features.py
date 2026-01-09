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

from core.strategy.features_asof import extract_features_backtest
from core.utils import curated_candles_path


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
    curated_path = curated_candles_path(symbol, timeframe)
    legacy_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"

    if curated_path.exists():
        candles_path = curated_path
    elif legacy_path.exists():
        candles_path = legacy_path
    else:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "status": "error",
            "message": (
                "Candles file not found. Expected curated dataset at "
                f"{curated_path}. Run fetch_historical.py först."
            ),
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
            "timestamp": df["timestamp"].iloc[: i + 1].tolist(),
        }

        # Extract features AS-OF current bar (all bars are closed in backtest datasets)
        feats, meta = extract_features_backtest(
            candles_window,
            asof_bar=i,
            timeframe=timeframe,
            symbol=symbol,
        )

        # Store timestamp + features
        features_list.append(
            {
                "timestamp": df["timestamp"].iloc[i],
                **feats,
            }
        )

    # Convert to DataFrame
    features_df = pd.DataFrame(features_list)

    # Save features under archive
    features_dir = Path("data/archive/features")
    features_dir.mkdir(parents=True, exist_ok=True)

    feather_path = features_dir / f"{symbol}_{timeframe}_features.feather"
    features_df.to_feather(feather_path)

    parquet_path = features_dir / f"{symbol}_{timeframe}_features.parquet"
    features_df.to_parquet(parquet_path, index=False)

    if verbose:
        print(f"[SAVED] {feather_path} ({len(features_df)} rows, Feather)")
        print(f"[SAVED] {parquet_path} ({len(features_df)} rows, Parquet)")

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "success",
        "candles_count": len(df),
        "features_count": len(features_df),
        "output_path": str(parquet_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Precompute features from historical candles")
    parser.add_argument("--symbol", type=str, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, help="Timeframe (e.g., 15m, 1h)")
    parser.add_argument("--all", action="store_true", help="Process all available candles")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    if args.all:
        curated_dir = Path("data/curated/v1/candles")
        legacy_dir = Path("data/candles")

        if curated_dir.exists():
            parquet_files = list(curated_dir.glob("*.parquet"))
        else:
            parquet_files = []

        if not parquet_files and legacy_dir.exists():
            parquet_files = list(legacy_dir.glob("*.parquet"))

        if not parquet_files:
            print("[ERROR] No parquet files found in curated or legacy directories")
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
