import os
import sys

sys.path.insert(0, "src")
os.environ["GENESIS_HTF_EXITS"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

from core.backtest.engine import BacktestEngine

# Best params from 50-trial optimization
best_params = {
    "entry_conf_overall": 0.069,
    "partial_1_pct": 0.40,
    "partial_2_pct": 0.50,
    "trail_atr_multiplier": 2.5,
}

configs = {
    "thresholds": {
        "entry_conf_overall": best_params["entry_conf_overall"],
        "regime_proba": {"bull": 0.05, "bear": 0.05, "ranging": 0.05},
    },
    "exit": {"enabled": True},
    "htf_fib": {
        "exit": {
            "partial_1_pct": best_params["partial_1_pct"],
            "partial_2_pct": best_params["partial_2_pct"],
            "trail_atr_multiplier": best_params["trail_atr_multiplier"],
        },
        "entry": {"enabled": False},
    },
    "ltf_fib": {"entry": {"enabled": False}},
}

engine = BacktestEngine(
    symbol="tBTCUSD",
    timeframe="30m",
    warmup_bars=200,
    start_date="2024-01-01",
    end_date="2024-06-30",
    fast_window=True,
)
engine.precompute_features = True
engine.load_data()

results = engine.run(
    policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs=configs, verbose=False
)

# Get detailed metrics
summary = results.get("summary", {})
trades = results.get("trades", [])

print("=" * 60)
print("DETAILED RESULTS - Best HTF Exit Parameters")
print("=" * 60)
print("Period: 2024-01-01 to 2024-06-30 (6 months)")
print()
print("--- Performance ---")
print(f"Total Return:      {summary.get('total_return', 0):.2f}%")
print(f"Total Return USD:  ${summary.get('total_return_usd', 0):.2f}")
print(f"Final Capital:     ${summary.get('final_capital', 10000):.2f}")
print()
print("--- Trade Statistics ---")
print(f"Total Trades:      {summary.get('num_trades', 0)}")
print(f"Winning Trades:    {summary.get('winning_trades', 0)}")
print(f"Losing Trades:     {summary.get('losing_trades', 0)}")
print(f"Win Rate:          {summary.get('win_rate', 0):.1f}%")
print()
print("--- Risk Metrics ---")
print(f"Profit Factor:     {summary.get('profit_factor', 0):.2f}")
print(f"Max Drawdown:      {summary.get('max_drawdown', 0):.2f}%")
print(f"Avg Win:           ${summary.get('avg_win', 0):.2f}")
print(f"Avg Loss:          ${summary.get('avg_loss', 0):.2f}")
print()
print("--- Best Parameters Used ---")
for k, v in best_params.items():
    print(f"  {k}: {v}")
print("=" * 60)

# Show last 5 trades
if trades:
    print("\n--- Last 5 Trades ---")
    for t in trades[-5:]:
        side = t.get("side", "N/A")
        pnl = t.get("pnl", 0)
        pnl_pct = t.get("pnl_pct", 0)
        reason = t.get("exit_reason", "N/A")
        print(f"  {side}: ${pnl:.2f} ({pnl_pct:.2f}%) - {reason}")
