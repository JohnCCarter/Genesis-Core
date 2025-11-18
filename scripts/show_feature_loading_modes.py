#!/usr/bin/env python3
"""Show the 3 different ways features are loaded depending on context."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main():
    print("=" * 70)
    print("3 SATT ATT LADDA FEATURES - BEROR PÅ KONTEXT")
    print("=" * 70)

    print("\n1. BACKTEST/OPTUNA - RUNTIME BERAKNING")
    print("-" * 70)
    print("   Kontext: Backtest eller Optuna-trial")
    print("   Fil: src/core/strategy/features_asof.py")
    print("   Funktion: _extract_asof()")
    print("\n   Flode:")
    print("   1. BacktestEngine/Optuna anropar evaluate_pipeline()")
    print("   2. evaluate_pipeline() anropar extract_features()")
    print("   3. extract_features() anropar _extract_asof()")
    print("   4. _extract_asof() beraknar alla features on-the-fly")
    print("\n   Features beraknas:")
    print("   - Direkt fran candles (OHLCV)")
    print("   - For varje bar i backtesten")
    print("   - Inga feature-filer anvands")
    print("\n   Exempel:")
    print("   python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h")
    print("   python -m core.optimizer.runner config/optimizer/...")

    print("\n2. BACKTEST/OPTUNA - MED PRECOMPUTED INDIKATORER (Optimering)")
    print("-" * 70)
    print("   Kontext: Backtest/Optuna med --precompute-features")
    print("   Fil: src/core/backtest/engine.py")
    print("   Funktion: load_data() -> precompute_features()")
    print("\n   Flode:")
    print("   1. BacktestEngine beraknar vissa indikatorer i forhand")
    print("   2. Lagras i configs['precomputed_features']")
    print("   3. _extract_asof() anvander dessa om tillgängliga")
    print("   4. Fibonacci-kombinationer beraknas fortfarande i runtime")
    print("\n   Precomputed indikatorer:")
    print("   - atr_14, atr_50")
    print("   - ema_20, ema_50")
    print("   - rsi_14")
    print("   - bb_position_20_2")
    print("   - adx_14")
    print("   - fib_high_idx, fib_low_idx, fib_high_px, fib_low_px")
    print("\n   Varför:")
    print("   - Snabbare (undviker omberakning av indikatorer)")
    print("   - Men v17-kombinationerna beraknas alltid i runtime")
    print("\n   Exempel:")
    print("   python scripts/run_backtest.py --precompute-features ...")
    print("   GENESIS_PRECOMPUTE_FEATURES=1 python -m core.optimizer.runner ...")

    print("\n3. ML TRAINING - FRAN FIL")
    print("-" * 70)
    print("   Kontext: Modelltraining")
    print("   Fil: src/core/utils/data_loader.py")
    print("   Funktion: load_features()")
    print("\n   Flode:")
    print("   1. train_model.py anropar load_features_and_prices()")
    print("   2. load_features_and_prices() anropar load_features()")
    print("   3. load_features() laddar fran precomputed feature-filer")
    print("   4. Features ar redan beraknade och sparade")
    print("\n   Feature-filer:")
    print("   - data/archive/features/tBTCUSD_1h_features_v17.feather")
    print("   - data/archive/features/tBTCUSD_1h_features_v17.parquet")
    print("\n   Genereras av:")
    print("   python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h")
    print("\n   Anvands av:")
    print("   python scripts/train_model.py --feature-version v17 ...")
    print("\n   Varför:")
    print("   - Snabbare training (features redan beraknade)")
    print("   - Konsistenta features for hela datasettet")
    print("   - Anvands ENDAST for training, INTE for backtest/Optuna")

    print("\n" + "=" * 70)
    print("SAMMANFATTNING")
    print("=" * 70)
    print("\n[1] BACKTEST/OPTUNA (Standard)")
    print("    - Features beraknas i runtime")
    print("    - Ingen fil-laddning")
    print("    - Alla features beraknas on-the-fly")
    print("\n[2] BACKTEST/OPTUNA (Med precomputed indikatorer)")
    print("    - Vissa indikatorer beraknas i forhand")
    print("    - Lagras i cache/config")
    print("    - v17-kombinationer beraknas fortfarande i runtime")
    print("    - Snabbare an [1] men samma resultat")
    print("\n[3] ML TRAINING")
    print("    - Features laddas fran precomputed filer")
    print("    - Alla features redan beraknade")
    print("    - Anvands ENDAST for training")
    print("\n" + "=" * 70)
    print("VIKTIGT")
    print("=" * 70)
    print("\n- Backtest/Optuna anvander ALDRIG feature-filer")
    print("- Feature-filer anvands ENDAST for ML training")
    print("- Precomputed indikatorer ar en optimering, inte ett annat satt")
    print("- v17 Fibonacci-kombinationer beraknas ALLTID i runtime")

    return 0


if __name__ == "__main__":
    sys.exit(main())
