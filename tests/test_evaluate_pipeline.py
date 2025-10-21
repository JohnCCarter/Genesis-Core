from __future__ import annotations

from typing import Any

import pytest

from core.strategy.evaluate import evaluate_pipeline


@pytest.fixture()
def sample_policy() -> dict[str, Any]:
    return {"symbol": "tBTCUSD", "timeframe": "1h"}


@pytest.fixture()
def sample_configs() -> dict[str, Any]:
    return {"thresholds": {"entry_conf_overall": 0.5}}


def build_sample_candles() -> dict[str, Any]:
    closes = [50100.0, 50250.0, 50300.0]
    opens = [50000.0, 50100.0, 50200.0]
    highs = [50200.0, 50300.0, 50400.0]
    lows = [49800.0, 49950.0, 50050.0]
    volumes = [10.0, 8.0, 9.0]
    timestamps = [1700000000000, 1700003600000, 1700007200000]
    return {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "candles": list(zip(timestamps, opens, highs, lows, closes, volumes, strict=True)),
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


def test_evaluate_pipeline_returns_meta(
    sample_policy: dict[str, Any], sample_configs: dict[str, Any]
) -> None:
    candles = build_sample_candles()
    result, meta = evaluate_pipeline(candles, policy=sample_policy, configs=sample_configs)

    assert "features" in result
    assert "probas" in result
    assert "confidence" in result
    assert "regime" in result
    assert "action" in result

    assert "features" in meta
    assert "proba" in meta
    assert "confidence" in meta
    assert "regime" in meta
    assert "decision" in meta
    assert "champion" in meta
