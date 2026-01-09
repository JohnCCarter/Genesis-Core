#!/usr/bin/env python3
"""Show which model is loaded for a symbol/timeframe."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.strategy.model_registry import ModelRegistry  # noqa: E402


def main():
    symbol = "tBTCUSD"
    timeframe = "1h"

    print("=" * 70)
    print(f"MODEL LOADING FOR {symbol} {timeframe}")
    print("=" * 70)

    registry = ModelRegistry()

    # Check registry first
    registry_path = ROOT_DIR / "config" / "models" / "registry.json"
    if registry_path.exists():
        reg_data = json.loads(registry_path.read_text(encoding="utf-8"))
        key = f"{symbol}:{timeframe}"
        entry = reg_data.get(key)
        if entry:
            print(f"\n[REGISTRY] Found entry for {key}:")
            print(f"  Champion: {entry.get('champion', 'N/A')}")
            print(f"  Challenger: {entry.get('challenger', 'N/A')}")

    # Load model
    meta = registry.get_meta(symbol, timeframe)

    if meta is None:
        print(f"\n[ERROR] No model found for {symbol} {timeframe}")
        print(f"\n[FALLBACK] Tried path: config/models/{symbol}_{timeframe}.json")
        return 1

    # Show model info
    print("\n[MODEL] Loaded successfully!")
    print(f"  Version: {meta.get('version', 'N/A')}")
    print(f"  Schema: {len(meta.get('schema', []))} features")
    print(f"  Features: {', '.join(meta.get('schema', [])[:5])}...")

    # Show weights info
    buy_w = meta.get("buy", {}).get("w", [])
    sell_w = meta.get("sell", {}).get("w", [])
    print("\n[WEIGHTS]")
    print(f"  Buy weights: {len(buy_w)} values")
    print(f"  Sell weights: {len(sell_w)} values")
    print(f"  Buy bias: {meta.get('buy', {}).get('b', 0.0):.6f}")
    print(f"  Sell bias: {meta.get('sell', {}).get('b', 0.0):.6f}")

    # Show calibration
    buy_calib = meta.get("buy", {}).get("calib", {})
    sell_calib = meta.get("sell", {}).get("calib", {})
    print("\n[CALIBRATION]")
    print(f"  Buy: a={buy_calib.get('a', 1.0)}, b={buy_calib.get('b', 0.0)}")
    print(f"  Sell: a={sell_calib.get('a', 1.0)}, b={sell_calib.get('b', 0.0)}")

    # Check for regime-specific calibration
    regime_calib = meta.get("calibration_by_regime")
    if regime_calib:
        print("\n[REGIME CALIBRATION] Found!")
        print(f"  Regimes: {list(regime_calib.get('buy', {}).keys())}")
    else:
        print("\n[REGIME CALIBRATION] Not found (using default)")

    # Show file path
    model_path = ROOT_DIR / "config" / "models" / f"{symbol}_{timeframe}.json"
    if model_path.exists():
        print(f"\n[FILE] {model_path}")
        print(f"  Size: {model_path.stat().st_size} bytes")
        print(f"  Modified: {model_path.stat().st_mtime}")

    print("\n" + "=" * 70)
    print("SAMMA MODELL ANVÄNDS I BÅDE BACKTEST OCH OPTUNA")
    print("=" * 70)
    print("\nFlöde:")
    print("  1. evaluate_pipeline() anropar predict_proba_for()")
    print("  2. predict_proba_for() anropar ModelRegistry.get_meta()")
    print("  3. ModelRegistry laddar från config/models/<SYMBOL>_<TF>.json")
    print("  4. Både backtest och Optuna använder samma flöde")

    return 0


if __name__ == "__main__":
    sys.exit(main())
