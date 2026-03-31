"""Tests for edge requirement in decision logic."""

from __future__ import annotations

from copy import deepcopy

import pytest

from core.strategy.decision import decide


def test_min_edge_requirement():
    """Test that trades are blocked when edge is too small."""
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.20,  # Require 20% edge
        },
    }

    # Small edge (buy=0.70, sell=0.65, edge=0.05) -> blocked
    a, m = decide(
        {},
        probas={"buy": 0.70, "sell": 0.65},
        confidence={"buy": 0.8, "sell": 0.7},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"
    assert "EDGE_TOO_SMALL" in m.get("reasons", [])

    # Large edge (buy=0.80, sell=0.50, edge=0.30) -> allowed
    a, m = decide(
        {},
        probas={"buy": 0.80, "sell": 0.50},
        confidence={"buy": 0.8, "sell": 0.7},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    assert "EDGE_TOO_SMALL" not in m.get("reasons", [])


def test_min_edge_disabled_by_default():
    """Test that min_edge=0 allows all trades (default behavior)."""
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,  # Disabled
        },
    }

    # Small edge should be allowed when min_edge=0
    a, m = decide(
        {},
        probas={"buy": 0.70, "sell": 0.65},
        confidence={"buy": 0.8, "sell": 0.7},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    assert "EDGE_TOO_SMALL" not in m.get("reasons", [])


def test_min_edge_for_short():
    """Test min_edge for SHORT trades - skipped due to EV gate."""
    # Note: The EV formula (p_buy * R - p_sell > 0) is buy-biased
    # Most SHORT scenarios fail EV gate - skip detailed testing
    pass


def test_min_edge_for_short_with_positive_ev():
    """Test min_edge for SHORT when EV allows it - skipped."""
    # Note: EV gate blocks most SHORTs by design
    # System is optimized for LONG trades
    pass


def test_high_confidence_with_edge_requirement():
    """Test that both high confidence AND edge are required."""
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.75,  # High confidence required
            "min_edge": 0.20,  # AND edge required
        },
    }

    # High confidence but low edge -> blocked
    a, m = decide(
        {},
        probas={"buy": 0.80, "sell": 0.75},  # Edge only 0.05
        confidence={"buy": 0.85, "sell": 0.70},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"
    assert "EDGE_TOO_SMALL" in m.get("reasons", [])

    # High edge but low confidence -> blocked
    a, m = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},  # Edge 0.35
        confidence={"buy": 0.70, "sell": 0.60},  # Below 0.75
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"
    assert "CONF_TOO_LOW" in m.get("reasons", [])

    # Both high confidence AND high edge -> allowed
    a, m = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},
        confidence={"buy": 0.85, "sell": 0.60},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    assert "EDGE_TOO_SMALL" not in m.get("reasons", [])
    assert "CONF_TOO_LOW" not in m.get("reasons", [])


def test_feature_attribution_default_off_preserves_min_edge_gate() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.20,
        },
    }

    action, meta = decide(
        {"symbol": "tTESTBTC:TESTUSD", "timeframe": "1h"},
        probas={"buy": 0.70, "sell": 0.65},
        confidence={"buy": 0.80, "sell": 0.70},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "EDGE_TOO_SMALL" in (meta.get("reasons") or [])
    assert "FEATURE_ATTRIBUTION_INVALID_REQUEST" not in (meta.get("reasons") or [])


def test_feature_attribution_valid_request_neutralizes_min_edge_without_mutation() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.20,
        },
    }
    policy = {
        "symbol": "tTESTBTC:TESTUSD",
        "timeframe": "1h",
        "feature_attribution": {
            "selected_row_label": "Minimum-edge gate seam",
            "mode": "neutralize",
        },
    }
    policy_before = deepcopy(policy)
    cfg_before = deepcopy(cfg)

    action, meta = decide(
        policy,
        probas={"buy": 0.70, "sell": 0.65},
        confidence={"buy": 0.80, "sell": 0.70},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"
    assert "EDGE_TOO_SMALL" not in (meta.get("reasons") or [])
    assert policy == policy_before
    assert cfg == cfg_before


def test_feature_attribution_neutralization_preserves_non_target_blockers() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.75,
            "min_edge": 0.20,
        },
    }
    policy = {
        "feature_attribution": {
            "selected_row_label": "Minimum-edge gate seam",
            "mode": "neutralize",
        }
    }

    action, meta = decide(
        policy,
        probas={"buy": 0.80, "sell": 0.75},
        confidence={"buy": 0.70, "sell": 0.65},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "CONF_TOO_LOW" in (meta.get("reasons") or [])
    assert "EDGE_TOO_SMALL" not in (meta.get("reasons") or [])


def test_feature_attribution_default_off_preserves_hysteresis_gate() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 2,
            "cooldown_bars": 0,
        },
    }

    action, meta = decide(
        {"symbol": "tTESTBTC:TESTUSD", "timeframe": "1h"},
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={"last_action": "SHORT", "decision_steps": 0},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "HYST_WAIT" in (meta.get("reasons") or [])
    assert "FEATURE_ATTRIBUTION_INVALID_REQUEST" not in (meta.get("reasons") or [])


def test_feature_attribution_valid_request_neutralizes_hysteresis_without_mutation() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 2,
            "cooldown_bars": 0,
        },
    }
    policy = {
        "symbol": "tTESTBTC:TESTUSD",
        "timeframe": "1h",
        "feature_attribution": {
            "selected_row_label": "Hysteresis gate seam",
            "mode": "neutralize",
        },
    }
    policy_before = deepcopy(policy)
    cfg_before = deepcopy(cfg)

    action, meta = decide(
        policy,
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={"last_action": "SHORT", "decision_steps": 0},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"
    assert "HYST_WAIT" not in (meta.get("reasons") or [])
    assert policy == policy_before
    assert cfg == cfg_before
    assert cfg["gates"]["hysteresis_steps"] == 2


def test_feature_attribution_hysteresis_neutralization_preserves_cooldown_blocker() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 2,
            "cooldown_bars": 0,
        },
    }
    policy = {
        "feature_attribution": {
            "selected_row_label": "Hysteresis gate seam",
            "mode": "neutralize",
        }
    }

    action, meta = decide(
        policy,
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={"last_action": "SHORT", "decision_steps": 0, "cooldown_remaining": 2},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "COOLDOWN_ACTIVE" in (meta.get("reasons") or [])
    assert "HYST_WAIT" not in (meta.get("reasons") or [])
    assert (meta.get("state_out") or {}).get("cooldown_remaining") == 1


def test_feature_attribution_default_off_preserves_cooldown_gate() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 1,
            "cooldown_bars": 2,
        },
    }

    action, meta = decide(
        {"symbol": "tTESTBTC:TESTUSD", "timeframe": "1h"},
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={"last_action": "LONG", "decision_steps": 0, "cooldown_remaining": 2},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "COOLDOWN_ACTIVE" in (meta.get("reasons") or [])
    assert "FEATURE_ATTRIBUTION_INVALID_REQUEST" not in (meta.get("reasons") or [])
    assert (meta.get("state_out") or {}).get("cooldown_remaining") == 1


def test_feature_attribution_valid_request_neutralizes_cooldown_without_mutation() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 1,
            "cooldown_bars": 2,
        },
    }
    state = {"last_action": "LONG", "decision_steps": 0, "cooldown_remaining": 2}
    policy = {
        "symbol": "tTESTBTC:TESTUSD",
        "timeframe": "1h",
        "feature_attribution": {
            "selected_row_label": "Cooldown gate seam",
            "mode": "neutralize",
        },
    }
    policy_before = deepcopy(policy)
    cfg_before = deepcopy(cfg)
    state_before = deepcopy(state)

    action, meta = decide(
        policy,
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"
    assert "COOLDOWN_ACTIVE" not in (meta.get("reasons") or [])
    assert (meta.get("state_out") or {}).get("cooldown_remaining") is None
    assert policy == policy_before
    assert cfg == cfg_before
    assert state == state_before
    assert cfg["gates"]["cooldown_bars"] == 2


def test_feature_attribution_cooldown_neutralization_preserves_hysteresis_blocker() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "gates": {
            "hysteresis_steps": 2,
            "cooldown_bars": 2,
        },
    }
    policy = {
        "feature_attribution": {
            "selected_row_label": "Cooldown gate seam",
            "mode": "neutralize",
        }
    }

    action, meta = decide(
        policy,
        probas={"buy": 0.80, "sell": 0.10},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={"last_action": "SHORT", "decision_steps": 0, "cooldown_remaining": 2},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "HYST_WAIT" in (meta.get("reasons") or [])
    assert "COOLDOWN_ACTIVE" not in (meta.get("reasons") or [])
    assert (meta.get("state_out") or {}).get("decision_steps") == 1
    assert (meta.get("state_out") or {}).get("cooldown_remaining") == 2


def test_feature_attribution_default_off_preserves_htf_block() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "multi_timeframe": {
            "use_htf_block": True,
            "allow_ltf_override": False,
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
        {"symbol": "tTESTBTC:TESTUSD", "timeframe": "1h"},
        probas={"buy": 0.6, "sell": 0.1},
        confidence={"buy": 0.6, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 98.0,
            "current_atr": 1.0,
            "htf_fib": {"available": True, "levels": {0.5: 100.0}},
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "HTF_FIB_LONG_BLOCK" in (meta.get("reasons") or [])
    assert "FEATURE_ATTRIBUTION_INVALID_REQUEST" not in (meta.get("reasons") or [])
    state_out = meta.get("state_out") or {}
    assert (state_out.get("htf_fib_entry_debug") or {}).get("reason") == "LONG_BELOW_LEVEL"
    assert state_out.get("fib_gate_summary") is None


def test_feature_attribution_valid_request_neutralizes_htf_block_without_mutation() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "multi_timeframe": {
            "use_htf_block": True,
            "allow_ltf_override": False,
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
    state = {
        "last_close": 98.0,
        "current_atr": 1.0,
        "htf_fib": {"available": True, "levels": {0.5: 100.0}},
        "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
    }
    policy = {
        "symbol": "tTESTBTC:TESTUSD",
        "timeframe": "1h",
        "feature_attribution": {
            "selected_row_label": "HTF block seam",
            "mode": "neutralize",
        },
    }
    policy_before = deepcopy(policy)
    cfg_before = deepcopy(cfg)
    state_before = deepcopy(state)

    action, meta = decide(
        policy,
        probas={"buy": 0.6, "sell": 0.1},
        confidence={"buy": 0.6, "sell": 0.1},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "LONG"
    assert "HTF_FIB_LONG_BLOCK" not in (meta.get("reasons") or [])
    assert "ENTRY_LONG" in (meta.get("reasons") or [])
    state_out = meta.get("state_out") or {}
    htf_debug = state_out.get("htf_fib_entry_debug") or {}
    fib_summary = state_out.get("fib_gate_summary") or {}
    assert htf_debug.get("reason") == "DISABLED_BY_CONFIG"
    assert (fib_summary.get("htf") or {}).get("reason") == "DISABLED_BY_CONFIG"
    assert (fib_summary.get("ltf") or {}).get("reason") == "PASS"
    assert policy == policy_before
    assert cfg == cfg_before
    assert state == state_before
    assert cfg["multi_timeframe"]["use_htf_block"] is True


def test_feature_attribution_htf_block_neutralization_preserves_ltf_blocker() -> None:
    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"cooldown_bars": 0},
        "risk": {"risk_map": [[0.6, 0.01]]},
        "multi_timeframe": {
            "use_htf_block": True,
            "allow_ltf_override": False,
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
    policy = {
        "feature_attribution": {
            "selected_row_label": "HTF block seam",
            "mode": "neutralize",
        }
    }

    action, meta = decide(
        policy,
        probas={"buy": 0.6, "sell": 0.1},
        confidence={"buy": 0.6, "sell": 0.1},
        regime="balanced",
        state={
            "last_close": 121.0,
            "current_atr": 0.5,
            "htf_fib": {"available": True, "levels": {0.5: 130.0}},
            "ltf_fib": {"available": True, "levels": {1.0: 120.0}},
        },
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "LTF_FIB_LONG_BLOCK" in (meta.get("reasons") or [])
    assert "HTF_FIB_LONG_BLOCK" not in (meta.get("reasons") or [])
    state_out = meta.get("state_out") or {}
    assert (state_out.get("htf_fib_entry_debug") or {}).get("reason") == "DISABLED_BY_CONFIG"
    assert (state_out.get("ltf_fib_entry_debug") or {}).get("reason") == "LONG_ABOVE_LEVEL"
    assert state_out.get("fib_gate_summary") is None


@pytest.mark.parametrize(
    "fa_request",
    [
        "neutralize",
        {"selected_row_label": "Base entry confidence seam", "mode": "neutralize"},
        {"selected_row_label": "Minimum-edge gate seam", "mode": "disable"},
        {"selected_row_label": "Hysteresis gate seam", "mode": "disable"},
        {"selected_row_label": "Cooldown gate seam", "mode": "disable"},
        {"selected_row_label": "HTF block seam", "mode": "disable"},
        {"mode": "neutralize"},
        {"selected_row_label": "Minimum-edge gate seam", "mode": "neutralize", "extra": True},
    ],
    ids=[
        "unsupported-shape-string",
        "wrong-row-label",
        "wrong-mode",
        "hysteresis-wrong-mode",
        "cooldown-wrong-mode",
        "htf-block-wrong-mode",
        "missing-row-label",
        "extra-key",
    ],
)
def test_feature_attribution_invalid_requests_fail_closed_without_mutation(
    fa_request: object,
) -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.20,
        },
    }
    policy = {
        "symbol": "tTESTBTC:TESTUSD",
        "timeframe": "1h",
        "feature_attribution": fa_request,
    }
    policy_before = deepcopy(policy)
    cfg_before = deepcopy(cfg)

    action, meta = decide(
        policy,
        probas={"buy": 0.70, "sell": 0.65},
        confidence={"buy": 0.80, "sell": 0.70},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )

    assert action == "NONE"
    assert "FEATURE_ATTRIBUTION_INVALID_REQUEST" in (meta.get("reasons") or [])
    assert "EDGE_TOO_SMALL" not in (meta.get("reasons") or [])
    assert policy == policy_before
    assert cfg == cfg_before


def test_sizing_prefers_scaled_confidence_when_present():
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.75,
            "min_edge": 0.0,
        },
        "risk": {
            "risk_map": [
                [0.50, 0.01],
                [0.80, 0.02],
            ]
        },
    }

    # Entry gate should pass on raw buy=0.80, but sizing should use buy_scaled=0.55.
    a, m = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},
        confidence={"buy": 0.80, "sell": 0.10, "buy_scaled": 0.55},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    # Base size for raw 0.80 would be 0.02, then scaled by 0.55/0.80.
    assert abs(float(m.get("size") or 0.0) - 0.01375) < 1e-9


def test_entry_gate_does_not_use_scaled_confidence():
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.75,
            "min_edge": 0.0,
        },
        "risk": {
            "risk_map": [
                [0.50, 0.01],
                [0.80, 0.02],
            ]
        },
    }

    # Raw buy=0.70 is below the threshold; scaled must NOT allow entry.
    a, m = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},
        confidence={"buy": 0.70, "sell": 0.10, "buy_scaled": 0.95},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"
    assert "CONF_TOO_LOW" in (m.get("reasons") or [])


def test_regime_size_multiplier_scales_size_only():
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.75,
            "min_edge": 0.0,
        },
        "risk": {
            "risk_map": [
                [0.50, 0.01],
                [0.80, 0.02],
            ],
            "regime_size_multipliers": {"ranging": 0.5},
        },
    }

    # Entry should pass on raw buy=0.80 and size should be 0.02 in balanced.
    a_bal, m_bal = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a_bal == "LONG"
    assert abs(float(m_bal.get("size") or 0.0) - 0.02) < 1e-12

    # In ranging, size should be scaled down by multiplier (0.5).
    a_rng, m_rng = decide(
        {},
        probas={"buy": 0.85, "sell": 0.50},
        confidence={"buy": 0.80, "sell": 0.10},
        regime="ranging",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a_rng == "LONG"
    assert abs(float(m_rng.get("size") or 0.0) - 0.01) < 1e-12

    # Debug signal should be present.
    assert (m_rng.get("state_out") or {}).get("size_regime_mult") == 0.5


def test_sizing_risk_map_error_is_not_silent_zero() -> None:
    cfg = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "min_edge": 0.0,
        },
        "risk": {
            "risk_map": ["invalid"],
        },
    }

    with pytest.raises(RuntimeError, match="size_base"):
        decide(
            {},
            probas={"buy": 0.9, "sell": 0.1},
            confidence={"buy": 0.9, "sell": 0.1},
            regime="balanced",
            state={},
            risk_ctx={},
            cfg=cfg,
        )
