#!/usr/bin/env python3
"""
Timeframe-specific configurations for optimized performance.
"""


def get_6h_config():
    """6h timeframe config - EXCELLENT performance, behåll nuvarande."""
    return {
        "thresholds": {
            "entry_conf_overall": 0.35,  # Fungerar bra
            "regime_proba": {"ranging": 0.5, "bull": 0.5, "bear": 0.5, "balanced": 0.5},
        },
        "risk": {
            "risk_map": [
                [0.35, 0.1],  # 0.35 confidence -> 0.1 size
                [0.45, 0.15],
                [0.55, 0.2],
                [0.65, 0.25],
                [0.75, 0.3],
            ]
        },
        "exit": {
            "enabled": True,
            "exit_conf_threshold": 0.3,
            "max_hold_bars": 20,  # Fungerar bra
            "regime_aware_exits": True,
        },
        "gates": {
            "cooldown_bars": 0,
            "hysteresis_steps": 2,
        },
        "htf_exit_config": {
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            "partial_1_pct": 0.40,  # Fungerar bra
            "partial_2_pct": 0.30,
            "fib_threshold_atr": 0.3,
            "trail_atr_multiplier": 1.3,
            "swing_update_strategy": "fixed",
        },
        "warmup_bars": 50,
    }


def get_3h_config():
    """3h timeframe config – mellanläge mellan 6h och 1h."""
    return {
        "thresholds": {
            "entry_conf_overall": 0.34,
            "regime_proba": {
                "ranging": 0.7,
                "bull": 0.65,
                "bear": 0.65,
                "balanced": 0.7,
            },
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {
                        "entry_conf_overall": 0.35,
                        "regime_proba": {
                            "ranging": 0.65,
                            "bull": 0.55,
                            "bear": 0.55,
                            "balanced": 0.65,
                        },
                    },
                    "mid": {
                        "entry_conf_overall": 0.40,
                        "regime_proba": {
                            "ranging": 0.75,
                            "bull": 0.65,
                            "bear": 0.65,
                            "balanced": 0.75,
                        },
                    },
                    "high": {
                        "entry_conf_overall": 0.46,
                        "regime_proba": {
                            "ranging": 0.85,
                            "bull": 0.75,
                            "bear": 0.75,
                            "balanced": 0.85,
                        },
                    },
                },
            },
        },
        "risk": {
            "risk_map": [
                [0.40, 0.02],
                [0.50, 0.03],
                [0.60, 0.04],
            ]
        },
        "exit": {
            "enabled": True,
            "exit_conf_threshold": 0.35,
            "max_hold_bars": 25,
            "regime_aware_exits": True,
        },
        "gates": {
            "cooldown_bars": 2,
            "hysteresis_steps": 3,
        },
        "htf_exit_config": {
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            "partial_1_pct": 0.50,
            "partial_2_pct": 0.40,
            "fib_threshold_atr": 0.6,
            "trail_atr_multiplier": 2.0,
            "swing_update_strategy": "fixed",
        },
        "warmup_bars": 100,
    }


def get_1h_config():
    """1h timeframe config – champion baseline."""
    return {
        "thresholds": {
            "entry_conf_overall": 0.35,
            "regime_proba": {
                "ranging": 0.8,
                "bull": 0.7,
                "bear": 0.7,
                "balanced": 0.7,
            },
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {
                        "entry_conf_overall": 0.36,
                        "regime_proba": {
                            "ranging": 0.7,
                            "bull": 0.6,
                            "bear": 0.6,
                            "balanced": 0.7,
                        },
                    },
                    "mid": {
                        "entry_conf_overall": 0.42,
                        "regime_proba": {
                            "ranging": 0.8,
                            "bull": 0.7,
                            "bear": 0.7,
                            "balanced": 0.8,
                        },
                    },
                    "high": {
                        "entry_conf_overall": 0.48,
                        "regime_proba": {
                            "ranging": 0.88,
                            "bull": 0.78,
                            "bear": 0.78,
                            "balanced": 0.88,
                        },
                    },
                },
            },
        },
        "risk": {
            "risk_map": [
                [0.45, 0.015],
                [0.55, 0.025],
                [0.65, 0.035],
            ]
        },
        "exit": {
            "enabled": True,
            "exit_conf_threshold": 0.4,
            "max_hold_bars": 20,
            "regime_aware_exits": True,
        },
        "gates": {
            "cooldown_bars": 2,
            "hysteresis_steps": 3,
        },
        "htf_exit_config": {
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            "partial_1_pct": 0.60,  # STÖRRE: Snabbare profit-taking
            "partial_2_pct": 0.50,
            "fib_threshold_atr": 0.7,  # STÖRRE: Mindre känslig
            "trail_atr_multiplier": 2.5,  # STÖRRE: Bättre trailing
            "swing_update_strategy": "fixed",
        },
        "htf_fib": {
            "entry": {
                "enabled": True,
                "tolerance_atr": 0.5,
                "long_max_level": 0.618,
                "short_min_level": 0.382,
            }
        },
        "ltf_fib": {
            "entry": {
                "enabled": True,
                "tolerance_atr": 0.5,
                "long_max_level": 0.618,
                "short_min_level": 0.382,
            }
        },
        "warmup_bars": 150,  # ÖKAD: Mer data för bättre signals
    }


def get_1d_config():
    """1D timeframe config - OPTIMIZED based on 6h and 1h learnings."""
    return {
        "thresholds": {
            "entry_conf_overall": 0.30,
            "regime_proba": {"ranging": 0.6, "bull": 0.5, "bear": 0.5, "balanced": 0.6},
        },
        "risk": {
            "risk_map": [
                [0.30, 0.15],
                [0.40, 0.20],
                [0.50, 0.25],
                [0.60, 0.30],
                [0.70, 0.35],
            ]
        },
        "exit": {
            "enabled": True,
            "exit_conf_threshold": 0.25,
            "max_hold_bars": 30,
            "regime_aware_exits": True,
        },
        "gates": {
            "cooldown_bars": 1,
            "hysteresis_steps": 2,
        },
        "htf_exit_config": {
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            "partial_1_pct": 0.35,
            "partial_2_pct": 0.25,
            "fib_threshold_atr": 0.4,
            "trail_atr_multiplier": 1.5,
            "swing_update_strategy": "fixed",
        },
        "warmup_bars": 30,
    }


def get_timeframe_config(timeframe: str) -> dict:
    """
    Get optimized configuration for specific timeframe.

    Args:
        timeframe: "1D", "6h", "1h"

    Returns:
        dict: Optimized configuration for timeframe
    """
    configs = {
        "1D": get_1d_config,
        "6h": get_6h_config,
        "3h": get_3h_config,
        "1h": get_1h_config,
    }

    if timeframe not in configs:
        raise ValueError(f"Unsupported timeframe: {timeframe}. Supported: {list(configs.keys())}")

    return configs[timeframe]()


def get_timeframe_backtest_config(timeframe: str) -> dict:
    """
    Get backtest engine configuration for specific timeframe.

    Args:
        timeframe: "1D", "6h", "1h"

    Returns:
        dict: Backtest engine configuration
    """
    # Base config
    base_config = {
        "symbol": "tBTCUSD",
        "timeframe": timeframe,
        "initial_capital": 10000.0,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
    }

    # Timeframe-specific dates and parameters
    timeframe_configs = {
        "1D": {
            "start_date": "2025-07-17",
            "end_date": "2025-10-14",
            "warmup_bars": 20,
        },
        "6h": {
            "start_date": "2025-07-01",
            "end_date": "2025-10-13",
            "warmup_bars": 50,
        },
        "3h": {  # 🆕 Ny block
            "start_date": "2025-08-01",
            "end_date": "2025-10-14",
            "warmup_bars": 80,
        },
        "1h": {
            "start_date": "2025-09-14",
            "end_date": "2025-10-14",
            "warmup_bars": 120,
        },
    }
    if timeframe not in timeframe_configs:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    # Merge base config with timeframe-specific config
    config = {**base_config, **timeframe_configs[timeframe]}

    # Add HTF exit config from strategy config
    strategy_config = get_timeframe_config(timeframe)
    config["htf_exit_config"] = strategy_config["htf_exit_config"]

    return config


if __name__ == "__main__":
    # Test configurations
    for timeframe in ["1D", "6h", "1h"]:
        print(f"\n=== {timeframe} CONFIG ===")
        config = get_timeframe_config(timeframe)
        print(f"Entry Conf: {config['thresholds']['entry_conf_overall']}")
        print(f"Max Hold: {config['exit']['max_hold_bars']}")
        print(f"Risk Map: {config['risk']['risk_map'][0]}")
        print(f"Partial 1: {config['htf_exit_config']['partial_1_pct']}")

        backtest_config = get_timeframe_backtest_config(timeframe)
        print(f"Period: {backtest_config['start_date']} to {backtest_config['end_date']}")
        print(f"Warmup: {backtest_config['warmup_bars']}")
