"""Force entries via a mocked evaluate_pipeline (variant v2).

This script is similar to `verify_exits_forced.py` but uses different synthetic HTF
levels and a different entry cadence.

Notes:
- Sets `GENESIS_HTF_EXITS=1` and `GENESIS_PRECOMPUTE_FEATURES=1` for the run.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch


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


def mock_evaluate_pipeline(candles: dict, policy: dict, configs: dict, state: dict):
    idx = int(configs.get("_global_index", 0))
    price = float(candles["close"][-1])

    htf_levels = {
        "htf_fib_100": price * 1.10,
        "htf_fib_0": price * 0.90,
        "htf_fib_0618": price * 0.92,
        "htf_fib_05": price * 1.02,
        "htf_fib_0382": price * 1.0001,  # tiny TP1 to ensure hit
    }

    features = {
        "ema": price,
        "ema_slope50_z": 0.1,
        "htf_fibonacci": {"available": True, "levels": htf_levels},
    }

    result = {"action": "NONE", "confidence": 0.8, "regime": "BULL", "features": features}
    meta = {
        "decision": {"size": 0.1, "reasons": ["MOCK_ENTRY"], "state_out": {}},
        "features": features,
    }

    if idx % 200 == 50:
        result["action"] = "BUY"

    return result, meta


def run_forced_test() -> None:
    print("Running Forced Entry Test v2...")

    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    with patch("core.backtest.engine.evaluate_pipeline", side_effect=mock_evaluate_pipeline):
        engine = BacktestEngine(
            symbol="tBTCUSD",
            timeframe="30m",
            warmup_bars=50,
            start_date="2024-02-01",
            end_date="2024-03-01",
            fast_window=True,
        )

        if not engine.load_data():
            print("Failed to load data")
            return

        print(f"Data loaded: {len(engine.candles_df)} bars. Running...")

        results = engine.run(
            policy={"symbol": "tBTCUSD", "timeframe": "30m"},
            configs={"exit": {"enabled": True}},
            verbose=True,
        )

        metrics = results.get("metrics", {})
        print("\nTest Results:")
        print(f"Total Trades (Metrics): {metrics.get('total_trades', 0)}")
        print(f"Total Trades (Tracker): {len(engine.position_tracker.trades)}")

        tr = metrics.get("total_return_pct")
        if tr is None:
            tr = 0.0
        print(f"Total Return: {tr:.2%}")


if __name__ == "__main__":
    run_forced_test()
