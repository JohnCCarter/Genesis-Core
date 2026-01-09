from __future__ import annotations

import pandas as pd

import core.indicators.htf_fibonacci as htf


def test_get_htf_fibonacci_context_requires_all_required_levels() -> None:
    # Ensure we hit the cached fib_df path (no file I/O).
    fib_df = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
            "htf_fib_0382": [100.0],
            # 0.5 missing even though 0.618 exists.
            "htf_fib_05": [None],
            "htf_fib_0618": [90.0],
            "htf_fib_0786": [85.0],
            "htf_swing_high": [110.0],
            "htf_swing_low": [80.0],
            "htf_swing_age_bars": [3],
        }
    )

    cache_key = "tBTCUSD_1D_default"
    htf._htf_context_cache[cache_key] = {"fib_df": fib_df}

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
    assert ctx.get("reason") == "HTF_LEVELS_INCOMPLETE"
    assert 0.5 in (ctx.get("missing_levels") or [])
    assert ctx.get("htf_timeframe") == "1D"
