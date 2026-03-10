from __future__ import annotations

import pandas as pd

from core.indicators.htf_fibonacci import get_ltf_fibonacci_context


def test_get_ltf_fibonacci_context_returns_required_schema_and_levels() -> None:
    n = 80
    ts = pd.date_range("2025-01-01T00:00:00Z", periods=n, freq="1h")

    # Deterministic, non-degenerate price series.
    base = 100.0
    highs = [base + i * 0.2 + (0.5 if i % 10 == 0 else 0.0) for i in range(n)]
    lows = [base + i * 0.2 - 1.0 for i in range(n)]
    closes = [base + i * 0.2 - 0.5 for i in range(n)]

    ctx = get_ltf_fibonacci_context(
        {
            "high": highs,
            "low": lows,
            "close": closes,
            "timestamp": list(ts),
        },
        timeframe="1h",
        atr_values=[1.0] * n,
    )

    assert ctx.get("available") is True
    assert ctx.get("timeframe") == "1h"

    levels = ctx.get("levels")
    assert isinstance(levels, dict)
    for required in (0.382, 0.5, 0.618, 0.786):
        assert required in levels
        assert isinstance(levels[required], float)

    assert float(ctx.get("swing_high")) > float(ctx.get("swing_low"))
    assert isinstance(ctx.get("swing_age_bars"), int)

    last_update = ctx.get("last_update")
    assert isinstance(last_update, pd.Timestamp)
    assert last_update.tz is not None


def test_get_ltf_fibonacci_context_insufficient_data() -> None:
    ctx = get_ltf_fibonacci_context({"high": [1.0], "low": [1.0], "close": [1.0]}, timeframe="1h")

    assert ctx.get("available") is False
    assert ctx.get("reason") == "LTF_INSUFFICIENT_DATA"
