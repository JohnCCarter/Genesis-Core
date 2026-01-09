"""Force entries via a mocked evaluate_pipeline to exercise HTF exit logic.

This is a manual verification script (not a pytest test). It patches
`core.backtest.engine.evaluate_pipeline` to emit deterministic BUY signals and inject
fake HTF Fibonacci levels so the exit engine can be observed.

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
    # Retrieve global index (BacktestEngine uses this to pass current bar index)
    idx = int(configs.get("_global_index", 0))

    price = float(candles["close"][-1])

    result = {
        "action": "NONE",
        "confidence": 0.8,
        "regime": "BULL",
        "features": {
            "ema": price,
            "ema_slope50_z": 0.1,
            "htf_fibonacci": {
                "available": True,
                "levels": {
                    "htf_fib_100": price * 1.10,
                    "htf_fib_0": price * 0.90,
                    "htf_fib_0618": price * 1.02,
                    "htf_fib_05": price * 1.01,
                    "htf_fib_0382": price * 1.005,
                },
            },
        },
    }

    meta = {
        "decision": {"size": 0.1, "reasons": ["MOCK_ENTRY"], "state_out": {}},
        "features": {"htf_fibonacci": result["features"]["htf_fibonacci"]},
    }

    if idx % 500 == 100:
        result["action"] = "BUY"
        print(f"[MOCK] Forcing BUY at bar {idx}")

    return result, meta


def run_forced_test() -> None:
    print("Running Forced Entry Test for HTF Exits...")

    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    with patch("core.backtest.engine.evaluate_pipeline", side_effect=mock_evaluate_pipeline):
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

        print("Data loaded. Running backtest with MOCKED signal...")

        results = engine.run(
            policy={"symbol": "tBTCUSD", "timeframe": "30m"},
            configs={"exit": {"enabled": True}},
            verbose=True,
        )

        metrics = results.get("metrics", {})
        print("\nTest Results:")
        print(f"Total Trades: {metrics.get('total_trades')}")
        tr = metrics.get("total_return_pct")
        if tr is None:
            print("Total Return: n/a")
        else:
            print(f"Total Return: {tr:.2%}")


if __name__ == "__main__":
    run_forced_test()
