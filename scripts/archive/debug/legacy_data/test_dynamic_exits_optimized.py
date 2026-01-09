#!/usr/bin/env python3
"""
OPTIMIZED Dynamic Exits Test - Following Documentation Guidelines.
Uses Feather format + vectorized processing with live swing updates.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.exit_strategies import SwingUpdateStrategy
from core.indicators.vectorized import calculate_all_features_vectorized


class OptimizedDynamicExitTelemetry:
    """Optimized telemetri for dynamic exit testing."""

    def __init__(self):
        self.results = {
            "test_type": "dynamic_exits_optimized",
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {},
            "swing_update_analysis": {},
            "exit_comparison": {},
            "dynamic_vs_static": {},
        }

    def analyze_swing_updates_vectorized(self, positions: list[dict]) -> dict:
        """Vectorized analysis of swing updates."""
        update_stats = {
            "total_positions": len(positions),
            "positions_with_updates": 0,
            "total_updates": 0,
            "avg_updates_per_position": 0.0,
            "update_frequency": {},
            "improvement_analysis": {},
        }

        for pos in positions:
            updates = pos.get("swing_updates", 0)
            if updates > 0:
                update_stats["positions_with_updates"] += 1
                update_stats["total_updates"] += updates

        if update_stats["total_positions"] > 0:
            update_stats["avg_updates_per_position"] = (
                update_stats["total_updates"] / update_stats["total_positions"]
            )

        return update_stats

    def compare_dynamic_vs_static(
        self, dynamic_positions: list[dict], static_positions: list[dict]
    ) -> dict:
        """Compare dynamic vs static exit performance."""
        comparison = {
            "dynamic_stats": self._analyze_positions(dynamic_positions),
            "static_stats": self._analyze_positions(static_positions),
            "improvement": {},
        }

        # Calculate improvements
        if comparison["static_stats"]["total_exits"] > 0:
            exit_improvement = (
                (
                    comparison["dynamic_stats"]["total_exits"]
                    - comparison["static_stats"]["total_exits"]
                )
                / comparison["static_stats"]["total_exits"]
                * 100
            )
            comparison["improvement"]["exit_rate"] = exit_improvement

        return comparison

    def _analyze_positions(self, positions: list[dict]) -> dict:
        """Analyze position performance."""
        if not positions:
            return {"total_exits": 0, "exit_rate": 0.0}

        total_exits = sum(p.get("partial_exits", 0) for p in positions)
        exit_rate = total_exits / len(positions) * 100

        return {
            "total_positions": len(positions),
            "total_exits": total_exits,
            "exit_rate": exit_rate,
        }

    def save_results(self, filename: str):
        """Save optimized results."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"[SAVE] Dynamic results saved to: {filename}")


def load_candles_feather(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load candles using Feather format (2× faster than Parquet)."""
    feather_path = Path(f"data/candles/{symbol}_{timeframe}.feather")
    parquet_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")

    # Try Feather first (2× faster)
    if feather_path.exists():
        print(f"[LOAD] Using Feather format: {feather_path}")
        return pd.read_feather(feather_path)

    # Fallback to Parquet and convert to Feather
    elif parquet_path.exists():
        print(f"[LOAD] Converting Parquet to Feather: {parquet_path}")
        df = pd.read_parquet(parquet_path)
        df.to_feather(feather_path)
        print(f"[CONVERT] Saved Feather version: {feather_path}")
        return df

    else:
        raise FileNotFoundError(f"No data found for {symbol}_{timeframe}")


def test_dynamic_exits_optimized():
    """OPTIMIZED dynamic exit test with live swing updates."""

    print("=" * 80)
    print("OPTIMIZED DYNAMIC EXITS TEST")
    print("Following Documentation: Feather + Vectorized + Live Updates")
    print("=" * 80)

    # Initialize telemetry
    telemetry = OptimizedDynamicExitTelemetry()

    # Load data using Feather format (2× faster)
    start_time = datetime.now()
    df = load_candles_feather("tBTCUSD", "1h")
    load_time = (datetime.now() - start_time).total_seconds()
    print(f"[PERFORMANCE] Data loading: {load_time:.3f}s ({len(df):,} bars)")

    # Filter date range
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"[DEBUG] Date range in data: {df['timestamp'].min()} to {df['timestamp'].max()}")

    # Use actual date range from data
    start_date = df["timestamp"].min() + timedelta(days=5)
    end_date = df["timestamp"].max() - timedelta(days=5)

    df = df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]
    print(f"[FILTER] Date range: {len(df):,} bars ({start_date} to {end_date})")

    # Vectorized feature computation (27,734× faster than per-sample)
    print("[FEATURES] Computing features vectorized...")
    start_time = datetime.now()
    features_df = calculate_all_features_vectorized(df)
    feature_time = (datetime.now() - start_time).total_seconds()
    print(f"[PERFORMANCE] Feature computation: {feature_time:.3f}s")

    # Combine candles and features
    df = pd.concat([df, features_df], axis=1)

    # Generate entry signals (vectorized)
    print("[SIGNALS] Generating entry signals vectorized...")
    entry_signals = generate_entry_signals_vectorized(df, features_df)
    print(f"[SIGNALS] Generated {len(entry_signals)} entry signals")

    # Process positions with dynamic exit context (live swing updates)
    print("[DYNAMIC] Processing positions with live swing updates...")
    dynamic_positions = []
    for signal in entry_signals:
        position_data = process_position_with_dynamic_exits(df, signal, SwingUpdateStrategy.DYNAMIC)
        if position_data:
            dynamic_positions.append(position_data)

    # Process positions with hybrid exit context (improvement-based updates)
    print("[HYBRID] Processing positions with hybrid swing updates...")
    hybrid_positions = []
    for signal in entry_signals:
        position_data = process_position_with_dynamic_exits(df, signal, SwingUpdateStrategy.HYBRID)
        if position_data:
            hybrid_positions.append(position_data)

    # Vectorized analysis
    print("[ANALYSIS] Running vectorized analysis...")
    analyze_dynamic_positions_vectorized(df, dynamic_positions, hybrid_positions, telemetry)

    # Performance summary
    print("\n" + "=" * 80)
    print("OPTIMIZED DYNAMIC PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"Data loading: {load_time:.3f}s (Feather format)")
    print(f"Feature computation: {feature_time:.3f}s (Vectorized)")
    print(f"Total processing: {(load_time + feature_time):.3f}s")
    print(f"Dynamic positions: {len(dynamic_positions)}")
    print(f"Hybrid positions: {len(hybrid_positions)}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/dynamic_exits_optimized_{timestamp}.json"
    telemetry.save_results(filename)

    print("\n[COMPLETE] Optimized dynamic exits test completed!")
    return telemetry.results


def generate_entry_signals_vectorized(df: pd.DataFrame, features_df: pd.DataFrame) -> list[dict]:
    """Generate entry signals using vectorized approach."""
    signals = []

    # Vectorized signal generation (simplified)
    for i in range(120, len(df)):  # Skip warmup
        if i % 50 == 0:  # Every 50 bars for testing
            signals.append(
                {
                    "bar_idx": i,
                    "timestamp": df.iloc[i]["timestamp"],
                    "price": df.iloc[i]["close"],
                    "side": "LONG",
                    "size": 0.1,
                }
            )

    return signals


def process_position_with_dynamic_exits(
    df: pd.DataFrame, signal: dict, strategy: SwingUpdateStrategy
) -> dict:
    """Process position with dynamic exit context (live swing updates)."""
    bar_idx = signal["bar_idx"]

    # Mock position opening with dynamic context
    position_data = {
        "entry_bar": bar_idx,
        "entry_time": signal["timestamp"],
        "entry_price": signal["price"],
        "side": signal["side"],
        "size": signal["size"],
        "strategy": strategy.value,
        "exit_ctx": {
            "swing_id": f"swing_{signal['timestamp']}_{signal['price']}",
            "fib_levels": {
                0.382: signal["price"] * 1.02,
                0.5: signal["price"] * 1.05,
                0.618: signal["price"] * 1.08,
                0.786: signal["price"] * 1.12,
            },
            "swing_bounds": (signal["price"] * 0.95, signal["price"] * 1.15),
        },
        "swing_updates": 0,
        "partial_exits": 0,
        "exit_analysis": {},
        "swing_update_log": [],
    }

    # Analyze dynamic exit potential with swing updates
    position_df = df.iloc[bar_idx : bar_idx + 100]  # Next 100 bars
    if len(position_df) > 0:
        dynamic_analysis = analyze_dynamic_exits_vectorized(
            position_df, position_data["exit_ctx"]["fib_levels"], strategy
        )
        position_data["exit_analysis"] = dynamic_analysis
        position_data["partial_exits"] = dynamic_analysis["total_crosses"]
        position_data["swing_updates"] = dynamic_analysis["swing_updates"]
        position_data["swing_update_log"] = dynamic_analysis["update_log"]

    return position_data


def analyze_dynamic_exits_vectorized(
    df: pd.DataFrame, initial_fib_levels: dict[float, float], strategy: SwingUpdateStrategy
) -> dict:
    """Vectorized dynamic exit analysis with swing updates."""
    analysis = {
        "total_crosses": 0,
        "swing_updates": 0,
        "update_log": [],
        "crosses_by_level": {},
        "improvement_tracking": {},
    }

    # Simulate dynamic swing updates
    current_fib_levels = initial_fib_levels.copy()
    update_frequency = (
        20 if strategy == SwingUpdateStrategy.DYNAMIC else 40
    )  # Update every 20 or 40 bars

    for i in range(0, len(df), update_frequency):
        if i + update_frequency < len(df):
            # Simulate swing update
            price_change = (df.iloc[i + update_frequency]["close"] - df.iloc[i]["close"]) / df.iloc[
                i
            ]["close"]

            if strategy == SwingUpdateStrategy.DYNAMIC or (
                strategy == SwingUpdateStrategy.HYBRID and abs(price_change) > 0.02
            ):
                # Update swing levels
                new_swing_id = f"swing_update_{i}_{df.iloc[i]['timestamp']}"
                analysis["swing_updates"] += 1

                # Adjust fib levels based on price movement
                adjustment_factor = 1 + price_change * 0.5  # Moderate adjustment
                updated_levels = {}
                for level_name, level_price in current_fib_levels.items():
                    updated_levels[level_name] = level_price * adjustment_factor

                current_fib_levels = updated_levels

                analysis["update_log"].append(
                    {
                        "bar": i,
                        "timestamp": df.iloc[i]["timestamp"],
                        "price_change": price_change,
                        "new_levels": updated_levels,
                        "swing_id": new_swing_id,
                    }
                )

    # Analyze crosses with updated levels
    for level_name, level_price in current_fib_levels.items():
        # Vectorized cross detection
        crosses = (df["low"] <= level_price) & (level_price <= df["high"])
        cross_count = crosses.sum()

        analysis["crosses_by_level"][level_name] = {
            "final_price": level_price,
            "initial_price": initial_fib_levels[level_name],
            "crosses": int(cross_count),
            "price_change": level_price - initial_fib_levels[level_name],
        }

        analysis["total_crosses"] += cross_count

    return analysis


def analyze_dynamic_positions_vectorized(
    df: pd.DataFrame,
    dynamic_positions: list[dict],
    hybrid_positions: list[dict],
    telemetry: OptimizedDynamicExitTelemetry,
):
    """Vectorized analysis of dynamic positions."""

    # Analyze swing updates
    dynamic_update_stats = telemetry.analyze_swing_updates_vectorized(dynamic_positions)
    hybrid_update_stats = telemetry.analyze_swing_updates_vectorized(hybrid_positions)

    telemetry.results["swing_update_analysis"] = {
        "dynamic": dynamic_update_stats,
        "hybrid": hybrid_update_stats,
    }

    # Compare strategies
    comparison = telemetry.compare_dynamic_vs_static(dynamic_positions, hybrid_positions)
    telemetry.results["exit_comparison"] = comparison

    # Performance metrics
    telemetry.results["performance_metrics"] = {
        "dynamic_positions": len(dynamic_positions),
        "hybrid_positions": len(hybrid_positions),
        "dynamic_exit_rate": dynamic_update_stats["avg_updates_per_position"],
        "hybrid_exit_rate": hybrid_update_stats["avg_updates_per_position"],
    }


if __name__ == "__main__":
    test_dynamic_exits_optimized()
