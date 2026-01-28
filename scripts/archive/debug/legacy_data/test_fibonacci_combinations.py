#!/usr/bin/env python3
"""
Test Fibonacci features combined with existing context features.
This validates if combinations improve IC before implementing new features.
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


def calculate_forward_returns(close_prices: pd.Series, horizon: int = 10) -> pd.Series:
    """Calculate forward returns for IC calculation."""
    return close_prices.pct_change(horizon).shift(-horizon)


def calculate_ic(feature_values: np.ndarray, returns: np.ndarray) -> tuple[float, float]:
    """Calculate Information Coefficient (Spearman correlation)."""
    # Remove NaN values
    mask = ~(np.isnan(feature_values) | np.isnan(returns) | np.isinf(feature_values))
    if mask.sum() < 30:  # Need minimum samples
        return np.nan, np.nan

    ic, p_val = spearmanr(feature_values[mask], returns[mask])
    return ic, p_val


def main():
    parser = argparse.ArgumentParser(description="Test Fibonacci + Context Feature Combinations")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe (1D, 6h, 3h, 1h, etc)")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    args = parser.parse_args()

    print("=" * 80)
    print("FIBONACCI COMBINATION FEATURE ANALYSIS")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Horizon: {args.horizon} bars")
    print("=" * 80)
    print()

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    if not candles_path.exists():
        print(f"[ERROR] Candles not found at {candles_path}")
        return 1

    candles_df = pd.read_parquet(candles_path)
    print(f"[LOAD] Loaded {len(candles_df)} candles")

    # Calculate ALL features (Fibonacci + existing)
    print("[COMPUTE] Calculating ALL features (Fibonacci + existing)...")

    # Get Fibonacci features
    df = candles_df.copy()
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    fib_features_df = calculate_fibonacci_features_vectorized(df, fib_config)

    # Calculate basic features we need
    from src.core.indicators.vectorized import (
        calculate_adx_vectorized,
        calculate_atr_vectorized,
        calculate_bollinger_bands_vectorized,
        calculate_ema_vectorized,
        calculate_rsi_vectorized,
    )

    # Calculate required features
    close = df["close"]
    high = df["high"]
    low = df["low"]

    ema20 = calculate_ema_vectorized(close, period=20)
    rsi = calculate_rsi_vectorized(close, period=14)
    atr = calculate_atr_vectorized(high, low, close, period=14)
    adx = calculate_adx_vectorized(high, low, close, period=14)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands_vectorized(
        close, period=20, std_dev=2.0
    )

    # Create features dataframe
    features_df = fib_features_df.copy()

    # Add context features
    features_df["volatility_shift"] = (atr / atr.shift(20)).fillna(1.0)
    features_df["volatility_shift_ma3"] = features_df["volatility_shift"].rolling(3).mean()
    features_df["vol_regime"] = (atr > atr.rolling(50).quantile(0.75)).astype(float)
    features_df["adx"] = adx
    features_df["ema_slope_20"] = ema20.diff(5) / ema20.shift(5)
    features_df["price_vs_ema20"] = (close - ema20) / ema20
    features_df["rsi_inv"] = -rsi / 100
    features_df["rsi_vol_interaction"] = (rsi / 100) * features_df["volatility_shift"]
    features_df["bb_position_inv_ma3"] = (
        (1.0 - ((close - bb_lower) / (bb_upper - bb_lower + 1e-8))).rolling(3).mean()
    )

    print(f"[COMPUTED] {len(features_df.columns)} total features")

    # Calculate forward returns
    print(f"[RETURNS] Calculating {args.horizon}-bar forward returns...")
    returns = calculate_forward_returns(df["close"], horizon=args.horizon)

    print()
    print("=" * 80)
    print("BASELINE FIBONACCI FEATURES (SOLO)")
    print("=" * 80)
    print()

    # Test baseline Fibonacci features
    fib_features = [
        "fib_prox_score",
        "fib05_prox_atr",
        "fib0618_prox_atr",
        "fib_dist_min_atr",
    ]

    baseline_results = {}

    for feature in fib_features:
        if feature not in features_df.columns:
            continue

        ic, p_val = calculate_ic(features_df[feature].values, returns.values)
        baseline_results[feature] = {"ic": ic, "p_val": p_val}

        sig = "[SIG]" if p_val < 0.05 else ""
        print(f"{feature:30s} IC: {ic:+.4f} (p={p_val:.4f}) {sig}")

    print()
    print("=" * 80)
    print("COMBINATION FEATURES (FIB + CONTEXT)")
    print("=" * 80)
    print()

    # Define combinations to test
    combinations = [
        # Fib + Volatility Context
        {
            "name": "fib_prox_x_vol_shift",
            "formula": lambda df: df["fib_prox_score"] * df["volatility_shift"],
            "description": "Fib proximity weighted by volatility expansion",
        },
        {
            "name": "fib_prox_x_vol_shift_ma3",
            "formula": lambda df: df["fib_prox_score"] * df["volatility_shift_ma3"],
            "description": "Fib proximity weighted by smoothed volatility",
        },
        {
            "name": "fib05_x_vol_regime",
            "formula": lambda df: df["fib05_prox_atr"] * df["vol_regime"],
            "description": "Fib 0.5 proximity weighted by volatility regime",
        },
        # Fib + Trend Context
        {
            "name": "fib_prox_x_adx",
            "formula": lambda df: df["fib_prox_score"] * (df["adx"] / 100),
            "description": "Fib proximity weighted by trend strength (ADX)",
        },
        {
            "name": "fib05_x_ema_slope",
            "formula": lambda df: df["fib05_prox_atr"] * df["ema_slope_20"],
            "description": "Fib 0.5 weighted by EMA slope (trend direction)",
        },
        # Fib + Momentum Context
        {
            "name": "fib_prox_x_rsi_vol_int",
            "formula": lambda df: df["fib_prox_score"] * df["rsi_vol_interaction"],
            "description": "Fib proximity weighted by RSI-volatility interaction",
        },
        {
            "name": "fib05_x_rsi_inv",
            "formula": lambda df: df["fib05_prox_atr"] * df["rsi_inv"],
            "description": "Fib 0.5 weighted by inverted RSI (mean reversion)",
        },
        # Fib + Price Position
        {
            "name": "fib_prox_x_bb_position",
            "formula": lambda df: df["fib_prox_score"] * df["bb_position_inv_ma3"],
            "description": "Fib proximity weighted by Bollinger Band position",
        },
        {
            "name": "fib_dist_x_price_vs_ema",
            "formula": lambda df: df["fib_dist_min_atr"] * abs(df["price_vs_ema20"]),
            "description": "Fib distance weighted by price deviation from EMA",
        },
        # Multi-Context Combinations
        {
            "name": "fib_prox_x_vol_x_adx",
            "formula": lambda df: df["fib_prox_score"] * df["volatility_shift"] * (df["adx"] / 100),
            "description": "Fib proximity weighted by vol expansion AND trend strength",
        },
        {
            "name": "fib05_x_vol_x_rsi_vol",
            "formula": lambda df: df["fib05_prox_atr"]
            * df["volatility_shift_ma3"]
            * df["rsi_vol_interaction"],
            "description": "Fib 0.5 weighted by vol AND momentum interaction",
        },
    ]

    combo_results = []

    for combo in combinations:
        try:
            # Calculate combination feature
            combo_feature = combo["formula"](features_df)

            # Calculate IC
            ic, p_val = calculate_ic(combo_feature.values, returns.values)

            # Store result
            combo_results.append(
                {
                    "name": combo["name"],
                    "ic": ic,
                    "p_val": p_val,
                    "abs_ic": abs(ic) if not np.isnan(ic) else 0,
                    "description": combo["description"],
                }
            )

            # Print result
            sig = "[SIG]" if p_val < 0.05 else ""
            print(f"{combo['name']:30s} IC: {ic:+.4f} (p={p_val:.4f}) {sig}")
            print(f"  > {combo['description']}")
            print()

        except Exception as e:
            print(f"[ERROR] {combo['name']}: {e}")
            continue

    # Sort by absolute IC
    combo_results_df = pd.DataFrame(combo_results)
    combo_results_df = combo_results_df.sort_values("abs_ic", ascending=False)

    print()
    print("=" * 80)
    print("TOP COMBINATION FEATURES (by absolute IC)")
    print("=" * 80)
    print()

    for _idx, row in combo_results_df.head(10).iterrows():
        sig = (
            "***"
            if row["p_val"] < 0.001
            else "**" if row["p_val"] < 0.01 else "*" if row["p_val"] < 0.05 else ""
        )
        improvement = ""

        # Check if better than baseline
        baseline_ic = baseline_results.get("fib_prox_score", {}).get("ic", 0)
        if abs(row["ic"]) > abs(baseline_ic):
            pct_improvement = (
                ((abs(row["ic"]) - abs(baseline_ic)) / abs(baseline_ic) * 100)
                if baseline_ic != 0
                else 0
            )
            improvement = f" [+{pct_improvement:.1f}% vs baseline]"

        print(f"{row['name']:30s} IC: {row['ic']:+.4f} {sig}{improvement}")
        print(f"  > {row['description']}")
        print()

    # Save results
    output_dir = Path("results/fibonacci_combinations")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{args.symbol}_{args.timeframe}_combo_ic.csv"
    combo_results_df.to_csv(output_file, index=False)
    print()
    print(f"[SAVED] Results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
