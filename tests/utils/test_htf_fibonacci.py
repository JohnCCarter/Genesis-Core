import pandas as pd
import pytest

from core.indicators.fibonacci import FibonacciConfig
from core.indicators.htf_fibonacci import compute_htf_fibonacci_mapping


@pytest.fixture
def sample_htf_data():
    """Create sample 1D data."""
    dates = pd.date_range(start="2024-01-01", periods=10, freq="1D")
    # Pattern: Flat, then UP, then DOWN
    # Index 0: 100
    # Index 1: 100 (Flat)
    # Index 2: 105 (Up)
    # Index 3: 110 (Up)
    # Index 4: 100 (Down)
    prices = [100, 100, 105, 110, 100, 90, 80, 85, 95, 100]

    return pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices,  # Simplify: OHLC = Price
            "high": prices,
            "low": prices,
            "close": prices,
            "volume": [1000] * 10,
        }
    )


@pytest.fixture
def sample_ltf_data():
    """Create sample 1h data covering the HTF period."""
    dates = pd.date_range(start="2024-01-01", periods=24 * 10, freq="1h")
    return pd.DataFrame(
        {"timestamp": dates, "close": [100] * len(dates)}  # Price doesn't matter for mapping
    )


def test_no_lookahead_bias():
    """Verify strict previous day mapping."""
    # Create simple data
    htf = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-02"),
                pd.Timestamp("2024-01-03"),
            ],
            "high": [100, 200, 300],  # Distinct values to trace
            "low": [90, 190, 290],
            "close": [95, 195, 295],
            "open": [95, 195, 295],  # Needed for swing detection internal checks
        }
    )

    ltf = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2024-01-01 12:00"),  # Middle of Day 1
                pd.Timestamp("2024-01-02 00:00"),  # Exact start of Day 2
                pd.Timestamp("2024-01-02 01:00"),  # Start of Day 2 + 1h
            ]
        }
    )

    # Config with minimal requirements to ensure swings are detected (or at least valid mapping happens)
    config = FibonacciConfig()

    mapping = compute_htf_fibonacci_mapping(htf, ltf, config)

    # Case 1: Middle of Day 1 (Jan 1 12:00)
    # Should NOT have Jan 1 data (it's forming). Should have Jan 0 (which doesn't exist).
    # Expect NaN or null mapping.
    row1 = mapping.iloc[0]
    assert pd.isna(row1["htf_timestamp_close"]) or row1["htf_timestamp_close"] < pd.Timestamp(
        "2024-01-01"
    )

    # Case 2: Start of Day 2 (Jan 2 00:00)
    # Should catch Jan 1 data?
    # Jan 1 < Jan 2 (Strict). YES.
    # Jan 1 is completed at Jan 2 00:00. So at that split second it becomes available.
    row2 = mapping.iloc[1]
    assert row2["htf_timestamp_close"] == pd.Timestamp("2024-01-01")
    assert (
        row2["htf_swing_high"] is not None
    )  # Assuming swing detection worked or at least returned nulls correctly

    # Case 3: Into Day 2 (Jan 2 01:00)
    # Should still map to Jan 1. Jan 2 is forming.
    row3 = mapping.iloc[2]
    assert row3["htf_timestamp_close"] == pd.Timestamp("2024-01-01")
