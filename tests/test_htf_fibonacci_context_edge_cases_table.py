from __future__ import annotations

import pandas as pd
import pytest

import core.indicators.htf_fibonacci as htf


def _set_cached_fib_df(fib_df: pd.DataFrame) -> None:
    cache_key = "tBTCUSD_1D_default"
    htf._htf_context_cache[cache_key] = {"fib_df": fib_df}


@pytest.mark.parametrize(
    "case",
    [
        {
            "name": "timeframe missing",
            "timeframe": None,
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
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
            ),
            "reason": "HTF_TIMEFRAME_MISSING",
        },
        {
            "name": "timeframe not applicable",
            "timeframe": "4h",
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
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
            ),
            "reason": "HTF_NOT_APPLICABLE",
        },
        {
            "name": "missing reference timestamp (lookahead prevention)",
            "timeframe": "1h",
            "ltf": {"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0], "volume": [1.0]},
            "fib_df": pd.DataFrame(
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
            ),
            "reason": "HTF_MISSING_REFERENCE_TS",
        },
        {
            "name": "stale HTF data",
            "timeframe": "1h",
            "ltf": {"timestamp": [pd.Timestamp("2025-02-10T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
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
            ),
            "reason": "HTF_DATA_STALE",
        },
        {
            "name": "levels out of bounds",
            "timeframe": "1h",
            "ltf": {"timestamp": [pd.Timestamp("2025-01-02T00:00:00Z")], "close": [1.0]},
            "fib_df": pd.DataFrame(
                {
                    "timestamp": [pd.Timestamp("2025-01-01T00:00:00Z")],
                    "htf_fib_0382": [999.0],
                    "htf_fib_05": [95.0],
                    "htf_fib_0618": [90.0],
                    "htf_fib_0786": [85.0],
                    "htf_swing_high": [110.0],
                    "htf_swing_low": [80.0],
                    "htf_swing_age_bars": [3],
                }
            ),
            "reason": "HTF_LEVELS_OUT_OF_BOUNDS",
        },
    ],
    ids=lambda c: c["name"],
)
def test_get_htf_fibonacci_context_edge_cases_table(case) -> None:
    _set_cached_fib_df(case["fib_df"])

    ctx = htf.get_htf_fibonacci_context(
        case["ltf"],
        timeframe=case["timeframe"],
        symbol="tBTCUSD",
        htf_timeframe="1D",
    )

    assert ctx.get("available") is False
    assert ctx.get("reason") == case["reason"]
