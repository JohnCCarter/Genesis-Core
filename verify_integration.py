import os
import sys

# Enable New Engine
os.environ["GENESIS_HTF_EXITS"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"  # Required for fast_window

# Force usage of local src
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


def run_verification():
    print("Verifying BacktestEngine Integration with Phase 1 Exits...")

    # Init Engine
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="30m",  # Using downloaded data
        warmup_bars=50,
        start_date=None,
        end_date=None,
        fast_window=True,
    )

    # Load Data
    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data. Did you download it?")
        return

    print(f"Loaded {len(engine.candles_df)} bars.")

    # Check if correct engine was selected
    if getattr(engine, "_use_new_exit_engine", False):
        print("SUCCESS: New Exit Engine logic selected.")
    else:
        print("FAILURE: Legacy Engine selected.")
        return

    # Check instance type
    print(f"Engine Type: {type(engine.htf_exit_engine)}")

    # Run Loop (Dry run)
    print("Running backtest loop...")
    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs={}, verbose=False  # Default
    )

    print("Backtest finished.")
    print("Results:", results.keys())


if __name__ == "__main__":
    run_verification()
