import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.optimizer.runner import _resolve_sample_range


def reproduce_mismatch():
    print("=== Reproducing Bar Count Mismatch ===")

    # 1. Simulate Optuna Logic
    snapshot_id = "tBTCUSD_1h_2023-12-01_2025-11-19_v1"
    runs_cfg = {"sample_start": "2023-12-01", "sample_end": "2025-11-19"}

    # Optuna logic for resolving dates
    optuna_start, optuna_end = _resolve_sample_range(snapshot_id, runs_cfg)
    print(f"Optuna Resolved Range: {optuna_start} -> {optuna_end}")

    # 2. Simulate BacktestEngine Logic (Load Data)
    symbol = "tBTCUSD"
    timeframe = "1h"

    base_dir = Path(__file__).parent.parent / "data"
    data_file = base_dir / "candles" / f"{symbol}_{timeframe}.parquet"

    if not data_file.exists():
        # Try alternative path
        data_file = base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"

    if not data_file.exists():
        print(f"[ERROR] Data file not found: {data_file}")
        return

    df = pd.read_parquet(data_file)
    print(f"Total rows in parquet: {len(df)}")

    # Apply filters
    start_dt = pd.to_datetime(optuna_start)
    end_dt = pd.to_datetime(optuna_end)

    filtered_df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
    print(f"Filtered rows (Engine Logic): {len(filtered_df)}")

    # 3. Simulate "Runner" specific logic if any (e.g. if it uses a different start time)
    # The summary mentioned runner uses 17278 bars (start 2023-11-30 10:00) vs 17255 (2023-12-01)

    # Let's check what 17278 corresponds to
    diff = 17278 - len(filtered_df)
    print(f"Difference: {diff} bars", flush=True)

    if diff > 0:
        print(
            f"Mismatch confirmed! Missing {diff} bars in Engine logic compared to reported Runner count.",
            flush=True,
        )
        if not filtered_df.empty:
            start_label = filtered_df.index[0]
            start_pos = df.index.get_loc(start_label)
            print(f"Start label: {start_label}, Start pos: {start_pos}", flush=True)

            # Check if we can shift back
            if isinstance(start_pos, slice):
                start_pos = start_pos.start

            new_start_pos = start_pos - diff
            if new_start_pos >= 0:
                expanded_start_ts = df.iloc[new_start_pos]["timestamp"]
                print(
                    f"If we include {diff} previous bars, start time would be: {expanded_start_ts}",
                    flush=True,
                )
            else:
                print("Not enough history to backtrack!", flush=True)
        else:
            print("Filtered DataFrame is empty!", flush=True)
    else:
        print("No mismatch found with straightforward logic. Investigating deeper...", flush=True)


if __name__ == "__main__":
    reproduce_mismatch()
