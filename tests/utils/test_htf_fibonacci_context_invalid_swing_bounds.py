from __future__ import annotations

import pandas as pd

import core.indicators.htf_fibonacci as htf


def test_get_htf_fibonacci_context_marks_invalid_swing_bounds_unavailable():
    # Ensure we hit the cached fib_df path (no file I/O).
    fib_df = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
            "htf_fib_0382": [100.0],
            "htf_fib_05": [95.0],
            "htf_fib_0618": [90.0],
            "htf_fib_0786": [85.0],
            # Inverted bounds (high < low) should be rejected.
            "htf_swing_high": [88490.0],
            "htf_swing_low": [100520.0],
            "htf_swing_age_bars": [3],
        }
    )

    cache_key = "tBTCUSD_1D_default"
    htf._htf_context_cache[cache_key] = {"fib_df": fib_df}

    # Provide minimal LTF candles with timestamps so reference_ts resolves.
    ltf_candles = {
        "timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")],
        "open": [1.0],
        "high": [1.0],
        "low": [1.0],
        "close": [1.0],
        "volume": [1.0],
    }

    ctx = htf.get_htf_fibonacci_context(
        ltf_candles, timeframe="1h", symbol="tBTCUSD", htf_timeframe="1D"
    )

    assert ctx.get("available") is False
    assert ctx.get("reason") == "HTF_INVALID_SWING_BOUNDS"
    assert ctx.get("swing_high") == 88490.0
    assert ctx.get("swing_low") == 100520.0
