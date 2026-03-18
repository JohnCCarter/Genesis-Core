from __future__ import annotations

import pytest

from core.strategy.family_registry import (
    STRATEGY_FAMILY_LEGACY,
    STRATEGY_FAMILY_RI,
    StrategyFamilyValidationError,
    classify_strategy_family,
    inject_strategy_family,
    matches_ri_cluster,
    resolve_strategy_family,
    validate_cross_family_promotion,
)


def _ri_config(*, strategy_family: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "thresholds": {
            "entry_conf_overall": 0.25,
            "regime_proba": {"balanced": 0.36},
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                    "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                    "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                },
            },
        },
        "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
    }
    if strategy_family is not None:
        payload["strategy_family"] = strategy_family
    return payload


def test_classify_strategy_family_derives_legacy_when_ri_authority_absent() -> None:
    cfg = {"thresholds": {"entry_conf_overall": 0.6}, "gates": {"hysteresis_steps": 2}}

    assert classify_strategy_family(cfg) == STRATEGY_FAMILY_LEGACY
    assert inject_strategy_family(cfg)["strategy_family"] == STRATEGY_FAMILY_LEGACY


def test_resolve_strategy_family_requires_declared_family() -> None:
    with pytest.raises(StrategyFamilyValidationError, match="missing_strategy_family"):
        resolve_strategy_family({"thresholds": {"entry_conf_overall": 0.6}})


def test_resolve_strategy_family_accepts_declared_ri_when_cluster_matches() -> None:
    cfg = _ri_config(strategy_family="ri")

    assert matches_ri_cluster(cfg) is True
    assert resolve_strategy_family(cfg) == STRATEGY_FAMILY_RI
    assert inject_strategy_family(cfg)["strategy_family"] == STRATEGY_FAMILY_RI


def test_resolve_strategy_family_rejects_hybrid_regime_module_configs() -> None:
    cfg = _ri_config()
    cfg["gates"] = {"hysteresis_steps": 2, "cooldown_bars": 0}

    with pytest.raises(StrategyFamilyValidationError, match="hybrid_regime_module"):
        classify_strategy_family(cfg)


def test_resolve_strategy_family_rejects_declared_ri_with_wrong_gates() -> None:
    cfg = _ri_config(strategy_family="ri")
    cfg["gates"] = {"hysteresis_steps": 2, "cooldown_bars": 0}

    with pytest.raises(StrategyFamilyValidationError, match="ri_requires_canonical_gates"):
        resolve_strategy_family(cfg)


def test_resolve_strategy_family_rejects_declared_legacy_with_regime_module() -> None:
    with pytest.raises(StrategyFamilyValidationError, match="legacy_regime_module"):
        resolve_strategy_family(_ri_config(strategy_family="legacy"))


def test_resolve_strategy_family_rejects_legacy_with_ri_signature_markers() -> None:
    cfg = {
        "strategy_family": "legacy",
        "thresholds": {
            "entry_conf_overall": 0.25,
            "regime_proba": {"balanced": 0.36},
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                    "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                    "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                },
            },
        },
        "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
    }

    with pytest.raises(StrategyFamilyValidationError, match="legacy_hybrid_signature"):
        resolve_strategy_family(cfg)


def test_cross_family_promotion_requires_override_and_signoff() -> None:
    with pytest.raises(StrategyFamilyValidationError, match="cross_family_promotion"):
        validate_cross_family_promotion("legacy", "ri")

    validate_cross_family_promotion(
        "legacy",
        "ri",
        explicit_override=True,
        governance_signoff=True,
    )
