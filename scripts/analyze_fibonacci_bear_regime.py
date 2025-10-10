#!/usr/bin/env python3
"""
Analyze Fibonacci features specifically in BEAR regime.
Tests if Fibonacci mean reversion works differently in downtrends.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.indicators.fibonacci import (
    FibonacciConfig,
    calculate_fibonacci_features_vectorized,
)


def classify_bear_regime(closes: pd.Series, window: int = 50) -> pd.Series:
    """
    Classify Bear regime using EMA-based trend detection.
    Bear = price significantly below EMA.
    """
    ema = closes.ewm(span=window, adjust=False).mean()
    trend = (closes - ema) / ema

    # Bear: price > 2% below EMA
    is_bear = trend < -0.02
    return is_bear


def calculate_forward_returns(close_prices: pd.Series, horizon: int = 10) -> pd.Series:
    """Calculate forward returns for IC calculation."""
    return close_prices.pct_change(horizon).shift(-horizon)


def calculate_ic(feature_values: np.ndarray, returns: np.ndarray) -> tuple[float, float]:
    """Calculate Information Coefficient (Spearman correlation)."""
    # Remove NaN values
    mask = ~(np.isnan(feature_values) | np.isnan(returns))
    if mask.sum() < 30:  # Need minimum samples
        return np.nan, np.nan

    ic, p_val = spearmanr(feature_values[mask], returns[mask])
    return ic, p_val


def main():
    parser = argparse.ArgumentParser(description="Analyze Fibonacci IC in Bear regime")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe (1D, 6h, 3h, 1h, etc)")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    parser.add_argument(
        "--ema-window", type=int, default=50, help="EMA window for regime detection"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("FIBONACCI BEAR REGIME ANALYSIS")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Horizon: {args.horizon} bars")
    print(f"Regime Detection: EMA{args.ema_window}")
    print("=" * 80)
    print()

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    if not candles_path.exists():
        print(f"❌ ERROR: Candles not found at {candles_path}")
        return 1

    candles_df = pd.read_parquet(candles_path)
    print(f"[LOAD] Loaded {len(candles_df)} candles")

    # Calculate Fibonacci features
    print("[COMPUTE] Calculating Fibonacci features...")
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)

    # Use vectorized calculation
    df = candles_df.copy()
    df["close_series"] = df["close"]

    fib_features_df = calculate_fibonacci_features_vectorized(df, fib_config)

    # Add close price for regime detection
    fib_features_df["close"] = df["close"].values

    print(f"[COMPUTED] {len(fib_features_df.columns)-1} Fibonacci features")

    # Classify Bear regime
    print(f"[REGIME] Classifying Bear regime (EMA{args.ema_window})...")
    is_bear = classify_bear_regime(fib_features_df["close"], window=args.ema_window)
    bear_count = is_bear.sum()
    bear_pct = (bear_count / len(is_bear)) * 100

    print(f"[REGIME] Bear bars: {bear_count} / {len(is_bear)} ({bear_pct:.1f}%)")

    if bear_count < 50:
        print(f"[ERROR] Not enough Bear samples ({bear_count} < 50)")
        return 1

    # Calculate forward returns
    print(f"[RETURNS] Calculating {args.horizon}-bar forward returns...")
    returns = calculate_forward_returns(fib_features_df["close"], horizon=args.horizon)

    # Filter for Bear regime only
    bear_mask = is_bear.values

    print()
    print("=" * 80)
    print("FIBONACCI FEATURES - BEAR REGIME IC ANALYSIS")
    print("=" * 80)
    print()

    # Test each Fibonacci feature
    fib_feature_names = [
        "fib_dist_min_atr",
        "fib_dist_signed_atr",
        "fib_prox_score",
        "fib0618_prox_atr",
        "fib05_prox_atr",
        "swing_retrace_depth",
    ]

    results = []

    for feature_name in fib_feature_names:
        if feature_name not in fib_features_df.columns:
            print(f"⚠️  WARNING: {feature_name} not found in features")
            continue

        feature_values = fib_features_df[feature_name].values

        # Calculate IC for Bear regime only
        bear_feature_values = feature_values[bear_mask]
        bear_returns = returns.values[bear_mask]

        ic_bear, p_val_bear = calculate_ic(bear_feature_values, bear_returns)

        # Store results
        results.append(
            {
                "feature": feature_name,
                "ic_bear": ic_bear,
                "p_val_bear": p_val_bear,
                "abs_ic": abs(ic_bear) if not np.isnan(ic_bear) else 0,
            }
        )

        # Print result
        sig_bear = "[SIG]" if p_val_bear < 0.05 else ""
        print(f"{feature_name:30s} Bear IC: {ic_bear:+.4f} (p={p_val_bear:.4f}) {sig_bear}")

    # Sort by absolute IC
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("abs_ic", ascending=False)

    print()
    print("=" * 80)
    print("TOP FIBONACCI FEATURES IN BEAR REGIME")
    print("=" * 80)

    for _idx, row in results_df.iterrows():
        sig = (
            "***"
            if row["p_val_bear"] < 0.001
            else "**" if row["p_val_bear"] < 0.01 else "*" if row["p_val_bear"] < 0.05 else ""
        )
        print(f"{row['feature']:30s} IC: {row['ic_bear']:+.4f} {sig}")

    # Save results
    output_dir = Path("results/fibonacci_bear_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{args.symbol}_{args.timeframe}_bear_ic.csv"
    results_df.to_csv(output_file, index=False)
    print()
    print(f"[SAVED] Results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
