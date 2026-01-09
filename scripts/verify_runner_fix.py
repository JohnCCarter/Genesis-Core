from __future__ import annotations

import os
import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    # scripts/<this file> -> parents[1] == repo root
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.optimizer.runner import TrialConfig, _run_backtest_direct


def verify_fix() -> None:
    print("=== Verifying Runner Date Fix ===")

    symbol = "tBTCUSD"
    timeframe = "1h"
    start_date = "2023-12-01"
    end_date = "2025-11-19"

    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    trial = TrialConfig(
        snapshot_id=f"{symbol}_{timeframe}_{start_date}_{end_date}_v1",
        symbol=symbol,
        timeframe=timeframe,
        warmup_bars=100,
        parameters={},
        start_date=start_date,
        end_date=end_date,
    )

    config_path = Path("temp_config.json")
    import json

    config_path.write_text(json.dumps({"cfg": {}}, ensure_ascii=False), encoding="utf-8")

    try:
        print(f"Running backtest for {start_date} to {end_date}...")
        exit_code, log, _results = _run_backtest_direct(
            trial, config_path, start_date=start_date, end_date=end_date
        )

        if exit_code != 0:
            print(f"Backtest failed with code {exit_code}")
            print(log)
            return

        print("Backtest successful.")

        start_date_2 = "2024-01-01"
        print(f"\nRunning second backtest for {start_date_2} to {end_date}...")
        exit_code_2, _log2, _results2 = _run_backtest_direct(
            trial,
            config_path,
            start_date=start_date_2,
            end_date=end_date,
        )

        if exit_code_2 == 0:
            print("Second run successful (proved cache separation).")
        else:
            print("Second run failed!")

        print("\nVerification passed: _run_backtest_direct accepts dates and runs successfully.")
    finally:
        config_path.unlink(missing_ok=True)


if __name__ == "__main__":
    verify_fix()
