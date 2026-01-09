#!/usr/bin/env python3
"""
Debug script to understand why we get 0 signals in backtest.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.strategy.evaluate import evaluate_pipeline


def debug_strategy_signals():
    """Debug why we get 0 signals."""

    # Initialize engine
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2025-04-16",
        end_date="2025-10-13",
        initial_capital=10000.0,
        warmup_bars=120,
    )

    # Load data
    if not engine.load_data():
        print("[ERROR] Failed to load data")
        return

    print(f"[OK] Loaded {len(engine.candles_df):,} candles")

    # Test first few bars after warmup
    test_bars = 10
    start_idx = engine.warmup_bars

    print(f"\n[DEBUG] Testing bars {start_idx} to {start_idx + test_bars - 1}")

    signals_found = 0
    total_tested = 0

    for i in range(start_idx, min(start_idx + test_bars, len(engine.candles_df))):
        # Build candles window
        candles_window = engine._build_candles_window(i)

        # Create policy with symbol and timeframe
        policy = {"symbol": "tBTCUSD", "timeframe": "1h"}

        # Run pipeline with configs to see thresholds
        configs = {
            "thresholds": {
                "entry_conf_overall": 0.5,  # Lower threshold to test
                "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
            }
        }

        try:
            result, meta = evaluate_pipeline(candles_window, policy=policy, configs=configs)

            total_tested += 1

            # Check action
            action = result.get("action", "NONE")
            probas = result.get("probas", {})
            regime = result.get("regime", "unknown")

            if action != "NONE":
                signals_found += 1
                print(f"Bar {i}: {action} - probas: {probas} - regime: {regime}")
                print(f"  Decision meta: {meta.get('decision', {})}")

            # Show first few results regardless
            if i < start_idx + 3:
                print(f"Bar {i}: {action} - probas: {probas} - regime: {regime}")
                decision_meta = meta.get("decision", {})
                if decision_meta.get("reasons"):
                    print(f"  Reasons: {decision_meta['reasons']}")
                if decision_meta.get("versions"):
                    print(f"  Versions: {decision_meta['versions']}")
                if decision_meta.get("size"):
                    print(f"  Size: {decision_meta['size']}")

                # Show threshold info
                p_buy = probas.get("buy", 0.0)
                p_sell = probas.get("sell", 0.0)
                print(
                    f"  Threshold check: buy={p_buy:.3f} >= 0.5? {p_buy >= 0.5}, sell={p_sell:.3f} >= 0.5? {p_sell >= 0.5}"
                )

        except Exception as e:
            print(f"[ERROR] Bar {i}: {e}")

    print(f"\n[SUMMARY] Found {signals_found} signals out of {total_tested} tested bars")

    if signals_found == 0:
        print("\n[DEBUG] No signals found. Let's check model loading...")

        # Test model loading
        from core.strategy.model_registry import ModelRegistry

        registry = ModelRegistry()
        model_meta = registry.get_meta("tBTCUSD", "1h")

        if model_meta:
            print(f"[OK] Model loaded: {model_meta.get('version', 'unknown')}")
            print(f"Schema: {model_meta.get('schema', [])}")
        else:
            print("[ERROR] Model not found!")


if __name__ == "__main__":
    debug_strategy_signals()
