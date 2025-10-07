"""Tests for label generation (src/core/ml/labeling.py)."""

import pytest

from core.ml.labeling import (
    align_features_with_labels,
    generate_labels,
    generate_multiclass_labels,
)


class TestGenerateLabels:
    """Tests for binary label generation."""

    def test_basic_binary_labels(self):
        """Test basic binary label generation."""
        prices = [100, 102, 105, 103, 101, 99]
        labels = generate_labels(prices, lookahead_bars=2)

        # prices[0]=100 -> prices[2]=105: +5% -> label=1 (up)
        # prices[1]=102 -> prices[3]=103: +0.98% -> label=1 (up)
        # prices[2]=105 -> prices[4]=101: -3.8% -> label=0 (down)
        # prices[3]=103 -> prices[5]=99: -3.9% -> label=0 (down)
        # prices[4]=101 -> future not available -> None
        # prices[5]=99 -> future not available -> None

        assert len(labels) == 6
        assert labels[0] == 1  # Up
        assert labels[1] == 1  # Up
        assert labels[2] == 0  # Down
        assert labels[3] == 0  # Down
        assert labels[4] is None  # No future data
        assert labels[5] is None  # No future data

    def test_threshold_filtering(self):
        """Test that threshold_pct filters small movements."""
        prices = [100, 100.1, 99.9, 101, 99]
        labels = generate_labels(prices, lookahead_bars=1, threshold_pct=0.5)

        # prices[0]=100 -> prices[1]=100.1: +0.1% < 0.5% -> label=0
        # prices[1]=100.1 -> prices[2]=99.9: -0.2% < 0.5% -> label=0
        # prices[2]=99.9 -> prices[3]=101: +1.1% > 0.5% -> label=1
        # prices[3]=101 -> prices[4]=99: -2% < 0.5% -> label=0
        # prices[4]=99 -> future not available -> None

        assert labels[0] == 0
        assert labels[1] == 0
        assert labels[2] == 1
        assert labels[3] == 0
        assert labels[4] is None

    def test_empty_prices(self):
        """Test with empty price list."""
        labels = generate_labels([])
        assert labels == []

    def test_single_price(self):
        """Test with single price (no future data)."""
        labels = generate_labels([100.0])
        assert labels == [None]

    def test_lookahead_equals_length(self):
        """Test when lookahead_bars equals data length."""
        prices = [100, 102, 105]
        labels = generate_labels(prices, lookahead_bars=3)
        # All should be None (not enough future data)
        assert labels == [None, None, None]

    def test_lookahead_too_large(self):
        """Test when lookahead_bars > data length."""
        prices = [100, 102]
        labels = generate_labels(prices, lookahead_bars=10)
        assert labels == [None, None]

    def test_zero_lookahead_raises(self):
        """Test that zero lookahead raises ValueError."""
        with pytest.raises(ValueError, match="lookahead_bars must be positive"):
            generate_labels([100, 102], lookahead_bars=0)

    def test_negative_lookahead_raises(self):
        """Test that negative lookahead raises ValueError."""
        with pytest.raises(ValueError, match="lookahead_bars must be positive"):
            generate_labels([100, 102], lookahead_bars=-5)

    def test_zero_price_handling(self):
        """Test that zero prices are handled (label=None)."""
        prices = [100, 0, 105, 103]
        labels = generate_labels(prices, lookahead_bars=1)

        assert labels[0] is None  # current=100, future=0 (invalid)
        assert labels[1] is None  # current=0 (invalid)
        assert labels[2] == 0  # current=105, future=103 (down)
        assert labels[3] is None  # No future

    def test_negative_price_handling(self):
        """Test that negative prices are handled (label=None)."""
        prices = [100, -50, 105]
        labels = generate_labels(prices, lookahead_bars=1)

        assert labels[0] is None  # future=-50 (invalid)
        assert labels[1] is None  # current=-50 (invalid)
        assert labels[2] is None  # No future

    def test_flat_prices(self):
        """Test with flat prices (no movement)."""
        prices = [100, 100, 100, 100, 100]
        labels = generate_labels(prices, lookahead_bars=2, threshold_pct=0.0)

        # All should be 0 (no increase)
        assert labels[0] == 0
        assert labels[1] == 0
        assert labels[2] == 0
        assert labels[3] is None
        assert labels[4] is None


class TestGenerateMulticlassLabels:
    """Tests for 3-class label generation."""

    def test_basic_multiclass_labels(self):
        """Test basic 3-class label generation."""
        prices = [100, 102, 105, 103, 99, 98]
        labels = generate_multiclass_labels(
            prices, lookahead_bars=2, up_threshold_pct=2.0, down_threshold_pct=-2.0
        )

        # prices[0]=100 -> prices[2]=105: +5% > 2% -> label=2 (strong up)
        # prices[1]=102 -> prices[3]=103: +0.98% in [-2%, 2%] -> label=1 (neutral)
        # prices[2]=105 -> prices[4]=99: -5.7% < -2% -> label=0 (strong down)
        # prices[3]=103 -> prices[5]=98: -4.9% < -2% -> label=0 (strong down)
        # prices[4]=99 -> future not available -> None
        # prices[5]=98 -> future not available -> None

        assert labels[0] == 2  # Strong up
        assert labels[1] == 1  # Neutral
        assert labels[2] == 0  # Strong down
        assert labels[3] == 0  # Strong down
        assert labels[4] is None
        assert labels[5] is None

    def test_threshold_validation(self):
        """Test that up_threshold must be > down_threshold."""
        with pytest.raises(ValueError, match="up_threshold_pct must be > down_threshold_pct"):
            generate_multiclass_labels([100, 102], lookahead_bars=1, up_threshold_pct=-1.0, down_threshold_pct=1.0)

    def test_equal_thresholds_raises(self):
        """Test that equal thresholds raise ValueError."""
        with pytest.raises(ValueError, match="up_threshold_pct must be > down_threshold_pct"):
            generate_multiclass_labels([100, 102], lookahead_bars=1, up_threshold_pct=0.5, down_threshold_pct=0.5)

    def test_narrow_neutral_zone(self):
        """Test with very narrow neutral zone."""
        prices = [100, 100.1, 99.9, 100.0]
        labels = generate_multiclass_labels(
            prices, lookahead_bars=1, up_threshold_pct=0.05, down_threshold_pct=-0.05
        )

        # prices[0]=100 -> prices[1]=100.1: +0.1% > 0.05% -> label=2
        # prices[1]=100.1 -> prices[2]=99.9: -0.2% < -0.05% -> label=0
        # prices[2]=99.9 -> prices[3]=100.0: +0.1% > 0.05% -> label=2
        # prices[3]=100.0 -> no future -> None

        assert labels[0] == 2
        assert labels[1] == 0
        assert labels[2] == 2
        assert labels[3] is None

    def test_wide_neutral_zone(self):
        """Test with very wide neutral zone."""
        prices = [100, 105, 95, 100]
        labels = generate_multiclass_labels(
            prices, lookahead_bars=1, up_threshold_pct=10.0, down_threshold_pct=-10.0
        )

        # prices[0]=100 -> prices[1]=105: +5% in [-10%, 10%] -> label=1
        # prices[1]=105 -> prices[2]=95: -9.5% in [-10%, 10%] -> label=1
        # prices[2]=95 -> prices[3]=100: +5.3% in [-10%, 10%] -> label=1
        # prices[3]=100 -> no future -> None

        assert labels[0] == 1
        assert labels[1] == 1
        assert labels[2] == 1
        assert labels[3] is None


class TestAlignFeaturesWithLabels:
    """Tests for features-labels alignment."""

    def test_basic_alignment(self):
        """Test basic alignment with valid labels."""
        labels = [1, 0, 1, 0, None, None]
        start, end = align_features_with_labels(6, labels)

        assert start == 0
        assert end == 4  # First 4 have valid labels

    def test_all_valid_labels(self):
        """Test when all labels are valid."""
        labels = [1, 0, 1, 0, 1]
        start, end = align_features_with_labels(5, labels)

        assert start == 0
        assert end == 5

    def test_all_none_labels(self):
        """Test when all labels are None."""
        labels = [None, None, None]
        start, end = align_features_with_labels(3, labels)

        # Should return empty range
        assert start == 0
        assert end == 0

    def test_some_leading_nones(self):
        """Test with some leading None values."""
        labels = [None, None, 1, 0, 1, None]
        start, end = align_features_with_labels(6, labels)

        assert start == 2  # First valid at index 2
        assert end == 5  # Last valid at index 4

    def test_mismatched_count_raises(self):
        """Test that mismatched counts raise ValueError."""
        labels = [1, 0, None]
        with pytest.raises(ValueError, match="Features count .* must match labels length"):
            align_features_with_labels(5, labels)

    def test_empty_labels(self):
        """Test with empty labels."""
        start, end = align_features_with_labels(0, [])
        assert start == 0
        assert end == 0


class TestIntegrationWithRealData:
    """Integration tests with realistic data."""

    def test_realistic_price_series(self):
        """Test with realistic price series."""
        # Simulate BTC prices
        prices = [
            50000, 50500, 51000, 50800, 51200,
            51500, 51800, 51400, 51600, 52000,
            51800, 51500, 51200, 51000, 50800
        ]
        labels = generate_labels(prices, lookahead_bars=5)

        # Verify no lookahead bias
        for i, label in enumerate(labels):
            if label is not None:
                future_idx = i + 5
                assert future_idx < len(prices)
                # Verify label correctness
                pct_change = ((prices[future_idx] - prices[i]) / prices[i]) * 100
                expected_label = 1 if pct_change > 0 else 0
                assert label == expected_label

    def test_label_distribution_balance(self):
        """Test that labels have reasonable distribution."""
        # Alternating up/down
        prices = [100 + (i % 2) * 2 for i in range(100)]
        labels = generate_labels(prices, lookahead_bars=1)

        valid_labels = [l for l in labels if l is not None]
        up_count = sum(1 for l in valid_labels if l == 1)
        down_count = sum(1 for l in valid_labels if l == 0)

        # Should be roughly balanced
        assert up_count > 0
        assert down_count > 0
        assert abs(up_count - down_count) < len(valid_labels) * 0.2  # Within 20%

    def test_alignment_with_features(self):
        """Test alignment matches expected behavior."""
        prices = [100, 102, 105, 103, 101, 99, 98, 97]
        labels = generate_labels(prices, lookahead_bars=3)

        # Last 3 should be None
        assert labels[-1] is None
        assert labels[-2] is None
        assert labels[-3] is None

        # First 5 should be valid
        for i in range(5):
            assert labels[i] in (0, 1)

        # Alignment should give us first 5 rows
        start, end = align_features_with_labels(len(labels), labels)
        assert start == 0
        assert end == 5
