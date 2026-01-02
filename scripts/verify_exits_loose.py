import os
import sys

# Force usage of local src
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


def run_loose_test():
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

    # Loose Configs
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
        policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs=loose_configs, verbose=False
    )

    metrics = results.get("metrics", {})
    print("\n" + "=" * 40)
    print(f"Total Trades: {metrics.get('total_trades')}")
    print(f"Total Return: {metrics.get('total_return_pct'):.2%}")
    print(f"Win Rate:     {metrics.get('win_rate'):.2%}")
    print("=" * 40)


if __name__ == "__main__":
    run_loose_test()
