from __future__ import annotations

from typing import Any

from core.strategy.evaluate import evaluate_pipeline


def test_evaluate_pipeline_returns_meta(
    sample_policy: dict[str, Any], sample_configs: dict[str, Any], small_candle_history: dict[str, Any]
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
