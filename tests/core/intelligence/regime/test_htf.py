from __future__ import annotations

import pytest

from core.intelligence.regime.htf import compute_htf_regime


@pytest.mark.parametrize(
    ("htf_fib_data", "current_price", "expected"),
    [
        (None, 100.0, "unknown"),
        ("bad", 100.0, "unknown"),
        ({"available": False}, 100.0, "unknown"),
        ({"available": True}, None, "unknown"),
        ({"available": True}, 0.0, "unknown"),
        ({"available": True, "swing_high": None, "swing_low": 90.0}, 100.0, "unknown"),
        ({"available": True, "swing_high": 110.0, "swing_low": None}, 100.0, "unknown"),
        ({"available": True, "swing_high": 100.0, "swing_low": 100.0}, 100.0, "unknown"),
        ({"available": True, "swing_high": 110.0, "swing_low": 90.0}, 102.36, "bull"),
        ({"available": True, "swing_high": 110.0, "swing_low": 90.0}, 97.64, "bear"),
        ({"available": True, "swing_high": 110.0, "swing_low": 90.0}, 100.0, "ranging"),
    ],
    ids=[
        "none-data",
        "invalid-data-type",
        "unavailable",
        "missing-price",
        "non-positive-price",
        "missing-swing-high",
        "missing-swing-low",
        "invalid-swing-bounds",
        "bull-boundary-0618",
        "bear-boundary-0382",
        "mid-range",
    ],
)
def test_compute_htf_regime_returns_expected_values(
    htf_fib_data: object,
    current_price: float | None,
    expected: str,
) -> None:
    result = compute_htf_regime(htf_fib_data, current_price=current_price)

    assert result == expected
