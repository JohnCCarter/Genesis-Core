from __future__ import annotations

import math

import pandas as pd
import pytest

import core.strategy.features_asof as features_asof
from core.indicators.adx import calculate_adx
from core.indicators.atr import calculate_atr
from core.indicators.bollinger import bollinger_bands
from core.indicators.ema import calculate_ema
from core.indicators.fibonacci import FibonacciConfig, detect_swing_points
from core.indicators.rsi import calculate_rsi
from core.utils.diffing.feature_cache import IndicatorCache


def _make_candles(length: int = 260) -> dict[str, list[float]]:
    close: list[float] = []
    open_: list[float] = []
    high: list[float] = []
    low: list[float] = []
    volume: list[float] = []

    for idx in range(length):
        base = 100.0 + (idx * 0.08)
        wave = math.sin(idx / 6.0) * 3.0 + math.cos(idx / 17.0) * 1.2
        close_price = base + wave
        open_price = close_price + (0.35 if idx % 2 == 0 else -0.35)
        high_price = max(open_price, close_price) + 0.9 + ((idx % 5) * 0.03)
        low_price = min(open_price, close_price) - 0.9 - (((idx + 2) % 5) * 0.03)

        close.append(close_price)
        open_.append(open_price)
        high.append(high_price)
        low.append(low_price)
        volume.append(1000.0 + (idx * 5.0))

    return {
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }


def _mutate_future_bars(
    candles: dict[str, list[float]],
    *,
    start_idx: int,
) -> dict[str, list[float]]:
    mutated = {key: list(values) for key, values in candles.items()}

    for idx in range(start_idx, len(mutated["close"])):
        close_price = mutated["close"][idx] + 25.0 + math.sin(idx / 3.0)
        open_price = close_price + (0.8 if idx % 2 == 0 else -0.8)
        high_price = max(open_price, close_price) + 1.5
        low_price = min(open_price, close_price) - 1.5

        mutated["open"][idx] = open_price
        mutated["high"][idx] = high_price
        mutated["low"][idx] = low_price
        mutated["close"][idx] = close_price
        mutated["volume"][idx] = mutated["volume"][idx] + 5000.0 + idx

    return mutated


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

    fib_cfg = FibonacciConfig(atr_depth=3.0, max_swings=max(1, len(closes)), min_swings=1)
    sh_idx, sl_idx, sh_px, sl_px = detect_swing_points(
        pd.Series(highs),
        pd.Series(lows),
        pd.Series(closes),
        fib_cfg,
    )
    pre["fib_high_idx"] = [int(value) for value in sh_idx]
    pre["fib_low_idx"] = [int(value) for value in sl_idx]
    pre["fib_high_px"] = [float(value) for value in sh_px]
    pre["fib_low_px"] = [float(value) for value in sl_px]

    return pre


def _assert_feature_dicts_close(
    expected: dict[str, float],
    actual: dict[str, float],
    *,
    rel: float = 1e-9,
    abs_tol: float = 1e-9,
) -> None:
    assert set(expected) == set(actual)

    for key in sorted(expected):
        expected_value = expected[key]
        actual_value = actual[key]
        assert math.isfinite(float(expected_value)), f"Expected non-finite feature {key}"
        assert math.isfinite(float(actual_value)), f"Actual non-finite feature {key}"
        assert actual_value == pytest.approx(expected_value, rel=rel, abs=abs_tol), key


def _run_with_fresh_caches(fn):
    original_indicator_cache = features_asof._indicator_cache
    original_warn_once = features_asof._PRECOMPUTE_WARN_ONCE
    try:
        features_asof._feature_cache.clear()
        features_asof._indicator_cache = IndicatorCache(max_size=2048)
        features_asof._PRECOMPUTE_WARN_ONCE = False
        return fn()
    finally:
        features_asof._feature_cache.clear()
        features_asof._indicator_cache = original_indicator_cache
        features_asof._PRECOMPUTE_WARN_ONCE = original_warn_once


def test_extract_features_backtest_is_prefix_invariant_to_future_bar_mutation(monkeypatch) -> None:
    candles = _make_candles(260)
    asof_bar = 180
    mutated = _mutate_future_bars(candles, start_idx=asof_bar + 1)
    monkeypatch.delenv("GENESIS_PRECOMPUTE_FEATURES", raising=False)

    def _extract(source: dict[str, list[float]]) -> dict[str, float]:
        features, _ = features_asof.extract_features_backtest(
            source,
            asof_bar,
            timeframe="3h",
            symbol="tBTCUSD",
        )
        return features

    base_features = _run_with_fresh_caches(lambda: _extract(candles))
    mutated_features = _run_with_fresh_caches(lambda: _extract(mutated))

    _assert_feature_dicts_close(base_features, mutated_features)


def test_extract_features_backtest_remapped_precompute_is_prefix_invariant_on_fast_window(
    monkeypatch,
) -> None:
    candles = _make_candles(260)
    global_idx = 230
    mutated = _mutate_future_bars(candles, start_idx=global_idx + 1)
    precomputed = _build_precomputed(candles)
    mutated_precomputed = _build_precomputed(mutated)
    window_size = 200
    window_start_idx = max(0, global_idx - window_size + 1)
    candles_window = {
        key: list(values[window_start_idx : global_idx + 1]) for key, values in candles.items()
    }
    local_asof_bar = len(candles_window["close"]) - 1

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

    precompute_features = _run_with_fresh_caches(
        lambda: features_asof.extract_features_backtest(
            candles_window,
            local_asof_bar,
            timeframe="3h",
            symbol="tBTCUSD",
            config={
                "_global_index": global_idx,
                "precomputed_features": precomputed,
            },
        )[0]
    )

    mutated_precompute_features = _run_with_fresh_caches(
        lambda: features_asof.extract_features_backtest(
            candles_window,
            local_asof_bar,
            timeframe="3h",
            symbol="tBTCUSD",
            config={
                "_global_index": global_idx,
                "precomputed_features": mutated_precomputed,
            },
        )[0]
    )

    _assert_feature_dicts_close(precompute_features, mutated_precompute_features)


def test_extract_features_backtest_fast_window_matches_full_runtime_on_same_global_bar(
    monkeypatch,
) -> None:
    candles = _make_candles(260)
    global_idx = 230
    precomputed = _build_precomputed(candles)
    window_size = 200
    window_start_idx = max(0, global_idx - window_size + 1)
    candles_window = {
        key: list(values[window_start_idx : global_idx + 1]) for key, values in candles.items()
    }
    local_asof_bar = len(candles_window["close"]) - 1

    monkeypatch.delenv("GENESIS_PRECOMPUTE_FEATURES", raising=False)
    runtime_features = _run_with_fresh_caches(
        lambda: features_asof.extract_features_backtest(
            candles,
            global_idx,
            timeframe="3h",
            symbol="tBTCUSD",
        )[0]
    )

    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")
    fast_window_features = _run_with_fresh_caches(
        lambda: features_asof.extract_features_backtest(
            candles_window,
            local_asof_bar,
            timeframe="3h",
            symbol="tBTCUSD",
            config={
                "_global_index": global_idx,
                "precomputed_features": precomputed,
            },
        )[0]
    )

    _assert_feature_dicts_close(
        runtime_features,
        fast_window_features,
        rel=1e-6,
        abs_tol=1e-6,
    )
