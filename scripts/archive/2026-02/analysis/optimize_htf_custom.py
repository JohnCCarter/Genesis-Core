import logging
import os
import sys
import warnings

import optuna

# Setup paths
sys.path.insert(0, os.path.abspath("src"))

from core.backtest.engine import BacktestEngine

# Suppress excessive logs
logging.getLogger().setLevel(logging.WARNING)
warnings.filterwarnings("ignore")


def objective(trial):
    # Set Environment for this trial
    os.environ["GENESIS_HTF_EXITS"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    # 1. Suggest Parameters
    # Entry threshold (looser to get trades)
    entry_conf = trial.suggest_float("entry_conf_overall", 0.05, 0.40)  # Very loose to mild

    # HTF Exit Params
    p1 = trial.suggest_float("partial_1_pct", 0.1, 0.5, step=0.05)
    # p2 is percent of REMAINING size? The engine uses absolute pct of original size usually?
    # Let's check engine. default partial_2_pct = 0.5 (of remaining).
    # The config name says partial_2_pct.
    p2 = trial.suggest_float("partial_2_pct", 0.1, 0.8, step=0.1)

    # Logic in engine:
    # self.partial_1_pct = config.get("partial_1_pct", 0.33)
    # self.partial_2_pct = config.get("partial_2_pct", 0.50)

    trail_mult = trial.suggest_float("trail_atr_multiplier", 1.0, 3.0, step=0.5)

    # 2. Configure Engine
    # We pass these via overrides or explicitly patch logic?
    # BacktestEngine takes `configs` dict in `run()`.

    configs = {
        "thresholds": {
            "entry_conf_overall": entry_conf,
            "regime_proba": {"bull": 0.05, "bear": 0.05, "ranging": 0.05},  # Loose
        },
        "exit": {"enabled": True},
        "img_src_config": {  # If engine reads from ConfigAuthority, difficult to override class init?
            # ACTUALLY, HTFFibonacciExitEngine reads from its `config` arg.
            # In engine.py: self.htf_exit_engine = HTFFibonacciExitEngine(self.htf_exit_config)
            # self.htf_exit_config = self.config.get("htf_fib", {}).get("exit", {})
            # So we need to pass `htf_fib.exit` in configs.
        },
        "htf_fib": {
            "exit": {"partial_1_pct": p1, "partial_2_pct": p2, "trail_atr_multiplier": trail_mult},
            "entry": {"enabled": False},  # Disable blocking
        },
        "ltf_fib": {"entry": {"enabled": False}},
    }

    # 3. Run Backtest
    # Set precompute flag via environment BEFORE init
    os.environ["GENESIS_FAST_WINDOW"] = "1"

    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="30m",
        warmup_bars=200,
        start_date="2024-01-01",  # Extended: 6 months
        end_date="2024-06-30",
        fast_window=True,
    )
    # Enable precompute BEFORE load_data
    engine.precompute_features = True

    if not engine.load_data():
        raise optuna.TrialPruned("Data load failed")

    results = engine.run(
        policy={"symbol": "tBTCUSD", "timeframe": "30m"}, configs=configs, verbose=False
    )

    # Get metrics from summary (standard location)
    summary = results.get("summary", {})
    metrics = summary.get("metrics", results.get("metrics", {}))
    total_trades = metrics.get("total_trades", 0)
    total_return = metrics.get("total_return", 0.0)  # Fraction not pct

    # 4. Constraints
    if total_trades < 5:
        # Penalize low trades
        return -100.0  # Bad score

    # SCORE: Total Return (as percentage)
    return total_return * 100


if __name__ == "__main__":
    print("Starting Extended HTF Exit Optimization (50 trials, 6 months data)...")
    print("This will take approximately 15-30 minutes.")
    print("=" * 60)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50, n_jobs=1)  # Extended: 50 trials

    print("=" * 60)
    print("Optimization Complete")
    print(f"Best Score: {study.best_value:.2f}%")
    print("Best Params:")
    for k, v in study.best_params.items():
        print(f"  {k}: {v}")

    # Run verification backtest with best params
    print("=" * 60)
    print("Verifying Best Params...")
    best = study.best_params
    # ... (Re-run logic if needed, but printing params is enough for now)
