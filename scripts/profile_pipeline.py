#!/usr/bin/env python3
"""Profile pipeline latency per module."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features_backtest
from core.strategy.prob_model import predict_proba_for
from core.strategy.regime import classify_regime


def generate_dummy_candles(n: int = 120) -> dict:
    """Generate dummy OHLCV data."""
    import random

    base = 100.0
    candles = {
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": [],
    }
    for _ in range(n):
        o = base + random.uniform(-1, 1)
        c = o + random.uniform(-0.5, 0.5)
        h = max(o, c) + random.uniform(0, 0.3)
        low = min(o, c) - random.uniform(0, 0.3)
        v = random.uniform(100, 1000)
        candles["open"].append(o)
        candles["high"].append(h)
        candles["low"].append(low)
        candles["close"].append(c)
        candles["volume"].append(v)
        base = c
    return candles


def time_function(func, *args, **kwargs):
    """Time a function call and return (result, elapsed_ms)."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    return result, elapsed


def main():
    print("=== Genesis-Core Pipeline Profiling ===\n")

    # Warm-up (import overhead)
    candles = generate_dummy_candles(120)
    configs = {
        "features": {
            "percentiles": {"ema_delta_pct": [-0.05, 0.05], "rsi": [-1.0, 1.0]},
            "versions": {"feature_set": "v1"},
        },
        "thresholds": {"entry_conf_overall": 0.7, "regime_proba": {"balanced": 0.58}},
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
        "ev": {"R_default": 1.8},
    }

    # Run multiple iterations for more accurate measurements
    iterations = 100
    results = {"features": [], "prob_model": [], "confidence": [], "regime": [], "decision": []}

    print(f"Running {iterations} iterations per module...\n")

    for _ in range(iterations):
        # 1. Features
        result, t_feats = time_function(
            extract_features_backtest,
            candles,
            asof_bar=len(candles["close"]) - 1,
            timeframe="1m",
            symbol="tBTCUSD",
            config=configs,
        )
        feats, feats_meta = result
        results["features"].append(t_feats)

        # 2. Probability
        result, t_prob = time_function(predict_proba_for, "tBTCUSD", "1m", feats)
        probas, pmeta = result
        results["prob_model"].append(t_prob)

        # 3. Confidence
        result, t_conf = time_function(compute_confidence, probas, config=configs.get("quality"))
        conf, conf_meta = result
        results["confidence"].append(t_conf)

        # 4. Regime
        htf_features = {}  # empty for stub
        result, t_regime = time_function(
            classify_regime, htf_features, prev_state={}, config=configs
        )
        regime, regime_state = result
        results["regime"].append(t_regime)

        # 5. Decision
        policy = {"symbol": "tBTCUSD", "timeframe": "1m"}
        result, t_decision = time_function(
            decide,
            policy,
            probas=probas,
            confidence=conf,
            regime=regime,
            state={},
            risk_ctx=configs.get("risk"),
            cfg=configs,
        )
        action, action_meta = result
        results["decision"].append(t_decision)

    # Calculate statistics
    with open("profile_results_utf8.txt", "w", encoding="utf-8") as f:
        f.write("=== Genesis-Core Pipeline Profiling ===\n\n")
        f.write(
            f"{'Module':<15} {'Min (ms)':<10} {'Avg (ms)':<10} {'Max (ms)':<10} {'Target':<10}\n"
        )
        f.write("=" * 60 + "\n")

        target_ms = 20.0
        all_pass = True

        for module, times in results.items():
            min_t = min(times)
            avg_t = sum(times) / len(times)
            max_t = max(times)
            status = "[PASS]" if avg_t <= target_ms else "[FAIL]"

            if avg_t > target_ms:
                all_pass = False

            f.write(f"{module:<15} {min_t:<10.3f} {avg_t:<10.3f} {max_t:<10.3f} {status}\n")

        # Total pipeline latency
        total_times = [
            sum(
                [
                    results["features"][i],
                    results["prob_model"][i],
                    results["confidence"][i],
                    results["regime"][i],
                    results["decision"][i],
                ]
            )
            for i in range(iterations)
        ]

        total_min = min(total_times)
        total_avg = sum(total_times) / len(total_times)
        total_max = max(total_times)
        total_status = "[PASS]" if total_avg <= 100.0 else "[FAIL]"

        f.write("=" * 60 + "\n")
        f.write(
            f"{'TOTAL PIPELINE':<15} {total_min:<10.3f} {total_avg:<10.3f} {total_max:<10.3f} {total_status}\n"
        )
        f.write("=" * 60 + "\n")

        f.write(f"\nTarget per module: <= {target_ms} ms\n")
        f.write("Target total pipeline: <= 100 ms\n")

        if all_pass and total_avg <= 100.0:
            f.write("\n[OK] All modules meet latency requirements!\n")
            print("DONE")
            return 0
        else:
            f.write("\n[WARN] Some modules exceed latency budget!\n")
            print("DONE_WARN")
            return 1


if __name__ == "__main__":
    sys.exit(main())
