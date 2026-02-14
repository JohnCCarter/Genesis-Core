"""Unit tests for EVGateComponent."""

from core.strategy.components.ev_gate import EVGateComponent


class TestEVGateComponent:
    """Test EVGateComponent behavior."""

    def test_allows_entry_when_ev_above_threshold(self):
        """Test that component allows entry when EV >= threshold."""
        component = EVGateComponent(min_ev=0.0)

        # EV above threshold
        context = {"expected_value": 0.5}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.reason is None
        assert decision.confidence == 1.0
        assert decision.metadata["ev_value"] == 0.5
        assert decision.metadata["min_ev"] == 0.0

    def test_allows_entry_when_ev_equals_threshold(self):
        """Test that component allows entry when EV == threshold (boundary)."""
        component = EVGateComponent(min_ev=0.2)

        # EV exactly at threshold
        context = {"expected_value": 0.2}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.reason is None
        assert decision.metadata["ev_value"] == 0.2

    def test_vetoes_entry_when_ev_below_threshold(self):
        """Test that component vetoes entry when EV < threshold."""
        component = EVGateComponent(min_ev=0.0)

        # EV below threshold
        context = {"expected_value": -0.1}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "EV_BELOW_THRESHOLD"
        assert decision.confidence == 0.0
        assert decision.metadata["ev_value"] == -0.1
        assert decision.metadata["min_ev"] == 0.0

    def test_vetoes_entry_when_ev_missing_from_context(self):
        """Test that component vetoes when expected_value key is missing."""
        component = EVGateComponent(min_ev=0.0)

        # Empty context
        context = {}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "EV_MISSING"
        assert decision.confidence == 0.0
        assert decision.metadata["ev_value"] is None
        assert decision.metadata["min_ev"] == 0.0

    def test_vetoes_entry_when_ev_is_none(self):
        """Test that component vetoes when expected_value is None."""
        component = EVGateComponent(min_ev=0.0)

        context = {"expected_value": None}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "EV_MISSING"
        assert decision.metadata["ev_value"] is None

    def test_metadata_correctness(self):
        """Test that metadata is correct in all cases."""
        component = EVGateComponent(min_ev=0.1)

        # Allow case
        context = {"expected_value": 0.3}
        decision = component.evaluate(context)
        assert decision.metadata["component"] == "ev_gate"
        assert decision.metadata["min_ev"] == 0.1
        assert decision.metadata["ev_value"] == 0.3

        # Veto case
        context = {"expected_value": 0.05}
        decision = component.evaluate(context)
        assert decision.metadata["component"] == "ev_gate"
        assert decision.metadata["min_ev"] == 0.1
        assert decision.metadata["ev_value"] == 0.05

    def test_stateless_deterministic_behavior(self):
        """Test that component is stateless (same context = same decision)."""
        component = EVGateComponent(min_ev=0.0)

        context = {"expected_value": 0.25}

        # Evaluate multiple times
        decision1 = component.evaluate(context)
        decision2 = component.evaluate(context)
        decision3 = component.evaluate(context)

        # All decisions should be identical
        assert decision1.allowed == decision2.allowed == decision3.allowed
        assert decision1.reason == decision2.reason == decision3.reason
        assert decision1.confidence == decision2.confidence == decision3.confidence
        assert decision1.metadata["ev_value"] == decision2.metadata["ev_value"] == 0.25

    def test_custom_component_name(self):
        """Test that custom component name appears in metadata."""
        component = EVGateComponent(min_ev=0.0, name="CustomEVGate")

        context = {"expected_value": 0.1}
        decision = component.evaluate(context)

        assert decision.metadata["component"] == "CustomEVGate"

    def test_negative_ev_threshold(self):
        """Test that negative thresholds work (permissive filtering)."""
        # Allow negative EV up to -0.2
        component = EVGateComponent(min_ev=-0.2)

        # EV above threshold (but still negative)
        context = {"expected_value": -0.1}
        decision = component.evaluate(context)
        assert decision.allowed is True

        # EV below threshold
        context = {"expected_value": -0.3}
        decision = component.evaluate(context)
        assert decision.allowed is False
        assert decision.reason == "EV_BELOW_THRESHOLD"

    def test_high_ev_threshold(self):
        """Test that high thresholds work (strict filtering)."""
        # Require EV >= 0.5 (very strict)
        component = EVGateComponent(min_ev=0.5)

        # EV above threshold
        context = {"expected_value": 0.6}
        decision = component.evaluate(context)
        assert decision.allowed is True

        # EV below threshold (but still positive)
        context = {"expected_value": 0.3}
        decision = component.evaluate(context)
        assert decision.allowed is False

    def test_handles_invalid_ev_type(self):
        """Test that component handles non-numeric EV gracefully."""
        component = EVGateComponent(min_ev=0.0)

        # String EV (invalid)
        context = {"expected_value": "invalid"}
        decision = component.evaluate(context)
        assert decision.allowed is False
        assert decision.reason == "EV_MISSING"
        assert decision.metadata["ev_value"] is None
        assert "ev_raw" in decision.metadata

    def test_boundary_conditions(self):
        """Test boundary conditions (zero, very small, very large EV)."""
        component = EVGateComponent(min_ev=0.0)

        # Zero EV
        context = {"expected_value": 0.0}
        decision = component.evaluate(context)
        assert decision.allowed is True  # 0.0 >= 0.0

        # Very small positive EV
        context = {"expected_value": 0.001}
        decision = component.evaluate(context)
        assert decision.allowed is True

        # Very small negative EV
        context = {"expected_value": -0.001}
        decision = component.evaluate(context)
        assert decision.allowed is False

        # Very large EV
        context = {"expected_value": 100.0}
        decision = component.evaluate(context)
        assert decision.allowed is True
