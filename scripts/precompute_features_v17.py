#!/usr/bin/env python3
"""
Precompute features v17 (including Fibonacci combinations) in vectorized mode.
This script generates features compatible with the updated features.py v17.
"""
import argparse
import sys
import time
from pathlib import Path

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_fibonacci_features_vectorized,
)
from src.core.indicators.vectorized import (
    calculate_adx_vectorized,
    calculate_atr_vectorized,
    calculate_bollinger_bands_vectorized,
    calculate_ema_vectorized,
    calculate_rsi_vectorized,
)


def precompute_features_v17(symbol: str, timeframe: str, verbose: bool = True) -> dict:
    """
    Precompute features v17 with Fibonacci combinations.

    Returns summary statistics.
    """
    start_time = time.time()

    # Load candle data (try two-layer structure first, fallback to legacy)
    candles_path_curated = Path(f"data/curated/v1/candles/{symbol}_{timeframe}.parquet")
    candles_path_legacy = Path(f"data/candles/{symbol}_{timeframe}.parquet")

    if candles_path_curated.exists():
        candles_path = candles_path_curated
    elif candles_path_legacy.exists():
        candles_path = candles_path_legacy
    else:
        raise FileNotFoundError(
            f"Candles not found:\n"
            f"  Tried curated: {candles_path_curated}\n"
            f"  Tried legacy: {candles_path_legacy}\n"
            f"Run: python scripts/fetch_historical.py --symbol {symbol} --timeframe {timeframe}"
        )

    if verbose:
        print(f"[LOAD] {candles_path}")

    df = pd.read_parquet(candles_path)

    if verbose:
        print(f"[VECTORIZE] Computing features v17 for {len(df):,} samples...")

    # === CALCULATE BASE INDICATORS ===
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # EMA (timeframe-specific parameters for slope calculation)
    EMA_SLOPE_PARAMS = {
        "30m": {"ema_period": 50, "lookback": 20},
        "1h": {"ema_period": 20, "lookback": 5},
    }
    params = EMA_SLOPE_PARAMS.get(timeframe, {"ema_period": 20, "lookback": 5})

    ema = calculate_ema_vectorized(close, period=params["ema_period"])

    # RSI
    rsi = calculate_rsi_vectorized(close, period=14)

    # ATR
    atr = calculate_atr_vectorized(high, low, close, period=14)

    # ADX
    adx = calculate_adx_vectorized(high, low, close, period=14)

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands_vectorized(
        close, period=20, std_dev=2.0
    )

    # === CALCULATE DERIVED FEATURES ===

    # Volatility features
    volatility_shift = (atr / atr.shift(20)).fillna(1.0)
    volatility_shift_ma3 = volatility_shift.rolling(3).mean()
    vol_regime = (atr > atr.rolling(50).quantile(0.75)).astype(float)

    # RSI features
    rsi_inv = -rsi / 100
    rsi_inv_lag1 = rsi_inv.shift(1)
    rsi_vol_interaction = (rsi / 100) * volatility_shift

    # Bollinger features
    bb_position = (close - bb_lower) / (bb_upper - bb_lower + 1e-8)
    bb_position_inv = 1.0 - bb_position
    bb_position_inv_ma3 = bb_position_inv.rolling(3).mean()

    # EMA Slope (with timeframe-specific parameters)
    ema_slope = ema.diff(params["lookback"]) / ema.shift(params["lookback"])
    ema_slope = ema_slope.clip(-0.10, 0.10)

    # === CALCULATE FIBONACCI FEATURES ===
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    fib_features_df = calculate_fibonacci_features_vectorized(df, fib_config)

    # === CALCULATE FIBONACCI COMBINATION FEATURES ===

    # 1. fib05_x_ema_slope (CHAMPION)
    fib05_x_ema_slope = fib_features_df["fib05_prox_atr"] * ema_slope

    # 2. fib_prox_x_adx (TREND CONTINUATION)
    fib_prox_x_adx = fib_features_df["fib_prox_score"] * (adx / 100.0)

    # 3. fib05_x_rsi_inv (MEAN REVERSION)
    fib05_x_rsi_inv = fib_features_df["fib05_prox_atr"] * rsi_inv

    # === ASSEMBLE FINAL FEATURES DATAFRAME ===
    features_df = pd.DataFrame(
        {
            # Timestamp
            "timestamp": df["timestamp"],
            # Original 5 features
            "rsi_inv_lag1": rsi_inv_lag1.clip(-1.0, 1.0),
            "volatility_shift_ma3": volatility_shift_ma3.clip(0.5, 2.0),
            "bb_position_inv_ma3": bb_position_inv_ma3.clip(0.0, 1.0),
            "rsi_vol_interaction": rsi_vol_interaction.clip(-2.0, 2.0),
            "vol_regime": vol_regime,
            # Fibonacci 6 features
            "fib_dist_min_atr": fib_features_df["fib_dist_min_atr"].clip(0.0, 10.0),
            "fib_dist_signed_atr": fib_features_df["fib_dist_signed_atr"].clip(-10.0, 10.0),
            "fib_prox_score": fib_features_df["fib_prox_score"].clip(0.0, 1.0),
            "fib0618_prox_atr": fib_features_df["fib0618_prox_atr"].clip(0.0, 1.0),
            "fib05_prox_atr": fib_features_df["fib05_prox_atr"].clip(0.0, 1.0),
            "swing_retrace_depth": fib_features_df["swing_retrace_depth"].clip(0.0, 1.0),
            # Fibonacci Combination 3 features (v17)
            "fib05_x_ema_slope": fib05_x_ema_slope.clip(-0.10, 0.10),
            "fib_prox_x_adx": fib_prox_x_adx.clip(0.0, 1.0),
            "fib05_x_rsi_inv": fib05_x_rsi_inv.clip(-1.0, 1.0),
        }
    )

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
    feather_path = Path(f"data/features/{symbol}_{timeframe}_features_v17.feather")
    feather_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.reset_index(drop=True).to_feather(feather_path)

    if verbose:
        print(f"[SAVED] Feather: {feather_path}")

    # Also save as Parquet (backup, compressed)
    parquet_path = Path(f"data/features/{symbol}_{timeframe}_features_v17.parquet")
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
        "ema_slope_params": params,
        "version": "v17_fibonacci_combinations",
    }


def main():
    parser = argparse.ArgumentParser(description="Precompute features v17 (Fibonacci combinations)")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe (1D, 6h, 3h, 1h, 30m)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
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
        summary = precompute_features_v17(args.symbol, args.timeframe, verbose=verbose)

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
            print(
                f"EMA Slope Params: EMA={summary['ema_slope_params']['ema_period']}, Lookback={summary['ema_slope_params']['lookback']}"
            )

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
