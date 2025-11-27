#!/usr/bin/env python3
"""
Debug Swing Detection Differences Between Modes

Jämför swing point detektion mellan streaming och fast mode för att identifiera:
1. Vilka swings som detekteras i varje mode
2. Invalid swings (high < low)
3. Varför streaming mode genererar fler trades

Usage:
    python scripts/debug_swing_detection.py --trial 1032 --start-bar 1000 --num-bars 100
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.strategy.features_asof import _extract_asof


def load_trial_config(trial_path: Path) -> dict:
    """Load config from trial result."""
    with open(trial_path) as f:
        trial_data = json.load(f)
    return trial_data.get("merged_config", trial_data.get("config", {}))


def get_candle_data(
    symbol: str = "tBTCUSD",
    timeframe: str = "1h",
    start_date: str = "2023-11-30",
    end_date: str = "2025-11-19",
) -> dict:
    """Load candle data."""
    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        initial_capital=10000.0,
        start_date=start_date,
        end_date=end_date,
        warmup_bars=150,
        fast_window=False,
    )
    engine.load_data()

    # Convert DataFrame to dict format expected by features_asof
    return {
        "open": engine.candles_df["open"].values,
        "high": engine.candles_df["high"].values,
        "low": engine.candles_df["low"].values,
        "close": engine.candles_df["close"].values,
        "volume": engine.candles_df["volume"].values,
        "timestamp": engine.candles_df["timestamp"].values,
    }


def detect_swings_for_bar(
    candles: dict,
    bar_idx: int,
    config: dict,
    fast_mode: bool = False,
) -> dict:
    """Detect swings at a specific bar using features_asof."""

    # Extract features which includes swing detection
    features, meta = _extract_asof(
        candles=candles,
        asof_bar=bar_idx,
        timeframe="1h",
        symbol="tBTCUSD",
        config=config,
    )

    # Get HTF fibonacci context if available
    htf_fib = meta.get("htf_fibonacci", {})
    ltf_fib = meta.get("ltf_fibonacci", {})

    return {
        "bar_idx": bar_idx,
        "close": candles["close"][bar_idx],
        "htf_fib": htf_fib,
        "ltf_fib": ltf_fib,
        "htf_valid": htf_fib.get("is_valid", False),
        "ltf_valid": ltf_fib.get("is_valid", False),
        "htf_high": htf_fib.get("swing_high"),
        "htf_low": htf_fib.get("swing_low"),
        "ltf_high": ltf_fib.get("swing_high"),
        "ltf_low": ltf_fib.get("swing_low"),
    }


def compare_swing_detection(
    config: dict,
    start_bar: int = 1000,
    num_bars: int = 100,
    symbol: str = "tBTCUSD",
    timeframe: str = "1h",
) -> dict:
    """Compare swing detection between streaming and fast mode."""

    print(f"\n🔍 Comparing swing detection from bar {start_bar} to {start_bar + num_bars}")
    print("=" * 80)

    # Load candle data
    candles = get_candle_data(symbol, timeframe)

    # Store results
    results = {
        "streaming": [],
        "fast": [],
        "invalid_swings": [],
        "differences": [],
    }

    # Compare bar by bar
    for bar_idx in range(start_bar, start_bar + num_bars):
        if bar_idx >= len(candles["close"]):
            break

        # Streaming mode
        streaming_result = detect_swings_for_bar(candles, bar_idx, config, fast_mode=False)
        results["streaming"].append(streaming_result)

        # Fast mode
        fast_result = detect_swings_for_bar(candles, bar_idx, config, fast_mode=True)
        results["fast"].append(fast_result)

        # Check for invalid swings (high < low)
        for mode, result in [("streaming", streaming_result), ("fast", fast_result)]:
            # HTF
            if result["htf_valid"]:
                htf_high = result["htf_high"]
                htf_low = result["htf_low"]
                if htf_high is not None and htf_low is not None and htf_high < htf_low:
                    results["invalid_swings"].append(
                        {
                            "mode": mode,
                            "bar": bar_idx,
                            "type": "HTF",
                            "high": htf_high,
                            "low": htf_low,
                        }
                    )

            # LTF
            if result["ltf_valid"]:
                ltf_high = result["ltf_high"]
                ltf_low = result["ltf_low"]
                if ltf_high is not None and ltf_low is not None and ltf_high < ltf_low:
                    results["invalid_swings"].append(
                        {
                            "mode": mode,
                            "bar": bar_idx,
                            "type": "LTF",
                            "high": ltf_high,
                            "low": ltf_low,
                        }
                    )

        # Check for differences
        htf_diff = (
            streaming_result["htf_valid"] != fast_result["htf_valid"]
            or streaming_result["htf_high"] != fast_result["htf_high"]
            or streaming_result["htf_low"] != fast_result["htf_low"]
        )

        ltf_diff = (
            streaming_result["ltf_valid"] != fast_result["ltf_valid"]
            or streaming_result["ltf_high"] != fast_result["ltf_high"]
            or streaming_result["ltf_low"] != fast_result["ltf_low"]
        )

        if htf_diff or ltf_diff:
            results["differences"].append(
                {
                    "bar": bar_idx,
                    "htf_diff": htf_diff,
                    "ltf_diff": ltf_diff,
                    "streaming": streaming_result,
                    "fast": fast_result,
                }
            )

    return results


def print_results(results: dict):
    """Print analysis results."""

    print("\n" + "=" * 80)
    print("SWING DETECTION ANALYSIS")
    print("=" * 80)

    # Invalid swings
    if results["invalid_swings"]:
        print(f"\n🚨 INVALID SWINGS DETECTED: {len(results['invalid_swings'])}")
        print("-" * 80)
        for inv in results["invalid_swings"][:10]:  # Show first 10
            print(f"  Bar {inv['bar']} ({inv['mode']} mode, {inv['type']}):")
            print(f"    High: {inv['high']:.2f}")
            print(f"    Low:  {inv['low']:.2f}")
            print(f"    ⚠️  High < Low by {inv['low'] - inv['high']:.2f}")
        if len(results["invalid_swings"]) > 10:
            print(f"  ... and {len(results['invalid_swings']) - 10} more")
    else:
        print("\n✅ No invalid swings detected")

    # Differences
    if results["differences"]:
        print(f"\n📊 DIFFERENCES FOUND: {len(results['differences'])} bars")
        print("-" * 80)

        htf_diffs = sum(1 for d in results["differences"] if d["htf_diff"])
        ltf_diffs = sum(1 for d in results["differences"] if d["ltf_diff"])

        print(f"  HTF differences: {htf_diffs}")
        print(f"  LTF differences: {ltf_diffs}")

        print("\n  First 5 differences:")
        for diff in results["differences"][:5]:
            bar = diff["bar"]
            print(f"\n  Bar {bar}:")

            if diff["htf_diff"]:
                s = diff["streaming"]
                f = diff["fast"]
                print(
                    f"    HTF Streaming: valid={s['htf_valid']}, high={s['htf_high']}, low={s['htf_low']}"
                )
                print(
                    f"    HTF Fast:      valid={f['htf_valid']}, high={f['htf_high']}, low={f['htf_low']}"
                )

            if diff["ltf_diff"]:
                s = diff["streaming"]
                f = diff["fast"]
                print(
                    f"    LTF Streaming: valid={s['ltf_valid']}, high={s['ltf_high']}, low={s['ltf_low']}"
                )
                print(
                    f"    LTF Fast:      valid={f['ltf_valid']}, high={f['ltf_high']}, low={f['ltf_low']}"
                )
    else:
        print("\n✅ No differences detected - modes produce identical swings")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Bars analyzed:     {len(results['streaming'])}")
    print(f"  Invalid swings:    {len(results['invalid_swings'])}")
    print(f"  Bars with diffs:   {len(results['differences'])}")

    if results["invalid_swings"]:
        print("\n⚠️  ACTION REQUIRED: Fix invalid swing detection (high < low)")

    if results["differences"]:
        print("\n⚠️  ACTION REQUIRED: Investigate why modes produce different swings")

    if not results["invalid_swings"] and not results["differences"]:
        print("\n✅ All checks passed - swing detection is consistent")

    print("=" * 80 + "\n")


def save_results(results: dict, output_path: Path):
    """Save detailed results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to serializable format
    serializable = {
        "invalid_swings": results["invalid_swings"],
        "differences": [
            {
                "bar": d["bar"],
                "htf_diff": d["htf_diff"],
                "ltf_diff": d["ltf_diff"],
                "streaming": {
                    "htf_valid": d["streaming"]["htf_valid"],
                    "htf_high": d["streaming"]["htf_high"],
                    "htf_low": d["streaming"]["htf_low"],
                    "ltf_valid": d["streaming"]["ltf_valid"],
                    "ltf_high": d["streaming"]["ltf_high"],
                    "ltf_low": d["streaming"]["ltf_low"],
                },
                "fast": {
                    "htf_valid": d["fast"]["htf_valid"],
                    "htf_high": d["fast"]["htf_high"],
                    "htf_low": d["fast"]["htf_low"],
                    "ltf_valid": d["fast"]["ltf_valid"],
                    "ltf_high": d["fast"]["ltf_high"],
                    "ltf_low": d["fast"]["ltf_low"],
                },
            }
            for d in results["differences"]
        ],
        "num_bars": len(results["streaming"]),
    }

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    print(f"💾 Detailed results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Debug swing detection differences")
    parser.add_argument("--trial", type=int, help="Trial number", default=1032)
    parser.add_argument("--start-bar", type=int, help="Start bar index", default=1000)
    parser.add_argument("--num-bars", type=int, help="Number of bars to analyze", default=100)
    parser.add_argument(
        "--output", type=str, help="Output JSON path", default="results/swing_debug.json"
    )

    args = parser.parse_args()

    # Load config
    trial_path = Path(f"results/hparam_search/run_20251125_161913/trial_{args.trial:04d}.json")
    if not trial_path.exists():
        print(f"❌ Trial file not found: {trial_path}")
        sys.exit(1)

    config = load_trial_config(trial_path)
    print(f"Loaded config from Trial {args.trial}")

    # Run analysis
    results = compare_swing_detection(
        config=config,
        start_bar=args.start_bar,
        num_bars=args.num_bars,
    )

    # Print results
    print_results(results)

    # Save results
    save_results(results, Path(args.output))


if __name__ == "__main__":
    main()
