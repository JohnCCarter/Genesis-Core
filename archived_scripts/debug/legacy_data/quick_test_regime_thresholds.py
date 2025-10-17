#!/usr/bin/env python3
"""
Quick test of regime-specific thresholds in pipeline.

Simulates actual pipeline execution with real candles and new thresholds.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.strategy.evaluate import evaluate_pipeline

# Load real candles
candles_df = pd.read_parquet("data/candles/tBTCUSD_1h.parquet")

# Take last 200 bars for testing
test_candles = {
    "open": candles_df["open"].tail(200).tolist(),
    "high": candles_df["high"].tail(200).tolist(),
    "low": candles_df["low"].tail(200).tolist(),
    "close": candles_df["close"].tail(200).tolist(),
    "volume": candles_df["volume"].tail(200).tolist(),
}

# Load config with regime thresholds
runtime_cfg = json.load(open("config/runtime.json"))

# Policy
policy = {"symbol": "tBTCUSD", "timeframe": "1h"}

print("=" * 80)
print("REGIME THRESHOLDS TEST")
print("=" * 80)
print("\nConfig thresholds:")
print(json.dumps(runtime_cfg["cfg"]["thresholds"], indent=2))

# Test scenarios
scenarios = [
    {"name": "UNIFORM (old)", "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {}}},
    {
        "name": "REGIME-SPECIFIC (new)",
        "thresholds": runtime_cfg["cfg"]["thresholds"],
    },
]

results = {}

for scenario in scenarios:
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"{'='*80}")

    # Update config with scenario thresholds
    test_cfg = dict(runtime_cfg["cfg"])
    test_cfg["thresholds"] = scenario["thresholds"]

    # Run pipeline
    result, meta = evaluate_pipeline(test_candles, policy=policy, configs=test_cfg, state={})

    # Extract key info
    action = result.get("action", "NONE")
    probas = result.get("probas", {})
    confidence = result.get("confidence", {})
    regime = result.get("regime", "unknown")
    reasons = meta.get("decision", {}).get("reasons", [])
    size = meta.get("decision", {}).get("size", 0.0)

    print(f"\nRegime:      {regime}")
    print(f"Probas:      buy={probas.get('buy', 0):.4f}, sell={probas.get('sell', 0):.4f}")
    print(f"Confidence:  buy={confidence.get('buy', 0):.4f}, sell={confidence.get('sell', 0):.4f}")
    print(f"Action:      {action}")
    print(f"Size:        {size:.4f}")
    if reasons:
        print(f"Reasons:     {', '.join(reasons)}")

    results[scenario["name"]] = {
        "action": action,
        "regime": regime,
        "probas": probas,
        "confidence": confidence,
        "size": size,
        "reasons": reasons,
    }

# Compare
print(f"\n{'='*80}")
print("COMPARISON")
print(f"{'='*80}")

uniform = results["UNIFORM (old)"]
regime_spec = results["REGIME-SPECIFIC (new)"]

print(f"\nUNIFORM:           Action={uniform['action']}, Size={uniform['size']:.4f}")
print(f"REGIME-SPECIFIC:   Action={regime_spec['action']}, Size={regime_spec['size']:.4f}")

if uniform["action"] == regime_spec["action"]:
    print("\n[SAME] Both strategies give same action")
else:
    print("\n[DIFFERENT] Strategies differ!")
    print(f"  Uniform blocked by: {', '.join(uniform['reasons'])}")
    print(
        f"  Regime-specific: {', '.join(regime_spec['reasons']) if regime_spec['reasons'] else 'PASSED ALL GATES'}"
    )

print(f"\n{'='*80}")
