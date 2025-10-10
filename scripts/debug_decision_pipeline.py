#!/usr/bin/env python3
"""
Debug full decision pipeline to see where LONGs are blocked.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from core.config.authority import ConfigAuthority
from core.strategy.evaluate import evaluate_pipeline
from core.utils.data_loader import load_features


def main():
    symbol = "tBTCUSD"
    timeframe = "6h"

    print("=" * 70)
    print("DECISION PIPELINE DEBUG")
    print("=" * 70)

    # Load config
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    cfg = cfg_obj.model_dump()

    # Load candles and features
    candles_path_curated = Path(f"data/curated/v1/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path_curated)
    features_df = load_features(symbol, timeframe)

    print(f"\n[DATA] {len(candles_df)} candles loaded")
    print(f"[DATA] {len(features_df)} features loaded")

    # Test 10 samples
    policy = {"symbol": symbol, "timeframe": timeframe}

    long_count = 0
    short_count = 0
    none_count = 0

    reasons_counter = {}

    # Sample detailed analysis
    sample_details = []

    for i in range(120, min(130, len(candles_df))):  # First 10 samples for detailed analysis
        # Build candles dict for evaluate_pipeline
        candles = {
            "open": candles_df["open"].iloc[: i + 1].tolist(),
            "high": candles_df["high"].iloc[: i + 1].tolist(),
            "low": candles_df["low"].iloc[: i + 1].tolist(),
            "close": candles_df["close"].iloc[: i + 1].tolist(),
            "volume": candles_df["volume"].iloc[: i + 1].tolist(),
        }

        # Run pipeline
        result, meta = evaluate_pipeline(candles, policy=policy, configs=cfg, state={})

        action = result.get("action", "NONE")
        probas = result.get("probas", {})
        confidence = result.get("confidence", {})

        # Store details for first 10
        if i < 130:
            sample_details.append(
                {
                    "i": i,
                    "action": action,
                    "p_buy": probas.get("buy", 0.0),
                    "p_sell": probas.get("sell", 0.0),
                    "c_buy": confidence.get("buy", 0.0),
                    "c_sell": confidence.get("sell", 0.0),
                }
            )

        if action == "LONG":
            long_count += 1
        elif action == "SHORT":
            short_count += 1
        else:
            none_count += 1
            # Track reasons
            reasons = meta.get("decision", {}).get("reasons", [])
            for reason in reasons:
                reasons_counter[reason] = reasons_counter.get(reason, 0) + 1

    # Continue with remaining 90 samples without storing details
    for i in range(130, min(220, len(candles_df))):
        candles = {
            "open": candles_df["open"].iloc[: i + 1].tolist(),
            "high": candles_df["high"].iloc[: i + 1].tolist(),
            "low": candles_df["low"].iloc[: i + 1].tolist(),
            "close": candles_df["close"].iloc[: i + 1].tolist(),
            "volume": candles_df["volume"].iloc[: i + 1].tolist(),
        }

        result, meta = evaluate_pipeline(candles, policy=policy, configs=cfg, state={})
        action = result.get("action", "NONE")

        if action == "LONG":
            long_count += 1
        elif action == "SHORT":
            short_count += 1
        else:
            none_count += 1
            reasons = meta.get("decision", {}).get("reasons", [])
            for reason in reasons:
                reasons_counter[reason] = reasons_counter.get(reason, 0) + 1

    total = long_count + short_count + none_count

    # Print detailed sample analysis
    print("\n[SAMPLE ANALYSIS] First 10 decisions:")
    print("=" * 70)
    print(f"{'i':>4s} {'Action':7s} {'P(buy)':>7s} {'P(sell)':>7s} {'C(buy)':>7s} {'C(sell)':>7s}")
    print("-" * 70)
    for sample in sample_details:
        print(
            f"{sample['i']:4d} {sample['action']:7s} {sample['p_buy']:7.4f} {sample['p_sell']:7.4f} {sample['c_buy']:7.4f} {sample['c_sell']:7.4f}"
        )

    print("\n[RESULTS] Analysis of 100 decisions:")
    print("=" * 70)
    print(f"LONG:  {long_count:3d} ({100*long_count/total:.1f}%)")
    print(f"SHORT: {short_count:3d} ({100*short_count/total:.1f}%)")
    print(f"NONE:  {none_count:3d} ({100*none_count/total:.1f}%)")

    if none_count > 0:
        print("\n[NONE REASONS] Why trades were blocked:")
        print("=" * 70)
        for reason, count in sorted(reasons_counter.items(), key=lambda x: -x[1]):
            print(f"  {reason:20s}: {count:3d} ({100*count/none_count:.1f}%)")

    # Diagnose
    print("\n[DIAGNOSIS]")
    print("=" * 70)
    if short_count > 90:
        print("⚠️  EXTREME SHORT BIAS - Model/config heavily favors shorts!")
    elif long_count > 90:
        print("⚠️  EXTREME LONG BIAS - Model/config heavily favors longs!")
    elif none_count > 90:
        print("⚠️  EXTREME FILTERING - Almost all trades blocked!")
        print("   Top blocker reasons shown above")
    else:
        print("✅ Seems relatively balanced")

    print("=" * 70)


if __name__ == "__main__":
    main()
