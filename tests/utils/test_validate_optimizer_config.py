from __future__ import annotations

from scripts.validate.validate_optimizer_config import (
    normalize_champion_payload,
    validate_optimizer_strategy_family,
)


def test_normalize_champion_payload_prefers_cfg() -> None:
    payload = {
        "cfg": {"risk": {"risk_map": [[0.48, 0.01]]}, "thresholds": {"entry_conf_overall": 0.3}},
        "parameters": {"risk": {"risk_map": [[0.48, 0.99]]}},
        "merged_config": {"risk": {"risk_map": [[0.48, 0.88]]}},
    }
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.01]]


def test_normalize_champion_payload_uses_parameters_when_present() -> None:
    payload = {"parameters": {"risk": {"risk_map": [[0.48, 0.02]]}}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.02]]


def test_normalize_champion_payload_uses_merged_config_when_present() -> None:
    payload = {"merged_config": {"risk": {"risk_map": [[0.48, 0.03]]}}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.03]]


def test_normalize_champion_payload_falls_back_to_payload() -> None:
    payload = {"risk": {"risk_map": [[0.48, 0.04]]}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.04]]


def test_validate_optimizer_strategy_family_accepts_matching_ri_cluster() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            },
            "thresholds.signal_adaptation.atr_period": {"type": "fixed", "value": 14},
            "gates.hysteresis_steps": {"type": "fixed", "value": 3},
            "gates.cooldown_bars": {"type": "fixed", "value": 2},
            "thresholds.entry_conf_overall": {"type": "fixed", "value": 0.25},
            "thresholds.regime_proba.balanced": {"type": "fixed", "value": 0.36},
            "thresholds.signal_adaptation.zones.low.entry_conf_overall": {
                "type": "fixed",
                "value": 0.16,
            },
            "thresholds.signal_adaptation.zones.low.regime_proba": {"type": "fixed", "value": 0.33},
            "thresholds.signal_adaptation.zones.mid.entry_conf_overall": {
                "type": "fixed",
                "value": 0.40,
            },
            "thresholds.signal_adaptation.zones.mid.regime_proba": {"type": "fixed", "value": 0.51},
            "thresholds.signal_adaptation.zones.high.entry_conf_overall": {
                "type": "fixed",
                "value": 0.32,
            },
            "thresholds.signal_adaptation.zones.high.regime_proba": {
                "type": "fixed",
                "value": 0.57,
            },
        },
    }

    errors, warnings = validate_optimizer_strategy_family(opt_cfg)

    assert errors == []
    assert warnings == []


def test_validate_optimizer_strategy_family_rejects_legacy_with_regime_module() -> None:
    opt_cfg = {
        "strategy_family": "legacy",
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            },
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("strategy_family=legacy" in error for error in errors)


def test_validate_optimizer_strategy_family_requires_explicit_family() -> None:
    opt_cfg = {"parameters": {}}

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("obligatoriskt" in error for error in errors)


def test_validate_optimizer_strategy_family_rejects_non_exact_ri_authority() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "grid",
                "values": ["legacy", "regime_module"],
            },
            "thresholds.signal_adaptation.atr_period": {"type": "fixed", "value": 14},
            "gates.hysteresis_steps": {"type": "fixed", "value": 3},
            "gates.cooldown_bars": {"type": "fixed", "value": 2},
            "thresholds.entry_conf_overall": {"type": "fixed", "value": 0.25},
            "thresholds.regime_proba.balanced": {"type": "fixed", "value": 0.36},
            "thresholds.signal_adaptation.zones.low.entry_conf_overall": {
                "type": "fixed",
                "value": 0.16,
            },
            "thresholds.signal_adaptation.zones.low.regime_proba": {"type": "fixed", "value": 0.33},
            "thresholds.signal_adaptation.zones.mid.entry_conf_overall": {
                "type": "fixed",
                "value": 0.40,
            },
            "thresholds.signal_adaptation.zones.mid.regime_proba": {"type": "fixed", "value": 0.51},
            "thresholds.signal_adaptation.zones.high.entry_conf_overall": {
                "type": "fixed",
                "value": 0.32,
            },
            "thresholds.signal_adaptation.zones.high.regime_proba": {
                "type": "fixed",
                "value": 0.57,
            },
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("fixed regime_module" in error for error in errors)
