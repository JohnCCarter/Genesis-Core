#!/usr/bin/env python3
"""Test Optuna med EXAKT konfiguration - 1-3 månader."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.optimizer.runner import run_optimizer


def main():
    print("=== OPTUNA EXAKT KONFIGURATION - 1-3 MÅNADER ===")
    print()
    print("Konfiguration:")
    print("- Timeframe: 1h")
    print("- Period: 1-3 månader (Apr-Jun 2025)")
    print("- Snapshot: tBTCUSD_1h_2024-10-22_2025-10-01_v1")
    print("- Study: tBTCUSD_1h_longer_test (SAMMA)")
    print("- Storage: sqlite:///test_optuna_longer.db (SAMMA)")
    print()
    print("EXAKT: Samma parametrar som fungerade tidigare!")
    print("OK Samma risk_map som fungerade")
    print("OK Samma thresholds som fungerade")
    print("OK Samma exit parametrar som fungerade")
    print("OK Fortsätt från befintlig study")
    print()
    print("Optuna kommer att:")
    print("OK Komma ihag alla 13 tidigare trials")
    print("OK Fortsatta lara sig fran tidigare resultat")
    print("OK Testa nya parametrar med 1-3 manaders data")
    print("OK Hitta battre resultat med mer data")
    print()

    try:
        print("Startar Optuna exakt test...")
        config_path = Path("config/optimizer/tBTCUSD_1h_exact_optuna.yaml")
        result = run_optimizer(config_path)

        if result:
            print("OK Optuna exakt test slutford!")
            print(f"Resultat: {result}")
        else:
            print("BAD Optuna exakt test misslyckades")
            return 1

    except Exception as e:
        print(f"BAD Fel under Optuna exakt test: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
