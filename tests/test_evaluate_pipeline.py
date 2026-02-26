from __future__ import annotations

from copy import deepcopy
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


def test_evaluate_pipeline_shadow_regime_observer_preserves_default_parity(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    """Shadow observer from regime.py must not affect authority outputs.

    This guards T1 behavior: evaluate_pipeline may compute a shadow regime from
    regime.py, but action/confidence/regime must remain identical regardless of
    the shadow value because decision-path authority stays detect_regime_unified.
    """

    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")

    base_configs = deepcopy(sample_configs)
    base_configs.pop("precomputed_features", None)
    base_configs.pop("_global_index", None)

    observed_shadow_values: list[str] = []

    def _shadow_bull(_candles: dict[str, Any]) -> str:
        observed_shadow_values.append("bull")
        return "bull"

    def _shadow_bear(_candles: dict[str, Any]) -> str:
        observed_shadow_values.append("bear")
        return "bear"

    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", _shadow_bull)
    result_shadow_bull, _meta_shadow_bull = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )

    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", _shadow_bear)
    result_shadow_bear, _meta_shadow_bear = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )

    projection_bull = {
        "action": result_shadow_bull["action"],
        "confidence": result_shadow_bull["confidence"],
        "regime": result_shadow_bull["regime"],
    }
    projection_bear = {
        "action": result_shadow_bear["action"],
        "confidence": result_shadow_bear["confidence"],
        "regime": result_shadow_bear["regime"],
    }

    assert projection_bull == projection_bear
    assert projection_bull["regime"] == "ranging"
    assert observed_shadow_values == ["bull", "bear"]
