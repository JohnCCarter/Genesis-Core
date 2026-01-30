"""Unit tests for RegimeFilterComponent."""

from core.strategy.components.regime_filter import RegimeFilterComponent


class TestRegimeFilterComponent:
    """Test RegimeFilterComponent behavior."""

    def test_allows_entry_when_regime_in_list(self):
        """Test that component allows entry when regime is in allowed list."""
        component = RegimeFilterComponent(allowed_regimes=["trending", "bull"])

        context = {"regime": "trending"}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.reason is None
        assert decision.confidence == 1.0
        assert decision.metadata["regime_found"] == "trending"
        assert decision.metadata["allowed_regimes"] == ["trending", "bull"]

    def test_allows_entry_when_regime_matches_exactly(self):
        """Test exact string match (case-sensitive)."""
        component = RegimeFilterComponent(allowed_regimes=["bull"])

        # Exact match
        context = {"regime": "bull"}
        decision = component.evaluate(context)
        assert decision.allowed is True

        # Different case - should NOT match (case-sensitive)
        context = {"regime": "Bull"}
        decision = component.evaluate(context)
        assert decision.allowed is False
        assert decision.reason == "REGIME_NOT_ALLOWED"

    def test_vetoes_entry_when_regime_not_in_list(self):
        """Test that component vetoes entry when regime not in allowed list."""
        component = RegimeFilterComponent(allowed_regimes=["trending", "bull"])

        context = {"regime": "ranging"}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "REGIME_NOT_ALLOWED"
        assert decision.confidence == 0.0
        assert decision.metadata["regime_found"] == "ranging"
        assert decision.metadata["allowed_regimes"] == ["trending", "bull"]

    def test_vetoes_entry_when_regime_missing_from_context(self):
        """Test that component vetoes when regime key is missing."""
        component = RegimeFilterComponent(allowed_regimes=["trending"])

        # Empty context
        context = {}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "REGIME_MISSING"
        assert decision.confidence == 0.0
        assert decision.metadata["regime_found"] is None
        assert decision.metadata["allowed_regimes"] == ["trending"]

    def test_vetoes_entry_when_regime_is_none(self):
        """Test that component vetoes when regime value is None."""
        component = RegimeFilterComponent(allowed_regimes=["trending"])

        context = {"regime": None}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "REGIME_MISSING"
        assert decision.metadata["regime_found"] is None

    def test_metadata_correctness_on_allow(self):
        """Test that metadata is correct when entry is allowed."""
        component = RegimeFilterComponent(allowed_regimes=["bull", "trending"])

        context = {"regime": "bull"}
        decision = component.evaluate(context)

        # Check all metadata fields
        assert "component" in decision.metadata
        assert decision.metadata["component"] == "RegimeFilter"
        assert "allowed_regimes" in decision.metadata
        assert decision.metadata["allowed_regimes"] == ["bull", "trending"]
        assert "regime_found" in decision.metadata
        assert decision.metadata["regime_found"] == "bull"

    def test_metadata_correctness_on_veto(self):
        """Test that metadata is correct when entry is vetoed."""
        component = RegimeFilterComponent(allowed_regimes=["trending"])

        context = {"regime": "ranging"}
        decision = component.evaluate(context)

        # Check metadata on veto
        assert decision.metadata["component"] == "RegimeFilter"
        assert decision.metadata["allowed_regimes"] == ["trending"]
        assert decision.metadata["regime_found"] == "ranging"

    def test_empty_allowed_list_vetoes_all(self):
        """Test that empty allowed_regimes list blocks all entries."""
        component = RegimeFilterComponent(allowed_regimes=[])

        context = {"regime": "trending"}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "REGIME_NOT_ALLOWED"

    def test_multiple_regimes_in_allowed_list(self):
        """Test that multiple allowed regimes work correctly."""
        component = RegimeFilterComponent(
            allowed_regimes=["trending", "bull", "balanced", "unknown"]
        )

        # Test each allowed regime
        for regime in ["trending", "bull", "balanced", "unknown"]:
            context = {"regime": regime}
            decision = component.evaluate(context)
            assert decision.allowed is True, f"Should allow regime: {regime}"
            assert decision.metadata["regime_found"] == regime

        # Test disallowed regimes
        for regime in ["ranging", "bear", "choppy"]:
            context = {"regime": regime}
            decision = component.evaluate(context)
            assert decision.allowed is False, f"Should veto regime: {regime}"
            assert decision.reason == "REGIME_NOT_ALLOWED"

    def test_custom_component_name(self):
        """Test that custom component name appears in metadata."""
        component = RegimeFilterComponent(allowed_regimes=["trending"], name="CustomRegimeFilter")

        context = {"regime": "trending"}
        decision = component.evaluate(context)

        assert decision.metadata["component"] == "CustomRegimeFilter"

    def test_handles_unknown_regime_gracefully(self):
        """Test that 'unknown' regime can be explicitly allowed or denied."""
        # Allow unknown
        component_allow = RegimeFilterComponent(allowed_regimes=["unknown"])
        context = {"regime": "unknown"}
        decision = component_allow.evaluate(context)
        assert decision.allowed is True

        # Deny unknown
        component_deny = RegimeFilterComponent(allowed_regimes=["trending"])
        decision = component_deny.evaluate(context)
        assert decision.allowed is False
        assert decision.reason == "REGIME_NOT_ALLOWED"

    def test_stateless_behavior(self):
        """Test that component is stateless (same context = same decision)."""
        component = RegimeFilterComponent(allowed_regimes=["trending", "bull"])

        context = {"regime": "trending"}

        # Evaluate multiple times
        decision1 = component.evaluate(context)
        decision2 = component.evaluate(context)
        decision3 = component.evaluate(context)

        # All decisions should be identical
        assert decision1.allowed == decision2.allowed == decision3.allowed
        assert decision1.reason == decision2.reason == decision3.reason
        assert decision1.confidence == decision2.confidence == decision3.confidence
