"""
Unit tests for individual POC components (ML, HTF, ATR).
"""

import pytest

from core.strategy.components.atr_filter import ATRFilterComponent
from core.strategy.components.htf_gate import HTFGateComponent
from core.strategy.components.ml_confidence import MLConfidenceComponent


class TestMLConfidenceComponent:
    """Tests for ML Confidence component."""

    def test_name(self):
        """Component should return correct name."""
        comp = MLConfidenceComponent()
        assert comp.name() == "ml_confidence"

    def test_threshold_validation(self):
        """Threshold should be validated to 0-1 range."""
        with pytest.raises(ValueError, match="Threshold must be 0-1"):
            MLConfidenceComponent(threshold=1.5)

        with pytest.raises(ValueError, match="Threshold must be 0-1"):
            MLConfidenceComponent(threshold=-0.1)

    def test_passes_above_threshold(self):
        """Should allow trade when confidence >= threshold."""
        comp = MLConfidenceComponent(threshold=0.5)
        result = comp.evaluate({"ml_confidence": 0.6})

        assert result.allowed is True
        assert result.confidence == 0.6
        assert result.reason is None

    def test_blocks_below_threshold(self):
        """Should block trade when confidence < threshold."""
        comp = MLConfidenceComponent(threshold=0.5)
        result = comp.evaluate({"ml_confidence": 0.4})

        assert result.allowed is False
        assert result.confidence == 0.4
        assert result.reason == "ML_CONFIDENCE_LOW"

    def test_missing_confidence(self):
        """Should block when ml_confidence key is missing."""
        comp = MLConfidenceComponent()
        result = comp.evaluate({})

        assert result.allowed is False
        assert result.confidence == 0.0
        assert result.reason == "ML_CONFIDENCE_MISSING"

    def test_invalid_confidence_type(self):
        """Should block when ml_confidence is not a number."""
        comp = MLConfidenceComponent()
        result = comp.evaluate({"ml_confidence": "high"})

        assert result.allowed is False
        assert result.reason == "ML_CONFIDENCE_MISSING"


class TestHTFGateComponent:
    """Tests for HTF Gate component."""

    def test_name(self):
        """Component should return correct name."""
        comp = HTFGateComponent()
        assert comp.name() == "htf_gate"

    def test_default_regimes(self):
        """Should use default regimes if none specified."""
        comp = HTFGateComponent()
        assert comp.required_regimes == ["trending", "bull"]

    def test_custom_regimes(self):
        """Should accept custom regime list."""
        comp = HTFGateComponent(required_regimes=["bull", "bear"])
        assert comp.required_regimes == ["bull", "bear"]

    def test_passes_in_required_regime(self):
        """Should allow trade when HTF regime is in required list."""
        comp = HTFGateComponent(required_regimes=["trending"])
        result = comp.evaluate({"htf_regime": "trending"})

        assert result.allowed is True
        assert result.confidence == 1.0
        assert result.reason is None

    def test_blocks_in_wrong_regime(self):
        """Should block trade when HTF regime is not in required list."""
        comp = HTFGateComponent(required_regimes=["trending"])
        result = comp.evaluate({"htf_regime": "ranging"})

        assert result.allowed is False
        assert result.confidence == 0.0
        assert result.reason == "HTF_REGIME_RANGING"

    def test_missing_regime(self):
        """Should block when htf_regime key is missing."""
        comp = HTFGateComponent()
        result = comp.evaluate({})

        assert result.allowed is False
        assert result.reason == "HTF_REGIME_UNKNOWN"

    def test_invalid_regime_type(self):
        """Should block when htf_regime is not a string."""
        comp = HTFGateComponent()
        result = comp.evaluate({"htf_regime": 123})

        assert result.allowed is False
        assert result.reason == "HTF_REGIME_MISSING"


class TestATRFilterComponent:
    """Tests for ATR Filter component."""

    def test_name(self):
        """Component should return correct name."""
        comp = ATRFilterComponent()
        assert comp.name() == "atr_filter"

    def test_min_ratio_validation(self):
        """min_ratio should be validated to >= 0."""
        with pytest.raises(ValueError, match="min_ratio must be >= 0"):
            ATRFilterComponent(min_ratio=-0.5)

        comp = ATRFilterComponent(min_ratio=0.0)
        assert comp.min_ratio == 0.0

    def test_passes_above_ratio(self):
        """Should allow trade when ATR/ATR_MA >= min_ratio."""
        comp = ATRFilterComponent(min_ratio=1.0)
        result = comp.evaluate({"atr": 0.02, "atr_ma": 0.015})

        assert result.allowed is True
        assert result.reason is None
        assert result.metadata["atr_ratio"] > 1.0

    def test_blocks_below_ratio(self):
        """Should block trade when ATR/ATR_MA < min_ratio."""
        comp = ATRFilterComponent(min_ratio=1.0)
        result = comp.evaluate({"atr": 0.01, "atr_ma": 0.015})

        assert result.allowed is False
        assert result.reason == "ATR_TOO_LOW"

    def test_confidence_normalization(self):
        """Confidence should be normalized (ratio / 2.0, max 1.0)."""
        comp = ATRFilterComponent(min_ratio=1.0)

        result = comp.evaluate({"atr": 0.02, "atr_ma": 0.01})
        assert result.confidence == 1.0

        result = comp.evaluate({"atr": 0.01, "atr_ma": 0.01})
        assert result.confidence == 0.5

    def test_missing_atr_data(self):
        """Should block when ATR data is missing."""
        comp = ATRFilterComponent()

        result = comp.evaluate({})
        assert result.allowed is False
        assert result.reason == "ATR_DATA_MISSING"

        result = comp.evaluate({"atr": 0.01})
        assert result.allowed is False
        assert result.reason == "ATR_DATA_MISSING"

    def test_invalid_atr_ma(self):
        """Should block when ATR_MA is <= 0."""
        comp = ATRFilterComponent()
        result = comp.evaluate({"atr": 0.01, "atr_ma": 0.0})

        assert result.allowed is False
        assert result.reason == "ATR_MA_INVALID"
