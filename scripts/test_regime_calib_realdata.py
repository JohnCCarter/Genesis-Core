#!/usr/bin/env python3
"""
Test regime-aware calibration with REAL data from different regimes.

Finds actual Bear/Bull/Ranging periods and tests predictions.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.strategy.evaluate import evaluate_pipeline

# Load candles
# Try two-layer structure first
from pathlib import Path
candles_path_curated = Path("data/curated/v1/candles/tBTCUSD_1h.parquet")
candles_path_legacy = Path("data/candles/tBTCUSD_1h.parquet")
if candles_path_curated.exists():
    candles_df = pd.read_parquet(candles_path_curated)
elif candles_path_legacy.exists():
    candles_df = pd.read_parquet(candles_path_legacy)
else:
    raise FileNotFoundError("tBTCUSD_1h.parquet not found in curated or legacy location")


# Classify regimes for all data
def classify_trend(closes, window=50):
    ema = closes.ewm(span=window, adjust=False).mean()
    trend = (closes - ema) / ema
    regimes = []
    for t in trend:
        if t > 0.02:
            regimes.append("bull")
        elif t < -0.02:
            regimes.append("bear")
        else:
            regimes.append("ranging")
    return regimes


regimes = classify_trend(candles_df["close"])

# Find examples of each regime (take middle of regime periods for stability)
bear_indices = [i for i, r in enumerate(regimes) if r == "bear"]
bull_indices = [i for i, r in enumerate(regimes) if r == "bull"]
ranging_indices = [i for i, r in enumerate(regimes) if r == "ranging"]

# Load config
runtime_cfg = json.load(open("config/runtime.json"))

print("=" * 80)
print("REGIME-AWARE CALIBRATION TEST (REAL DATA)")
print("=" * 80)
print(f"\nDataset: {len(candles_df)} candles")
print(f"Bear periods: {len(bear_indices)} ({len(bear_indices)/len(candles_df)*100:.1f}%)")
print(f"Bull periods: {len(bull_indices)} ({len(bull_indices)/len(candles_df)*100:.1f}%)")
print(f"Ranging periods: {len(ranging_indices)} ({len(ranging_indices)/len(candles_df)*100:.1f}%)")

# Test each regime type
test_cases = [
    ("BEAR", bear_indices[len(bear_indices) // 2] if bear_indices else None),
    ("BULL", bull_indices[len(bull_indices) // 2] if bull_indices else None),
    ("RANGING", ranging_indices[len(ranging_indices) // 2] if ranging_indices else None),
]

results = {}

for regime_name, idx in test_cases:
    if idx is None:
        print(f"\n{regime_name}: NO DATA AVAILABLE")
        continue

    print(f"\n{'='*80}")
    print(f"TEST: {regime_name} REGIME (index {idx})")
    print(f"{'='*80}")

    # Get candles window (200 bars up to this point)
    start_idx = max(0, idx - 199)
    test_candles = {
        "open": candles_df["open"].iloc[start_idx : idx + 1].tolist(),
        "high": candles_df["high"].iloc[start_idx : idx + 1].tolist(),
        "low": candles_df["low"].iloc[start_idx : idx + 1].tolist(),
        "close": candles_df["close"].iloc[start_idx : idx + 1].tolist(),
        "volume": candles_df["volume"].iloc[start_idx : idx + 1].tolist(),
    }

    policy = {"symbol": "tBTCUSD", "timeframe": "1h"}

    # Run pipeline
    result, meta = evaluate_pipeline(
        test_candles, policy=policy, configs=runtime_cfg["cfg"], state={}
    )

    # Extract info
    detected_regime = result.get("regime", "unknown")
    probas = result.get("probas", {})
    confidence = result.get("confidence", {})
    action = result.get("action", "NONE")
    size = meta.get("decision", {}).get("size", 0.0)
    reasons = meta.get("decision", {}).get("reasons", [])

    # Check calibration info
    calib_info = meta.get("proba", {}).get("calibration_used", {})
    regime_used = calib_info.get("regime", "none")
    calib_a = calib_info.get("buy_calib", {}).get("a", 1.0)

    print(f"\nDetected Regime:  {detected_regime}")
    print(f"Calib Regime:     {regime_used}")
    print(f"Calib a (buy):    {calib_a:.4f}")
    print("")
    print(f"Probabilities:    buy={probas.get('buy', 0):.4f}, sell={probas.get('sell', 0):.4f}")
    print(
        f"Confidence:       buy={confidence.get('buy', 0):.4f}, sell={confidence.get('sell', 0):.4f}"
    )
    print("")
    print(f"Decision:         {action}")
    print(f"Size:             {size:.4f}")
    if reasons:
        print(f"Blocked by:       {', '.join(reasons)}")

    results[regime_name] = {
        "detected_regime": detected_regime,
        "probas": probas,
        "action": action,
        "calib_a": calib_a,
    }

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")

for regime_name, result in results.items():
    print(f"\n{regime_name}:")
    print(f"  Detected: {result['detected_regime']}")
    print(f"  Calib a:  {result['calib_a']:.4f}")
    print(f"  P(buy):   {result['probas'].get('buy', 0):.4f}")
    print(f"  Action:   {result['action']}")

# Check if Bear has higher probabilities
if "BEAR" in results and "BULL" in results:
    bear_prob = results["BEAR"]["probas"].get("buy", 0)
    bull_prob = results["BULL"]["probas"].get("buy", 0)
    print(f"\nBear boost working: {abs(results['BEAR']['calib_a'] - 1.0) > 1.0}")
    print(f"Bear vs Bull P(buy): {bear_prob:.4f} vs {bull_prob:.4f}")

print("=" * 80)
