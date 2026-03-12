from __future__ import annotations

from typing import Any

CacheResult = tuple[dict[str, float], dict[str, Any]]


def validate_input_or_return_early(
    candles: dict[str, list[float]],
    asof_bar: int,
    *,
    min_lookback: int = 50,
) -> tuple[int, CacheResult | None]:
    lengths = [len(candles[k]) for k in ["open", "high", "low", "close", "volume"]]
    if not all(length == lengths[0] for length in lengths):
        raise ValueError("All OHLCV lists must have same length")

    total_bars = lengths[0]

    if asof_bar < 0:
        raise ValueError(f"asof_bar must be >= 0, got {asof_bar}")
    if asof_bar >= total_bars:
        raise ValueError(f"asof_bar={asof_bar} >= total_bars={total_bars}")

    if asof_bar < min_lookback:
        return total_bars, (
            {},
            {
                "versions": {},
                "reasons": [
                    f"INSUFFICIENT_DATA: asof_bar={asof_bar} < min_lookback={min_lookback}"
                ],
                "asof_bar": asof_bar,
                "uses_bars": [0, asof_bar],
            },
        )

    return total_bars, None
