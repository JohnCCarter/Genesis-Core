#!/usr/bin/env python3
"""
Complete Model Registry Update
=============================

Detta script uppdaterar ALLA modeller till:
1. Avancerade 5-feature schema
2. Alla Bitfinex timeframes: 1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h, 1D, 1W, 14D, 1M
3. Komplett registry för alla symboler
"""

import json
import os
from pathlib import Path

# Bitfinex stödda timeframes
BITFINEX_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "3h", "6h", "12h", "1D", "1W", "14D", "1M"]

# Alla symboler
ALL_SYMBOLS = [
    "tBTCUSD",
    "tETHUSD",
    "tADAUSD",
    "tDOTUSD",
    "tDOGEUSD",
    "tEOSUSD",
    "tFILUSD",
    "tLTCUSD",
    "tNEARUSD",
    "tSOLUSD",
    "tXTZUSD",
    "tXAUTUSD",
    "tALGOUSD",
    "tAPTUSD",
    "tAVAXUSD",
]


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


def create_all_models():
    """Skapa alla modeller för alla symboler och timeframes."""
    print("Skapar alla modeller...")

    template = create_advanced_model_template()
    created_count = 0
    skipped_count = 0

    for symbol in ALL_SYMBOLS:
        for timeframe in BITFINEX_TIMEFRAMES:
            model_file = f"{symbol}_{timeframe}.json"
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
                skipped_count += 1

    print(f"\nTotalt skapade modeller: {created_count}")
    print(f"Totalt hoppade över: {skipped_count}")
    return created_count


def create_complete_registry():
    """Skapa komplett registry för alla symboler och timeframes."""
    print("\nSkapar komplett registry...")

    registry = {}

    for symbol in ALL_SYMBOLS:
        for timeframe in BITFINEX_TIMEFRAMES:
            key = f"{symbol}:{timeframe}"
            model_path = f"config/models/{symbol}_{timeframe}.json"

            registry[key] = {"champion": model_path}

    # Spara registry
    with open("config/models/registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    print(f"Skapade registry med {len(registry)} entries")
    return len(registry)


def update_existing_models():
    """Uppdatera befintliga modeller till 5-feature schema."""
    print("\nUppdaterar befintliga modeller...")

    models_dir = Path("config/models")
    updated_count = 0

    for model_file in models_dir.glob("*.json"):
        if model_file.name == "registry.json":
            continue

        try:
            with open(model_file) as f:
                data = json.load(f)

            # Kontrollera om det är en multi-timeframe fil
            if isinstance(data, dict) and any(
                isinstance(v, dict) and "schema" in v for v in data.values()
            ):
                # Detta är en multi-timeframe fil, uppdatera varje timeframe
                for timeframe, config in data.items():
                    if isinstance(config, dict) and "schema" in config:
                        if len(config["schema"]) == 2:  # Gamla 2-feature schema
                            # Uppdatera till 5-feature schema
                            config["schema"] = [
                                "rsi_inv_lag1",
                                "volatility_shift_ma3",
                                "bb_position_inv_ma3",
                                "rsi_vol_interaction",
                                "vol_regime",
                            ]

                            # Uppdatera weights (använd samma som template)
                            config["buy"] = {
                                "w": [
                                    0.24632984264101013,
                                    0.29627872058253374,
                                    0.37364758207066845,
                                    -0.1015278767772536,
                                    -0.10937285558591385,
                                ],
                                "b": -0.3012037705902129,
                                "calib": {"a": 1.0, "b": 0.0},
                            }
                            config["sell"] = {
                                "w": [
                                    -0.24632984264093774,
                                    -0.2962787205824723,
                                    -0.3736475820705902,
                                    0.10152787677724555,
                                    0.10937285558588404,
                                ],
                                "b": 0.30120377059013576,
                                "calib": {"a": 1.0, "b": 0.0},
                            }

                            # Lägg till regime calibration
                            config["calibration_by_regime"] = {
                                "buy": {
                                    "bear": {
                                        "method": "platt",
                                        "a": 4.1452196845980405,
                                        "b": -0.0950151904841081,
                                    },
                                    "bull": {
                                        "method": "platt",
                                        "a": 1.2429055852810174,
                                        "b": -0.12182298132360019,
                                    },
                                    "ranging": {
                                        "method": "platt",
                                        "a": 1.9755742797512388,
                                        "b": -0.012889927514931985,
                                    },
                                },
                                "sell": {
                                    "bear": {
                                        "method": "platt",
                                        "a": 2.792164583392896,
                                        "b": 0.28828286412864296,
                                    },
                                    "bull": {
                                        "method": "platt",
                                        "a": 0.7254672583677596,
                                        "b": 0.13367963516248377,
                                    },
                                    "ranging": {
                                        "method": "platt",
                                        "a": 1.025879191958136,
                                        "b": 0.027000282000388818,
                                    },
                                },
                            }

                            print(f"Uppdaterade: {model_file.name}:{timeframe}")
                            updated_count += 1

                # Spara uppdaterad fil
                with open(model_file, "w") as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Fel vid uppdatering av {model_file.name}: {e}")

    print(f"Totalt uppdaterade timeframes: {updated_count}")
    return updated_count


def fix_4h_timeframes():
    """Fixa 4h timeframes till 3h i befintliga modeller."""
    print("\nFixar 4h timeframes...")

    models_dir = Path("config/models")
    fixed_count = 0

    for model_file in models_dir.glob("*.json"):
        if model_file.name == "registry.json":
            continue

        try:
            with open(model_file) as f:
                data = json.load(f)

            # Kontrollera om det är en multi-timeframe fil
            if isinstance(data, dict) and "4h" in data:
                # Byt 4h till 3h
                data["3h"] = data["4h"]
                del data["4h"]

                # Spara uppdaterad fil
                with open(model_file, "w") as f:
                    json.dump(data, f, indent=2)

                print(f"Fixade: {model_file.name} (4h -> 3h)")
                fixed_count += 1

        except Exception as e:
            print(f"Fel vid fix av {model_file.name}: {e}")

    print(f"Totalt fixade timeframes: {fixed_count}")
    return fixed_count


def verify_complete_setup():
    """Verifiera att allt är korrekt konfigurerat."""
    print("\nVerifierar komplett setup...")

    # Kontrollera registry
    with open("config/models/registry.json") as f:
        registry = json.load(f)

    expected_entries = len(ALL_SYMBOLS) * len(BITFINEX_TIMEFRAMES)
    actual_entries = len(registry)

    print(f"Förväntade registry entries: {expected_entries}")
    print(f"Faktiska registry entries: {actual_entries}")

    if actual_entries != expected_entries:
        print("WARNING: Registry har fel antal entries!")
        return False

    # Kontrollera att alla modeller finns
    missing_models = []
    for symbol in ALL_SYMBOLS:
        for timeframe in BITFINEX_TIMEFRAMES:
            model_path = f"config/models/{symbol}_{timeframe}.json"
            if not os.path.exists(model_path):
                missing_models.append(model_path)

    if missing_models:
        print(f"WARNING: {len(missing_models)} modeller saknas!")
        for model in missing_models[:5]:  # Visa första 5
            print(f"  - {model}")
        if len(missing_models) > 5:
            print(f"  ... och {len(missing_models) - 5} fler")
        return False

    print("SUCCESS: Alla modeller och registry entries finns!")
    return True


def main():
    """Huvudfunktion."""
    print("COMPLETE MODEL REGISTRY UPDATE")
    print("=" * 60)
    print(f"Symboler: {len(ALL_SYMBOLS)}")
    print(f"Timeframes: {len(BITFINEX_TIMEFRAMES)}")
    print(f"Totalt modeller: {len(ALL_SYMBOLS) * len(BITFINEX_TIMEFRAMES)}")
    print("=" * 60)

    try:
        # Steg 1: Uppdatera befintliga modeller
        updated = update_existing_models()

        # Steg 2: Fixa 4h timeframes
        fixed = fix_4h_timeframes()

        # Steg 3: Skapa alla nya modeller
        created = create_all_models()

        # Steg 4: Skapa komplett registry
        registry_entries = create_complete_registry()

        # Steg 5: Verifiera allt
        success = verify_complete_setup()

        print("\n" + "=" * 60)
        print("SAMMANFATTNING:")
        print(f"Uppdaterade befintliga timeframes: {updated}")
        print(f"Fixade 4h timeframes: {fixed}")
        print(f"Skapade nya modeller: {created}")
        print(f"Registry entries: {registry_entries}")
        print(f"Verifiering: {'SUCCESS' if success else 'FAILED'}")
        print("=" * 60)

        if success:
            print("\nSUCCESS: Alla modeller uppdaterade!")
            print("Nästa steg: Testa att modellerna fungerar i backtest")
        else:
            print("\nWARNING: Några problem kvarstår")

    except Exception as e:
        print(f"Fel: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
