from __future__ import annotations

import pytest

import core.strategy.features_asof as features_asof
from core.strategy.features_asof_parts.indicator_state_utils import build_indicator_state


def _make_candles(length: int = 90) -> tuple[list[float], list[float], list[float]]:
    closes = [100.0 + (i * 0.2) + (0.15 if i % 3 == 0 else -0.05) for i in range(length)]
    highs = [value + 0.5 for value in closes]
    lows = [value - 0.5 for value in closes]
    return highs, lows, closes


def _raise_unexpected(name: str):
    def _inner(*_args, **_kwargs):
        raise AssertionError(f"Unexpected slow-path call: {name}")

    return _inner


def test_build_indicator_state_uses_precomputed_fast_paths() -> None:
    highs, lows, closes = _make_candles(90)
    pre_idx = 60
    pre = {
        "rsi_14": [float(i) for i in range(120)],
        "bb_position_20_2": [float(i) / 100.0 for i in range(120)],
        "atr_14": [float(i) / 10.0 for i in range(120)],
        "volatility_shift": [1.0 + (i / 100.0) for i in range(120)],
    }

    state = build_indicator_state(
        highs,
        lows,
        closes,
        60,
        pre,
        pre_idx,
        14,
        features_asof.make_indicator_fingerprint,
        lambda _key: None,
        lambda _key, _value: None,
        _raise_unexpected("calculate_rsi"),
        _raise_unexpected("bollinger_bands"),
        _raise_unexpected("calculate_atr"),
        _raise_unexpected("calculate_volatility_shift"),
    )

    assert state.rsi_used_fast_path is True
    assert state.rsi_current_raw == 60.0
    assert state.rsi_lag1_raw == 59.0
    assert state.bb_last_3 == [0.58, 0.59, 0.6]
    assert state.atr14_current == 6.0
    assert state.atr_window_56[0] == 0.5
    assert state.atr_window_56[-1] == 6.0
    assert state.vol_shift_last_3 == pytest.approx([1.58, 1.59, 1.6])
    assert state.vol_shift_current == 1.6


def test_build_indicator_state_keeps_true_atr14_when_period_differs() -> None:
    highs, lows, closes = _make_candles(90)
    pre_idx = 60
    pre = {
        "rsi_14": [float(i) for i in range(120)],
        "bb_position_20_2": [float(i) / 100.0 for i in range(120)],
        "atr_21": [float(i) / 10.0 for i in range(120)],
        "atr_14": [float(i) / 20.0 for i in range(120)],
        "volatility_shift": [1.0 + (i / 100.0) for i in range(120)],
    }

    state = build_indicator_state(
        highs,
        lows,
        closes,
        60,
        pre,
        pre_idx,
        21,
        features_asof.make_indicator_fingerprint,
        lambda _key: None,
        lambda _key, _value: None,
        _raise_unexpected("calculate_rsi"),
        _raise_unexpected("bollinger_bands"),
        _raise_unexpected("calculate_atr"),
        _raise_unexpected("calculate_volatility_shift"),
    )

    assert state.atr_vals is not None
    assert float(state.atr_vals[-1]) == 6.0
    assert state.atr14_current == 3.0


def test_build_indicator_state_uses_slow_rsi_path_when_precomputed_rsi_missing() -> None:
    highs, lows, closes = _make_candles(90)
    pre_idx = 60
    pre = {
        "bb_position_20_2": [float(i) / 100.0 for i in range(120)],
        "atr_14": [float(i) / 10.0 for i in range(120)],
        "volatility_shift": [1.0 + (i / 100.0) for i in range(120)],
    }
    fake_rsi = [50.0 + (i / 10.0) for i in range(61)]

    state = build_indicator_state(
        highs,
        lows,
        closes,
        60,
        pre,
        pre_idx,
        14,
        features_asof.make_indicator_fingerprint,
        lambda _key: None,
        lambda _key, _value: None,
        lambda _closes, period: fake_rsi,
        _raise_unexpected("bollinger_bands"),
        _raise_unexpected("calculate_atr"),
        _raise_unexpected("calculate_volatility_shift"),
    )

    assert state.rsi_used_fast_path is False
    assert state.rsi_current_raw == fake_rsi[-1]
    assert state.rsi_lag1_raw == fake_rsi[-2]


def test_build_indicator_state_builds_volatility_shift_from_atr_fallback() -> None:
    highs, lows, closes = _make_candles(90)
    pre_idx = 60
    pre = {
        "rsi_14": [float(i) for i in range(120)],
        "bb_position_20_2": [float(i) / 100.0 for i in range(120)],
        "atr_14": [1.0 + (i / 100.0) for i in range(120)],
        "atr_50": [1.5 + (i / 100.0) for i in range(120)],
    }
    fake_vol_shift = [1.2 + (i / 100.0) for i in range(61)]

    state = build_indicator_state(
        highs,
        lows,
        closes,
        60,
        pre,
        pre_idx,
        14,
        features_asof.make_indicator_fingerprint,
        lambda _key: None,
        lambda _key, _value: None,
        _raise_unexpected("calculate_rsi"),
        _raise_unexpected("bollinger_bands"),
        _raise_unexpected("calculate_atr"),
        lambda atr_short, atr_long: fake_vol_shift,
    )

    assert state.atr_vals is not None
    assert len(state.atr_vals) == 61
    assert state.vol_shift_last_3 == pytest.approx(fake_vol_shift[-3:])
    assert state.vol_shift_current == pytest.approx(fake_vol_shift[-1])


def test_extract_features_backtest_keeps_counter_accounting_in_features_asof() -> None:
    highs, lows, closes = _make_candles(90)
    candles = {
        "open": [value - 0.1 for value in closes],
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0 + i for i in range(len(closes))],
    }
    precomputed = {
        "rsi_14": [55.0 + (i / 10.0) for i in range(120)],
        "bb_position_20_2": [0.5 for _ in range(120)],
        "atr_14": [1.0 + (i / 100.0) for i in range(120)],
        "atr_50": [1.5 + (i / 100.0) for i in range(120)],
        "volatility_shift": [1.1 for _ in range(120)],
    }

    features_asof._feature_cache.clear()
    features_asof.get_feature_hit_counts()
    features_asof.extract_features_backtest(
        candles,
        60,
        config={"precomputed_features": precomputed},
    )
    assert features_asof.get_feature_hit_counts() == (1, 0)

    features_asof._feature_cache.clear()
    features_asof.get_feature_hit_counts()
    features_asof.extract_features_backtest(candles, 61, config={})
    assert features_asof.get_feature_hit_counts() == (0, 1)
