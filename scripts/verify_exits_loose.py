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

from core.backtest.engine import BacktestEngine


def run_loose_test() -> None:
    print("Running Backtest with LOOSE constraints to trigger exits...")

    # Enable Phase 1 Exits
    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="30m",
        warmup_bars=50,
        start_date=None,
        end_date=None,
        fast_window=True,
    )

    if not engine.load_data():
        print("Failed to load data")
        return

    loose_configs = {
        "exit": {"enabled": True},
        "thresholds": {
            "entry_conf_overall": 0.01,
            "regime_proba": {
                "bull": 0.01,
                "bear": 0.01,
                "ranging": 0.01,
                "balanced": 0.01,
                "trend": 0.01,
            },
        },
        "htf_fib": {"entry": {"enabled": False}},
        "ltf_fib": {"entry": {"enabled": False}},
        "ev": {"R_default": 0.1},
        "multi_timeframe": {"use_htf_block": False},
    }

    print("Running backtest...")
    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "30m"},
        configs=loose_configs,
        verbose=False,
    )

    metrics = results.get("metrics", {})
    print("\n" + "=" * 40)
    print(f"Total Trades: {metrics.get('total_trades')}")
    print(f"Total Return: {metrics.get('total_return_pct'):.2%}")
    print(f"Win Rate:     {metrics.get('win_rate'):.2%}")
    print("=" * 40)


if __name__ == "__main__":
    run_loose_test()
