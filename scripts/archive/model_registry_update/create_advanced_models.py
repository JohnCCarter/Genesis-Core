#!/usr/bin/env python3
"""
Skapa Avancerade Modeller
========================

Detta script skapar nya modeller med 5-feature schema för alla
symbol-timeframe kombinationer som saknas.
"""

import json
import os


def create_advanced_model_template():
    """Skapa template för avancerad 5-feature model."""
    return {
        "version": "v3",
        "schema": [
            "rsi_inv_lag1",
            "volatility_shift_ma3",
            "bb_position_inv_ma3",
            "rsi_vol_interaction",
            "vol_regime",
        ],
        "buy": {
            "w": [
                0.24632984264101013,
                0.29627872058253374,
                0.37364758207066845,
                -0.1015278767772536,
                -0.10937285558591385,
            ],
            "b": -0.3012037705902129,
            "calib": {"a": 1.0, "b": 0.0},
        },
        "sell": {
            "w": [
                -0.24632984264093774,
                -0.2962787205824723,
                -0.3736475820705902,
                0.10152787677724555,
                0.10937285558588404,
            ],
            "b": 0.30120377059013576,
            "calib": {"a": 1.0, "b": 0.0},
        },
        "calibration_by_regime": {
            "buy": {
                "bear": {"method": "platt", "a": 4.1452196845980405, "b": -0.0950151904841081},
                "bull": {"method": "platt", "a": 1.2429055852810174, "b": -0.12182298132360019},
                "ranging": {"method": "platt", "a": 1.9755742797512388, "b": -0.012889927514931985},
            },
            "sell": {
                "bear": {"method": "platt", "a": 2.792164583392896, "b": 0.28828286412864296},
                "bull": {"method": "platt", "a": 0.7254672583677596, "b": 0.13367963516248377},
                "ranging": {"method": "platt", "a": 1.025879191958136, "b": 0.027000282000388818},
            },
        },
    }


def create_missing_models():
    """Skapa alla saknade modeller."""
    print("Skapar saknade modeller...")

    # Läs planen
    with open("model_update_plan.json") as f:
        plan = json.load(f)

    template = create_advanced_model_template()
    created_count = 0

    for item in plan["new_models_to_create"]:
        model_file = item["file"]
        symbol = item["symbol"]
        timeframe = item["timeframe"]

        # Skapa model fil
        model_path = f"config/models/{model_file}"

        if not os.path.exists(model_path):
            try:
                with open(model_path, "w") as f:
                    json.dump(template, f, indent=2)
                print(f"Skapade: {model_file}")
                created_count += 1
            except Exception as e:
                print(f"Fel vid skapande av {model_file}: {e}")
        else:
            print(f"Finns redan: {model_file}")

    print(f"\nTotalt skapade modeller: {created_count}")
    return created_count


def main():
    """Huvudfunktion."""
    print("Startar skapande av avancerade modeller...")

    try:
        created = create_missing_models()
        print(f"\nKlart! Skapade {created} nya modeller.")

    except Exception as e:
        print(f"Fel: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
