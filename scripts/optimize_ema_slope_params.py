#!/usr/bin/env python3
"""
Optimize EMA slope parameters (period + lookback) for Fibonacci combinations.
Tests different EMA periods and slope lookback windows to find optimal parameters.
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
from src.core.indicators.vectorized import calculate_ema_vectorized


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


def test_ema_slope_params(
    candles_df: pd.DataFrame,
    fib_features_df: pd.DataFrame,
    ema_periods: list[int],
    lookbacks: list[int],
    train_ratio: float = 0.7,
) -> pd.DataFrame:
    """
    Test different EMA slope parameters and return results.

    Args:
        candles_df: Candle data with OHLCV
        fib_features_df: Pre-calculated Fibonacci features
        ema_periods: List of EMA periods to test
        lookbacks: List of slope lookback windows to test
        train_ratio: Ratio of data to use for training (rest for testing)

    Returns:
        DataFrame with results for each parameter combination
    """
    # Split data
    split_idx = int(len(candles_df) * train_ratio)

    close = candles_df["close"]
    returns = calculate_forward_returns(close, horizon=10)

    # Get Fibonacci 0.5 proximity feature
    fib05_prox = fib_features_df["fib05_prox_atr"]

    results = []

    print(
        f"\nTesting {len(ema_periods)} EMA periods × {len(lookbacks)} lookbacks = {len(ema_periods) * len(lookbacks)} combinations"
    )
    print("=" * 80)

    for ema_period in ema_periods:
        # Calculate EMA
        ema = calculate_ema_vectorized(close, period=ema_period)

        for lookback in lookbacks:
            # Calculate EMA slope (percentage change)
            ema_slope = ema.diff(lookback) / ema.shift(lookback)

            # Clip extreme values
            ema_slope = np.clip(ema_slope, -0.10, 0.10)

            # Calculate combination: fib05_prox_atr × ema_slope
            fib05_x_ema_slope = fib05_prox * ema_slope

            # Calculate IC on train set
            train_mask = slice(0, split_idx)
            ic_train, p_train = calculate_ic(
                fib05_x_ema_slope.iloc[train_mask].values, returns.iloc[train_mask].values
            )

            # Calculate IC on test set
            test_mask = slice(split_idx, None)
            ic_test, p_test = calculate_ic(
                fib05_x_ema_slope.iloc[test_mask].values, returns.iloc[test_mask].values
            )

            # Calculate baseline (EMA=20, lookback=5)
            if ema_period == 20 and lookback == 5:
                baseline_ic_train = ic_train
                baseline_ic_test = ic_test

            results.append(
                {
                    "ema_period": ema_period,
                    "lookback": lookback,
                    "ic_train": ic_train,
                    "p_train": p_train,
                    "ic_test": ic_test,
                    "p_test": p_test,
                    "ic_diff": (
                        abs(ic_train - ic_test)
                        if not (np.isnan(ic_train) or np.isnan(ic_test))
                        else np.nan
                    ),
                    "abs_ic_test": abs(ic_test) if not np.isnan(ic_test) else 0,
                }
            )

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Calculate improvement vs baseline
    if "baseline_ic_test" in locals():
        results_df["improvement_vs_baseline"] = (
            (results_df["abs_ic_test"] - abs(baseline_ic_test)) / abs(baseline_ic_test) * 100
        )

    # Sort by test IC (descending absolute value) and low train-test difference
    results_df = results_df.sort_values(["abs_ic_test", "ic_diff"], ascending=[False, True])

    return results_df


def main():
    parser = argparse.ArgumentParser(
        description="Optimize EMA slope parameters for Fibonacci combinations"
    )
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe (1W, 1D, 6h, 1h, 30m, etc)")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Train/test split ratio")
    args = parser.parse_args()

    print("=" * 80)
    print("EMA SLOPE PARAMETER OPTIMIZATION")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Train/Test Split: {args.train_ratio:.0%} / {(1-args.train_ratio):.0%}")
    print("=" * 80)

    # Load candles
    candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
    if not candles_path.exists():
        print(f"[ERROR] Candles not found at {candles_path}")
        return 1

    candles_df = pd.read_parquet(candles_path)
    print(f"\n[LOAD] Loaded {len(candles_df)} candles")

    # Calculate Fibonacci features
    print("[COMPUTE] Calculating Fibonacci features...")
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    fib_features_df = calculate_fibonacci_features_vectorized(candles_df, fib_config)
    print(f"[COMPUTED] {len(fib_features_df.columns)} Fibonacci features")

    # Define parameter search space
    ema_periods = [10, 15, 20, 25, 30, 40, 50]
    lookbacks = [3, 5, 7, 10, 15, 20]

    print("\n[SEARCH SPACE]")
    print(f"EMA Periods: {ema_periods}")
    print(f"Lookbacks: {lookbacks}")

    # Run parameter sweep
    results_df = test_ema_slope_params(
        candles_df,
        fib_features_df,
        ema_periods,
        lookbacks,
        train_ratio=args.train_ratio,
    )

    # Display top 10 results
    print("\n" + "=" * 80)
    print("TOP 10 PARAMETER COMBINATIONS (by Test IC)")
    print("=" * 80)
    print()

    for _idx, row in results_df.head(10).iterrows():
        sig_train = "[SIG]" if row["p_train"] < 0.05 else ""
        sig_test = "[SIG]" if row["p_test"] < 0.05 else ""

        print(f"EMA={int(row['ema_period']):2d}, Lookback={int(row['lookback']):2d}")
        print(f"  Train IC: {row['ic_train']:+.4f} (p={row['p_train']:.4f}) {sig_train}")
        print(f"  Test IC:  {row['ic_test']:+.4f} (p={row['p_test']:.4f}) {sig_test}")
        print(f"  IC Diff:  {row['ic_diff']:.4f} (lower is better - less overfit)")

        if "improvement_vs_baseline" in row:
            improvement = row["improvement_vs_baseline"]
            if not np.isnan(improvement):
                print(f"  Improvement vs baseline: {improvement:+.1f}%")
        print()

    # Find baseline (EMA=20, lookback=5)
    baseline = results_df[(results_df["ema_period"] == 20) & (results_df["lookback"] == 5)]

    if not baseline.empty:
        print("=" * 80)
        print("BASELINE (EMA=20, Lookback=5)")
        print("=" * 80)
        baseline_row = baseline.iloc[0]
        print(f"Train IC: {baseline_row['ic_train']:+.4f}")
        print(f"Test IC:  {baseline_row['ic_test']:+.4f}")
        print(f"IC Diff:  {baseline_row['ic_diff']:.4f}")
        print()

    # Recommendation
    best = results_df.iloc[0]
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if best["p_test"] < 0.05 and best["ic_diff"] < 0.05:
        improvement = best.get("improvement_vs_baseline", 0)

        if improvement > 5:
            print(f"[STRONG] Use EMA={int(best['ema_period'])}, Lookback={int(best['lookback'])}")
            print(f"  Test IC: {best['ic_test']:+.4f} (p<0.05)")
            print(f"  Improvement: +{improvement:.1f}% vs baseline")
            print(f"  Low overfit risk (IC diff = {best['ic_diff']:.4f})")
        else:
            print(f"[KEEP BASELINE] Improvement (+{improvement:.1f}%) is < 5%")
            print("  Stick with EMA=20, Lookback=5 (standard parameters)")
    else:
        print("[KEEP BASELINE] No significant improvement found")
        print("  Best params not statistically significant or high overfit risk")
        print("  Stick with EMA=20, Lookback=5 (standard parameters)")

    # Save results
    output_dir = Path("results/ema_slope_optimization")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{args.symbol}_{args.timeframe}_ema_slope_params.csv"
    results_df.to_csv(output_file, index=False)
    print()
    print(f"[SAVED] Full results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
