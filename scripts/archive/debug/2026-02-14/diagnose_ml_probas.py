#!/usr/bin/env python3
"""
Diagnose ML probability distribution to understand EV=0 issue.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

from core.backtest.engine import BacktestEngine


def diagnose_probas(symbol: str, timeframe: str, start_date: str, end_date: str):
    """Extract proba_long and proba_short for diagnosis."""

    probas_data = []

    def proba_hook(result, meta, candles):
        """Hook to capture probas."""
        probas = result.get("probas", {})
        if probas:
            p_long = probas.get("LONG", 0.0)
            p_short = probas.get("SHORT", 0.0)
            probas_data.append({"long": p_long, "short": p_short})

        return result, meta

    # Create engine with hook
    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        fast_window=True,
        evaluation_hook=proba_hook,
    )

    # Load data
    if not engine.load_data():
        print("ERROR: Failed to load data")
        return []

    # Run backtest
    engine.run(verbose=False)

    return probas_data


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose ML probabilities")
    parser.add_argument("--symbol", default="tBTCUSD")
    parser.add_argument("--timeframe", default="1h")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)

    args = parser.parse_args()

    print(f"Diagnosing ML probabilities: {args.symbol} {args.timeframe}")
    print(f"Period: {args.start} to {args.end}")

    probas_data = diagnose_probas(
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start,
        end_date=args.end,
    )

    if not probas_data:
        print("ERROR: No probas extracted")
        return 1

    # Analyze
    import numpy as np

    p_long = np.array([p["long"] for p in probas_data])
    p_short = np.array([p["short"] for p in probas_data])
    p_diff = p_long - p_short

    print(f"\n{'='*70}")
    print("ML PROBABILITY DISTRIBUTION (Q1 2024)")
    print(f"{'='*70}")
    print(f"Samples: {len(probas_data)}")
    print()
    print("proba_long:")
    print(f"  Mean: {np.mean(p_long):.6f}")
    print(f"  Std: {np.std(p_long):.6f}")
    print(f"  Min: {np.min(p_long):.6f}")
    print(f"  Max: {np.max(p_long):.6f}")
    print()
    print("proba_short:")
    print(f"  Mean: {np.mean(p_short):.6f}")
    print(f"  Std: {np.std(p_short):.6f}")
    print(f"  Min: {np.min(p_short):.6f}")
    print(f"  Max: {np.max(p_short):.6f}")
    print()
    print("proba_long - proba_short:")
    print(f"  Mean: {np.mean(p_diff):.6f}")
    print(f"  Std: {np.std(p_diff):.6f}")
    print(f"  Min: {np.min(p_diff):.6f}")
    print(f"  Max: {np.max(p_diff):.6f}")
    print()

    # Check if all equal (50/50 model)
    all_equal = np.allclose(p_long, p_short, atol=1e-6)
    if all_equal:
        print("WARNING: proba_long == proba_short for ALL bars")
        print("  -> ML model is outputting 50/50 probabilities (no signal)")
        print("  -> This explains EV=0 for all bars")
        print("  -> EVGate cannot function with degenerate probabilities")
    else:
        print("OK: proba_long != proba_short (model is producing signals)")
        print(f"  -> Non-zero diffs: {np.sum(np.abs(p_diff) > 1e-6)}/{len(p_diff)}")

    # Sample first 10
    print("\nFirst 10 samples:")
    for i in range(min(10, len(probas_data))):
        p = probas_data[i]
        diff = p["long"] - p["short"]
        print(f"  [{i}] long={p['long']:.6f}, short={p['short']:.6f}, diff={diff:.6f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
