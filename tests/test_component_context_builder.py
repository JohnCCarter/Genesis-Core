"""Tests for ComponentContextBuilder."""

import pytest

from core.strategy.components.context_builder import ComponentContextBuilder


class TestComponentContextBuilder:
    """Test ComponentContextBuilder."""

    def test_build_with_full_context(self):
        """Test building context from full pipeline output."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "confidence": {"buy": 0.70, "sell": 0.30},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {
                "atr_14": 150.0,
                "rsi": 60.0,
                "adx": 25.0,
                "ema_delta_pct": 0.5,
            },
        }
        meta = {
            "features": {
                "current_atr_used": 150.0,
                "htf_fibonacci": {"available": True},
                "ltf_fibonacci": {"available": False},
            }
        }
        candles = {"close": [100.0, 105.0, 110.0], "timestamp": [1000, 2000, 3000]}

        context = ComponentContextBuilder.build(result, meta, candles=candles)

        # Check ML confidence mapping
        assert context["ml_proba_long"] == 0.65
        assert context["ml_proba_short"] == 0.35
        assert context["ml_confidence_long"] == 0.70
        assert context["ml_confidence_short"] == 0.30
        assert context["ml_confidence"] == 0.70  # defaults to LONG confidence

        # Check EV calculation (new in Phase 2)
        # EV_long = 0.65 * 1.0 - 0.35 = 0.30
        # EV_short = 0.35 * 1.0 - 0.65 = -0.30
        # expected_value = max(0.30, -0.30) = 0.30
        assert context["ev_long"] == pytest.approx(0.30, abs=1e-10)
        assert context["ev_short"] == pytest.approx(-0.30, abs=1e-10)
        assert context["expected_value"] == pytest.approx(0.30, abs=1e-10)

        # Check regime
        assert context["regime"] == "trending"
        assert context["htf_regime"] == "bull"

        # Check features
        assert context["atr"] == 150.0
        assert context["rsi"] == 60.0
        assert context["adx"] == 25.0
        assert context["ema_delta_pct"] == 0.5

        # Check action
        assert context["action"] == "LONG"

        # Check meta
        assert context["current_atr"] == 150.0
        assert context["htf_fib_available"] is True
        assert context["ltf_fib_available"] is False

        # Check candles
        assert context["current_price"] == 110.0
        assert context["timestamp"] == 3000

    def test_build_with_missing_probas(self):
        """Test when probas is missing or empty."""
        result = {
            "confidence": {"buy": 0.70, "sell": 0.30},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {},
        }
        meta = {"features": {}}

        context = ComponentContextBuilder.build(result, meta)

        # Should fallback to confidence
        assert "ml_proba_long" not in context
        assert context["ml_confidence_long"] == 0.70
        assert context["ml_confidence"] == 0.70

    def test_build_with_missing_confidence(self):
        """Test when confidence is missing."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {},
        }
        meta = {"features": {}}

        context = ComponentContextBuilder.build(result, meta)

        # Should fallback to probas
        assert context["ml_proba_long"] == 0.65
        assert "ml_confidence_long" not in context
        assert context["ml_confidence"] == 0.65

    def test_build_with_missing_features(self):
        """Test when features are missing."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
        }
        meta = {}

        context = ComponentContextBuilder.build(result, meta)

        # Should not crash, just omit feature keys
        assert "atr" not in context
        assert "rsi" not in context
        assert context["ml_confidence"] == 0.65

    def test_build_with_no_candles(self):
        """Test when candles are not provided."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {},
        }
        meta = {"features": {}}

        context = ComponentContextBuilder.build(result, meta, candles=None)

        # Should not crash
        assert "current_price" not in context
        assert "timestamp" not in context

    def test_build_with_empty_candles(self):
        """Test when candles dict is empty."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {},
        }
        meta = {"features": {}}

        context = ComponentContextBuilder.build(result, meta, candles={})

        # Should not crash
        assert "current_price" not in context
        assert "timestamp" not in context

    def test_build_with_none_values(self):
        """Test when pipeline returns None for some values."""
        result = {
            "probas": None,
            "confidence": {"buy": 0.70, "sell": 0.30},
            "regime": None,
            "htf_regime": "bull",
            "action": "LONG",
            "features": None,
        }
        meta = {"features": None}

        context = ComponentContextBuilder.build(result, meta)

        # Should handle None gracefully
        assert "ml_proba_long" not in context
        assert context["ml_confidence_long"] == 0.70
        assert context["regime"] is None
        assert context["htf_regime"] == "bull"

    def test_atr_ma_approximation(self):
        """Test ATR MA approximation when not available."""
        result = {
            "probas": {"LONG": 0.65, "SHORT": 0.35},
            "regime": "trending",
            "htf_regime": "bull",
            "action": "LONG",
            "features": {"atr_14": 100.0},
        }
        meta = {"features": {}}

        context = ComponentContextBuilder.build(result, meta)

        # Should approximate ATR MA as 0.9 * ATR
        assert context["atr"] == 100.0
        assert context["atr_ma"] == 90.0

    def test_get_required_keys(self):
        """Test required keys list."""
        keys = ComponentContextBuilder.get_required_keys()

        assert "ml_confidence" in keys
        assert "regime" in keys
        assert "htf_regime" in keys
        assert "atr" in keys
        assert "action" in keys

    def test_get_optional_keys(self):
        """Test optional keys list."""
        keys = ComponentContextBuilder.get_optional_keys()

        assert "ml_proba_long" in keys
        assert "rsi" in keys
        assert "current_price" in keys

    def test_ev_calculation_determinism(self):
        """Test that EV calculation is deterministic and correct."""
        # Test case 1: Balanced probabilities (50/50)
        result = {"probas": {"LONG": 0.5, "SHORT": 0.5}}
        context = ComponentContextBuilder.build(result, {})

        # EV_long = 0.5 * 1.0 - 0.5 = 0.0
        # EV_short = 0.5 * 1.0 - 0.5 = 0.0
        # expected_value = max(0.0, 0.0) = 0.0
        assert context["ev_long"] == 0.0
        assert context["ev_short"] == 0.0
        assert context["expected_value"] == 0.0

        # Test case 2: Strong long bias (70/30)
        result = {"probas": {"LONG": 0.7, "SHORT": 0.3}}
        context = ComponentContextBuilder.build(result, {})

        # EV_long = 0.7 * 1.0 - 0.3 = 0.4
        # EV_short = 0.3 * 1.0 - 0.7 = -0.4
        # expected_value = max(0.4, -0.4) = 0.4
        assert context["ev_long"] == pytest.approx(0.4, abs=1e-10)
        assert context["ev_short"] == pytest.approx(-0.4, abs=1e-10)
        assert context["expected_value"] == pytest.approx(0.4, abs=1e-10)

        # Test case 3: Strong short bias (30/70)
        result = {"probas": {"LONG": 0.3, "SHORT": 0.7}}
        context = ComponentContextBuilder.build(result, {})

        # EV_long = 0.3 * 1.0 - 0.7 = -0.4
        # EV_short = 0.7 * 1.0 - 0.3 = 0.4
        # expected_value = max(-0.4, 0.4) = 0.4
        assert context["ev_long"] == pytest.approx(-0.4, abs=1e-10)
        assert context["ev_short"] == pytest.approx(0.4, abs=1e-10)
        assert context["expected_value"] == pytest.approx(0.4, abs=1e-10)

    def test_ev_missing_when_probas_incomplete(self):
        """Test that EV is not calculated when probas are missing or incomplete."""
        # Missing probas entirely
        result = {"regime": "trending"}
        context = ComponentContextBuilder.build(result, {})
        assert "expected_value" not in context
        assert "ev_long" not in context
        assert "ev_short" not in context

        # Probas is None
        result = {"probas": None}
        context = ComponentContextBuilder.build(result, {})
        assert "expected_value" not in context

        # Empty probas dict
        result = {"probas": {}}
        context = ComponentContextBuilder.build(result, {})
        assert "expected_value" not in context

    def test_ev_boundary_cases(self):
        """Test EV calculation at boundary conditions."""
        # Case 1: 100% LONG probability (edge case)
        result = {"probas": {"LONG": 1.0, "SHORT": 0.0}}
        context = ComponentContextBuilder.build(result, {})

        # EV_long = 1.0 * 1.0 - 0.0 = 1.0
        # EV_short = 0.0 * 1.0 - 1.0 = -1.0
        # expected_value = max(1.0, -1.0) = 1.0
        assert context["ev_long"] == 1.0
        assert context["ev_short"] == -1.0
        assert context["expected_value"] == 1.0

        # Case 2: 100% SHORT probability
        result = {"probas": {"LONG": 0.0, "SHORT": 1.0}}
        context = ComponentContextBuilder.build(result, {})

        assert context["ev_long"] == -1.0
        assert context["ev_short"] == 1.0
        assert context["expected_value"] == 1.0
