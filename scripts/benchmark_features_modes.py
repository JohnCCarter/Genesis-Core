import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")

from core.backtest.engine import BacktestEngine

# Use a known existing candidate or champion file
CANDIDATE_PATH = "config/strategy/champions/tBTCUSD_1h.json"


def run_once(use_precompute: bool):
    # Canonical policy:
    # - precompute run should be 1/1 (fast_window + precompute)
    # - non-precompute run should be 0/0
    if use_precompute:
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
    else:
        os.environ["GENESIS_FAST_WINDOW"] = "0"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "0"

    if not Path(CANDIDATE_PATH).exists():
        print(f"Error: Config file not found: {CANDIDATE_PATH}")
        return

    with Path(CANDIDATE_PATH).open("r") as f:
        data = json.load(f)

    # Handle champion format vs candidate format
    if "config" in data:
        cfg = data["config"]
    elif "cfg" in data:
        cfg = data["cfg"]
    else:
        cfg = data  # Assume raw config

    print(f"\n=== Starting run with use_precompute={use_precompute} ===")

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        initial_capital=10_000.0,
        start_date="2024-01-01",  # Shorter period for quick benchmark
        end_date="2024-06-01",
        warmup_bars=150,
        fast_window=use_precompute,
    )

    # Explicitly set the flag on engine as runner does
    if use_precompute:
        engine.precompute_features = True

    t0 = time.perf_counter()
    if not engine.load_data():
        print("Failed to load data")
        return
    t1 = time.perf_counter()

    results = engine.run(configs=cfg)
    t2 = time.perf_counter()

    print(f"load_data: {t1 - t0:.3f}s")
    print(f"run:      {t2 - t1:.3f}s")
    print(f"total:    {t2 - t0:.3f}s")
    summary = results.get("summary") or {}
    if summary:
        trades = summary.get("num_trades", 0)
        total_return = summary.get("total_return", 0.0)
        profit_factor = summary.get("profit_factor")
        print(f"trades:   {trades}")
        print(f"return:   {total_return:.2f}%")
        if profit_factor is not None:
            print(f"pf:       {profit_factor:.2f}")
    else:
        print("Summary unavailable. Keys:", list(results.keys()))
        if "error" in results:
            print("Error:", results["error"])


if __name__ == "__main__":
    print("Running benchmark...")
    # Run without precompute first
    run_once(False)
    # Run with precompute
    run_once(True)
