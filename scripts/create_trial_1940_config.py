import json
from pathlib import Path


def create_config():
    # Base config structure (simplified for brevity, matching the structure used in create_trial_208_config.py)
    config = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "strategy_name": "Trial 1940 Analysis",
        "thresholds": {
            "entry_conf_overall": 0.27,
            "min_edge": 0.011,
            "signal_adaptation": {
                "zones": {
                    "low": {"entry_conf_overall": 0.24, "regime_proba": 0.38},
                    "mid": {"entry_conf_overall": 0.35, "regime_proba": 0.49},
                    "high": {"entry_conf_overall": 0.38, "regime_proba": 0.61},
                }
            },
        },
        "exit": {"exit_conf_threshold": 0.4, "max_hold_bars": 16, "trailing_stop_pct": 0.015},
        "htf_exit_config": {
            "enable_partials": False,
            "enable_trailing": True,
            "fib_threshold_atr": 0.75,
            "trail_atr_multiplier": 2.6,
        },
        "multi_timeframe": {
            "use_htf_block": True,
            "allow_ltf_override": True,
            "ltf_override_threshold": 0.45,
            "ltf_override_adaptive": {"enabled": True, "percentile": 0.82, "window": 100},
        },
        "htf_fib": {"entry": {"tolerance_atr": 4.0}},
        "ltf_fib": {"entry": {"tolerance_atr": 1.8}},
        "risk": {
            "risk_map": [
                # Base: [0.48, 0.01], [0.59, 0.015], [0.70, 0.07] (From Trial 208 script)
                # Deltas:
                # 0: conf -0.13 -> 0.35, size -0.004 -> 0.006
                # 1: conf -0.02 -> 0.57, size +0.001 -> 0.016
                # 2: conf 0.0 -> 0.70, size -0.015 -> 0.055
                [0.35, 0.006],
                [0.57, 0.016],
                [0.70, 0.055],
            ]
        },
    }

    output_path = Path("config/tmp/trial_1940_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Wrap in 'parameters' key for run_backtest.py compatibility
    final_config = {"parameters": config}

    with open(output_path, "w") as f:
        json.dump(final_config, f, indent=2)


if __name__ == "__main__":
    create_config()
