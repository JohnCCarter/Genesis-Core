#!/usr/bin/env python3
"""
OPTIMIZED Static Frozen Exits Test - Following Documentation Guidelines.
Uses Feather format + vectorized processing for 27,734× faster performance.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.indicators.vectorized import calculate_all_features_vectorized

# from core.utils.data_loader import load_features_data  # Not needed for this test


class OptimizedStaticExitTelemetry:
    """Optimized telemetri using vectorized operations."""

    def __init__(self):
        self.results = {
            "test_type": "static_frozen_exits_optimized",
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {},
            "position_analysis": {},
            "fib_analysis": {},
            "exit_analysis": {},
        }

    def analyze_fib_proximity_vectorized(
        self, df: pd.DataFrame, fib_levels: dict[float, float], atr: float
    ) -> pd.DataFrame:
        """Vectorized Fibonacci proximity analysis."""
        proximity_data = {}

        for level_name, level_price in fib_levels.items():
            # Vectorized distance calculations
            distance_abs = np.abs(df["close"] - level_price)
            distance_atr = distance_abs / atr
            distance_pct = distance_abs / df["close"]

            # Vectorized cross detection
            crossed = (df["low"] <= level_price) & (level_price <= df["high"])

            proximity_data[f"{level_name}_distance_atr"] = distance_atr
            proximity_data[f"{level_name}_distance_pct"] = distance_pct
            proximity_data[f"{level_name}_crossed"] = crossed
            proximity_data[f"{level_name}_proximity"] = distance_atr < 0.1  # Within 0.1 ATR

        return pd.DataFrame(proximity_data, index=df.index)

    def analyze_exit_performance_vectorized(self, df: pd.DataFrame, positions: list[dict]) -> dict:
        """Vectorized exit performance analysis."""
        exit_stats = {
            "total_positions": len(positions),
            "positions_with_exits": 0,
            "total_partial_exits": 0,
            "total_fib_crosses": 0,
            "exit_rate_by_level": {},
            "performance_by_duration": {},
        }

        for pos in positions:
            if pos.get("partial_exits", 0) > 0:
                exit_stats["positions_with_exits"] += 1
                exit_stats["total_partial_exits"] += pos["partial_exits"]

        return exit_stats

    def save_results(self, filename: str):
        """Save optimized results."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"[SAVE] Optimized results saved to: {filename}")


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


def test_static_frozen_exits_optimized():
    """OPTIMIZED static frozen exit test following documentation guidelines."""

    print("=" * 80)
    print("OPTIMIZED STATIC FROZEN EXITS TEST")
    print("Following Documentation: Feather + Vectorized")
    print("=" * 80)

    # Initialize telemetry
    telemetry = OptimizedStaticExitTelemetry()

    # Load data using Feather format (2× faster)
    start_time = datetime.now()
    df = load_candles_feather("tBTCUSD", "1h")
    load_time = (datetime.now() - start_time).total_seconds()
    print(f"[PERFORMANCE] Data loading: {load_time:.3f}s ({len(df):,} bars)")

    # Filter date range
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(f"[DEBUG] Date range in data: {df['timestamp'].min()} to {df['timestamp'].max()}")

    # Use actual date range from data
    start_date = df["timestamp"].min() + timedelta(days=5)  # Skip first few days
    end_date = df["timestamp"].max() - timedelta(days=5)  # Skip last few days

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

    # Initialize engine for position tracking
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2025-04-16",
        end_date="2025-06-16",
        initial_capital=10000.0,
        warmup_bars=120,
    )

    # Mock entry signals (vectorized approach)
    print("[SIGNALS] Generating entry signals vectorized...")
    entry_signals = generate_entry_signals_vectorized(df, features_df)
    print(f"[SIGNALS] Generated {len(entry_signals)} entry signals")

    # Process positions with frozen exit context
    positions = []
    for signal in entry_signals:
        position_data = process_position_with_frozen_exits(df, signal, engine)
        if position_data:
            positions.append(position_data)

    # Vectorized analysis
    print("[ANALYSIS] Running vectorized analysis...")
    analyze_positions_vectorized(df, positions, telemetry)

    # Performance summary
    print("\n" + "=" * 80)
    print("OPTIMIZED PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"Data loading: {load_time:.3f}s (Feather format)")
    print(f"Feature computation: {feature_time:.3f}s (Vectorized)")
    print(f"Total processing: {(load_time + feature_time):.3f}s")
    print(f"Positions analyzed: {len(positions)}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/static_frozen_exits_optimized_{timestamp}.json"
    telemetry.save_results(filename)

    print("\n[COMPLETE] Optimized static frozen exits test completed!")
    return telemetry.results


def generate_entry_signals_vectorized(df: pd.DataFrame, features_df: pd.DataFrame) -> list[dict]:
    """Generate entry signals using vectorized approach."""
    signals = []

    # Vectorized signal generation (simplified)
    # In real implementation, this would use ML model predictions
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


def process_position_with_frozen_exits(
    df: pd.DataFrame, signal: dict, engine: BacktestEngine
) -> dict:
    """Process position with frozen exit context."""
    bar_idx = signal["bar_idx"]

    # Mock position opening with frozen context
    position_data = {
        "entry_bar": bar_idx,
        "entry_time": signal["timestamp"],
        "entry_price": signal["price"],
        "side": signal["side"],
        "size": signal["size"],
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
        "partial_exits": 0,
        "exit_analysis": {},
    }

    # Analyze exit potential for this position
    position_df = df.iloc[bar_idx : bar_idx + 100]  # Next 100 bars
    if len(position_df) > 0:
        fib_analysis = analyze_fib_exits_vectorized(
            position_df, position_data["exit_ctx"]["fib_levels"]
        )
        position_data["exit_analysis"] = fib_analysis
        position_data["partial_exits"] = fib_analysis["total_crosses"]

    return position_data


def analyze_fib_exits_vectorized(df: pd.DataFrame, fib_levels: dict[float, float]) -> dict:
    """Vectorized Fibonacci exit analysis."""
    analysis = {
        "total_crosses": 0,
        "crosses_by_level": {},
        "first_cross_bar": None,
        "exit_potential": 0.0,
    }

    for level_name, level_price in fib_levels.items():
        # Vectorized cross detection
        crosses = (df["low"] <= level_price) & (level_price <= df["high"])
        cross_count = crosses.sum()

        analysis["crosses_by_level"][level_name] = {
            "price": level_price,
            "crosses": int(cross_count),
            "first_cross": int(crosses.idxmax()) if cross_count > 0 else None,
        }

        analysis["total_crosses"] += cross_count

        if cross_count > 0 and analysis["first_cross_bar"] is None:
            analysis["first_cross_bar"] = int(crosses.idxmax())

    # Calculate exit potential (percentage of bars with crosses)
    analysis["exit_potential"] = analysis["total_crosses"] / len(df) * 100

    return analysis


def analyze_positions_vectorized(
    df: pd.DataFrame, positions: list[dict], telemetry: OptimizedStaticExitTelemetry
):
    """Vectorized analysis of all positions."""
    if not positions:
        return

    # Aggregate statistics
    total_positions = len(positions)
    positions_with_exits = sum(1 for p in positions if p["partial_exits"] > 0)
    total_exits = sum(p["partial_exits"] for p in positions)

    # Exit rate analysis
    exit_rate = positions_with_exits / total_positions * 100 if total_positions > 0 else 0

    # Performance metrics
    telemetry.results["performance_metrics"] = {
        "total_positions": total_positions,
        "positions_with_exits": positions_with_exits,
        "exit_rate_percent": exit_rate,
        "total_partial_exits": total_exits,
        "avg_exits_per_position": total_exits / total_positions if total_positions > 0 else 0,
    }

    # Fib level analysis
    all_fib_analysis = [p["exit_analysis"] for p in positions if p["exit_analysis"]]
    if all_fib_analysis:
        telemetry.results["fib_analysis"] = {
            "avg_exit_potential": np.mean([a["exit_potential"] for a in all_fib_analysis]),
            "total_fib_crosses": sum(a["total_crosses"] for a in all_fib_analysis),
            "crosses_by_level": {},
        }

        # Aggregate crosses by level
        for level in [0.382, 0.5, 0.618, 0.786]:
            level_crosses = sum(
                a["crosses_by_level"].get(level, {}).get("crosses", 0) for a in all_fib_analysis
            )
            telemetry.results["fib_analysis"]["crosses_by_level"][level] = level_crosses


if __name__ == "__main__":
    test_static_frozen_exits_optimized()
