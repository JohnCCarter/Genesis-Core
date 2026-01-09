#!/usr/bin/env python3
"""
Optimize 1D Configuration
========================

Optimera 1D konfiguration för att få bättre prestanda.
"""

import json


def create_1d_optimization_plan():
    """Skapa optimeringsplan för 1D."""
    print("Skapar 1D optimeringsplan...")

    # Nuvarande konfiguration
    current_config = {
        "entry_conf_overall": 0.01,
        "regime_proba": {"ranging": 0.05, "bull": 0.05, "bear": 0.05, "balanced": 0.05},
        "max_hold_bars": 50,
        "warmup_bars": 10,
        "risk_map": [[0.05, 0.25], [0.15, 0.30], [0.25, 0.35], [0.35, 0.40], [0.45, 0.45]],
    }

    # Optimering plan
    optimization_plan = {
        "current": current_config,
        "optimizations": [
            {
                "name": "Conservative Entry",
                "description": "Högre entry confidence för bättre kvalitet",
                "changes": {
                    "entry_conf_overall": 0.15,
                    "regime_proba": {"ranging": 0.3, "bull": 0.2, "bear": 0.2, "balanced": 0.3},
                },
            },
            {
                "name": "Moderate Entry",
                "description": "Balanserad entry confidence",
                "changes": {
                    "entry_conf_overall": 0.25,
                    "regime_proba": {"ranging": 0.4, "bull": 0.3, "bear": 0.3, "balanced": 0.4},
                },
            },
            {
                "name": "Aggressive Entry",
                "description": "Låg entry confidence för fler trades",
                "changes": {
                    "entry_conf_overall": 0.05,
                    "regime_proba": {"ranging": 0.1, "bull": 0.05, "bear": 0.05, "balanced": 0.1},
                },
            },
            {
                "name": "Long Hold Strategy",
                "description": "Mycket långa holds för macro trends",
                "changes": {
                    "max_hold_bars": 100,
                    "warmup_bars": 20,
                    "risk_map": [[0.05, 0.3], [0.15, 0.35], [0.25, 0.4], [0.35, 0.45], [0.45, 0.5]],
                },
            },
            {
                "name": "Short Hold Strategy",
                "description": "Kortare holds för snabbare rotation",
                "changes": {
                    "max_hold_bars": 20,
                    "warmup_bars": 5,
                    "risk_map": [[0.05, 0.2], [0.15, 0.25], [0.25, 0.3], [0.35, 0.35], [0.45, 0.4]],
                },
            },
        ],
    }

    return optimization_plan


def create_optimized_1d_configs():
    """Skapa optimerade 1D konfigurationer."""
    print("Skapar optimerade 1D konfigurationer...")

    _plan = create_1d_optimization_plan()

    optimized_configs = {}

    for opt in _plan["optimizations"]:
        config_name = opt["name"].lower().replace(" ", "_")

        # Starta med nuvarande konfiguration
        config = {
            "thresholds": {
                "entry_conf_overall": 0.01,
                "regime_proba": {"ranging": 0.05, "bull": 0.05, "bear": 0.05, "balanced": 0.05},
            },
            "risk": {
                "risk_map": [[0.05, 0.25], [0.15, 0.30], [0.25, 0.35], [0.35, 0.40], [0.45, 0.45]]
            },
            "exit": {
                "enabled": True,
                "exit_conf_threshold": 0.05,
                "max_hold_bars": 50,
                "regime_aware_exits": True,
            },
            "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
            "htf_exit_config": {
                "enable_partials": True,
                "enable_trailing": True,
                "enable_structure_breaks": True,
                "partial_1_pct": 0.15,
                "partial_2_pct": 0.05,
                "fib_threshold_atr": 0.05,
                "trail_atr_multiplier": 0.3,
                "swing_update_strategy": "fixed",
            },
            "warmup_bars": 10,
        }

        # Applicera optimering
        for key, value in opt["changes"].items():
            if key == "entry_conf_overall":
                config["thresholds"]["entry_conf_overall"] = value
            elif key == "regime_proba":
                config["thresholds"]["regime_proba"] = value
            elif key == "max_hold_bars":
                config["exit"]["max_hold_bars"] = value
            elif key == "warmup_bars":
                config["warmup_bars"] = value
            elif key == "risk_map":
                config["risk"]["risk_map"] = value

        optimized_configs[config_name] = {
            "name": opt["name"],
            "description": opt["description"],
            "config": config,
        }

    return optimized_configs


def save_optimized_configs(optimized_configs):
    """Spara optimerade konfigurationer."""
    print("Sparar optimerade konfigurationer...")

    with open("1d_optimized_configs.json", "w") as f:
        json.dump(optimized_configs, f, indent=2)

    print("Konfigurationer sparade till: 1d_optimized_configs.json")


def print_optimization_summary(optimized_configs):
    """Skriv ut optimeringssammanfattning."""
    print("\n" + "=" * 80)
    print("1D OPTIMERING SAMMANFATTNING")
    print("=" * 80)

    for _config_name, config_data in optimized_configs.items():
        print(f"\n{config_data['name']}:")
        print(f"  Beskrivning: {config_data['description']}")

        config = config_data["config"]
        print(f"  Entry Confidence: {config['thresholds']['entry_conf_overall']}")
        print(f"  Regime Proba: {config['thresholds']['regime_proba']}")
        print(f"  Max Hold Bars: {config['exit']['max_hold_bars']}")
        print(f"  Warmup Bars: {config['warmup_bars']}")
        print(f"  Risk Map: {config['risk']['risk_map']}")

    print("\n" + "=" * 80)
    print("NÄSTA STEG:")
    print("1. Testa varje konfiguration individuellt")
    print("2. Jämför prestanda")
    print("3. Välj bästa konfigurationen")
    print("4. Uppdatera timeframe_configs.py")
    print("=" * 80)


def main():
    """Huvudfunktion."""
    print("OPTIMIZING 1D CONFIGURATION")
    print("=" * 50)

    try:
        # Skapa optimeringsplan
        _plan = create_1d_optimization_plan()

        # Skapa optimerade konfigurationer
        optimized_configs = create_optimized_1d_configs()

        # Spara konfigurationer
        save_optimized_configs(optimized_configs)

        # Skriv ut sammanfattning
        print_optimization_summary(optimized_configs)

        print("\nSUCCESS: 1D optimeringsplan skapad!")
        print("Vi kan nu testa olika konfigurationer.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
