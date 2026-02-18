import json
import os
import subprocess
import sys
from pathlib import Path


def reproduce_trial():
    # 1. Load the trial data
    trial_path = Path("results/hparam_search/run_20251125_161913/trial_1032.json")
    if not trial_path.exists():
        print(f"Error: Could not find {trial_path}")
        return

    with open(trial_path) as f:
        trial_data = json.load(f)

    print(f"Loaded trial {trial_data['trial_id']}")

    # 2. Extract merged config to a temp file
    config_path = Path("temp_reproduce_config.json")
    with open(config_path, "w") as f:
        json.dump({"cfg": trial_data["merged_config"]}, f, indent=2)

    print(f"Wrote config to {config_path}")

    # 3. Prepare environment variables
    # Based on runner.py logic and what we know about the run
    env = os.environ.copy()
    # Inject environment variables that the optimizer uses
    env["GENESIS_FAST_WINDOW"] = "1"
    env["GENESIS_PRECOMPUTE_FEATURES"] = "1"
    env["GENESIS_RANDOM_SEED"] = "42"

    # 4. Construct command
    # From log: Period: 2023-11-30 10:00:00 to 2025-11-19 00:00:00
    # From log: (warmup: 150)
    cmd = [
        sys.executable,
        "-m",
        "scripts.run_backtest",
        "--symbol",
        "tBTCUSD",
        "--timeframe",
        "1h",
        "--start",
        "2023-11-30",
        "--end",
        "2025-11-19",
        "--warmup",
        "150",
        "--config-file",
        str(config_path),
    ]

    print("\nExecuting command:")
    print(" ".join(cmd))
    print("-" * 50)

    # 5. Run subprocess
    try:
        # Stream output directly to console
        subprocess.run(cmd, env=env, check=False)

    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        # Cleanup
        if config_path.exists():
            os.remove(config_path)
            print(f"\nCleaned up {config_path}")


if __name__ == "__main__":
    reproduce_trial()
