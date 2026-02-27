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
    result_shadow_bull, meta_shadow_bull = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )

    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", _shadow_bear)
    result_shadow_bear, meta_shadow_bear = ev.evaluate_pipeline(
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

    shadow_obs_bull = meta_shadow_bull["observability"]["shadow_regime"]
    shadow_obs_bear = meta_shadow_bear["observability"]["shadow_regime"]

    assert shadow_obs_bull["authority"] == "ranging"
    assert shadow_obs_bear["authority"] == "ranging"
    assert shadow_obs_bull["shadow"] == "bull"
    assert shadow_obs_bear["shadow"] == "bear"
    assert shadow_obs_bull["mismatch"] is True
    assert shadow_obs_bear["mismatch"] is True
    assert shadow_obs_bull["decision_input"] is False
    assert shadow_obs_bear["decision_input"] is False
    assert shadow_obs_bull["authority_mode"] == "legacy"
    assert shadow_obs_bear["authority_mode"] == "legacy"


def test_evaluate_pipeline_authority_mode_legacy_off_parity(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")

    base_configs = deepcopy(sample_configs)
    base_configs.pop("precomputed_features", None)
    base_configs.pop("_global_index", None)
    base_configs.setdefault("multi_timeframe", {})

    explicit_legacy_configs = deepcopy(base_configs)
    explicit_legacy_configs["multi_timeframe"]["regime_intelligence"] = {"authority_mode": "legacy"}

    result_off, meta_off = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )
    result_legacy, meta_legacy = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(explicit_legacy_configs),
    )

    assert {
        "action": result_off["action"],
        "confidence": result_off["confidence"],
        "regime": result_off["regime"],
    } == {
        "action": result_legacy["action"],
        "confidence": result_legacy["confidence"],
        "regime": result_legacy["regime"],
    }
    assert meta_off["observability"]["shadow_regime"]["authority_mode"] == "legacy"
    assert meta_legacy["observability"]["shadow_regime"]["authority_mode"] == "legacy"


def test_evaluate_pipeline_invalid_authority_mode_falls_back_to_legacy_with_default_parity(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")

    base_configs = deepcopy(sample_configs)
    base_configs.pop("precomputed_features", None)
    base_configs.pop("_global_index", None)
    base_configs.setdefault("multi_timeframe", {})

    invalid_mode_configs = deepcopy(base_configs)
    invalid_mode_configs["multi_timeframe"]["regime_intelligence"] = {
        "authority_mode": "invalid_mode_xyz"
    }

    result_default, meta_default = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )
    result_invalid, meta_invalid = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(invalid_mode_configs),
    )

    assert {
        "action": result_default["action"],
        "confidence": result_default["confidence"],
        "regime": result_default["regime"],
    } == {
        "action": result_invalid["action"],
        "confidence": result_invalid["confidence"],
        "regime": result_invalid["regime"],
    }
    assert meta_default["observability"]["shadow_regime"]["authority_mode"] == "legacy"
    assert meta_invalid["observability"]["shadow_regime"]["authority_mode"] == "legacy"


def test_evaluate_pipeline_authority_mode_regime_module_is_deterministic(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "bear")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = deepcopy(sample_configs)
    cfg.setdefault("multi_timeframe", {})["regime_intelligence"] = {
        "authority_mode": "regime_module"
    }

    result_a, meta_a = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(cfg),
    )
    result_b, meta_b = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(cfg),
    )

    assert result_a["regime"] == "bull"
    assert result_b["regime"] == "bull"
    assert {
        "action": result_a["action"],
        "confidence": result_a["confidence"],
        "regime": result_a["regime"],
    } == {
        "action": result_b["action"],
        "confidence": result_b["confidence"],
        "regime": result_b["regime"],
    }
    shadow_obs_a = meta_a["observability"]["shadow_regime"]
    shadow_obs_b = meta_b["observability"]["shadow_regime"]
    assert shadow_obs_a["authority_mode"] == "regime_module"
    assert shadow_obs_b["authority_mode"] == "regime_module"
    assert shadow_obs_a["authoritative_source"] == "regime.detect_regime_from_candles"
    assert shadow_obs_b["authoritative_source"] == "regime.detect_regime_from_candles"
    assert shadow_obs_a["decision_input"] is False
    assert shadow_obs_b["decision_input"] is False


def test_evaluate_pipeline_authority_mode_alias_only_is_deterministic(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "bear")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = deepcopy(sample_configs)
    cfg.pop("precomputed_features", None)
    cfg.pop("_global_index", None)
    cfg["regime_unified"] = {"authority_mode": "regime_module"}

    result_a, meta_a = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(cfg),
    )
    result_b, meta_b = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(cfg),
    )

    assert result_a["regime"] == "bull"
    assert result_b["regime"] == "bull"
    assert {
        "action": result_a["action"],
        "confidence": result_a["confidence"],
        "regime": result_a["regime"],
    } == {
        "action": result_b["action"],
        "confidence": result_b["confidence"],
        "regime": result_b["regime"],
    }
    shadow_obs_a = meta_a["observability"]["shadow_regime"]
    shadow_obs_b = meta_b["observability"]["shadow_regime"]
    assert shadow_obs_a["authority_mode"] == "regime_module"
    assert shadow_obs_b["authority_mode"] == "regime_module"
    assert shadow_obs_a["authority_mode_source"] == "regime_unified.authority_mode"
    assert shadow_obs_b["authority_mode_source"] == "regime_unified.authority_mode"
    assert shadow_obs_a["decision_input"] is False
    assert shadow_obs_b["decision_input"] is False


def test_evaluate_pipeline_authority_mode_conflict_canonical_wins(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = deepcopy(sample_configs)
    cfg.pop("precomputed_features", None)
    cfg.pop("_global_index", None)
    cfg.setdefault("multi_timeframe", {})["regime_intelligence"] = {"authority_mode": "legacy"}
    cfg["regime_unified"] = {"authority_mode": "regime_module"}

    result, meta = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=cfg,
    )

    assert result["regime"] == "ranging"
    shadow_obs = meta["observability"]["shadow_regime"]
    assert shadow_obs["authority_mode"] == "legacy"
    assert (
        shadow_obs["authority_mode_source"] == "multi_timeframe.regime_intelligence.authority_mode"
    )
    assert shadow_obs["authoritative_source"] == "regime_unified.detect_regime_unified"


def test_evaluate_pipeline_canonical_invalid_alias_valid_falls_back_to_legacy(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = deepcopy(sample_configs)
    cfg.pop("precomputed_features", None)
    cfg.pop("_global_index", None)
    cfg.setdefault("multi_timeframe", {})["regime_intelligence"] = {
        "authority_mode": "invalid_mode_xyz"
    }
    cfg["regime_unified"] = {"authority_mode": "regime_module"}

    result, meta = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=cfg,
    )

    assert result["regime"] == "ranging"
    shadow_obs = meta["observability"]["shadow_regime"]
    assert shadow_obs["authority_mode"] == "legacy"
    assert shadow_obs["authority_mode_source"] == "canonical_invalid_fallback_legacy"
    assert shadow_obs["authoritative_source"] == "regime_unified.detect_regime_unified"
    assert shadow_obs["decision_input"] is False


def test_evaluate_pipeline_shadow_error_rate_contract(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    """T8A executable attestation for deterministic shadow mismatch rate.

    Contract:
    - rate must be deterministic for fixed input/observer sequence,
    - rate must remain bounded in [0,1].
    """

    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")

    shadow_sequence = ["ranging", "bull", "ranging", "bear"]

    def _shadow_sequence(_candles: dict[str, Any]) -> str:
        if not shadow_sequence:
            raise AssertionError("shadow sequence exhausted unexpectedly")
        return shadow_sequence.pop(0)

    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", _shadow_sequence)

    cfg = deepcopy(sample_configs)
    cfg.pop("precomputed_features", None)
    cfg.pop("_global_index", None)

    mismatches: list[bool] = []
    for _ in range(4):
        _result, meta = ev.evaluate_pipeline(
            small_candle_history,
            policy=sample_policy,
            configs=deepcopy(cfg),
        )
        mismatch = meta["observability"]["shadow_regime"]["mismatch"]
        assert isinstance(mismatch, bool)
        mismatches.append(mismatch)

    shadow_error_rate = sum(1 for m in mismatches if m) / len(mismatches)
    assert shadow_error_rate == 0.5
    assert 0.0 <= shadow_error_rate <= 1.0
