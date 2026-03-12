"""HTF to LTF Fibonacci mapping helpers."""

from typing import Any

import numpy as np
import pandas as pd

from core.indicators.fibonacci import FibonacciConfig


def _normalize_dt_series(values: Any, *, tz_aware: bool) -> pd.Series:
    ts = pd.to_datetime(values, utc=True, errors="coerce")
    if tz_aware:
        return ts
    try:
        return ts.dt.tz_convert("UTC").dt.tz_localize(None)
    except Exception:
        return pd.to_datetime(ts.dt.tz_localize(None), errors="coerce")


def compute_htf_fibonacci_mapping_impl(
    htf_candles: pd.DataFrame,
    ltf_candles: pd.DataFrame,
    config: FibonacciConfig | None = None,
    *,
    compute_levels_fn,
) -> pd.DataFrame:
    """Compute 1D Fibonacci levels and project them to LTF timestamps."""
    config_obj = config or FibonacciConfig()
    htf_df = compute_levels_fn(htf_candles, config_obj)
    if htf_df is None or htf_df.empty:
        return ltf_candles[["timestamp"]].assign(htf_data_age_hours=np.nan)

    ltf_left = ltf_candles[["timestamp"]].copy()
    ltf_ts_in = pd.to_datetime(ltf_left["timestamp"], errors="coerce")
    tz_aware = getattr(ltf_ts_in.dt, "tz", None) is not None
    ltf_left["timestamp"] = _normalize_dt_series(ltf_left["timestamp"], tz_aware=tz_aware)

    htf_df = htf_df.copy()
    if "htf_timestamp_close" in htf_df.columns:
        htf_df["htf_timestamp"] = _normalize_dt_series(
            htf_df["htf_timestamp_close"], tz_aware=tz_aware
        )
        deltas = htf_df["htf_timestamp"].diff().dropna()
        frequency = deltas.median() if len(deltas) > 0 else pd.Timedelta(days=1)
        htf_df["valid_from"] = htf_df["htf_timestamp"] + frequency
    elif "timestamp" in htf_df.columns:
        htf_df["htf_timestamp"] = _normalize_dt_series(htf_df["timestamp"], tz_aware=tz_aware)
        htf_df = htf_df.drop(columns=["timestamp"])
        htf_df["valid_from"] = htf_df["htf_timestamp"]
    else:
        raise KeyError("HTF fibonacci dataframe missing timestamp column")

    htf_df["valid_from"] = pd.to_datetime(htf_df["valid_from"], errors="coerce")

    merged = pd.merge_asof(
        ltf_left,
        htf_df,
        left_on="timestamp",
        right_on="valid_from",
        direction="backward",
        allow_exact_matches=True,
    )

    marker_col = "htf_fib_0618" if "htf_fib_0618" in merged.columns else None
    age_hours = (merged["timestamp"] - merged["htf_timestamp"]).dt.total_seconds() / 3600
    if marker_col is not None:
        merged["htf_data_age_hours"] = age_hours.where(merged[marker_col].notna(), np.nan)
    else:
        merged["htf_data_age_hours"] = age_hours.where(merged["htf_timestamp"].notna(), np.nan)

    return merged
