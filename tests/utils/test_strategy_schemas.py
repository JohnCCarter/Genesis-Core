from __future__ import annotations

from core.strategy.schemas import FIB_KEYS, HtfFibContext


def test_htf_fib_context_levels_coerces_and_filters() -> None:
    ctx = HtfFibContext(
        available=True,
        levels={
            "0.382": "100",
            0.5: 200,
            "bad": "x",
            1.0: 999,
        },
        swing_high=10.0,
        swing_low=5.0,
    )

    assert ctx.levels == {0.382: 100.0, 0.5: 200.0}
    assert ctx.is_usable() is False


def test_htf_fib_context_is_usable_requires_complete_levels() -> None:
    levels = {fib_key: 100.0 + idx for idx, fib_key in enumerate(FIB_KEYS)}
    ctx = HtfFibContext(
        available=True,
        levels=levels,
        swing_high=10.0,
        swing_low=5.0,
    )

    assert ctx.is_usable() is True
