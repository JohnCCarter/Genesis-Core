#!/usr/bin/env python3
"""
Benchmark script to measure performance improvements in the model-training pipeline.

This script runs backtests with different optimization flags to measure speedup.
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import os

from core.backtest.engine import BacktestEngine


def benchmark_backtest(
    symbol: str,
    timeframe: str,
    num_bars: int = 1000,
    fast_window: bool = False,
    precompute: bool = False,
) -> dict:
    """Run a backtest and measure performance."""
    print(f"\n{'='*70}")
    print(f"Benchmarking: fast_window={fast_window}, precompute={precompute}")
    print(f"{'='*70}")

    # Create engine
    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        warmup_bars=100,
        fast_window=fast_window,
    )

    if precompute:
        engine.precompute_features = True

    # Load data
    start = time.perf_counter()
    if not engine.load_data():
        print("[ERROR] Failed to load data")
        return {}
    load_time = time.perf_counter() - start

    # Limit to num_bars for consistent benchmark
    if len(engine.candles_df) > num_bars:
        engine.candles_df = engine.candles_df.iloc[:num_bars]
        print(f"[BENCHMARK] Limited to {num_bars} bars for consistent measurement")

    # Run backtest
    policy = {"symbol": symbol, "timeframe": timeframe}
    start = time.perf_counter()
    results = engine.run(policy=policy, verbose=False)
    run_time = time.perf_counter() - start

    if "error" in results:
        print(f"[ERROR] Backtest failed: {results['error']}")
        return {}

    bars_processed = results["backtest_info"]["bars_processed"]
    time_per_bar = (run_time * 1000) / bars_processed if bars_processed else 0

    metrics = {
        "load_time": load_time,
        "run_time": run_time,
        "bars_processed": bars_processed,
        "time_per_bar_ms": time_per_bar,
        "total_time": load_time + run_time,
    }

    print("\n[RESULTS]")
    print(f"  Load time: {load_time:.2f}s")
    print(f"  Run time: {run_time:.2f}s")
    print(f"  Bars processed: {bars_processed}")
    print(f"  Time per bar: {time_per_bar:.2f}ms")

    return metrics


def run_benchmark(symbol: str, timeframe: str, bars: int, warmup: int) -> None:
    os.environ.setdefault("GENESIS_FAST_WINDOW", "1")
    os.environ.setdefault("GENESIS_PRECOMPUTE_FEATURES", "1")

    engine = BacktestEngine(symbol=symbol, timeframe=timeframe, warmup_bars=warmup)
    engine.load_data()

    if bars and engine.candles_df is not None:
        # Trim to last N bars
        engine.candles_df = engine.candles_df.iloc[-bars:].reset_index(drop=True)

    t0 = time.perf_counter()
    result = engine.run(verbose=False)
    dt = time.perf_counter() - t0

    trades = result.get("summary", {}).get("num_trades", 0)
    print(
        f"[Benchmark] {symbol} {timeframe} bars={len(engine.candles_df)} -> {dt:.2f}s, trades={trades}"
    )


def main():
    parser = argparse.ArgumentParser(description="Benchmark backtest performance")
    parser.add_argument(
        "--symbol", type=str, default="tBTCUSD", help="Trading symbol (default: tBTCUSD)"
    )
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe (default: 1h)")
    parser.add_argument(
        "--bars", type=int, default=1000, help="Number of bars to process (default: 1000)"
    )
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of runs per configuration (default: 1)"
    )
    parser.add_argument(
        "--mode",
        choices=("full", "quick"),
        default="full",
        help="full=compare optimizations (default), quick=single run with fast settings",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=150,
        help="Warmup bars to skip when --mode quick is used (default: 150)",
    )

    args = parser.parse_args()

    if args.mode == "quick":
        run_benchmark(args.symbol, args.timeframe, args.bars, args.warmup)
        return

    print("=" * 70)
    print("Genesis-Core Backtest Performance Benchmark")
    print("=" * 70)
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Bars: {args.bars}")
    print(f"Runs: {args.runs}")

    # Run benchmarks for different configurations
    configs = [
        {"name": "Baseline", "fast_window": False, "precompute": False},
        {"name": "Fast Window", "fast_window": True, "precompute": False},
        {"name": "Precompute", "fast_window": False, "precompute": True},
        {"name": "All Optimizations", "fast_window": True, "precompute": True},
    ]

    results = {}
    for config in configs:
        name = config["name"]
        run_times = []

        for run in range(args.runs):
            if args.runs > 1:
                print(f"\n[RUN {run+1}/{args.runs}]")

            metrics = benchmark_backtest(
                args.symbol,
                args.timeframe,
                args.bars,
                config["fast_window"],
                config["precompute"],
            )

            if metrics:
                run_times.append(metrics["run_time"])

        if run_times:
            avg_time = sum(run_times) / len(run_times)
            results[name] = avg_time

    # Print summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    if results:
        baseline = results.get("Baseline", 1.0)
        print(f"\n{'Configuration':<20} {'Time (s)':<12} {'Speedup':<10}")
        print("-" * 70)

        for name, time_val in results.items():
            speedup = baseline / time_val if time_val > 0 else 0
            print(f"{name:<20} {time_val:>10.2f}s  {speedup:>8.2f}x")

        # Calculate improvement
        best_time = min(results.values())
        improvement = ((baseline - best_time) / baseline) * 100
        print(f"\n[IMPROVEMENT] Best configuration is {improvement:.1f}% faster than baseline")
    else:
        print("[ERROR] No successful runs")


if __name__ == "__main__":
    main()
