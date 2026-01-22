from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from core.indicators.fibonacci import FibonacciConfig
from core.indicators.htf_fibonacci import compute_htf_fibonacci_levels


def test_compute_htf_fibonacci_levels_produces_levels_in_early_history() -> None:
    """Regression: HTF levels must be available AS-OF, not only near the end.

    Prior bug:
        compute_htf_fibonacci_levels used a single global swing detection pass.
        Because swing detection keeps only swings within `max_lookback` of the
        latest swing in the full series, early history ended up with *no* swings
        and thus no fib levels.

    This test constructs a long-enough series with multiple swings so that
    early windows should still produce fib levels.
    """

    n = 400
    ts0 = datetime(2024, 1, 1, tzinfo=UTC)
    timestamps = [ts0 + timedelta(days=i) for i in range(n)]

    # Smooth oscillation to guarantee local extrema.
    x = np.linspace(0, 16 * np.pi, n)
    close = 100.0 + 10.0 * np.sin(x)
    high = close + 1.0
    low = close - 1.0

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": np.ones(n),
        }
    )

    cfg = FibonacciConfig(
        atr_depth=2.0,
        max_lookback=50,
        swing_threshold_multiple=0.0,
        swing_threshold_min=0.0,
        swing_threshold_step=0.0,
        max_swings=8,
        min_swings=1,
    )

    out = compute_htf_fibonacci_levels(df, cfg)

    # Expect fib levels to exist well before the end of the series.
    mask = out[["htf_fib_0382", "htf_fib_05", "htf_fib_0618", "htf_fib_0786"]].notna().all(axis=1)
    assert bool(mask.any())
    first_idx = int(mask.idxmax())
    assert first_idx < 200
