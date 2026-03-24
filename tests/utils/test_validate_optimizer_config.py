from __future__ import annotations

import textwrap

import scripts.validate.validate_optimizer_config as validate_optimizer_config_module
from scripts.validate.validate_optimizer_config import (
    normalize_champion_payload,
    validate_config,
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
        "meta": {"runs": {"run_intent": "champion_freeze"}},
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
    assert any("run_intent=champion_freeze" in warning for warning in warnings)


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
        "meta": {"runs": {"run_intent": "research_slice"}},
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


def test_validate_optimizer_strategy_family_rejects_legacy_with_ri_signature_markers() -> None:
    opt_cfg = {
        "strategy_family": "legacy",
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "legacy",
            },
            "thresholds.signal_adaptation.atr_period": {"type": "fixed", "value": 14},
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("RI-signaturmarkörer" in error for error in errors)


def test_validate_optimizer_strategy_family_rejects_non_mapping_parameters() -> None:
    opt_cfg = {"strategy_family": "legacy", "parameters": []}

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("parameters måste vara en dict/mapping" in error for error in errors)


def test_validate_optimizer_strategy_family_accepts_ri_research_slice_gate_sweep() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "meta": {"runs": {"run_intent": "research_slice"}},
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            },
            "thresholds.signal_adaptation.atr_period": {"type": "fixed", "value": 14},
            "gates.hysteresis_steps": {"type": "int", "low": 2, "high": 4, "step": 1},
            "gates.cooldown_bars": {"type": "int", "low": 1, "high": 3, "step": 1},
            "thresholds.entry_conf_overall": {"type": "fixed", "value": 0.28},
            "thresholds.regime_proba.balanced": {"type": "fixed", "value": 0.36},
            "thresholds.signal_adaptation.zones.low.entry_conf_overall": {
                "type": "fixed",
                "value": 0.14,
            },
            "thresholds.signal_adaptation.zones.low.regime_proba": {"type": "fixed", "value": 0.32},
            "thresholds.signal_adaptation.zones.mid.entry_conf_overall": {
                "type": "fixed",
                "value": 0.42,
            },
            "thresholds.signal_adaptation.zones.mid.regime_proba": {"type": "fixed", "value": 0.52},
            "thresholds.signal_adaptation.zones.high.entry_conf_overall": {
                "type": "fixed",
                "value": 0.34,
            },
            "thresholds.signal_adaptation.zones.high.regime_proba": {
                "type": "fixed",
                "value": 0.58,
            },
        },
    }

    errors, warnings = validate_optimizer_strategy_family(opt_cfg)

    assert errors == []
    assert any("run_intent=research_slice" in warning for warning in warnings)


def test_validate_optimizer_strategy_family_rejects_missing_run_intent_for_ri() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            }
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("run_intent är obligatoriskt" in error for error in errors)


def test_validate_optimizer_strategy_family_rejects_unknown_run_intent_for_ri() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "meta": {"runs": {"run_intent": "mystery"}},
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            }
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("run_intent måste vara" in error for error in errors)


def test_validate_optimizer_strategy_family_rejects_non_canonical_ri_for_champion_freeze() -> None:
    opt_cfg = {
        "strategy_family": "ri",
        "meta": {"runs": {"run_intent": "champion_freeze"}},
        "parameters": {
            "multi_timeframe.regime_intelligence.authority_mode": {
                "type": "fixed",
                "value": "regime_module",
            },
            "thresholds.signal_adaptation.atr_period": {"type": "fixed", "value": 14},
            "gates.hysteresis_steps": {"type": "int", "low": 2, "high": 4, "step": 1},
            "gates.cooldown_bars": {"type": "int", "low": 1, "high": 3, "step": 1},
        },
    }

    errors, _warnings = validate_optimizer_strategy_family(opt_cfg)

    assert any("family_admission" in error for error in errors)


def test_validate_config_rejects_non_mapping_parameters_without_crashing(
    tmp_path,
    monkeypatch,
) -> None:
    cfg_path = tmp_path / "bad_optimizer.yaml"
    cfg_path.write_text(
        textwrap.dedent(
            """
            meta:
              symbol: tBTCUSD
              timeframe: 1h
            strategy_family: legacy
            parameters: []
            """
        ).strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_optimizer_config_module, "load_champion", lambda *_args: {})

    assert validate_config(cfg_path) == 1
