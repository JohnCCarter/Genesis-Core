from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

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


@pytest.mark.parametrize(
    "authority_mode",
    ["legacy", "invalid_mode_xyz"],
    ids=["explicit_legacy_matches_default", "invalid_mode_falls_back_to_legacy"],
)
def test_evaluate_pipeline_authority_mode_legacy_parity_cases(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
    authority_mode: str,
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")

    base_configs = deepcopy(sample_configs)
    base_configs.pop("precomputed_features", None)
    base_configs.pop("_global_index", None)
    base_configs.setdefault("multi_timeframe", {})

    configured_mode_configs = deepcopy(base_configs)
    configured_mode_configs["multi_timeframe"]["regime_intelligence"] = {
        "authority_mode": authority_mode
    }

    result_default, meta_default = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_configs),
    )
    result_configured, meta_configured = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(configured_mode_configs),
    )

    assert {
        "action": result_default["action"],
        "confidence": result_default["confidence"],
        "regime": result_default["regime"],
    } == {
        "action": result_configured["action"],
        "confidence": result_configured["confidence"],
        "regime": result_configured["regime"],
    }
    assert meta_default["observability"]["shadow_regime"]["authority_mode"] == "legacy"
    assert meta_configured["observability"]["shadow_regime"]["authority_mode"] == "legacy"


@pytest.mark.parametrize(
    ("use_alias_only", "expected_source_key", "expected_source_value"),
    [
        (
            False,
            "authoritative_source",
            "regime.detect_regime_from_candles",
        ),
        (
            True,
            "authority_mode_source",
            "regime_unified.authority_mode",
        ),
    ],
    ids=["canonical_regime_intelligence", "alias_only_regime_unified"],
)
def test_evaluate_pipeline_authority_mode_regime_module_deterministic(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
    use_alias_only: bool,
    expected_source_key: str,
    expected_source_value: str,
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "bear")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = deepcopy(sample_configs)
    if use_alias_only:
        cfg.pop("precomputed_features", None)
        cfg.pop("_global_index", None)
        cfg["regime_unified"] = {"authority_mode": "regime_module"}
    else:
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
    assert shadow_obs_a[expected_source_key] == expected_source_value
    assert shadow_obs_b[expected_source_key] == expected_source_value
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


def test_evaluate_pipeline_authority_mode_source_invariant_contract(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    """T8B executable attestation for authority source invariants.

    Contract:
    - `authority_mode_source` must stay within the allowed deterministic set,
    - each fixed config scenario must resolve to an exact expected source.
    """

    from core.strategy import evaluate as ev
    from core.strategy import regime_intelligence as ri
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ri, "detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    allowed_sources = {
        "multi_timeframe.regime_intelligence.authority_mode",
        "regime_unified.authority_mode",
        "default_legacy",
        "canonical_invalid_fallback_legacy",
        "alias_invalid_fallback_legacy",
    }

    scenarios = [
        (
            "default",
            {},
            "default_legacy",
            "legacy",
        ),
        (
            "canonical_legacy",
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}}},
            "multi_timeframe.regime_intelligence.authority_mode",
            "legacy",
        ),
        (
            "alias_regime_module",
            {"regime_unified": {"authority_mode": "regime_module"}},
            "regime_unified.authority_mode",
            "regime_module",
        ),
        (
            "canonical_invalid_alias_valid",
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode_xyz"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            "canonical_invalid_fallback_legacy",
            "legacy",
        ),
        (
            "alias_invalid_only",
            {"regime_unified": {"authority_mode": "invalid_mode_xyz"}},
            "alias_invalid_fallback_legacy",
            "legacy",
        ),
    ]

    def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in override.items():
            if isinstance(merged.get(key), dict) and isinstance(value, dict):
                merged[key] = _merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged

    for _name, override_cfg, expected_source, expected_mode in scenarios:
        cfg = deepcopy(sample_configs)
        cfg.pop("precomputed_features", None)
        cfg.pop("_global_index", None)

        if isinstance(cfg.get("multi_timeframe"), dict):
            cfg["multi_timeframe"] = deepcopy(cfg["multi_timeframe"])
            cfg["multi_timeframe"].pop("regime_intelligence", None)
        cfg.pop("regime_unified", None)

        cfg = _merge(cfg, override_cfg)

        _result, meta = ev.evaluate_pipeline(
            small_candle_history,
            policy=sample_policy,
            configs=cfg,
        )
        shadow_obs = meta["observability"]["shadow_regime"]

        source = shadow_obs["authority_mode_source"]
        assert source in allowed_sources
        assert source == expected_source
        assert shadow_obs["authority_mode"] == expected_mode
        assert shadow_obs["decision_input"] is False


def test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "bull")
    monkeypatch.setattr(
        ev,
        "predict_proba_for",
        lambda *_a, **_k: ({"buy": 0.8, "sell": 0.2}, {"versions": {"proba": "stub"}}),
    )

    def _confidence_stub(
        _probas: dict[str, float],
        *,
        atr_pct: float | None = None,
        spread_bp: float | None = None,
        volume_score: float | None = None,
        data_quality: float | None = None,
        config: dict[str, Any] | None = None,
    ) -> tuple[dict[str, float], dict[str, Any]]:
        _ = (atr_pct, spread_bp, volume_score, data_quality)
        mode = "raw" if bool((config or {}).get("enabled") is False) else "scaled"
        return {"buy": 0.8, "sell": 0.2, "overall": 0.8}, {"mode": mode}

    monkeypatch.setattr(ev, "compute_confidence", _confidence_stub)

    cfg_base = deepcopy(sample_configs)
    cfg_base.pop("precomputed_features", None)
    cfg_base.pop("_global_index", None)
    cfg_base.setdefault("thresholds", {})["entry_conf_overall"] = 0.6
    cfg_base["thresholds"]["regime_proba"] = {"bull": 0.6, "balanced": 0.6}
    cfg_base.setdefault("ev", {})["R_default"] = 1.0
    cfg_base.setdefault("gates", {})["cooldown_bars"] = 0
    cfg_base["gates"]["hysteresis_steps"] = 1
    cfg_base.setdefault("risk", {})["risk_map"] = [[0.6, 1.0]]
    cfg_base["htf_fib"] = {"entry": {"enabled": False}}
    cfg_base["ltf_fib"] = {"entry": {"enabled": False}}
    cfg_base["quality"] = {"apply": "sizing_only"}
    cfg_base.setdefault("multi_timeframe", {})["use_htf_block"] = False

    cfg_off = deepcopy(cfg_base)
    cfg_off["multi_timeframe"]["regime_intelligence"] = {
        "enabled": False,
        "version": "v2",
        "clarity_score": {
            "enabled": True,
            "weights_version": "weights_v1",
            "weights_v1": {
                "confidence": 0.5,
                "edge": 0.2,
                "ev": 0.2,
                "regime_alignment": 0.1,
            },
            "size_multiplier_min": 0.5,
            "size_multiplier_max": 1.0,
        },
    }

    cfg_on = deepcopy(cfg_off)
    cfg_on["multi_timeframe"]["regime_intelligence"]["enabled"] = True

    result_off, meta_off = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=cfg_off,
    )
    result_on_1, meta_on_1 = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=cfg_on,
    )
    result_on_2, meta_on_2 = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=cfg_on,
    )

    assert result_off["action"] == result_on_1["action"] == result_on_2["action"] == "LONG"
    assert meta_off["decision"]["reasons"] == meta_on_1["decision"]["reasons"]
    assert meta_on_1["decision"]["reasons"] == meta_on_2["decision"]["reasons"]

    size_off = float(meta_off["decision"]["size"])
    size_on_1 = float(meta_on_1["decision"]["size"])
    size_on_2 = float(meta_on_2["decision"]["size"])
    assert size_on_1 == pytest.approx(size_on_2)
    assert size_on_1 < size_off

    state_off = meta_off["decision"]["state_out"]
    state_on = meta_on_1["decision"]["state_out"]
    assert state_off["ri_clarity_enabled"] is False
    assert state_on["ri_clarity_enabled"] is True
    assert state_on["ri_clarity_apply"] == "sizing_only"
    assert state_on["ri_clarity_round_policy"] == "half_even"
    assert isinstance(state_on["ri_clarity_score"], int)
    assert 0 <= state_on["ri_clarity_score"] <= 100
    assert state_on["size_after_ri_clarity"] == pytest.approx(size_on_1)
    assert state_on["size_before_ri_clarity"] > state_on["size_after_ri_clarity"]
