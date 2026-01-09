#!/usr/bin/env python3
"""
Execute Model Registry Update
============================

Master script som kör hela uppdateringsprocessen.
"""

import subprocess
import sys


def run_script(script_name, description):
    """Kör ett script och rapportera resultat."""
    print(f"\n{'='*60}")
    print(f"Kör: {description}")
    print(f"Script: {script_name}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, script_name], capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode == 0:
            print("SUCCESS!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("FAILED!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)

        return result.returncode == 0

    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    """Huvudfunktion som kör hela processen."""
    print("MODEL REGISTRY UPPDATERING")
    print("=" * 60)

    # Steg 1: Analysera nuvarande tillstånd
    if not run_script("update_model_registry_plan.py", "Analysera nuvarande modeller"):
        print("Analys misslyckades. Avbryter.")
        return

    # Steg 2: Skapa nya modeller
    if not run_script("create_advanced_models.py", "Skapa avancerade modeller"):
        print("Skapande av modeller misslyckades. Avbryter.")
        return

    # Steg 3: Fixa 4h timeframes
    if not run_script("fix_timeframe_4h.py", "Fixa 4h timeframes"):
        print("Fixa timeframes misslyckades. Avbryter.")
        return

    # Steg 4: Uppdatera registry mapping
    if not run_script("update_registry_mapping.py", "Uppdatera registry mapping"):
        print("Registry uppdatering misslyckades. Avbryter.")
        return

    # Steg 5: Verifiera allt
    if not run_script("verify_model_registry.py", "Verifiera modeller"):
        print("Verifiering misslyckades.")
        return

    print("\n" + "=" * 60)
    print("SUCCESS: Alla steg slutförda!")
    print("=" * 60)

    print("\nNästa steg:")
    print("1. Testa att modellerna fungerar i backtest")
    print("2. Ta bort gamla modeller om allt fungerar")
    print("3. Commit och push ändringar")


if __name__ == "__main__":
    main()
