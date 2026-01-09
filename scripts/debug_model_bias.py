#!/usr/bin/env python3
"""
Quick debug script to check model prediction bias.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from core.strategy.prob_model import predict_proba_for
from core.utils.data_loader import load_features


def main():
    symbol = "tBTCUSD"
    timeframe = "6h"

    print("=" * 70)
    print("MODEL BIAS DEBUG")
    print("=" * 70)

    # Load features
    features_df = load_features(symbol, timeframe)
    print(f"\n[LOAD] {len(features_df)} samples loaded")

    # Get predictions for first 100 samples
    buy_probs = []
    sell_probs = []

    for i in range(min(100, len(features_df))):
        row = features_df.iloc[i]
        feats = {col: row[col] for col in features_df.columns if col != "timestamp"}

        probas, _ = predict_proba_for(symbol, timeframe, feats, regime="balanced")
        buy_probs.append(probas.get("buy", 0.0))
        sell_probs.append(probas.get("sell", 0.0))

    buy_probs = np.array(buy_probs)
    sell_probs = np.array(sell_probs)

    print("\n[PREDICTIONS] Analysis of first 100 samples:")
    print("=" * 70)
    print("Buy Probability:")
    print(f"  Mean:   {buy_probs.mean():.4f}")
    print(f"  Std:    {buy_probs.std():.4f}")
    print(f"  Min:    {buy_probs.min():.4f}")
    print(f"  Max:    {buy_probs.max():.4f}")
    print(f"  Median: {np.median(buy_probs):.4f}")

    print("\nSell Probability:")
    print(f"  Mean:   {sell_probs.mean():.4f}")
    print(f"  Std:    {sell_probs.std():.4f}")
    print(f"  Min:    {sell_probs.min():.4f}")
    print(f"  Max:    {sell_probs.max():.4f}")
    print(f"  Median: {np.median(sell_probs):.4f}")

    # Count which side wins
    buy_wins = (buy_probs > sell_probs).sum()
    sell_wins = (sell_probs > buy_probs).sum()
    ties = (np.abs(buy_probs - sell_probs) < 1e-9).sum()

    print("\n[DISTRIBUTION]")
    print("=" * 70)
    print(f"Buy wins:  {buy_wins:3d} ({100*buy_wins/100:.1f}%)")
    print(f"Sell wins: {sell_wins:3d} ({100*sell_wins/100:.1f}%)")
    print(f"Ties:      {ties:3d} ({100*ties/100:.1f}%)")

    # Check if bias is extreme
    if sell_wins > 90:
        print("\n⚠️  WARNING: Extreme SELL bias detected!")
        print("   Model almost NEVER predicts buy > sell")
        print("   This will cause SHORT-only trading!")
    elif buy_wins > 90:
        print("\n⚠️  WARNING: Extreme BUY bias detected!")
        print("   Model almost NEVER predicts sell > buy")
    else:
        print("\n✅ Model seems balanced")

    print("=" * 70)


if __name__ == "__main__":
    main()
