#!/usr/bin/env python3
"""
Run Backtest in Fast Mode (Deprecated: Streaming Mode Comparison Removed)

DEPRECATED: This script previously compared streaming vs fast mode.
Since streaming mode causes non-deterministic results, we now ONLY use fast mode.

For simple backtesting, use: python scripts/run_backtest.py

Usage (for legacy compatibility):
    python scripts/compare_modes.py --trial 1032
    python scripts/compare_modes.py --config config/strategy/champions/tBTCUSD_1h.json
"""

import argparse
import json
import os
import sys
import warnings
from pathlib import Path

warnings.warn(
    "compare_modes.py is deprecated. Streaming mode is no longer supported for backtesting. "
    "Use 'python scripts/run_backtest.py' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine  # noqa: E402


def load_trial_config(trial_path: Path) -> dict:
    """Load config from trial result."""
    with open(trial_path) as f:
        trial_data = json.load(f)
    return trial_data.get("merged_config", trial_data.get("config", {}))


def load_config_file(config_path: Path) -> dict:
    """Load config from JSON file."""
    with open(config_path) as f:
        return json.load(f)


def run_backtest(
    config: dict,
    fast_mode: bool = True,  # Always True now
    symbol: str = "tBTCUSD",
    timeframe: str = "1h",
    warmup_bars: int = 150,
    start_date: str = "2023-11-30",
    end_date: str = "2025-11-19",
) -> dict:
    """Run backtest in fast mode (streaming mode deprecated)."""

    # Always use fast mode
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
    os.environ["GENESIS_FAST_WINDOW"] = "1"

    # Setup engine (always fast mode)
    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        initial_capital=10000.0,
        start_date=start_date,
        end_date=end_date,
        warmup_bars=warmup_bars,
        fast_window=True,  # Always True
    )

    engine.load_data()

    # Run backtest
    results = engine.run(configs=config)

    # Extract trade details
    trades = results.get("trades", [])
    trade_bars = [t.get("entry_bar", t.get("entry_idx")) for t in trades]

    return {
        "summary": results.get("summary", {}),
        "trades": trades,
        "trade_bars": sorted(set(trade_bars)),
        "num_trades": len(trades),
    }


def compare_results(streaming_results: dict, fast_results: dict) -> dict:
    """Compare results between modes."""

    streaming_summary = streaming_results["summary"]
    fast_summary = fast_results["summary"]

    streaming_bars = set(streaming_results["trade_bars"])
    fast_bars = set(fast_results["trade_bars"])

    # Find differences
    only_streaming = streaming_bars - fast_bars
    only_fast = fast_bars - streaming_bars
    common = streaming_bars & fast_bars

    comparison = {
        "streaming": {
            "num_trades": streaming_results["num_trades"],
            "return": streaming_summary.get("total_return", 0.0),
            "profit_factor": streaming_summary.get("profit_factor", 0.0),
            "win_rate": streaming_summary.get("win_rate", 0.0),
        },
        "fast": {
            "num_trades": fast_results["num_trades"],
            "return": fast_summary.get("total_return", 0.0),
            "profit_factor": fast_summary.get("profit_factor", 0.0),
            "win_rate": fast_summary.get("win_rate", 0.0),
        },
        "differences": {
            "trade_count_diff": streaming_results["num_trades"] - fast_results["num_trades"],
            "return_diff": streaming_summary.get("total_return", 0.0)
            - fast_summary.get("total_return", 0.0),
            "common_bars": len(common),
            "only_streaming_bars": sorted(only_streaming),
            "only_fast_bars": sorted(only_fast),
            "num_only_streaming": len(only_streaming),
            "num_only_fast": len(only_fast),
        },
    }

    return comparison


def print_comparison(comparison: dict):
    """Print detailed comparison."""

    print("\n" + "=" * 80)
    print("BACKTEST MODE COMPARISON")
    print("=" * 80)

    # Summary
    print("\n📊 STREAMING MODE (Default):")
    print(f"  Trades:        {comparison['streaming']['num_trades']}")
    print(f"  Return:        {comparison['streaming']['return']:.2f}%")
    print(f"  Profit Factor: {comparison['streaming']['profit_factor']:.2f}")
    print(f"  Win Rate:      {comparison['streaming']['win_rate']:.2f}%")

    print("\n⚡ FAST MODE (Optimizer):")
    print(f"  Trades:        {comparison['fast']['num_trades']}")
    print(f"  Return:        {comparison['fast']['return']:.2f}%")
    print(f"  Profit Factor: {comparison['fast']['profit_factor']:.2f}")
    print(f"  Win Rate:      {comparison['fast']['win_rate']:.2f}%")

    # Differences
    print("\n🔍 DIFFERENCES:")
    diff = comparison["differences"]
    print(f"  Trade Count Δ:  {diff['trade_count_diff']:+d} (Streaming - Fast)")
    print(f"  Return Δ:       {diff['return_diff']:+.2f}%")
    print(f"  Common Bars:    {diff['common_bars']}")
    print(f"  Only Streaming: {diff['num_only_streaming']} bars")
    print(f"  Only Fast:      {diff['num_only_fast']} bars")

    # Divergent bars
    if diff["num_only_streaming"] > 0:
        print("\n⚠️  Bars with trades ONLY in Streaming mode:")
        bars = diff["only_streaming_bars"]
        if len(bars) <= 20:
            print(f"    {bars}")
        else:
            print(f"    First 10: {bars[:10]}")
            print(f"    Last 10:  {bars[-10:]}")
            print(f"    (Total: {len(bars)} bars)")

    if diff["num_only_fast"] > 0:
        print("\n⚠️  Bars with trades ONLY in Fast mode:")
        bars = diff["only_fast_bars"]
        if len(bars) <= 20:
            print(f"    {bars}")
        else:
            print(f"    First 10: {bars[:10]}")
            print(f"    Last 10:  {bars[-10:]}")
            print(f"    (Total: {len(bars)} bars)")

    # Assessment
    print("\n" + "=" * 80)
    if diff["trade_count_diff"] == 0 and abs(diff["return_diff"]) < 0.01:
        print("✅ PARITY ACHIEVED - Modes produce identical results!")
    else:
        print("❌ DISCREPANCY DETECTED - Modes diverge significantly!")
        print("\nRecommended next steps:")
        print("  1. Run with --verbose to see detailed trade logs")
        print("  2. Inspect feature values at divergent bars")
        print("  3. Check if warmup/lookback differs between modes")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run backtest in fast mode (deprecated script)")
    parser.add_argument("--trial", type=int, help="Trial number to load from run_20251125_161913")
    parser.add_argument("--config", type=str, help="Path to config JSON file")
    parser.add_argument("--symbol", type=str, default="tBTCUSD", help="Symbol to backtest")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    parser.add_argument("--warmup", type=int, default=150, help="Warmup bars")
    parser.add_argument("--start", type=str, default="2023-11-30", help="Start date")
    parser.add_argument("--end", type=str, default="2025-11-19", help="End date")
    parser.add_argument("--verbose", action="store_true", help="Show detailed trade logs (ignored)")

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("⚠️  DEPRECATED: Use 'python scripts/run_backtest.py' instead")
    print("    This script now only runs fast mode (streaming removed)")
    print("=" * 80 + "\n")

    # Load config
    if args.trial:
        trial_path = Path(f"results/hparam_search/run_20251125_161913/trial_{args.trial:04d}.json")
        if not trial_path.exists():
            print(f"❌ Trial file not found: {trial_path}")
            sys.exit(1)
        config = load_trial_config(trial_path)
        print(f"Loaded config from Trial {args.trial}")
    elif args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}")
            sys.exit(1)
        config = load_config_file(config_path)
        print(f"Loaded config from {config_path}")
    else:
        print("❌ Must specify either --trial or --config")
        sys.exit(1)

    # Run backtest (fast mode only)
    print("\n🚀 Running backtest in FAST MODE...")
    results = run_backtest(
        config=config,
        symbol=args.symbol,
        timeframe=args.timeframe,
        warmup_bars=args.warmup,
        start_date=args.start,
        end_date=args.end,
    )

    # Print results
    summary = results["summary"]
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS (Fast Mode)")
    print("=" * 80)
    print(f"  Trades:        {results['num_trades']}")
    print(f"  Return:        {summary.get('total_return', 0.0):.2f}%")
    print(f"  Profit Factor: {summary.get('profit_factor', 0.0):.2f}")
    print(f"  Win Rate:      {summary.get('win_rate', 0.0):.2f}%")
    print(f"  Max DD:        {summary.get('max_drawdown', 0.0):.2f}%")
    print("=" * 80)

    print("\n💡 For full backtest features, use: python scripts/run_backtest.py")


if __name__ == "__main__":
    main()
