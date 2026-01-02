import os
import sys
from unittest.mock import patch

# Force usage of local src
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


# Mock Pipeline
def mock_evaluate_pipeline(candles, policy, configs, state):
    idx = configs.get("_global_index", 0)

    price = candles["close"][-1]

    # Create fake HTF levels
    htf_levels = {
        "htf_fib_100": price * 1.10,
        "htf_fib_0": price * 0.90,
        "htf_fib_0618": price * 0.92,
        "htf_fib_05": price * 1.02,
        "htf_fib_0382": price * 1.0001,  # Tiny TP1 to ensure hit
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

    # Force BUY every 200 bars
    if idx % 200 == 50:
        result["action"] = "BUY"

    return result, meta


def run_forced_test():
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
