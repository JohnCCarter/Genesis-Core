import copy
import json
import sys
from pathlib import Path

import optuna
import pandas as pd

# Add src to path
sys.path.append(str(Path.cwd() / "src"))

from core.pipeline import GenesisPipeline


def deep_merge(base, override):
    """Deep merge override dict into base dict."""
    for k, v in override.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            deep_merge(base[k], v)
        else:
            base[k] = v


def check_robustness(study_url, study_name, top_n=20):
    print(f"Loading study {study_name}...")
    study = optuna.load_study(study_name=study_name, storage=study_url)

    # Get completed trials
    trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    # Sort by value (descending)
    trials.sort(key=lambda t: t.value, reverse=True)

    top_trials = trials[:top_n]

    print(f"Checking robustness for top {len(top_trials)} trials...")
    print("Period: 2023-12-22 to 2025-12-11")

    results = []

    # Setup pipeline
    pipeline = GenesisPipeline()
    pipeline.setup_environment()

    # We need to reconstruct the config for each trial
    # This requires the parameter expansion logic

    for _i, trial in enumerate(top_trials):
        print(f"Checking Trial {trial.number} (Score: {trial.value:.4f})...")

        # 1. Expand parameters
        params = trial.params
        expanded_params = {}
        for key, value in params.items():
            if "." in key:
                parts = key.split(".")
                current = expanded_params
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                expanded_params[key] = value

        # 2. Reconstruct Risk Map (Special handling)
        if "risk" in expanded_params and "risk_map_deltas" in expanded_params["risk"]:
            deltas = expanded_params["risk"].pop("risk_map_deltas")
            # Base map from the script logic
            base_map = [
                (0.48, 0.01),
                (0.59, 0.015),
                (0.70, 0.07),
            ]
            risk_map = []
            for idx, (base_conf, base_size) in enumerate(base_map):
                # Handle both dict and scalar values
                d_conf = deltas.get(f"conf_{idx}", 0.0)
                d_size = deltas.get(f"size_{idx}", 0.0)
                if isinstance(d_conf, dict):
                    d_conf = 0.0
                if isinstance(d_size, dict):
                    d_size = 0.0
                risk_map.append([round(base_conf + d_conf, 2), round(base_size + d_size, 3)])
            expanded_params["risk"]["risk_map"] = risk_map

        # 3. Create Engine and Run
        # Initialize engine
        engine = pipeline.create_engine(
            symbol="tBTCUSD",
            timeframe="1h",
            start_date="2023-12-22",
            end_date="2025-12-11",
            capital=10000.0,
        )

        # Load data
        if not engine.load_data():
            print("  -> Failed to load data")
            continue

        # Inject config
        # The engine usually loads config from a file or is passed a config object.
        # In run_backtest.py, it loads a RuntimeConfig.
        # We need to patch the runtime config with our trial parameters.

        # Load default runtime to get the structure
        config_path = Path("config/runtime.json")
        if not config_path.exists():
            print(f"  -> Config file not found: {config_path}")
            continue

        try:
            with open(config_path) as f:
                base_runtime = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  -> Failed to parse config: {e}")
            continue

        # Create a deep copy of base cfg and merge trial params
        run_cfg = copy.deepcopy(base_runtime.get("cfg", {}))
        deep_merge(run_cfg, expanded_params)

        # Run backtest
        try:
            metrics = engine.run(run_cfg)

            results.append(
                {
                    "trial": trial.number,
                    "optuna_score": trial.value,
                    "long_return": metrics["total_return"] * 100,
                    "long_pf": metrics["profit_factor"],
                    "long_dd": metrics["max_drawdown"] * 100,
                    "trades": metrics["total_trades"],
                }
            )
            print(
                f"  -> Return: {metrics['total_return']*100:.2f}%, PF: {metrics['profit_factor']:.2f}"
            )

        except Exception as e:
            print(f"  -> Failed: {e}")

    # Print Summary
    print("\n=== Robustness Check Summary ===")
    df = pd.DataFrame(results)
    if not df.empty:
        print(df.to_string(index=False))

        # Check for any "Survivors" (Positive return + PF > 1.0)
        survivors = df[(df["long_return"] > 0) & (df["long_pf"] > 1.0)]
        if not survivors.empty:
            print("\n=== POTENTIAL SURVIVORS ===")
            print(survivors.to_string(index=False))
        else:
            print("\nNo survivors found among top trials.")
    else:
        print("No results generated.")


if __name__ == "__main__":
    url = "sqlite:///results/hparam_search/storage/optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627.db"
    name = "optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627"
    check_robustness(url, name, top_n=20)
