from __future__ import annotations

import pytest

from core.strategy.family_admission import (
    StrategyFamilyAdmissionError,
    validate_optimizer_family_admission,
    validate_strategy_family_admission,
)
from core.strategy.run_intent import RunIntentValidationError


def _ri_research_config() -> dict[str, object]:
    return {
        "strategy_family": "ri",
        "thresholds": {
            "entry_conf_overall": 0.28,
            "regime_proba": {"balanced": 0.36},
            "signal_adaptation": {
                "atr_period": 14,
                "zones": {
                    "low": {"entry_conf_overall": 0.14, "regime_proba": 0.32},
                    "mid": {"entry_conf_overall": 0.42, "regime_proba": 0.52},
                    "high": {"entry_conf_overall": 0.34, "regime_proba": 0.58},
                },
            },
        },
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 1},
        "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
    }


def _ri_optimizer_research_config(
    *, run_intent: str | None = "research_slice"
) -> dict[str, object]:
    runs: dict[str, object] = {}
    if run_intent is not None:
        runs["run_intent"] = run_intent
    return {
        "strategy_family": "ri",
        "meta": {"runs": runs},
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
            "thresholds.signal_adaptation.zones.low.regime_proba": {
                "type": "fixed",
                "value": 0.32,
            },
            "thresholds.signal_adaptation.zones.mid.entry_conf_overall": {
                "type": "fixed",
                "value": 0.42,
            },
            "thresholds.signal_adaptation.zones.mid.regime_proba": {
                "type": "fixed",
                "value": 0.52,
            },
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


def test_strategy_family_admission_accepts_ri_research_slice_gate_sweep() -> None:
    family, run_intent = validate_strategy_family_admission(
        _ri_research_config(),
        run_intent="research_slice",
    )

    assert family == "ri"
    assert run_intent == "research_slice"


def test_strategy_family_admission_rejects_same_ri_shape_for_champion_freeze() -> None:
    with pytest.raises(StrategyFamilyAdmissionError, match="champion_freeze"):
        validate_strategy_family_admission(
            _ri_research_config(),
            run_intent="champion_freeze",
        )


def test_optimizer_family_admission_accepts_ri_research_slice_gate_sweep() -> None:
    family, run_intent = validate_optimizer_family_admission(_ri_optimizer_research_config())

    assert family == "ri"
    assert run_intent == "research_slice"


def test_optimizer_family_admission_rejects_same_ri_shape_for_champion_freeze() -> None:
    with pytest.raises(StrategyFamilyAdmissionError, match="champion_freeze"):
        validate_optimizer_family_admission(
            _ri_optimizer_research_config(run_intent="champion_freeze")
        )


def test_optimizer_family_admission_rejects_unknown_run_intent() -> None:
    with pytest.raises(RunIntentValidationError, match="invalid_run_intent"):
        validate_optimizer_family_admission(_ri_optimizer_research_config(run_intent="mystery"))


def test_optimizer_family_admission_rejects_missing_run_intent_for_ri() -> None:
    with pytest.raises(RunIntentValidationError, match="missing_run_intent"):
        validate_optimizer_family_admission(_ri_optimizer_research_config(run_intent=None))
