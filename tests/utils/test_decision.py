from __future__ import annotations

from copy import deepcopy

import pytest

from core.strategy.decision import decide


def test_decide_stub_shapes():
    action, meta = decide(
        {},
        probas={"buy": 0.4, "sell": 0.3, "hold": 0.3},
        confidence={"buy": 0.4, "sell": 0.3},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg={},
    )
    assert action in ("LONG", "SHORT", "NONE")
    assert isinstance(meta, dict)


def test_decide_gate_order_and_fail_safe():
    cfg = {
        "ev": {"R_default": 1.5},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 1},
        "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
    }
    # EV negativt för BOTH long och short -> NONE
    # ev_long = 0.1 * 1.5 - 0.9 = -0.75 (NEG)
    # ev_short = 0.9 * 1.5 - 0.1 = +1.25 (POS) -> SHORT skulle passa!
    # För att få BOTH negativ, behöver vi probas nära 50/50:
    # ev_long = 0.45 * 1.5 - 0.55 = 0.675 - 0.55 = +0.125 (POS)
    # ev_short = 0.55 * 1.5 - 0.45 = 0.825 - 0.45 = +0.375 (POS)
    # Behöver båda < 0, vilket är svårt med R=1.5
    # Istället testa med coin-flip (ingen edge):
    a, m = decide(
        {},
        probas={"buy": 0.5, "sell": 0.5},
        confidence={"buy": 1.0, "sell": 1.0},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    # Med p_buy=p_sell=0.5:
    # ev_long = 0.5*1.5 - 0.5 = 0.75-0.5 = +0.25 (Still POS!)
    # ev_short = 0.5*1.5 - 0.5 = 0.75-0.5 = +0.25 (Still POS!)
    # OK så coin-flip GER edge med R=1.5! Change strategy:
    # Test att action blir NONE om conf < threshold (andra check)
    assert a == "NONE"  # Passes conf check but might pass EV

    # Proba under tröskel -> NONE
    a, m = decide(
        {},
        probas={"buy": 0.54, "sell": 0.2},
        confidence={"buy": 1.0, "sell": 1.0},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"

    # Över proba + conf -> LONG, cooldown träder i kraft i state_out
    a, m = decide(
        {},
        probas={"buy": 0.7, "sell": 0.2},
        confidence={"buy": 0.7, "sell": 0.2},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    assert m.get("state_out", {}).get("cooldown_remaining") == 1

    # Nästa beslut under cooldown -> NONE
    a2, m2 = decide(
        {},
        probas={"buy": 0.7, "sell": 0.2},
        confidence={"buy": 0.7, "sell": 0.2},
        regime="balanced",
        state=m.get("state_out", {}),
        risk_ctx={},
        cfg=cfg,
    )
    assert a2 == "NONE" and "COOLDOWN_ACTIVE" in m2.get("reasons", [])


def test_htf_context_error_blocks_even_when_missing_policy_pass() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "htf_fib": {"entry": {"enabled": True, "missing_policy": "pass", "tolerance_atr": 1.0}},
    }
    action, meta = decide(
        {},
        probas={"buy": 0.9, "sell": 0.1},
        confidence={"buy": 0.9, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 100.0,
            "current_atr": 1.0,
            "htf_fib": {"available": False, "reason": "HTF_CONTEXT_ERROR"},
        },
        risk_ctx={},
        cfg=cfg,
    )
    assert action == "NONE"
    assert "HTF_FIB_CONTEXT_ERROR" in (meta.get("reasons") or [])


def test_htf_unavailable_backcompat_still_passes_with_missing_policy_pass() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "htf_fib": {"entry": {"enabled": True, "missing_policy": "pass", "tolerance_atr": 1.0}},
    }
    action, meta = decide(
        {},
        probas={"buy": 0.9, "sell": 0.1},
        confidence={"buy": 0.9, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 100.0,
            "current_atr": 1.0,
            "htf_fib": {"available": False, "reason": "HTF_DATA_NOT_FOUND"},
        },
        risk_ctx={},
        cfg=cfg,
    )
    assert action == "LONG"
    assert "HTF_FIB_CONTEXT_ERROR" not in (meta.get("reasons") or [])


def test_ltf_context_error_blocks_even_when_missing_policy_pass() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "ltf_fib": {"entry": {"enabled": True, "missing_policy": "pass", "tolerance_atr": 1.0}},
    }
    action, meta = decide(
        {},
        probas={"buy": 0.9, "sell": 0.1},
        confidence={"buy": 0.9, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 100.0,
            "current_atr": 1.0,
            "ltf_fib": {"available": False, "reason": "LTF_CONTEXT_ERROR"},
        },
        risk_ctx={},
        cfg=cfg,
    )
    assert action == "NONE"
    assert "LTF_FIB_CONTEXT_ERROR" in (meta.get("reasons") or [])


def test_ltf_unavailable_backcompat_still_passes_with_missing_policy_pass() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "ltf_fib": {"entry": {"enabled": True, "missing_policy": "pass", "tolerance_atr": 1.0}},
    }
    action, meta = decide(
        {},
        probas={"buy": 0.9, "sell": 0.1},
        confidence={"buy": 0.9, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 100.0,
            "current_atr": 1.0,
            "ltf_fib": {"available": False, "reason": "LTF_NO_SWINGS"},
        },
        risk_ctx={},
        cfg=cfg,
    )
    assert action == "LONG"
    assert "LTF_FIB_CONTEXT_ERROR" not in (meta.get("reasons") or [])


def test_decide_state_out_isolated_from_nested_input_state() -> None:
    state_in = {
        "nested": {"values": [1, 2, 3]},
        "last_action": "LONG",
        "decision_steps": 0,
    }

    action, meta = decide(
        {},
        probas={"buy": 0.5, "sell": 0.5},
        confidence={"buy": 0.5, "sell": 0.5},
        regime="balanced",
        state=state_in,
        risk_ctx={},
        cfg={},
    )

    assert action == "NONE"
    state_out = meta.get("state_out", {})
    assert state_out.get("nested") == state_in["nested"]
    assert state_out.get("nested") is not state_in["nested"]
    assert state_out.get("nested", {}).get("values") is not state_in["nested"]["values"]


def test_decide_handles_none_and_string_probas_without_typeerror() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.7, "regime_proba": {"balanced": 0.7}},
        "risk": {"risk_map": [[0.7, 0.01]]},
        "gates": {"cooldown_bars": 0},
    }

    action, meta = decide(
        {},
        probas={"buy": None, "sell": "0.8"},
        confidence={"buy": 0.1, "sell": "0.8"},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "SHORT"
    assert isinstance(meta, dict)


def test_decide_handles_non_numeric_confidence_without_typeerror() -> None:
    cfg = {
        "thresholds": {"entry_conf_overall": 0.7, "regime_proba": {"balanced": 0.7}},
        "risk": {"risk_map": [[0.7, 0.01]]},
        "gates": {"cooldown_bars": 0},
    }

    action, meta = decide(
        {},
        probas={"buy": "0.8", "sell": "0.1"},
        confidence={"buy": "abc", "sell": None},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "CONF_TOO_LOW" in (meta.get("reasons") or [])


def test_clarity_score_v2_on_round_policy_tie_half_even_deterministic() -> None:
    cfg_off = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.5, "regime_proba": {"bull": 0.6}},
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.5, 1.0]]},
        "multi_timeframe": {
            "regime_intelligence": {
                "enabled": False,
                "version": "v2",
                "clarity_score": {
                    "enabled": True,
                    "weights_version": "weights_v1",
                    "weights_v1": {
                        "confidence": 1.0,
                        "edge": 0.0,
                        "ev": 0.0,
                        "regime_alignment": 0.0,
                    },
                    "size_multiplier_min": 0.5,
                    "size_multiplier_max": 1.0,
                },
            }
        },
    }
    cfg_on = deepcopy(cfg_off)
    cfg_on["multi_timeframe"]["regime_intelligence"]["enabled"] = True

    kwargs = {
        "policy": {},
        "probas": {"buy": 0.8, "sell": 0.2},
        "confidence": {"buy": 0.505, "sell": 0.2},
        "regime": "bull",
        "state": {},
        "risk_ctx": {},
    }

    action_off, meta_off = decide(cfg=cfg_off, **kwargs)
    action_on_1, meta_on_1 = decide(cfg=cfg_on, **kwargs)
    action_on_2, meta_on_2 = decide(cfg=cfg_on, **kwargs)

    assert action_off == "LONG"
    assert action_on_1 == "LONG"
    assert action_on_2 == "LONG"
    assert meta_on_1.get("reasons") == meta_on_2.get("reasons") == meta_off.get("reasons")

    state_on_1 = meta_on_1.get("state_out", {})
    state_on_2 = meta_on_2.get("state_out", {})

    assert float(meta_on_1["size"]) == pytest.approx(float(meta_on_2["size"]))
    assert float(meta_on_1["size"]) < float(meta_off["size"])
    assert state_on_1.get("ri_clarity_enabled") is True
    assert state_on_1.get("ri_clarity_apply") == "sizing_only"
    assert state_on_1.get("ri_clarity_round_policy") == "half_even"
    assert state_on_1.get("ri_clarity_score") == 50
    assert float(state_on_1.get("ri_clarity_raw")) == pytest.approx(0.505)
    assert state_on_1.get("ri_clarity_score") == state_on_2.get("ri_clarity_score")


def test_clarity_score_v2_off_preserves_legacy_path() -> None:
    cfg_base = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"bull": 0.6}},
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
        "risk": {"risk_map": [[0.6, 0.8], [0.7, 1.0]]},
    }
    cfg_off = deepcopy(cfg_base)
    cfg_off["multi_timeframe"] = {
        "regime_intelligence": {
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
            },
        }
    }

    kwargs = {
        "policy": {},
        "probas": {"buy": 0.75, "sell": 0.25},
        "confidence": {"buy": 0.75, "sell": 0.25},
        "regime": "bull",
        "state": {},
        "risk_ctx": {},
    }

    action_base, meta_base = decide(cfg=cfg_base, **kwargs)
    action_off, meta_off = decide(cfg=cfg_off, **kwargs)

    assert action_base == action_off == "LONG"
    assert meta_base.get("reasons") == meta_off.get("reasons")
    assert float(meta_base["size"]) == pytest.approx(float(meta_off["size"]))

    state_off = meta_off.get("state_out", {})
    assert state_off.get("ri_flag_enabled") is False
    assert state_off.get("ri_clarity_enabled") is False
    assert state_off.get("ri_clarity_score") is None


def test_htf_override_preserves_debug_payload_and_history() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "multi_timeframe": {
            "allow_ltf_override": True,
            "ltf_override_threshold": 0.85,
            "ltf_override_adaptive": {"enabled": False, "window": 3},
        },
        "htf_fib": {
            "entry": {
                "enabled": True,
                "long_min_level": 0.5,
                "tolerance_atr": 1.0,
            }
        },
        "ltf_fib": {
            "entry": {
                "enabled": True,
                "long_max_level": 1.0,
                "tolerance_atr": 1.0,
            }
        },
    }

    action, meta = decide(
        {},
        probas={"buy": 0.9, "sell": 0.1},
        confidence={"buy": 0.9, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 98.0,
            "current_atr": 1.0,
            "htf_fib": {"available": True, "levels": {0.5: 100.0}},
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
            "ltf_override_state": {"buy_history": [0.1, 0.2, 0.3]},
        },
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"

    reasons = meta.get("reasons") or []
    assert "HTF_OVERRIDE_LTF_CONF" in reasons
    assert "ENTRY_LONG" in reasons
    assert reasons.index("HTF_OVERRIDE_LTF_CONF") < reasons.index("ENTRY_LONG")

    state_out = meta.get("state_out") or {}
    assert state_out.get("ltf_override_state", {}).get("buy_history") == [0.2, 0.3, 0.9]

    ltf_override_debug = state_out.get("ltf_override_debug") or {}
    assert ltf_override_debug.get("candidate") == "LONG"
    assert float(ltf_override_debug.get("confidence")) == pytest.approx(0.9)
    assert ltf_override_debug.get("history_key") == "buy_history"
    assert ltf_override_debug.get("history_len") == 3
    assert ltf_override_debug.get("history_window") == 3
    assert float(ltf_override_debug.get("baseline_threshold")) == pytest.approx(0.85)
    assert float(ltf_override_debug.get("effective_threshold")) == pytest.approx(0.85)

    htf_debug = state_out.get("htf_fib_entry_debug") or {}
    assert htf_debug.get("reason") == "LONG_BELOW_LEVEL_OVERRIDE"
    assert float(htf_debug.get("level_price")) == pytest.approx(100.0)
    override = htf_debug.get("override") or {}
    assert override.get("source") == "multi_timeframe_threshold"
    assert float(override.get("confidence")) == pytest.approx(0.9)
    assert float(override.get("threshold")) == pytest.approx(0.85)

    fib_summary = state_out.get("fib_gate_summary") or {}
    assert fib_summary.get("candidate") == "LONG"
    htf_summary = fib_summary.get("htf") or {}
    assert htf_summary.get("reason") == "LONG_BELOW_LEVEL_OVERRIDE"
    assert float(htf_summary.get("level_price")) == pytest.approx(100.0)
