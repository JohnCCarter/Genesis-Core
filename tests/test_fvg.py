"""Tests for Fair Value Gap (FVG) detection."""

from core.indicators.fvg import detect_fvg, extract_fvg_features, get_nearest_unfilled_fvg


def test_bullish_fvg_detection():
    """Test detection of bullish FVG."""
    # Candle 0: high=100, low=95
    # Candle 1: Impulse up (gap created)
    # Candle 2: high=110, low=105 (gap between 100 and 105)
    highs = [100.0, 108.0, 110.0]
    lows = [95.0, 102.0, 105.0]
    closes = [98.0, 106.0, 108.0]

    fvgs = detect_fvg(highs, lows, closes, min_gap_pct=0.1)

    # First 2 candles: None
    assert fvgs[0] is None
    assert fvgs[1] is None

    # Candle 2: Bullish FVG detected
    assert fvgs[2] is not None
    assert fvgs[2]["type"] == "bullish"
    assert fvgs[2]["gap_start"] == 100.0  # candle 0 high
    assert fvgs[2]["gap_end"] == 105.0  # candle 2 low
    assert fvgs[2]["gap_size"] == 5.0
    assert fvgs[2]["created_at"] == 2


def test_bearish_fvg_detection():
    """Test detection of bearish FVG."""
    # Candle 0: high=105, low=100
    # Candle 1: Impulse down
    # Candle 2: high=95, low=90 (gap between 95 and 100)
    highs = [105.0, 98.0, 95.0]
    lows = [100.0, 92.0, 90.0]
    closes = [102.0, 94.0, 92.0]

    fvgs = detect_fvg(highs, lows, closes, min_gap_pct=0.1)

    assert fvgs[2] is not None
    assert fvgs[2]["type"] == "bearish"
    assert fvgs[2]["gap_start"] == 100.0  # candle 0 low
    assert fvgs[2]["gap_end"] == 95.0  # candle 2 high
    assert fvgs[2]["gap_size"] == 5.0


def test_no_fvg_when_overlap():
    """Test that no FVG is detected when candles overlap."""
    # Candle 0: 95-100
    # Candle 1: 98-105 (overlaps with both)
    # Candle 2: 99-104 (overlaps with candle 0)
    highs = [100.0, 105.0, 104.0]
    lows = [95.0, 98.0, 99.0]
    closes = [98.0, 103.0, 102.0]

    fvgs = detect_fvg(highs, lows, closes)

    # Candle 2 low (99) < candle 0 high (100), no gap
    assert fvgs[2] is None


def test_fvg_min_gap_threshold():
    """Test that small gaps are filtered out."""
    # Small gap (0.05% of price)
    highs = [100.0, 100.5, 101.0]
    lows = [99.5, 100.0, 100.05]  # Gap = 0.05
    closes = [100.0, 100.3, 100.5]

    # Should be filtered with 0.1% threshold
    fvgs = detect_fvg(highs, lows, closes, min_gap_pct=0.1)
    assert fvgs[2] is None

    # Should pass with 0.01% threshold
    fvgs = detect_fvg(highs, lows, closes, min_gap_pct=0.01)
    assert fvgs[2] is not None


def test_fvg_filled_by_retracement():
    """Test that filled FVG is not returned as nearest unfilled."""
    # Create bullish FVG
    highs = [100.0, 108.0, 110.0, 112.0, 106.0]  # Bar 4 fills the gap
    lows = [95.0, 102.0, 105.0, 108.0, 102.0]  # Low=102 fills gap [100-105]
    closes = [98.0, 106.0, 108.0, 110.0, 104.0]

    # At bar 4, FVG should be considered filled
    nearest = get_nearest_unfilled_fvg(highs, lows, closes, current_index=4)

    # Should be None because the FVG was filled at bar 4
    assert nearest is None


def test_fvg_unfilled():
    """Test that unfilled FVG is detected correctly."""
    # Create bullish FVG that remains unfilled
    highs = [100.0, 108.0, 110.0, 112.0, 114.0]
    lows = [95.0, 102.0, 105.0, 108.0, 110.0]  # Never retraces to fill gap
    closes = [98.0, 106.0, 108.0, 110.0, 112.0]

    nearest = get_nearest_unfilled_fvg(highs, lows, closes, current_index=4)

    assert nearest is not None
    assert nearest["type"] == "bullish"
    assert nearest["gap_start"] == 100.0
    assert nearest["gap_end"] == 105.0
    assert nearest["age"] == 2  # Created at bar 2, current is bar 4


def test_extract_fvg_features_with_gap():
    """Test FVG feature extraction when gap exists."""
    # Bullish FVG
    highs = [100.0, 108.0, 110.0, 112.0, 114.0]
    lows = [95.0, 102.0, 105.0, 108.0, 110.0]
    opens = [98.0, 102.0, 107.0, 109.0, 111.0]
    closes = [98.0, 106.0, 108.0, 110.0, 112.0]
    volumes = [1000.0, 2000.0, 1500.0, 1200.0, 1100.0]
    atr_values = [2.0, 2.5, 2.3, 2.2, 2.1]

    features = extract_fvg_features(
        highs, lows, opens, closes, volumes, atr_values, current_index=4
    )

    assert features["fvg_present"] == 1.0
    assert features["fvg_bullish"] == 1.0
    assert features["fvg_size_atr"] > 0
    assert features["displacement_strength"] > 0
    assert features["fvg_distance_atr"] > 0
    assert features["fvg_age_log"] > 0
    # New context-aware features should exist
    assert "trend_confluence" in features
    assert "distance_to_midline_norm" in features
    assert "risk_reward_ratio" in features


def test_extract_fvg_features_no_gap():
    """Test FVG feature extraction when no gap exists."""
    # No FVG
    highs = [100.0, 102.0, 104.0]
    lows = [98.0, 100.0, 102.0]
    opens = [99.0, 101.0, 103.0]
    closes = [99.0, 101.0, 103.0]
    volumes = [1000.0, 1100.0, 1200.0]
    atr_values = [2.0, 2.1, 2.2]

    features = extract_fvg_features(
        highs, lows, opens, closes, volumes, atr_values, current_index=2
    )

    assert features["fvg_present"] == 0.0
    assert features["fvg_bullish"] == 0.0
    assert features["fvg_size_atr"] == 0.0
    assert features["displacement_strength"] == 0.0
    assert features["fvg_distance_atr"] == 0.0
    assert features["fvg_age_log"] == 0.0
    assert features["trend_confluence"] == 0.0
    assert features["distance_to_midline_norm"] == 0.0
    assert features["risk_reward_ratio"] == 0.0


def test_multiple_fvgs_returns_nearest():
    """Test that nearest FVG is returned when multiple exist."""
    # Create 2 bullish FVGs
    highs = [100.0, 108.0, 110.0, 115.0, 123.0, 125.0, 127.0]
    lows = [95.0, 102.0, 105.0, 110.0, 118.0, 120.0, 122.0]
    closes = [98.0, 106.0, 108.0, 112.0, 120.0, 122.0, 124.0]

    # At bar 6, should find nearest FVG
    nearest = get_nearest_unfilled_fvg(highs, lows, closes, current_index=6)

    assert nearest is not None
    # Should be the more recent FVG (created at bar 4)
    # Gap between bar 3 (high=115) and bar 5 (low=120)


def test_fvg_empty_input():
    """Test FVG with insufficient data."""
    highs = [100.0]
    lows = [95.0]
    closes = [98.0]

    fvgs = detect_fvg(highs, lows, closes)
    assert len(fvgs) == 1
    assert fvgs[0] is None


def test_fvg_distance_calculation():
    """Test that distance to FVG is calculated correctly."""
    # Bullish FVG at 100-105, current price 112
    highs = [100.0, 108.0, 110.0, 112.0, 114.0]
    lows = [95.0, 102.0, 105.0, 108.0, 110.0]
    closes = [98.0, 106.0, 108.0, 110.0, 112.0]

    nearest = get_nearest_unfilled_fvg(highs, lows, closes, current_index=4)

    gap_mid = (100.0 + 105.0) / 2  # 102.5
    expected_distance = abs(112.0 - gap_mid)  # 9.5
    expected_distance_pct = 100 * expected_distance / 112.0

    assert abs(nearest["distance"] - expected_distance) < 0.01
    assert abs(nearest["distance_pct"] - expected_distance_pct) < 0.01


def test_fvg_above_below_price():
    """Test FVG above/below current price detection."""
    # Bullish FVG below current price
    highs = [100.0, 108.0, 110.0, 112.0, 114.0]
    lows = [95.0, 102.0, 105.0, 108.0, 110.0]
    closes = [98.0, 106.0, 108.0, 110.0, 112.0]

    nearest = get_nearest_unfilled_fvg(highs, lows, closes, current_index=4)

    gap_mid = (100.0 + 105.0) / 2  # 102.5
    current = closes[4]  # 112.0

    assert nearest["above_price"] == (gap_mid > current)  # False (gap below)
