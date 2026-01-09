#!/usr/bin/env python3
"""Debug why 30m backtest generates zero trades."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# CONFIGURABLE
import sys

import pandas as pd

from core.config.authority import ConfigAuthority
from core.strategy.evaluate import evaluate_pipeline

TIMEFRAME = sys.argv[1] if len(sys.argv) > 1 else "30m"

# Load candles
candles_df = pd.read_parquet(f"data/candles/tBTCUSD_{TIMEFRAME}.parquet")

# Load config
authority = ConfigAuthority()
cfg_obj, _, _ = authority.get()
cfg = cfg_obj.model_dump()

# Policy
policy = {"symbol": "tBTCUSD", "timeframe": TIMEFRAME}

# Test on 10 recent bars
print("Testing pipeline on 10 recent bars:")
print("=" * 80)

for i in range(-10, 0):
    # Get candles up to bar i
    candles_subset = {
        "open": candles_df["open"].iloc[: candles_df.index[i] + 1].tolist(),
        "high": candles_df["high"].iloc[: candles_df.index[i] + 1].tolist(),
        "low": candles_df["low"].iloc[: candles_df.index[i] + 1].tolist(),
        "close": candles_df["close"].iloc[: candles_df.index[i] + 1].tolist(),
        "volume": candles_df["volume"].iloc[: candles_df.index[i] + 1].tolist(),
    }

    # Run pipeline
    result, meta = evaluate_pipeline(candles_subset, policy=policy, configs=cfg)

    # Print summary
    print(f"\nBar {i} ({candles_df.index[i]}):")
    print(
        f"  Probas: BUY={result['probas']['buy']:.4f}, SELL={result['probas']['sell']:.4f}, HOLD={result['probas']['hold']:.4f}"
    )
    print(f"  Conf: BUY={result['confidence']['buy']:.4f}, SELL={result['confidence']['sell']:.4f}")
    print(f"  Regime: {result['regime']}")
    print(f"  Action: {result['action']}")

    # Print decision meta
    if meta.get("decision"):
        dec_meta = meta["decision"]
        print(f"  Decision meta: {dec_meta}")

    # Check EV
    p_buy = result["probas"]["buy"]
    p_sell = result["probas"]["sell"]
    R = 1.8  # R_default from config
    ev = p_buy * R - p_sell
    print(f"  EV: {ev:.4f} (p_buy={p_buy:.4f} * R={R} - p_sell={p_sell:.4f})")

    # Check if probabilities passed threshold
    if result["probas"]["buy"] > 0.55 and result["action"] == "NONE":
        print(f"  [DEBUG] BUY proba {result['probas']['buy']:.4f} > 0.55 but action is NONE!")
        if ev <= 0:
            print(f"  [REASON] EV_NEG: {ev:.4f} <= 0")
    if result["probas"]["sell"] > 0.55 and result["action"] == "NONE":
        print(f"  [DEBUG] SELL proba {result['probas']['sell']:.4f} > 0.55 but action is NONE!")
