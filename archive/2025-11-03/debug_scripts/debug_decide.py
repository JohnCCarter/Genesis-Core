#!/usr/bin/env python3
"""
Debug decide() function
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.strategy.decision import decide

# Test with exact same parameters as evaluate_pipeline
policy = {"symbol": "tBTCUSD", "timeframe": "6h"}
probas = {"buy": 0.011545905786870887, "sell": 0.9884540942131291, "hold": 0.0}
confidence = {"buy": 0.011545905786870887, "sell": 0.9884540942131291}
regime = "balanced"
state = {}
risk_ctx = {"risk_map": [[0.35, 0.1], [0.45, 0.15], [0.55, 0.2], [0.65, 0.25], [0.75, 0.3]]}
cfg = {
    "thresholds": {
        "entry_conf_overall": 0.35,
        "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
    },
    "risk": {"risk_map": [[0.35, 0.1], [0.45, 0.15], [0.55, 0.2], [0.65, 0.25], [0.75, 0.3]]},
    "exit": {
        "enabled": True,
        "exit_conf_threshold": 0.3,
        "max_hold_bars": 20,
        "regime_aware_exits": True,
    },
    "gates": {"cooldown_bars": 0, "hysteresis_steps": 2},
    "htf_exit_config": {
        "enable_partials": True,
        "enable_trailing": True,
        "enable_structure_breaks": True,
        "partial_1_pct": 0.4,
        "partial_2_pct": 0.3,
        "fib_threshold_atr": 0.3,
        "trail_atr_multiplier": 1.3,
        "swing_update_strategy": "fixed",
    },
    "warmup_bars": 50,
}

print("Testing decide() with exact parameters...")
action, meta = decide(
    policy,
    probas=probas,
    confidence=confidence,
    regime=regime,
    state=state,
    risk_ctx=risk_ctx,
    cfg=cfg,
)
print(f"Action: {action}")
print(f"Meta: {meta}")
print(f'Size: {meta.get("size", "NOT_FOUND")}')

# Debug risk management step by step
print("\n=== DEBUGGING RISK MANAGEMENT ===")
risk_map = (cfg.get("risk") or {}).get("risk_map", [])
print(f"Risk map from cfg: {risk_map}")

c_buy = float(confidence.get("buy", 0.0))
c_sell = float(confidence.get("sell", 0.0))
print(f"Buy confidence: {c_buy}")
print(f"Sell confidence: {c_sell}")

candidate = "SHORT"  # Based on probas
conf_val = c_buy if candidate == "LONG" else c_sell
print(f"Candidate: {candidate}")
print(f"Confidence value: {conf_val}")

size = 0.0
try:
    for thr_v, sz in sorted(risk_map, key=lambda x: float(x[0])):
        print(f"Checking: {conf_val} >= {thr_v}? {conf_val >= float(thr_v)}")
        if conf_val >= float(thr_v):
            size = float(sz)
            print(f"Size set to: {size}")
except Exception as e:
    print(f"Exception in risk management: {e}")
    size = 0.0

print(f"Final size: {size}")
