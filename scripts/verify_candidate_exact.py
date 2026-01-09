from __future__ import annotations

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
from core.backtest.metrics import calculate_metrics


def run_verification() -> None:
    print("Starting verification of Trial 005 configuration...")

    # Config exactly as in trial_005 (best_trial.json)
    # Note: regime_proba are floats here, which historically caused validation error in some CLIs
    config = {
        "thresholds": {
            "entry_conf_overall": 0.19,
            "regime_proba": {"balanced": 0.46, "bull": 0.5, "bear": 0.44, "ranging": 0.46},
            "min_edge": 0.011,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "low": {"entry_conf_overall": 0.25, "regime_proba": 0.36},
                    "mid": {"entry_conf_overall": 0.32, "regime_proba": 0.44},
                    "high": {"entry_conf_overall": 0.38, "regime_proba": 0.56},
                },
            },
        },
        "exit": {"exit_conf_threshold": 0.43, "max_hold_bars": 20, "trailing_stop_pct": 0.0225},
        "multi_timeframe": {
            "ltf_override_threshold": 0.36,
            "ltf_override_adaptive": {"percentile": 0.83},
            "allow_ltf_override": True,
        },
        "htf_fib": {"entry": {"tolerance_atr": 4.25}},
        "ltf_fib": {"entry": {"tolerance_atr": 1.9}},
        "risk": {
            "risk_map_deltas": {
                "conf_0": -0.05,
                "size_0": 0.002,
                "conf_1": 0.03,
                "size_1": 0.004,
                "conf_2": -0.1,
                "size_2": 0.005,
            }
        },
    }

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        initial_capital=10000,
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    if not engine.load_data():
        print("Failed to load data")
        return

    # Enable optimizations
    engine.precompute_features = True

    print("Running backtest...")
    results = engine.run(configs=config)

    metrics = calculate_metrics(results["trades"], engine.position_tracker.initial_capital)

    print("\n=== Verification Results ===")
    print(f"Num Trades: {metrics['num_trades']}")
    print(f"Total Return: {metrics['total_return']*100:.2f}%")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")

    expected_trades = 2382
    print(f"\nExpected Trades: {expected_trades}")
    if abs(metrics["num_trades"] - expected_trades) < 10:
        print("[SUCCESS] Result reproduced")
    else:
        print("[FAIL] Result mismatch")


if __name__ == "__main__":
    run_verification()
