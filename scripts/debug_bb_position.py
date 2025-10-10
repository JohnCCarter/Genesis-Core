#!/usr/bin/env python3
"""
Debug script to understand bb_position_inv_ma3 difference between methods.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.vectorized import calculate_all_features_vectorized
from core.strategy.features_asof import extract_features_backtest


def main():
    # Load candles
    candles_path = Path("data/candles/tBTCUSD_1h.parquet")
    df = pd.read_parquet(candles_path)

    # Take last 10 samples for debugging
    test_indices = list(range(len(df) - 10, len(df)))

    print("=" * 80)
    print("DEBUGGING bb_position_inv_ma3 DIFFERENCE")
    print("=" * 80)

    # Method 1: Vectorized
    features_vec = calculate_all_features_vectorized(df)
    vec_values = features_vec["bb_position_inv_ma3"].iloc[test_indices].values

    # Method 2: Per-sample
    per_sample_values = []
    for idx in test_indices:
        candles_window = {
            "open": df["open"].iloc[: idx + 1].tolist(),
            "high": df["high"].iloc[: idx + 1].tolist(),
            "low": df["low"].iloc[: idx + 1].tolist(),
            "close": df["close"].iloc[: idx + 1].tolist(),
            "volume": df["volume"].iloc[: idx + 1].tolist(),
        }
        feats, _ = extract_features_backtest(candles_window, asof_bar=idx)
        per_sample_values.append(feats["bb_position_inv_ma3"])

    per_sample_values = np.array(per_sample_values)

    # Compare
    print(f"\n{'Index':<8} {'Vectorized':<15} {'Per-Sample':<15} {'Diff':<15} {'Diff %':<10}")
    print("-" * 80)

    for i, idx in enumerate(test_indices):
        vec_val = vec_values[i]
        ps_val = per_sample_values[i]
        diff = abs(vec_val - ps_val)
        diff_pct = (diff / ps_val * 100) if ps_val != 0 else 0.0

        print(
            f"{idx:<8} {vec_val:<15.10f} {ps_val:<15.10f} {diff:<15.10e} {diff_pct:<10.6f}%"
        )

    # Summary
    max_diff = np.abs(vec_values - per_sample_values).max()
    mean_diff = np.abs(vec_values - per_sample_values).mean()

    print("\n" + "=" * 80)
    print(f"Max difference:  {max_diff:.10e}")
    print(f"Mean difference: {mean_diff:.10e}")
    print("=" * 80)

    # Now let's debug the intermediate values
    print("\n" + "=" * 80)
    print("DEBUGGING INTERMEDIATE VALUES (last sample)")
    print("=" * 80)

    # Get last index
    last_idx = test_indices[-1]

    # Vectorized: Get bb_position for last 3 bars
    from core.indicators.vectorized import calculate_bb_position_vectorized

    bb_position_vec = calculate_bb_position_vectorized(df["close"], period=20, std_dev=2.0)
    bb_pos_inv_vec = 1.0 - bb_position_vec

    # Get last 4 bars (to show lag effect)
    print("\nVectorized BB position (last 4 bars):")
    for i in range(4):
        idx = last_idx - 3 + i
        print(f"  Bar {idx}: bb_pos={bb_position_vec.iloc[idx]:.10f}, bb_pos_inv={bb_pos_inv_vec.iloc[idx]:.10f}")

    # Calculate rolling mean manually
    last_3_inv = bb_pos_inv_vec.iloc[last_idx - 2 : last_idx + 1].values
    manual_mean = last_3_inv.mean()
    rolling_mean = bb_pos_inv_vec.rolling(window=3, min_periods=1).mean().iloc[last_idx]

    print(f"\nLast 3 inverted values: {last_3_inv}")
    print(f"Manual mean: {manual_mean:.10f}")
    print(f"Rolling mean: {rolling_mean:.10f}")
    print(f"Clipped rolling mean: {np.clip(rolling_mean, 0.0, 1.0):.10f}")

    # Per-sample: Get bb_position for last 3 bars
    print("\nPer-sample BB position (last 3 bars):")
    from core.indicators.bollinger import bollinger_bands

    candles_window = {
        "open": df["open"].iloc[: last_idx + 1].tolist(),
        "high": df["high"].iloc[: last_idx + 1].tolist(),
        "low": df["low"].iloc[: last_idx + 1].tolist(),
        "close": df["close"].iloc[: last_idx + 1].tolist(),
        "volume": df["volume"].iloc[: last_idx + 1].tolist(),
    }

    closes = candles_window["close"]
    bb = bollinger_bands(closes, period=20, std_dev=2.0)
    bb_positions = bb["position"]

    print(f"  Total positions calculated: {len(bb_positions)}")
    print(f"  Last 4 positions:")
    for i in range(4):
        pos_idx = len(bb_positions) - 4 + i
        if pos_idx >= 0:
            print(f"    Position[{pos_idx}] = {bb_positions[pos_idx]:.10f}, inverted = {1.0 - bb_positions[pos_idx]:.10f}")

    # Get last 3 and calculate mean
    bb_last_3 = bb_positions[-3:] if len(bb_positions) >= 3 else [0.5] * 3
    bb_inv_values = [1.0 - pos for pos in bb_last_3]
    ps_mean = sum(bb_inv_values) / len(bb_inv_values)

    print(f"\nLast 3 positions: {bb_last_3}")
    print(f"Last 3 inverted: {bb_inv_values}")
    print(f"Per-sample mean: {ps_mean:.10f}")
    print(f"Clipped mean: {np.clip(ps_mean, 0.0, 1.0):.10f}")


if __name__ == "__main__":
    main()

