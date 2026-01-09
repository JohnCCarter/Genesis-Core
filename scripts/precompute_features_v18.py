#!/usr/bin/env python3
"""
Precompute features v18 (compact set: 5 base indicators + Fibonacci combos).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.fibonacci import FibonacciConfig, calculate_fibonacci_features_vectorized
from core.indicators.vectorized import calculate_atr_vectorized, calculate_rsi_vectorized
from core.utils import get_candles_path

BASE_FEATURES = [
    "rsi_inv_lag1",
    "volatility_shift_ma3",
    "bb_position_inv_ma3",
    "rsi_vol_interaction",
    "vol_regime",
]

COMBO_FEATURES = [
    "fib05_x_ema_slope",
    "fib_prox_x_adx",
    "fib05_x_rsi_inv",
]

ALL_COLUMNS = ["timestamp", *BASE_FEATURES, "fib05_prox_atr", "fib_prox_score", *COMBO_FEATURES]


def compute_base_features(candles: pd.DataFrame) -> pd.DataFrame:
    close = candles["close"]
    high = candles["high"]
    low = candles["low"]

    rsi = calculate_rsi_vectorized(close)
    rsi_inv = (rsi - 50.0) / 50.0
    rsi_inv_lag1 = rsi_inv.shift(1).clip(-1.0, 1.0).fillna(0.0)

    atr_short = calculate_atr_vectorized(high, low, close, period=14)
    atr_long = calculate_atr_vectorized(high, low, close, period=50)
    vol_shift = (atr_short / atr_long.replace(0, np.nan)).fillna(1.0).clip(0.5, 2.0)

    vol_shift_ma3 = vol_shift.rolling(window=3, min_periods=1).mean().fillna(1.0).clip(0.5, 2.0)

    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std(ddof=0)
    bb_upper = bb_middle + 2.0 * bb_std
    bb_lower = bb_middle - 2.0 * bb_std
    bb_pos = ((close - bb_lower) / (bb_upper - bb_lower).replace(0, np.nan)).clip(0.0, 1.0)
    bb_inv_ma3 = (1.0 - bb_pos).rolling(window=3, min_periods=1).mean().clip(0.0, 1.0)

    rsi_vol_interaction = (rsi_inv * vol_shift).clip(-2.0, 2.0).fillna(0.0)

    vol_regime = (vol_shift > 1.0).astype(float)

    df = pd.DataFrame(
        {
            "timestamp": candles["timestamp"].values,
            "rsi_inv_lag1": rsi_inv_lag1,
            "volatility_shift_ma3": vol_shift_ma3,
            "bb_position_inv_ma3": bb_inv_ma3.fillna(0.5),
            "rsi_vol_interaction": rsi_vol_interaction,
            "vol_regime": vol_regime,
        }
    )

    return df


def compute_fibonacci_features(candles: pd.DataFrame) -> pd.DataFrame:
    fib_config = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    fib_df = calculate_fibonacci_features_vectorized(candles, fib_config)
    return fib_df[
        [
            "fib_prox_score",
            "fib05_prox_atr",
        ]
    ].copy()


def compute_combos(
    base_df: pd.DataFrame, fib_df: pd.DataFrame, candles: pd.DataFrame, timeframe: str
) -> pd.DataFrame:
    EMA_PARAMS = {"30m": (50, 20), "1h": (20, 5)}
    ema_period, lookback = EMA_PARAMS.get(timeframe, (20, 5))

    ema = candles["close"].ewm(span=ema_period, adjust=False).mean()
    ema_slope = ((ema - ema.shift(lookback)) / ema.shift(lookback)).fillna(0.0).clip(-0.10, 0.10)

    high = candles["high"]
    low = candles["low"]
    close = candles["close"]

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.DataFrame({"tr1": tr1, "tr2": tr2, "tr3": tr3}).max(axis=1)
    atr = tr.rolling(window=14).mean().replace(0, np.nan)
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    plus_di = 100 * pd.Series(plus_dm).rolling(window=14).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(window=14).mean() / atr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(window=14).mean().fillna(25.0) / 100.0

    rsi_raw = calculate_rsi_vectorized(close)
    rsi_inv = (rsi_raw - 50.0) / 50.0

    combos = pd.DataFrame(
        {
            "fib05_x_ema_slope": fib_df["fib05_prox_atr"] * ema_slope,
            "fib_prox_x_adx": fib_df["fib_prox_score"] * adx,
            "fib05_x_rsi_inv": fib_df["fib05_prox_atr"] * (-rsi_inv),
        }
    )
    combos["fib05_x_ema_slope"] = combos["fib05_x_ema_slope"].clip(-0.10, 0.10)
    combos["fib_prox_x_adx"] = combos["fib_prox_x_adx"].clip(0.0, 1.0)
    combos["fib05_x_rsi_inv"] = combos["fib05_x_rsi_inv"].clip(-1.0, 1.0)
    return combos


def compute_v18(symbol: str, timeframe: str) -> pd.DataFrame:
    candles_path = get_candles_path(symbol, timeframe)
    candles = pd.read_parquet(candles_path)

    base = compute_base_features(candles)
    fib = compute_fibonacci_features(candles)
    combos = compute_combos(base, fib, candles, timeframe)

    merged = pd.concat([base, fib, combos], axis=1)
    return merged[ALL_COLUMNS]


def save_v18(features: pd.DataFrame, symbol: str, timeframe: str):
    curated_dir = Path("data/curated/v1/features") / symbol / timeframe / "v18"
    curated_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    feather_path = curated_dir / f"{symbol}_{timeframe}_features_v18_{timestamp}.feather"
    metadata_path = feather_path.with_suffix(".json")
    features.reset_index(drop=True).to_feather(feather_path)
    metadata = {
        "symbol": symbol,
        "timeframe": timeframe,
        "version": "v18",
        "columns": ALL_COLUMNS[1:],
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": str(feather_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))
    print(f"[SAVED] {feather_path}")


def main():
    parser = argparse.ArgumentParser(description="Precompute v18 compact features")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    args = parser.parse_args()

    features = compute_v18(args.symbol, args.timeframe)
    save_v18(features, args.symbol, args.timeframe)


if __name__ == "__main__":
    main()
