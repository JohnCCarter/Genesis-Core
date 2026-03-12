from __future__ import annotations

import numpy as np
import pytest

import core.strategy.features_asof as features_asof
from core.strategy.features_asof_parts.input_guard_utils import validate_input_or_return_early


@pytest.fixture(autouse=True)
def _clear_features_asof_result_cache() -> None:
    features_asof._feature_cache.clear()
    yield
    features_asof._feature_cache.clear()


def _synthetic_candles(*, n: int = 60, seed: int = 7) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    closes = (30_000.0 + np.cumsum(rng.normal(0, 15, size=n))).tolist()
    opens = [closes[0]] + closes[:-1]
    highs = (np.maximum(opens, closes) + 10.0).tolist()
    lows = (np.minimum(opens, closes) - 10.0).tolist()
    volume = (np.ones(n) * 100.0).tolist()
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    }


def test_validate_input_or_return_early_rejects_mismatched_ohlcv_lengths() -> None:
    candles = _synthetic_candles(n=55)
    candles["volume"] = candles["volume"][:-1]

    with pytest.raises(ValueError, match="All OHLCV lists must have same length"):
        validate_input_or_return_early(candles, 54)


@pytest.mark.parametrize(
    ("asof_bar", "message"),
    [
        (-1, r"asof_bar must be >= 0, got -1"),
        (60, r"asof_bar=60 >= total_bars=60"),
    ],
)
def test_validate_input_or_return_early_rejects_invalid_asof_bounds(
    asof_bar: int,
    message: str,
) -> None:
    candles = _synthetic_candles(n=60)

    with pytest.raises(ValueError, match=message):
        validate_input_or_return_early(candles, asof_bar)


def test_validate_input_or_return_early_returns_exact_insufficient_data_payload() -> None:
    candles = _synthetic_candles(n=60)

    total_bars, early_result = validate_input_or_return_early(candles, 20)

    assert total_bars == 60
    assert early_result == (
        {},
        {
            "versions": {},
            "reasons": ["INSUFFICIENT_DATA: asof_bar=20 < min_lookback=50"],
            "asof_bar": 20,
            "uses_bars": [0, 20],
        },
    )
    assert list(early_result[1].keys()) == ["versions", "reasons", "asof_bar", "uses_bars"]


def test_extract_asof_cache_hit_short_circuits_before_guard(monkeypatch) -> None:
    sentinel = ({"cached": 1.0}, {"meta": "cached"})

    def _explode_guard(*_args, **_kwargs):
        raise AssertionError("guard helper should not run on cache hit")

    monkeypatch.setattr(features_asof, "_feature_cache_lookup", lambda _cache_key: sentinel)
    monkeypatch.setattr(features_asof, "_validate_input_or_return_early_impl", _explode_guard)

    result = features_asof._extract_asof(_synthetic_candles(n=60), 55, timeframe="1h")

    assert result is sentinel


def test_extract_asof_insufficient_data_is_not_cached(monkeypatch) -> None:
    cache_calls: list[tuple[str, tuple[dict[str, float], dict[str, object]]]] = []

    def _record_cache_store(cache_key, result):
        cache_calls.append((cache_key, result))

    monkeypatch.setattr(features_asof, "_feature_cache_lookup", lambda _cache_key: None)
    monkeypatch.setattr(features_asof, "_feature_cache_store", _record_cache_store)

    result = features_asof._extract_asof(_synthetic_candles(n=60), 20, timeframe="1h")

    assert cache_calls == []
    assert result == (
        {},
        {
            "versions": {},
            "reasons": ["INSUFFICIENT_DATA: asof_bar=20 < min_lookback=50"],
            "asof_bar": 20,
            "uses_bars": [0, 20],
        },
    )
