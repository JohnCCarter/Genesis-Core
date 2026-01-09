#!/usr/bin/env python3
"""Show how features for v4 model are loaded and computed."""

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
    print("V4 MODELL - FEATURE LADDNING OCH BERAKNING")
    print("=" * 70)

    print("\nTERMINOLOGI:")
    print("-" * 70)
    print("   Modellversion: v4 (version 4 av modellen)")
    print("   Featureversion: v17 (version 17 av features)")
    print("   v4-modellen anvander v17-features")

    print("\n1. FEATURE-BERAKNING (Runtime)")
    print("-" * 70)
    print("   Features beraknas i runtime i features_asof.py")
    print("   Fil: src/core/strategy/features_asof.py")
    print("   Funktion: _extract_asof()")
    print("\n   Flode:")
    print("   1. evaluate_pipeline() anropar extract_features()")
    print("   2. extract_features() anropar _extract_asof()")
    print("   3. _extract_asof() beraknar alla features on-the-fly")

    print("\n2. V4 MODELLENS FEATURES (v17-features)")
    print("-" * 70)
    print("   v4-modellen anvander v17-features som inkluderar")
    print("   3 nya Fibonacci-kombinationer:")
    print("   - fib05_x_ema_slope")
    print("   - fib_prox_x_adx")
    print("   - fib05_x_rsi_inv")
    print("\n   Dessa beraknas i features_asof.py rad 470-479:")
    print("   - fib05_x_ema_slope = fib05_prox_atr * ema_slope")
    print("   - fib_prox_x_adx = fib_prox_score * adx_normalized")
    print("   - fib05_x_rsi_inv = fib05_prox_atr * (-rsi_current)")

    print("\n3. PRECOMPUTED FEATURES (Optional)")
    print("-" * 70)
    print("   Om --precompute-features eller GENESIS_PRECOMPUTE_FEATURES=1:")
    print("   - BacktestEngine beraknar vissa indikatorer i forhand")
    print("   - Lagras i configs['precomputed_features']")
    print("   - Anvands av _extract_asof() om tillgängliga")
    print("\n   Precomputed indikatorer:")
    print("   - atr_14, atr_50")
    print("   - ema_20, ema_50")
    print("   - rsi_14")
    print("   - bb_position_20_2")
    print("   - adx_14")
    print("   - fib_high_idx, fib_low_idx, fib_high_px, fib_low_px")
    print("\n   Men Fibonacci-kombinationerna beraknas alltid i runtime!")

    print("\n4. FEATURE-FILER (For ML Training)")
    print("-" * 70)
    print("   Precomputed feature-filer anvands ENDAST for ML training:")
    print("   - data/archive/features/tBTCUSD_1h_features_v17.feather")
    print("   - data/archive/features/tBTCUSD_1h_features_v17.parquet")
    print("\n   Genereras av: scripts/precompute_features_v17.py")
    print("   Anvands av: scripts/train_model.py (--feature-version v17)")
    print("\n   I backtest/Optuna: Features beraknas i runtime, INTE laddade fran fil!")

    print("\n5. V4 MODELLENS SCHEMA")
    print("-" * 70)
    from core.strategy.model_registry import ModelRegistry

    registry = ModelRegistry()
    model_meta = registry.get_meta("tBTCUSD", "1h")
    if model_meta:
        schema = model_meta.get("schema", [])
        print(f"   Modellversion: {model_meta.get('version', 'N/A')}")
        print("   Featureversion: v17 (som modellen anvander)")
        print(f"   Schema ({len(schema)} features):")
        for i, feat in enumerate(schema, 1):
            marker = (
                " [Fibonacci-kombination]"
                if feat in ["fib05_x_ema_slope", "fib_prox_x_adx", "fib05_x_rsi_inv"]
                else ""
            )
            print(f"     {i:2d}. {feat}{marker}")

    print("\n6. SAMMANFATTNING")
    print("-" * 70)
    print("   [MODELL] v4 (version 4 av modellen)")
    print("   [FEATURES] v17 (version 17 av features)")
    print("   [RUNTIME] Features beraknas alltid i runtime")
    print("   [OPTIONAL] Precomputed indikatorer kan anvandas for hastighet")
    print("   [TRAINING] Feature-filer anvands endast for ML training")

    print("\n" + "=" * 70)
    print("VIKTIGT")
    print("=" * 70)
    print("\nv4-modellen anvander v17-features. Features beraknas ALLTID")
    print("i runtime i features_asof.py. De laddas INTE fran precomputed")
    print("feature-filer i backtest eller Optuna.")
    print("\nPrecomputed feature-filer anvands endast for ML training.")
    print("Precomputed indikatorer (ATR, EMA, RSI, etc.) kan anvandas for")
    print("hastighet om --precompute-features anvands, men Fibonacci-")
    print("kombinationerna beraknas alltid i runtime.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
