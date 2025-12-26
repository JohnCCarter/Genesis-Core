from __future__ import annotations

import pandas as pd

import core.indicators.htf_fibonacci as htf


def test_compute_htf_fibonacci_mapping_computes_age_from_matched_htf_timestamp(monkeypatch) -> None:
    # Stub HTF levels so we don't depend on swing detection details.
    htf_fib_df = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2025-01-01T00:00:00Z"),
                pd.Timestamp("2025-01-02T00:00:00Z"),
            ],
            "htf_fib_0382": [100.0, 101.0],
            "htf_fib_05": [95.0, 96.0],
            "htf_fib_0618": [90.0, 91.0],
            "htf_fib_0786": [85.0, 86.0],
            "htf_swing_high": [110.0, 111.0],
            "htf_swing_low": [80.0, 81.0],
            "htf_swing_age_bars": [3, 4],
        }
    )

    def _fake_compute(_htf_candles, _config=None):
        return htf_fib_df

    monkeypatch.setattr(htf, "compute_htf_fibonacci_levels", _fake_compute)

    htf_candles = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [1.0],
        }
    )

    ltf_candles = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2024-12-31T23:00:00Z"),
                pd.Timestamp("2025-01-02T01:00:00Z"),
                pd.Timestamp("2025-01-02T23:00:00Z"),
            ],
            "open": [1.0, 1.0, 1.0],
            "high": [1.0, 1.0, 1.0],
            "low": [1.0, 1.0, 1.0],
            "close": [1.0, 1.0, 1.0],
            "volume": [1.0, 1.0, 1.0],
        }
    )

    mapped = htf.compute_htf_fibonacci_mapping(htf_candles, ltf_candles)

    assert list(mapped["timestamp"]) == list(ltf_candles["timestamp"])

    # Before first HTF bar: no HTF levels, age should be None.
    assert pd.isna(mapped.loc[0, "htf_fib_0618"])
    assert pd.isna(mapped.loc[0, "htf_data_age_hours"])

    # Matched to 2025-01-02 00:00:00Z.
    assert mapped.loc[1, "htf_timestamp"] == pd.Timestamp("2025-01-02T00:00:00Z")
    assert mapped.loc[1, "htf_data_age_hours"] == 1.0

    assert mapped.loc[2, "htf_timestamp"] == pd.Timestamp("2025-01-02T00:00:00Z")
    assert mapped.loc[2, "htf_data_age_hours"] == 23.0
