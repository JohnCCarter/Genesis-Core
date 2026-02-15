#!/usr/bin/env python3
"""
Validate that passing precomputed indicators into _extract_asof yields
identical features to running without precompute.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.ema import calculate_ema
from core.indicators.fibonacci import FibonacciConfig, detect_swing_points
from core.indicators.rsi import calculate_rsi
from core.indicators.vectorized import calculate_adx_vectorized
from core.strategy.features_asof import extract_features_backtest

SAMPLE_PATH = Path("tests/data/tBTCUSD_1h_sample.parquet")
SYMBOL = "tBTCUSD"
TIMEFRAME = "1h"
MIN_ASOF = 60


def _load_candles(path: Path) -> dict[str, list[float]]:
    df = pd.read_parquet(path)
    required = ["open", "high", "low", "close", "volume", "timestamp"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Candle file missing columns: {missing}")
    return {col: df[col].tolist() for col in required}


def _build_precomputed(candles: dict[str, list[float]]) -> dict[str, list[float]]:
    closes = candles["close"]
    highs = candles["high"]
    lows = candles["low"]

    pre: dict[str, list[float]] = {}
    pre["atr_14"] = calculate_atr(highs, lows, closes, period=14)
    pre["atr_50"] = calculate_atr(highs, lows, closes, period=50)
    pre["ema_20"] = calculate_ema(closes, period=20)
    pre["ema_50"] = calculate_ema(closes, period=50)
    pre["rsi_14"] = calculate_rsi(closes, period=14)
    bb = bollinger_bands(closes, period=20, std_dev=2.0)
    pre["bb_position_20_2"] = list(bb.get("position") or [])
    pre["adx_14"] = calculate_adx(highs, lows, closes, period=14)

    fib_cfg = FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)
    sh_idx, sl_idx, sh_px, sl_px = detect_swing_points(
        pd.Series(highs), pd.Series(lows), pd.Series(closes), fib_cfg
    )
    pre["fib_high_idx"] = [int(x) for x in sh_idx]
    pre["fib_low_idx"] = [int(x) for x in sl_idx]
    pre["fib_high_px"] = [float(x) for x in sh_px]
    pre["fib_low_px"] = [float(x) for x in sl_px]

    return pre


def _compute_feature_frame(
    candles: dict[str, list[float]],
    *,
    config: dict | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    total = len(candles["close"])
    for asof_bar in range(MIN_ASOF, total):
        feats, _ = extract_features_backtest(
            candles,
            asof_bar,
            timeframe=TIMEFRAME,
            symbol=SYMBOL,
            config=config,
        )
        if not feats:
            continue
        feats["timestamp"] = candles["timestamp"][asof_bar]
        rows.append(feats)
    return pd.DataFrame(rows)


def test_precompute_features_match_runtime():
    candles = _load_candles(SAMPLE_PATH)
    base_df = _compute_feature_frame(candles, config=None)
    assert not base_df.empty, "Runtime feature dataframe is empty"

    precomputed = _build_precomputed(candles)
    config = {"precomputed_features": precomputed}
    pre_df = _compute_feature_frame(candles, config=config)
    assert not pre_df.empty, "Precompute feature dataframe is empty"

    merged = base_df.merge(pre_df, on="timestamp", suffixes=("_runtime", "_pre"))
    assert not merged.empty, "No overlapping timestamps between runtime/precompute results"

    runtime_cols = {col[:-8] for col in merged.columns if col.endswith("_runtime")}
    precomputed_cols = {col[:-4] for col in merged.columns if col.endswith("_pre")}
    column_candidates = runtime_cols & precomputed_cols
    assert column_candidates, "No common columns to compare"

    for col in sorted(column_candidates):
        runtime_vals = merged[f"{col}_runtime"].to_numpy()
        pre_vals = merged[f"{col}_pre"].to_numpy()

        assert not np.isnan(runtime_vals).any(), f"Runtime NaN detected in {col}"
        assert not np.isnan(pre_vals).any(), f"Precompute NaN detected in {col}"
        assert not np.isinf(runtime_vals).any(), f"Runtime inf detected in {col}"
        assert not np.isinf(pre_vals).any(), f"Precompute inf detected in {col}"

        np.testing.assert_allclose(
            runtime_vals,
            pre_vals,
            rtol=1e-9,
            atol=1e-9,
            err_msg=f"Feature mismatch with precompute for {col}",
        )


def test_vectorized_adx_matches_reference_from_warmup() -> None:
    candles = _load_candles(SAMPLE_PATH)
    period = 14

    high = pd.Series(candles["high"], dtype=float)
    low = pd.Series(candles["low"], dtype=float)
    close = pd.Series(candles["close"], dtype=float)

    adx_vectorized = calculate_adx_vectorized(high, low, close, period=period).to_numpy(dtype=float)
    adx_reference = (
        np.asarray(
            calculate_adx(candles["high"], candles["low"], candles["close"], period=period),
            dtype=float,
        )
        / 100.0
    )

    assert len(adx_vectorized) == len(adx_reference)
    start_idx = 2 * period - 2
    np.testing.assert_allclose(
        adx_vectorized[start_idx:],
        adx_reference[start_idx:],
        rtol=1e-12,
        atol=1e-12,
        err_msg="Vectorized ADX diverges from reference Wilder ADX",
    )
