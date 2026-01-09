#!/usr/bin/env python3
"""
Detaljerad statisk test för frozen exit context.
Mäter och debuggar partial exits med full telemetri.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.backtest.position_tracker import Position


class StaticExitTelemetry:
    """Telemetri för statisk exit testing."""

    def __init__(self):
        self.bar_logs: list[dict] = []
        self.position_logs: list[dict] = []
        self.exit_logs: list[dict] = []
        self.fib_proximity_logs: list[dict] = []

    def log_bar(self, bar_idx: int, bar_data: dict, position: Position = None):
        """Logga bar data och position state."""
        log_entry = {
            "bar_idx": bar_idx,
            "timestamp": bar_data["timestamp"],
            "price": {
                "open": bar_data["open"],
                "high": bar_data["high"],
                "low": bar_data["low"],
                "close": bar_data["close"],
            },
            "position": None,
        }

        if position and position.current_size > 0:
            log_entry["position"] = {
                "side": position.side,
                "size": position.current_size,
                "entry_price": position.entry_price,
                "entry_time": position.entry_time.isoformat(),
                "unrealized_pnl": position.unrealized_pnl,
                "exit_ctx_armed": position.exit_ctx is not None,
            }

            if position.exit_ctx:
                log_entry["position"]["exit_ctx"] = {
                    "swing_id": position.exit_ctx["swing_id"],
                    "fib_levels": position.exit_ctx["fib"],
                    "swing_bounds": position.exit_ctx["swing_bounds"],
                }

        self.bar_logs.append(log_entry)

    def log_fib_proximity(self, bar_idx: int, current_price: float, fib_levels: dict, atr: float):
        """Logga Fibonacci proximity analysis."""
        if not fib_levels:
            return

        proximity_analysis = {
            "bar_idx": bar_idx,
            "current_price": current_price,
            "atr": atr,
            "fib_proximity": {},
        }

        for level_name, level_price in fib_levels.items():
            distance_abs = abs(current_price - level_price)
            distance_atr = distance_abs / max(atr, 1e-9)
            distance_pct = distance_abs / max(current_price, 1e-9)

            proximity_analysis["fib_proximity"][level_name] = {
                "level_price": level_price,
                "distance_abs": distance_abs,
                "distance_atr": distance_atr,
                "distance_pct": distance_pct,
                "crossed_this_bar": False,  # Will be updated by exit engine
            }

        # Find nearest fib
        nearest_level = min(fib_levels.items(), key=lambda x: abs(current_price - x[1]))
        proximity_analysis["nearest_fib"] = {
            "level": nearest_level[0],
            "price": nearest_level[1],
            "distance_atr": abs(current_price - nearest_level[1]) / max(atr, 1e-9),
        }

        self.fib_proximity_logs.append(proximity_analysis)

    def log_exit_attempt(self, bar_idx: int, exit_action: str, reason: str, details: dict):
        """Logga exit försök."""
        log_entry = {
            "bar_idx": bar_idx,
            "timestamp": datetime.now().isoformat(),
            "exit_action": exit_action,
            "reason": reason,
            "details": details,
        }
        self.exit_logs.append(log_entry)

    def save_results(self, filename: str):
        """Spara alla loggar till fil."""
        results = {
            "test_type": "static_frozen_exits",
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "bar_logs": self.bar_logs,
            "fib_proximity_logs": self.fib_proximity_logs,
            "exit_logs": self.exit_logs,
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"[SAVE] Results saved to: {filename}")


def test_static_frozen_exits():
    """Test statisk frozen exit context med full telemetri."""

    print("=" * 80)
    print("STATIC FROZEN EXITS TEST")
    print("=" * 80)

    # Initialize telemetry
    telemetry = StaticExitTelemetry()

    # Initialize engine
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2025-04-16",
        end_date="2025-06-16",  # 2 months for detailed analysis
        initial_capital=10000.0,
        warmup_bars=120,
    )

    # Load data
    if not engine.load_data():
        print("[ERROR] Failed to load data")
        return

    print(f"[OK] Loaded {len(engine.candles_df):,} candles")

    # Track statistics
    stats = {
        "total_bars": 0,
        "positions_opened": 0,
        "positions_with_exit_ctx": 0,
        "partial_exits": 0,
        "full_exits": 0,
        "bars_with_position": 0,
        "fib_crosses": 0,
        "reachability_issues": 0,
    }

    # Process bars
    start_idx = engine.warmup_bars

    for i in range(start_idx, len(engine.candles_df)):
        bar = engine.candles_df.iloc[i]
        timestamp = bar["timestamp"]
        close_price = bar["close"]

        stats["total_bars"] += 1

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

            # Check for entry signal
            action = result.get("action", "NONE")
            size = meta.get("decision", {}).get("size", 0.0)

            if action != "NONE" and size > 0:
                print(f"\n[ENTRY] Bar {i}: {action} {size:.4f} @ ${close_price:.2f}")

                # Execute position opening
                exec_result = engine.position_tracker.execute_action(
                    action=action,
                    size=size,
                    price=close_price,
                    timestamp=timestamp,
                    symbol=engine.symbol,
                )

                if exec_result.get("executed"):
                    position = engine.position_tracker.position
                    stats["positions_opened"] += 1

                    # Initialize exit context
                    engine._initialize_position_exit_context(result, meta, close_price, timestamp)

                    if position.exit_ctx:
                        stats["positions_with_exit_ctx"] += 1
                        print(f"[EXIT_CTX] Armed: {position.exit_ctx['swing_id']}")
                        print(f"[EXIT_CTX] Fib levels: {list(position.exit_ctx['fib'].keys())}")

                        # Log initial fib proximity
                        atr = result.get("features", {}).get("atr", 100.0)
                        telemetry.log_fib_proximity(i, close_price, position.exit_ctx["fib"], atr)

            # Check current position
            if engine.position_tracker.position and engine.position_tracker.position.is_open:
                position = engine.position_tracker.position
                stats["bars_with_position"] += 1

                # Log bar with position
                telemetry.log_bar(i, bar.to_dict(), position)

                # Check for exits (simplified version)
                if position.exit_ctx:
                    fib_levels = position.exit_ctx["fib"]
                    atr = result.get("features", {}).get("atr", 100.0)

                    # Update fib proximity
                    telemetry.log_fib_proximity(i, close_price, fib_levels, atr)

                    # Check for fib crosses (simplified)
                    for level_name, level_price in fib_levels.items():
                        if bar["low"] <= level_price <= bar["high"]:
                            stats["fib_crosses"] += 1
                            telemetry.log_exit_attempt(
                                i,
                                "PARTIAL_POTENTIAL",
                                f"Fib_{level_name}_crossed",
                                {
                                    "level_price": level_price,
                                    "bar_high": bar["high"],
                                    "bar_low": bar["low"],
                                    "bar_close": bar["close"],
                                },
                            )

                            print(
                                f"[FIB_CROSS] Bar {i}: {level_name} @ {level_price:.2f} crossed by price {bar['low']:.2f}-{bar['high']:.2f}"
                            )

            # Show progress every 100 bars
            if i % 100 == 0:
                print(
                    f"[PROGRESS] Bar {i}/{len(engine.candles_df)} - Positions: {stats['positions_opened']}, Exits: {stats['partial_exits']}"
                )

        except Exception as e:
            print(f"[ERROR] Bar {i}: {e}")
            continue

    # Print final statistics
    print("\n" + "=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    print(f"Total bars processed: {stats['total_bars']:,}")
    print(f"Positions opened: {stats['positions_opened']}")
    print(f"Positions with exit context: {stats['positions_with_exit_ctx']}")
    print(f"Bars with open position: {stats['bars_with_position']}")
    print(f"Fibonacci crosses detected: {stats['fib_crosses']}")
    print(f"Partial exits executed: {stats['partial_exits']}")

    if stats["positions_opened"] > 0:
        exit_ctx_rate = stats["positions_with_exit_ctx"] / stats["positions_opened"] * 100
        print(f"Exit context success rate: {exit_ctx_rate:.1f}%")

    if stats["bars_with_position"] > 0:
        cross_rate = stats["fib_crosses"] / stats["bars_with_position"] * 100
        print(f"Fib cross rate per bar: {cross_rate:.2f}%")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/static_frozen_exits_{timestamp}.json"
    telemetry.save_results(filename)

    print("\n[COMPLETE] Static frozen exits test completed!")
    return stats


if __name__ == "__main__":
    test_static_frozen_exits()
