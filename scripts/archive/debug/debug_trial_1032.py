import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


def run_debug():
    # Load ORIGINAL trial result to get the EXACT config used
    trial_path = Path("results/hparam_search/run_20251125_161913/trial_1032.json")
    with open(trial_path) as f:
        trial_data = json.load(f)

    # Use the merged_config which represents the full state during the trial
    config = trial_data["merged_config"]

    # Setup engine with EXACTLY the same parameters as Optuna runner
    # Optuna runner passes warmup_bars from trial params (150)
    # Enable performance optimizations (fast_window + precompute) to match Optuna speed
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        initial_capital=10000.0,
        start_date="2023-11-30",  # Full period from log
        end_date="2025-11-19",
        warmup_bars=150,
        fast_window=True,
    )
    engine.precompute_features = True
    engine.load_data()

    print(f"Running backtest for {engine.symbol} {engine.timeframe}...")
    print(f"Warmup bars: {engine.warmup_bars}")

    # Run with the exact config
    results = engine.run(configs=config)

    summary = results.get("summary", {})
    print("\nResults:")
    print(f"Total Trades: {summary.get('num_trades', 0)}")
    print(f"Total Return: {summary.get('total_return', 0.0):.2f}%")
    print(f"Win Rate: {summary.get('win_rate', 0.0):.2f}%")
    print(f"Profit Factor: {summary.get('profit_factor', 0.0):.2f}")
    print(f"Max Drawdown: {summary.get('max_drawdown', 0.0):.2f}%")

    # Compare with expected
    expected_return = trial_data["score"]["metrics"]["total_return"]
    print(f"\nExpected Return (from trial file): {expected_return:.2f}%")
    print(f"Difference: {summary.get('total_return', 0.0) - expected_return:.2f}%")


if __name__ == "__main__":
    # Set seed as runner does
    os.environ["GENESIS_RANDOM_SEED"] = "42"
    run_debug()
