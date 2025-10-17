#!/usr/bin/env python3
"""
Cleanup Old Models
=================

Ta bort gamla multi-timeframe modeller eftersom vi nu har
individuella modeller för varje timeframe.
"""

import shutil
from pathlib import Path


def cleanup_old_models():
    """Ta bort gamla multi-timeframe modeller."""
    print("Rensar gamla multi-timeframe modeller...")

    # Lista över gamla modeller att ta bort
    old_models = [
        "tADAUSD.json",
        "tALGOUSD.json",
        "tAPTUSD.json",
        "tAVAXUSD.json",
        "tBTCUSD.json",
        "tDOGEUSD.json",
        "tDOTUSD.json",
        "tEOSUSD.json",
        "tETHUSD.json",
        "tFILUSD.json",
        "tLTCUSD.json",
        "tNEARUSD.json",
        "tSOLUSD.json",
        "tXAUTUSD.json",
        "tXTZUSD.json",
    ]

    # Skapa backup mapp
    backup_dir = Path("config/models/backup_old_models")
    backup_dir.mkdir(exist_ok=True)

    removed_count = 0
    for model_file in old_models:
        model_path = Path(f"config/models/{model_file}")

        if model_path.exists():
            try:
                # Flytta till backup
                backup_path = backup_dir / model_file
                shutil.move(str(model_path), str(backup_path))
                print(f"Flyttade: {model_file} -> backup/")
                removed_count += 1
            except Exception as e:
                print(f"Fel vid flytt av {model_file}: {e}")
        else:
            print(f"Finns inte: {model_file}")

    print(f"\nTotalt flyttade modeller: {removed_count}")
    print(f"Backup mapp: {backup_dir}")
    return removed_count


def verify_cleanup():
    """Verifiera att cleanup fungerade."""
    print("\nVerifierar cleanup...")

    models_dir = Path("config/models")

    # Räkna individuella modeller
    individual_models = list(models_dir.glob("*_*.json"))
    print(f"Individuella modeller: {len(individual_models)}")

    # Räkna gamla modeller (borde vara 0)
    old_models = [
        f for f in models_dir.glob("t*.json") if "_" not in f.name and f.name != "registry.json"
    ]
    print(f"Gamla modeller kvar: {len(old_models)}")

    if len(old_models) == 0:
        print("SUCCESS: Alla gamla modeller borttagna!")
        return True
    else:
        print("WARNING: Några gamla modeller kvarstår!")
        for model in old_models:
            print(f"  - {model.name}")
        return False


def main():
    """Huvudfunktion."""
    print("CLEANUP OLD MODELS")
    print("=" * 50)

    try:
        # Steg 1: Ta bort gamla modeller
        removed = cleanup_old_models()

        # Steg 2: Verifiera cleanup
        success = verify_cleanup()

        print("\n" + "=" * 50)
        print("CLEANUP RESULTAT:")
        print(f"Flyttade modeller: {removed}")
        print(f"Verifiering: {'SUCCESS' if success else 'FAILED'}")

        if success:
            print("\nSUCCESS: Cleanup komplett!")
            print("Gamla modeller finns i backup/ mappen")
        else:
            print("\nWARNING: Några problem kvarstår")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
