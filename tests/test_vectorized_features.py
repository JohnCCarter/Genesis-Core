"""Regression tests ensuring vectorized feature computation stays in parity.

These tests are intentionally high-level and reuse the CLI validation helpers so we
exercise exactly the same comparison logic that developers run manually. The
per-sample extractor is still the single source of truth; parity here guarantees
the vectorized pipeline remains trustworthy as we iterate on performance.
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.indicators.vectorized import calculate_all_features_vectorized
from core.utils import get_candles_path
from scripts.validate_vectorized_features import (
    compare_features,
    compute_per_sample_features,
)


@pytest.mark.slow
def test_vectorized_features_parity_tbtc_usd_1h() -> None:
    """Vectorized features must match per-sample computation within tolerance."""

    symbol = "tBTCUSD"
    timeframe = "1h"
    tolerance = 1e-5
    sample_count = 200

    try:
        candles_path = get_candles_path(symbol, timeframe)
    except FileNotFoundError as exc:
        pytest.skip(f"Test data missing for {symbol} {timeframe}: {exc}")

    candles_df = pd.read_parquet(candles_path)

    # Reference implementation (slow, per-sample)
    per_sample_df = compute_per_sample_features(candles_df, max_samples=sample_count)

    # Vectorized computation (fast path)
    vectorized_df = calculate_all_features_vectorized(candles_df, timeframe=timeframe)
    vectorized_df = vectorized_df.copy()
    vectorized_df.insert(0, "timestamp", candles_df["timestamp"])
    vectorized_df = vectorized_df.tail(sample_count)

    results = compare_features(per_sample_df, vectorized_df, tolerance=tolerance)

    summary = results["summary"]
    assert summary["all_within_tolerance"], (
        "Vectorized features diverged: "
        f"max_diff={summary['max_diff_overall']:.2e} on {summary['worst_feature']}"
    )
