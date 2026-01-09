#!/usr/bin/env python3
"""
Filter a Genesis-Core model JSON down to a specific feature subset.

Usage:
  python scripts/filter_model_features.py --input results/models/tBTCUSD_1h_v3.json \
      --features volatility_shift_ma3,fib05_prox_atr,fib_prox_x_adx,fib_prox_score,fib05_x_rsi_inv,vol_regime \
      --output results/models/tBTCUSD_1h_v3_top.json
"""

import argparse
import json
from pathlib import Path


def filter_model(model: dict, keep_features: list[str]) -> dict:
    schema = model.get("schema", [])
    buy = model.get("buy", {})
    sell = model.get("sell", {})

    # Preserve order according to provided keep_features
    ordered_indices = [schema.index(f) for f in keep_features if f in schema]

    def _slice(weights: list[float], indices: list[int]) -> list[float]:
        return [weights[i] for i in indices]

    buy_w = buy.get("w", [])
    sell_w = sell.get("w", [])

    filtered = {
        "version": model.get("version", "v3"),
        "schema": [schema[i] for i in ordered_indices],
        "buy": {
            "w": _slice(buy_w, ordered_indices),
            "b": buy.get("b", 0.0),
            "calib": buy.get("calib", {"a": 1.0, "b": 0.0}),
        },
        "sell": {
            "w": _slice(sell_w, ordered_indices),
            "b": sell.get("b", 0.0),
            "calib": sell.get("calib", {"a": 1.0, "b": 0.0}),
        },
    }

    # Preserve optional regime calibration if present
    if "calibration_by_regime" in model:
        filtered["calibration_by_regime"] = model["calibration_by_regime"]

    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter model to top features")
    parser.add_argument("--input", required=True, help="Input model JSON path")
    parser.add_argument("--features", required=True, help="Comma-separated feature names to keep")
    parser.add_argument("--output", required=True, help="Output model JSON path")

    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    model = json.loads(in_path.read_text(encoding="utf-8"))
    keep = [f.strip() for f in args.features.split(",") if f.strip()]

    filtered = filter_model(model, keep)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(filtered, indent=2), encoding="utf-8")

    print(f"[SAVED] {out_path}")
    print(f"Kept {len(filtered['schema'])} features: {', '.join(filtered['schema'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
