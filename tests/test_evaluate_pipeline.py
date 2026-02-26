from __future__ import annotations

from typing import Any

from core.strategy.evaluate import _volume_score_from_candles, evaluate_pipeline


def test_evaluate_pipeline_returns_meta(
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    result, meta = evaluate_pipeline(
        small_candle_history, policy=sample_policy, configs=sample_configs
    )

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


def test_volume_score_cap_ratio_below_one_does_not_penalize_normal_volume() -> None:
    candles = {"volume": [100.0] * 60}

    score = _volume_score_from_candles(candles, window=50, cap_ratio=0.5)

    assert score == 1.0
