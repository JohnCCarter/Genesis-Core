import os
import sys

# Force usage of local src
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine


def run_backtest_with_mode(mode: str, symbol="tBTCUSD", timeframe="30m"):
    print(f"\n--- Running Backtest: {mode} ---")

    if mode == "NEW":
        os.environ["GENESIS_HTF_EXITS"] = "1"
    else:
        os.environ["GENESIS_HTF_EXITS"] = "0"

    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        warmup_bars=50,
        start_date=None,  # Use all available downloaded data
        end_date=None,
        fast_window=True,
    )

    if not engine.load_data():
        print("Failed to load data")
        return None

    results = engine.run(
        policy={"symbol": symbol, "timeframe": timeframe},
        configs={"exit": {"enabled": True}},  # Ensure exits are enabled generally
        verbose=False,
    )

    return results


def compare():
    print("Comparing HTF Exit Strategies...")

    # 1. Baseline (Legacy/Current)
    res_legacy = run_backtest_with_mode("LEGACY")

    # 2. New Phase 1
    res_new = run_backtest_with_mode("NEW")

    if not res_legacy or not res_new:
        print("Error: Could not complete backtests.")
        return

    # 3. Print Comparison
    metrics_legacy = res_legacy.get("metrics", {})
    metrics_new = res_new.get("metrics", {})

    cols = ["Total Return", "Win Rate", "Max Drawdown", "Total Trades"]

    print("\n" + "=" * 40)
    print(f"{'Metric':<20} | {'Legacy':<10} | {'New (Phase 1)':<10}")
    print("-" * 40)

    for metric in cols:
        k = metric.lower().replace(" ", "_")
        if metric == "Total Return":
            k = "total_return_pct"
        if metric == "Win Rate":
            k = "win_rate"

        val_leg = metrics_legacy.get(k, 0.0)
        val_new = metrics_new.get(k, 0.0)

        # Format
        if "pct" in k or "rate" in k or "drawdown" in k:
            s_leg = f"{val_leg:.2%}"
            s_new = f"{val_new:.2%}"
        else:
            s_leg = f"{val_leg:.0f}"
            s_new = f"{val_new:.0f}"

        print(f"{metric:<20} | {s_leg:<10} | {s_new:<10}")
    print("=" * 40)


if __name__ == "__main__":
    compare()
