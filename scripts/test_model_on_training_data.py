#!/usr/bin/env python3
"""
Test if model predictions are sane on training data itself.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.strategy.prob_model import predict_proba

# Load model
model_path = Path("results/models/tBTCUSD_6h_v3.json")
with open(model_path) as f:
    model = json.load(f)

# Create dummy features (all zeros)
schema = model["schema"]
features_zero = dict.fromkeys(schema, 0.0)

# Test with zero features
probas_zero = predict_proba(
    features_zero,
    schema=schema,
    buy_w=model["buy"]["w"],
    buy_b=model["buy"]["b"],
    sell_w=model["sell"]["w"],
    sell_b=model["sell"]["b"],
)

print("=" * 70)
print("MODEL SANITY CHECK")
print("=" * 70)
print("\n[TEST 1] All features = 0.0:")
print(f"  P(buy):  {probas_zero['buy']:.4f}")
print(f"  P(sell): {probas_zero['sell']:.4f}")
print(f"  P(hold): {probas_zero['hold']:.4f}")

# The bias terms tell us the default prediction
print("\n[MODEL BIASES]:")
print(f"  Buy bias:  {model['buy']['b']:.4f}")
print(f"  Sell bias: {model['sell']['b']:.4f}")

# With large negative buy bias and large positive sell bias,
# the model will ALWAYS prefer sell!


def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


p_buy_raw = sigmoid(model["buy"]["b"])
p_sell_raw = sigmoid(model["sell"]["b"])

print("\n[RAW PROBABILITIES] (from biases only):")
print(f"  Buy:  {p_buy_raw:.4f}")
print(f"  Sell: {p_sell_raw:.4f}")

if model["buy"]["b"] < -3:
    print(f"\n⚠️  BUY BIAS IS EXTREMELY NEGATIVE ({model['buy']['b']:.2f})")
    print("   This means model learned to NEVER predict buy!")
    print("   Even with positive features, sigmoid(-4.5) ≈ 0.01")

if model["sell"]["b"] > 3:
    print(f"\n⚠️  SELL BIAS IS EXTREMELY POSITIVE ({model['sell']['b']:.2f})")
    print("   This means model learned to ALWAYS predict sell!")
    print("   Even with negative features, sigmoid(4.5) ≈ 0.99")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("The model bias terms are extreme, causing constant SHORT signals.")
print("This suggests training data had severe class imbalance or")
print("there's a bug in how labels are generated/used.")
print("=" * 70)
