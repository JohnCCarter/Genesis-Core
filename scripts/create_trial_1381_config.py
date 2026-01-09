import json
from pathlib import Path


def create_config():
    # Params for Trial 1381
    config = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "strategy_name": "Trial 1381 Analysis",
        "thresholds": {
            "entry_conf_overall": 0.30,
            "min_edge": 0.012,
            "signal_adaptation": {
                "zones": {
                    "low": {"entry_conf_overall": 0.26, "regime_proba": 0.37},
                    "mid": {"entry_conf_overall": 0.32, "regime_proba": 0.41},
                    "high": {"entry_conf_overall": 0.38, "regime_proba": 0.58},
                }
            },
        },
        "exit": {"exit_conf_threshold": 0.38, "max_hold_bars": 12, "trailing_stop_pct": 0.01},
        "htf_exit_config": {
            "enable_partials": False,
            "enable_trailing": False,
            "fib_threshold_atr": 0.75,
            "trail_atr_multiplier": 2.6,
        },
        "multi_timeframe": {
            "use_htf_block": True,
            "allow_ltf_override": True,
            "ltf_override_threshold": 0.37,
            "ltf_override_adaptive": {"enabled": True, "percentile": 0.89, "window": 100},
        },
        "htf_fib": {"entry": {"tolerance_atr": 4.0}},
        "ltf_fib": {"entry": {"tolerance_atr": 1.4}},
        "risk": {
            "risk_map": [
                # Base: [0.45, 0.015], [0.55, 0.025], [0.65, 0.035]
                # Deltas:
                # 0: conf 0.05 -> 0.50, size -0.005 -> 0.010
                # 1: conf 0.05 -> 0.60, size +0.001 -> 0.026
                # 2: conf 0.04 -> 0.69, size -0.005 -> 0.030
                [0.50, 0.010],
                [0.60, 0.026],
                [0.69, 0.030],
            ]
        },
    }

    output_path = Path("config/tmp/trial_1381_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Wrap in 'parameters' key for run_backtest.py compatibility
    final_config = {"parameters": config}

    with open(output_path, "w") as f:
        json.dump(final_config, f, indent=2)

    print(f"Created config at {output_path}")


if __name__ == "__main__":
    create_config()
