from __future__ import annotations

import pandas as pd
import pytest

import core.indicators.htf_fibonacci as htf


@pytest.mark.parametrize(
    "timeframe", ["1H", " 1h ", "60m", "30min", "15MIN", "360m"]
)  # alias/case/whitespace
def test_get_htf_fibonacci_context_accepts_timeframe_aliases(timeframe: str) -> None:
    fib_df = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
            "htf_fib_0382": [100.0],
            "htf_fib_05": [95.0],
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
        ltf_candles, timeframe=timeframe, symbol="tBTCUSD", htf_timeframe="1D"
    )

    assert ctx.get("available") is True
    levels = ctx.get("levels")
    assert isinstance(levels, dict)
    assert 0.786 in levels
    assert levels[0.786] == 85.0
