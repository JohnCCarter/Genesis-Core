#!/usr/bin/env python3
"""
Test script to verify frozen exit context works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine


def test_frozen_exit_context():
    """Test that frozen exit context is properly initialized."""

    # Initialize engine
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2025-04-16",
        end_date="2025-06-16",  # Longer period for testing
        initial_capital=10000.0,
        warmup_bars=120,
    )

    # Load data
    if not engine.load_data():
        print("[ERROR] Failed to load data")
        return

    print(f"[OK] Loaded {len(engine.candles_df):,} candles")

    # Test first few bars after warmup
    test_bars = 5
    start_idx = engine.warmup_bars

    for i in range(start_idx, min(start_idx + test_bars, len(engine.candles_df))):
        bar = engine.candles_df.iloc[i]
        timestamp = bar["timestamp"]
        close_price = bar["close"]

        # Build candles window for pipeline
        candles_window = engine._build_candles_window(i)

        # Run pipeline
        try:
            from core.strategy.evaluate import evaluate_pipeline

            result, meta = evaluate_pipeline(
                candles=candles_window,
                policy={"symbol": "tBTCUSD", "timeframe": "1h"},
                configs={
                    "thresholds": {"entry_conf_overall": 0.5},
                    "risk": {"risk_map": [[0.5, 0.1], [0.6, 0.2]]},
                },
                state=engine.state,
            )

            # Check action
            action = result.get("action", "NONE")
            size = meta.get("decision", {}).get("size", 0.0)

            if action != "NONE" and size > 0:
                print(f"\n[ENTRY] Bar {i}: {action} {size:.4f} @ ${close_price:.2f}")

                # Simulate position opening
                exec_result = engine.position_tracker.execute_action(
                    action=action,
                    size=size,
                    price=close_price,
                    timestamp=timestamp,
                    symbol=engine.symbol,
                )

                if exec_result.get("executed"):
                    position = engine.position_tracker.position
                    print(f"[POSITION] Opened: {position.side} {position.current_size:.4f}")

                    # Manually initialize exit context (like in engine.run)
                    print(f"[DEBUG] Before init: exit_ctx = {position.exit_ctx}")
                    print(f"[DEBUG] Meta keys: {list(meta.keys())}")
                    print(f"[DEBUG] Features meta: {meta.get('features', {})}")
                    engine._initialize_position_exit_context(result, meta, close_price, timestamp)
                    print(f"[DEBUG] After init: exit_ctx = {position.exit_ctx}")

                    # Check if exit context was armed
                    if position.exit_ctx:
                        print(f"[EXIT_CTX] Armed: {position.exit_ctx['swing_id']}")
                        print(f"[EXIT_CTX] Fib levels: {list(position.exit_ctx['fib'].keys())}")
                        print(f"[EXIT_CTX] Swing bounds: {position.exit_ctx['swing_bounds']}")

                        # Test reachability
                        fib_levels = position.exit_ctx["fib"]
                        if fib_levels:
                            nearest = min(abs(close_price - v) for v in fib_levels.values())
                            print(f"[REACH] Nearest Fib: {nearest:.2f} from current price")

                            # Test a few more bars to see if exits trigger
                            for j in range(i + 1, min(i + 4, len(engine.candles_df))):
                                next_bar = engine.candles_df.iloc[j]
                                next_bar["close"]

                                # Check if any Fib level is crossed
                                crossed = False
                                for level_name, level_price in fib_levels.items():
                                    if next_bar["low"] <= level_price <= next_bar["high"]:
                                        print(
                                            f"[CROSS] Bar {j}: Price crossed {level_name} @ {level_price:.2f}"
                                        )
                                        crossed = True
                                        break

                                if crossed:
                                    break
                    else:
                        print("[EXIT_CTX] NOT ARMED - this is the problem!")

                    break  # Only test first position

        except Exception as e:
            print(f"[ERROR] Bar {i}: {e}")
            continue

    print("\n[TEST] Frozen exit context test complete")


if __name__ == "__main__":
    test_frozen_exit_context()
