#!/usr/bin/env python3
"""
Parity test between runtime feature pipeline (_extract_asof) and
precomputed v17 feature files.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.strategy.features_asof import extract_features_backtest

MODEL_FEATURE_COLUMNS: tuple[str, ...] = (
    "rsi_inv_lag1",
    "volatility_shift_ma3",
    "bb_position_inv_ma3",
    "rsi_vol_interaction",
    "vol_regime",
    "fib05_prox_atr",
    "fib_prox_score",
    "fib05_x_ema_slope",
    "fib_prox_x_adx",
    "fib05_x_rsi_inv",
)


def _load_candles(path: Path) -> dict[str, list[float]]:
    df = pd.read_parquet(path)
    required = ["open", "high", "low", "close", "volume", "timestamp"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Candle file missing columns: {missing}")
    return {col: df[col].tolist() for col in required}


def _compute_runtime_features(
    candles: dict[str, list[float]], timeframe: str, symbol: str, min_asof: int
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    total_bars = len(candles["close"])
    for asof_bar in range(min_asof, total_bars):
        feats, _ = extract_features_backtest(candles, asof_bar, timeframe=timeframe, symbol=symbol)
        if not feats:
            continue
        feats["timestamp"] = candles["timestamp"][asof_bar]
        rows.append(feats)
    return pd.DataFrame(rows)


@pytest.mark.parametrize(
    "candles_path,features_path,timeframe",
    [
        (
            Path("tests/data/tBTCUSD_1h_sample.parquet"),
            Path("tests/data/tBTCUSD_1h_features_v17.parquet"),
            "1h",
        )
    ],
)
def test_runtime_vs_precomputed_features(candles_path: Path, features_path: Path, timeframe: str):
    symbol = "tBTCUSD"
    candles = _load_candles(candles_path)
    features_pre = pd.read_parquet(features_path)

    # Skip first ~60 bars to ensure indicators have warmup.
    runtime_df = _compute_runtime_features(candles, timeframe=timeframe, symbol=symbol, min_asof=60)
    assert not runtime_df.empty, "Runtime feature dataframe is empty"

    # Align on timestamp (inner join).
    merged = runtime_df.merge(
        features_pre,
        on="timestamp",
        how="inner",
        suffixes=("_runtime", "_pre"),
    )
    assert not merged.empty, "No overlapping timestamps between runtime and precomputed features"

    runtime_cols = {col[:-8] for col in merged.columns if col.endswith("_runtime")}
    precomputed_cols = {col[:-4] for col in merged.columns if col.endswith("_pre")}
    column_candidates = runtime_cols & precomputed_cols
    common_columns = sorted(column_candidates & set(MODEL_FEATURE_COLUMNS))
    assert common_columns, "No shared feature columns to compare"

    for col in common_columns:
        runtime_vals = merged[f"{col}_runtime"].to_numpy()
        pre_vals = merged[f"{col}_pre"].to_numpy()

        assert not np.isnan(runtime_vals).any(), f"Runtime NaN detected in {col}"
        assert not np.isnan(pre_vals).any(), f"Precomputed NaN detected in {col}"
        assert not np.isinf(runtime_vals).any(), f"Runtime inf detected in {col}"
        assert not np.isinf(pre_vals).any(), f"Precomputed inf detected in {col}"

        np.testing.assert_allclose(
            runtime_vals,
            pre_vals,
            rtol=1e-9,
            atol=1e-9,
            err_msg=f"Feature mismatch for {col}",
        )
