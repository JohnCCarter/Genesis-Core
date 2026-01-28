#!/usr/bin/env python3
"""
Quick IC validation for features v17.
Confirms that precomputed features match expected IC from analysis.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_forward_returns(close_prices: pd.Series, horizon: int = 10) -> pd.Series:
    """Calculate forward returns for IC calculation."""
    return close_prices.pct_change(horizon).shift(-horizon)


def calculate_ic(feature_values: np.ndarray, returns: np.ndarray) -> tuple[float, float]:
    """Calculate Information Coefficient (Spearman correlation)."""
    mask = ~(np.isnan(feature_values) | np.isnan(returns) | np.isinf(feature_values))
    if mask.sum() < 30:
        return np.nan, np.nan

    ic, p_val = spearmanr(feature_values[mask], returns[mask])
    return ic, p_val


def main():
    parser = argparse.ArgumentParser(description="Validate v17 features IC")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    args = parser.parse_args()

    print("=" * 80)
    print("FEATURES V17 IC VALIDATION")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Horizon: {args.horizon} bars")
    print("=" * 80)
    print()

    # Load features v17
    features_path = Path(f"data/features/{args.symbol}_{args.timeframe}_features_v17.feather")
    if not features_path.exists():
        print(f"[ERROR] Features v17 not found: {features_path}")
        return 1

    features_df = pd.read_feather(features_path)
    print(f"[LOAD] Loaded {len(features_df):,} samples with {len(features_df.columns)-1} features")

    # Load candles for returns
    from core.utils import get_candles_path

    candles_path = get_candles_path(args.symbol, args.timeframe)
    candles_df = pd.read_parquet(candles_path)

    # Calculate forward returns
    returns = calculate_forward_returns(candles_df["close"], horizon=args.horizon)

    print()
    print("=" * 80)
    print("FIBONACCI COMBINATION FEATURES - IC VALIDATION")
    print("=" * 80)
    print()

    # Test the 3 new combination features
    combination_features = {
        "fib05_x_ema_slope": "Fib 0.5 × EMA Slope (CHAMPION)",
        "fib_prox_x_adx": "Fib Proximity × ADX (TREND)",
        "fib05_x_rsi_inv": "Fib 0.5 × RSI Inv (MEAN REV)",
    }

    results = []

    for feature_name, description in combination_features.items():
        if feature_name not in features_df.columns:
            print(f"[ERROR] {feature_name} not found in features_df")
            continue

        ic, p_val = calculate_ic(features_df[feature_name].values, returns.values)

        sig = "[SIG]" if p_val < 0.05 else ""
        print(f"{feature_name:25s} IC: {ic:+.4f} (p={p_val:.4f}) {sig}")
        print(f"  > {description}")
        print()

        results.append(
            {
                "feature": feature_name,
                "ic": ic,
                "p_val": p_val,
                "significant": p_val < 0.05,
            }
        )

    # Also test baseline Fibonacci features
    print("=" * 80)
    print("BASELINE FIBONACCI FEATURES")
    print("=" * 80)
    print()

    baseline_features = ["fib_prox_score", "fib05_prox_atr", "fib0618_prox_atr"]

    for feature_name in baseline_features:
        if feature_name in features_df.columns:
            ic, p_val = calculate_ic(features_df[feature_name].values, returns.values)
            sig = "[SIG]" if p_val < 0.05 else ""
            print(f"{feature_name:25s} IC: {ic:+.4f} (p={p_val:.4f}) {sig}")

    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    sig_count = sum(1 for r in results if r["significant"])
    print(f"Significant combinations: {sig_count}/3")

    if sig_count == 3:
        print("[SUCCESS] All 3 combinations are statistically significant!")
    elif sig_count >= 2:
        print("[GOOD] Majority of combinations are significant")
    else:
        print("[WARNING] Less than 2 combinations are significant")

    return 0


if __name__ == "__main__":
    sys.exit(main())
