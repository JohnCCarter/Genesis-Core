#!/usr/bin/env python3
"""
Extract EV distribution from backtest period.

Computes expected_value for each bar using the same formula as
ComponentContextBuilder to match what EVGate sees.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

from core.backtest.engine import BacktestEngine


def extract_ev_values(symbol: str, timeframe: str, start_date: str, end_date: str):
    """Extract EV values for each decision point."""

    ev_values = []

    def ev_hook(result, meta, candles):
        """Hook to capture EV values."""
        # Extract probas
        probas = result.get("probas", {})
        if probas:
            p_long = probas.get("LONG", 0.0)
            p_short = probas.get("SHORT", 0.0)

            # Same formula as ComponentContextBuilder
            R = 1.0
            ev_long = p_long * R - p_short
            ev_short = p_short * R - p_long
            expected_value = max(ev_long, ev_short)

            ev_values.append(expected_value)

        return result, meta

    # Create engine with hook
    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        fast_window=True,
        evaluation_hook=ev_hook,
    )

    # Load data
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return []

    # Run backtest (captures EV via hook)
    engine.run(verbose=False)

    return ev_values


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract EV distribution")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="1h", help="Candle timeframe")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    print(f"Extracting EV values: {args.symbol} {args.timeframe}")
    print(f"Period: {args.start} to {args.end}")

    ev_values = extract_ev_values(
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start,
        end_date=args.end,
    )

    if not ev_values:
        print("ERROR: No EV values extracted")
        return 1

    # Compute statistics
    import numpy as np

    ev_arr = np.array(ev_values)

    print(f"\n{'='*70}")
    print("EV DISTRIBUTION STATISTICS (Q1 2024)")
    print(f"{'='*70}")
    print(f"Samples: {len(ev_arr)}")
    print(f"Mean: {np.mean(ev_arr):.6f}")
    print(f"Std Dev: {np.std(ev_arr):.6f}")
    print(f"Min: {np.min(ev_arr):.6f}")
    print(f"Max: {np.max(ev_arr):.6f}")
    print()
    print("Percentiles:")
    print(f"  p10: {np.percentile(ev_arr, 10):.6f}")
    print(f"  p25: {np.percentile(ev_arr, 25):.6f}")
    print(f"  p50 (median): {np.percentile(ev_arr, 50):.6f}")
    print(f"  p75: {np.percentile(ev_arr, 75):.6f}")
    print(f"  p80: {np.percentile(ev_arr, 80):.6f}")
    print(f"  p85: {np.percentile(ev_arr, 85):.6f}")
    print(f"  p90: {np.percentile(ev_arr, 90):.6f}")
    print(f"  p95: {np.percentile(ev_arr, 95):.6f}")
    print()
    print("Recommended min_ev for target veto rates:")
    print(f"  10% veto rate: min_ev = {np.percentile(ev_arr, 90):.4f} (p90)")
    print(f"  15% veto rate: min_ev = {np.percentile(ev_arr, 85):.4f} (p85)")
    print(f"  20% veto rate: min_ev = {np.percentile(ev_arr, 80):.4f} (p80)")
    print(f"  25% veto rate: min_ev = {np.percentile(ev_arr, 75):.4f} (p75)")
    print()

    # Check if all values < 0.1 (explains v4 result)
    below_01 = np.sum(ev_arr < 0.1)
    pct_below_01 = 100.0 * below_01 / len(ev_arr)
    print(f"Values < 0.1: {below_01}/{len(ev_arr)} ({pct_below_01:.1f}%)")
    print("  -> Explains v4 100% veto at min_ev=0.1")

    return 0


if __name__ == "__main__":
    sys.exit(main())
