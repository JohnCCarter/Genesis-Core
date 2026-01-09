"""Verify that BacktestEngine selects the intended HTF exit engine.

This is a manual verification script (not a pytest test).

Notes:
- Sets `GENESIS_HTF_EXITS=1` and `GENESIS_PRECOMPUTE_FEATURES=1` for the run.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    """Make `import core` work when running the script without `pip install -e .`."""

    try:
        import core  # noqa: F401

        return
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]
        src_dir = repo_root / "src"
        if src_dir.is_dir() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.backtest.engine import BacktestEngine


def run_verification() -> None:
    print("Verifying BacktestEngine Integration with Phase 1 Exits...")

    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"  # required for fast_window

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="30m",
        warmup_bars=50,
        start_date=None,
        end_date=None,
        fast_window=True,
    )

    print("Loading data...")
    if not engine.load_data():
        print("ERROR: Failed to load data. Did you download it?")
        return

    print(f"Loaded {len(engine.candles_df)} bars.")

    if getattr(engine, "_use_new_exit_engine", False):
        print("SUCCESS: New Exit Engine logic selected.")
    else:
        print("FAILURE: Legacy Engine selected.")
        return

    print(f"Engine Type: {type(engine.htf_exit_engine)}")

    print("Running backtest loop...")
    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs={}, verbose=False
    )

    print("Backtest finished.")
    print("Results keys:", results.keys())


if __name__ == "__main__":
    run_verification()
