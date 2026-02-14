"""
Unit tests for ComponentContextBuilder key mapping fix (Bug #2).

Verifies that 'buy'/'sell' keys (model output) are correctly mapped to
ml_proba_long/short, with fallback to 'LONG'/'SHORT' for legacy compatibility.
"""

from core.strategy.components.context_builder import ComponentContextBuilder


class TestKeyMappingCoverage:
    """Test that both 'buy'/'sell' and 'LONG'/'SHORT' keys are handled."""

    def test_build_handles_buy_sell_keys(self):
        """Primary: 'buy'/'sell' keys should map to ml_proba_long/short."""
        result = {
            "probas": {"buy": 0.6, "sell": 0.4, "hold": 0.0},
            "regime": "trending",
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        assert context["ml_proba_long"] == 0.6
        assert context["ml_proba_short"] == 0.4

    def test_build_handles_long_short_keys_fallback(self):
        """Fallback: 'LONG'/'SHORT' keys should work for legacy compatibility."""
        result = {
            "probas": {"LONG": 0.55, "SHORT": 0.45},
            "regime": "ranging",
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        assert context["ml_proba_long"] == 0.55
        assert context["ml_proba_short"] == 0.45

    def test_build_case_insensitive_keys(self):
        """Keys should be case-insensitive (Buy, BUY, buy all work)."""
        result = {
            "probas": {"Buy": 0.7, "Sell": 0.3},
            "regime": "bull",
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        assert context["ml_proba_long"] == 0.7
        assert context["ml_proba_short"] == 0.3

    def test_build_prefers_buy_sell_over_long_short(self):
        """When both key sets present, 'buy'/'sell' should take precedence."""
        result = {
            "probas": {
                "buy": 0.65,
                "sell": 0.35,
                "LONG": 0.5,  # Should be ignored
                "SHORT": 0.5,  # Should be ignored
            },
            "regime": "trending",
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Should use 'buy'/'sell', not 'LONG'/'SHORT'
        assert context["ml_proba_long"] == 0.65
        assert context["ml_proba_short"] == 0.35


class TestEVFieldEmission:
    """Test that EV fields are only emitted when probas are present and valid."""

    def test_ev_fields_present_when_probas_valid(self):
        """EV fields should be calculated when probas are present."""
        result = {
            "probas": {"buy": 0.7, "sell": 0.3, "hold": 0.0},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # EV fields should be present
        assert "expected_value" in context
        assert "ev_long" in context
        assert "ev_short" in context

    def test_ev_fields_absent_when_probas_missing(self):
        """EV fields should NOT be emitted when probas missing (no degenerate 0.0)."""
        result = {"regime": "balanced"}
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # EV fields should NOT be present
        assert "expected_value" not in context
        assert "ev_long" not in context
        assert "ev_short" not in context

    def test_ev_fields_absent_when_probas_both_zero(self):
        """EV fields should NOT be emitted when probas are both 0.0 (degenerate)."""
        result = {
            "probas": {"buy": 0.0, "sell": 0.0, "hold": 0.0},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # EV fields should NOT be present (degenerate case)
        assert "expected_value" not in context


class TestEVMonotonicity:
    """Test EV behavior without hardcoding formula (monotonicity checks)."""

    def test_ev_increases_with_probability_gap(self):
        """EV should increase monotonically as buy-sell probability gap increases."""
        # Small gap
        result_small = {"probas": {"buy": 0.51, "sell": 0.49}}
        context_small = ComponentContextBuilder.build(result_small, {})

        # Large gap
        result_large = {"probas": {"buy": 0.8, "sell": 0.2}}
        context_large = ComponentContextBuilder.build(result_large, {})

        # EV should increase with gap
        assert context_large["expected_value"] > context_small["expected_value"]

    def test_ev_positive_when_buy_dominates(self):
        """EV should be positive when buy probability >> sell probability."""
        result = {"probas": {"buy": 0.8, "sell": 0.2}}
        context = ComponentContextBuilder.build(result, {})

        # Expected value should be positive (buy favored)
        assert context["expected_value"] > 0

    def test_ev_sign_matches_dominant_direction(self):
        """ev_long should be positive when buy > sell, negative when sell > buy."""
        # Buy dominant
        result_buy = {"probas": {"buy": 0.7, "sell": 0.3}}
        context_buy = ComponentContextBuilder.build(result_buy, {})
        assert context_buy["ev_long"] > 0
        assert context_buy["ev_short"] < 0

        # Sell dominant
        result_sell = {"probas": {"buy": 0.3, "sell": 0.7}}
        context_sell = ComponentContextBuilder.build(result_sell, {})
        assert context_sell["ev_long"] < 0
        assert context_sell["ev_short"] > 0

    def test_ev_symmetric_for_equal_probas(self):
        """When buy == sell, EV should be near zero (break-even)."""
        result = {"probas": {"buy": 0.5, "sell": 0.5}}
        context = ComponentContextBuilder.build(result, {})

        # EV should be approximately zero (symmetric)
        assert abs(context["expected_value"]) < 1e-6
        assert abs(context["ev_long"]) < 1e-6
        assert abs(context["ev_short"]) < 1e-6


class TestBackwardCompatibility:
    """Test that fix doesn't break existing behavior."""

    def test_ml_confidence_single_key_still_set(self):
        """Backward compat: 'ml_confidence' key should still be set."""
        result = {
            "probas": {"buy": 0.6, "sell": 0.4},
            "confidence": {"buy": 0.6, "sell": 0.4, "overall": 0.6},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Backward compat key should be set
        assert "ml_confidence" in context
        assert context["ml_confidence"] > 0

    def test_confidence_dict_still_mapped(self):
        """confidence dict (buy/sell keys) should still be mapped correctly."""
        result = {
            "confidence": {"buy": 0.65, "sell": 0.35, "overall": 0.65},
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        assert context["ml_confidence_long"] == 0.65
        assert context["ml_confidence_short"] == 0.35
