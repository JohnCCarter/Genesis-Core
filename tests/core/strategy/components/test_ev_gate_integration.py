"""
Integration tests for EVGate with corrected ComponentContextBuilder key mapping.

Verifies that EVGate receives non-zero EV values and veto logic works correctly
after Bug #2 fix.
"""

import pytest

from core.strategy.components.context_builder import ComponentContextBuilder
from core.strategy.components.ev_gate import EVGateComponent


class TestEVGateReceivesCorrectContext:
    """Test that EVGate receives correct EV values from context."""

    def test_ev_gate_receives_nonzero_ev_with_buy_sell_keys(self):
        """EVGate should receive non-zero EV when probas use 'buy'/'sell' keys."""
        # Simulate pipeline result with 'buy'/'sell' keys (model output)
        result = {
            "probas": {"buy": 0.7, "sell": 0.3, "hold": 0.0},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Verify context has expected_value
        assert "expected_value" in context
        assert context["expected_value"] > 0  # Should be positive (buy favored)

        # Create EVGate component
        ev_gate = EVGateComponent(min_ev=0.1)

        # Evaluate
        ev_result = ev_gate.evaluate(context)

        # Should ALLOW (EV > 0.1)
        assert ev_result.allowed is True
        assert ev_result.reason is None

    def test_ev_gate_veto_works_with_corrected_keys(self):
        """EVGate should veto when EV < min_ev (with corrected key mapping)."""
        # Low EV scenario (probas nearly equal)
        result = {
            "probas": {"buy": 0.51, "sell": 0.49, "hold": 0.0},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Verify context has expected_value
        assert "expected_value" in context
        assert context["expected_value"] < 0.1  # Should be small (near 50/50)

        # EVGate with min_ev=0.05 (higher than actual EV)
        ev_gate = EVGateComponent(min_ev=0.05)
        ev_result = ev_gate.evaluate(context)

        # Should VETO (EV < min_ev=0.05)
        assert ev_result.allowed is False
        assert ev_result.reason == "EV_BELOW_THRESHOLD"

    def test_ev_gate_allows_high_ev_signals(self):
        """EVGate should allow high EV signals."""
        # High EV scenario (strong buy signal)
        result = {
            "probas": {"buy": 0.85, "sell": 0.15, "hold": 0.0},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Verify context has expected_value
        assert "expected_value" in context
        assert context["expected_value"] > 0.5  # Should be high

        # EVGate with moderate threshold
        ev_gate = EVGateComponent(min_ev=0.3)
        ev_result = ev_gate.evaluate(context)

        # Should ALLOW (EV > 0.3)
        assert ev_result.allowed is True


class TestEVGateWithMissingProbas:
    """Test EVGate behavior when probas are missing (defensive)."""

    def test_ev_gate_defensive_when_ev_missing(self):
        """EVGate should handle missing expected_value gracefully."""
        # Context without probas (no EV fields)
        context = {
            "regime": "balanced",
            "action": "NONE",
        }

        ev_gate = EVGateComponent(min_ev=0.1)
        ev_result = ev_gate.evaluate(context)

        # Should veto (defensive: missing EV treated as 0)
        assert ev_result.allowed is False
        assert "EV" in ev_result.reason  # Should indicate EV issue


class TestEVGateCalibration:
    """Test EVGate with calibrated thresholds from investigation."""

    @pytest.mark.parametrize(
        "buy_proba,sell_proba,min_ev,should_allow",
        [
            # High EV (should pass most thresholds)
            (0.8, 0.2, 0.13, True),  # p90 threshold
            (0.75, 0.25, 0.10, True),  # p80 threshold
            # Medium EV (borderline)
            (0.65, 0.35, 0.13, True),  # Above p90
            (0.6, 0.4, 0.10, True),  # Above p80
            # Low EV (should veto)
            (0.55, 0.45, 0.13, False),  # Below p90
            (0.52, 0.48, 0.10, False),  # Below p80
        ],
    )
    def test_ev_gate_threshold_behavior(self, buy_proba, sell_proba, min_ev, should_allow):
        """EVGate should veto/allow based on calibrated thresholds."""
        result = {"probas": {"buy": buy_proba, "sell": sell_proba}}
        context = ComponentContextBuilder.build(result, {})

        ev_gate = EVGateComponent(min_ev=min_ev)
        ev_result = ev_gate.evaluate(context)

        assert ev_result.allowed == should_allow, (
            f"EV gate with min_ev={min_ev} should "
            f"{'allow' if should_allow else 'veto'} "
            f"buy={buy_proba}, sell={sell_proba}"
        )
