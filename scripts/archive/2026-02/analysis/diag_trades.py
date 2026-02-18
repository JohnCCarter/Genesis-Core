import os
import sys

sys.path.insert(0, "src")
os.environ["GENESIS_HTF_EXITS"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

from core.backtest.engine import BacktestEngine

engine = BacktestEngine(
    symbol="tBTCUSD",
    timeframe="30m",
    warmup_bars=200,
    start_date="2024-02-01",
    end_date="2024-04-01",
    fast_window=True,
)
engine.precompute_features = True
engine.load_data()

# Run with very loose configs
configs = {
    "thresholds": {
        "entry_conf_overall": 0.01,  # Ultra loose
        "regime_proba": {"bull": 0.01, "bear": 0.01, "ranging": 0.01},
    },
    "exit": {"enabled": True},
    "htf_fib": {"entry": {"enabled": False}},
    "ltf_fib": {"entry": {"enabled": False}},
}

results = engine.run(
    policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs=configs, verbose=False
)
summary = results.get("summary", {})
metrics = summary.get("metrics", results.get("metrics", {}))
print(f"Total trades: {metrics.get('total_trades', 0)}")
print(f"Total return: {metrics.get('total_return', 0)*100:.2f}%")
