import os
import sys
from unittest.mock import patch

# Force usage of local src
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


# Mock Pipeline
def mock_evaluate_pipeline(candles, policy, configs, state):
    # Retrieve global index
    idx = configs.get("_global_index", 0)

    # Simple logic: Buy every 200 bars if flat, Sell every 200 bars if flat
    # Actually, let's just Buy periodically to test Long Exits

    # We need to return valid result structure
    result = {
        "action": "NONE",
        "confidence": 0.8,
        "regime": "BULL",
        "features": {
            "ema": candles["close"][-1],  # Mock features needed for exit engine
            "ema_slope50_z": 0.1,
            "htf_fibonacci": {
                "available": True,
                "levels": {
                    # Create fake HTF levels around current price for testing
                    "htf_fib_100": candles["close"][-1] * 1.10,  # Swing High
                    "htf_fib_0": candles["close"][-1] * 0.90,  # Swing Low
                    "htf_fib_0618": candles["close"][-1] * 1.02,  # Target
                    "htf_fib_05": candles["close"][-1] * 1.01,
                    "htf_fib_0382": candles["close"][-1] * 1.005,  # TP1 close
                },
            },
        },
    }
    meta = {
        "decision": {"size": 0.1, "reasons": ["MOCK_ENTRY"], "state_out": {}},
        "features": {"htf_fibonacci": result["features"]["htf_fibonacci"]},
    }

    # Force Entry
    if idx % 500 == 100:
        result["action"] = "BUY"
        print(f"[MOCK] Forcing BUY at bar {idx}")
    elif idx % 500 == 350:
        # Force SELL to clear if not stopped out
        # result["action"] = "SELL"
        pass

    return result, meta


def run_forced_test():
    print("Running Forced Entry Test for HTF Exits...")

    # Enable New Exits
    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    # Patch the function in the engine module
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

        # Enable verbose to see exits
        results = engine.run(
            policy={"symbol": "tBTCUSD", "timeframe": "30m"},
            configs={"exit": {"enabled": True}},
            verbose=True,
        )

        metrics = results.get("metrics", {})
        print("\nTest Results:")
        print(f"Total Trades: {metrics.get('total_trades')}")
        print(f"Total Return: {metrics.get('total_return_pct'):.2%}")


if __name__ == "__main__":
    run_forced_test()
