from __future__ import annotations

import pytest

from core.agent.fib_strategy import (
    FibStrategyParams,
    _validate_candles,
    _zones_intersection,
    _zones_overlap_at_price,
    aggregate_candles,
    compute_signal_nested,
)


def _make_uptrend(n: int = 80, start: float = 40000.0, end: float = 50000.0) -> dict:
    closes = [start + (end - start) * i / (n - 1) for i in range(n)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes, strict=False)]
    return {"open": opens, "high": highs, "low": lows, "close": closes, "volume": [10.0] * n}


def test_aggregate_candles_4x_groups_1h_into_4h() -> None:
    n = 100
    src = _make_uptrend(n=n, start=100.0, end=200.0)
    out = aggregate_candles(src, factor=4)
    assert len(out["close"]) == n // 4
    assert out["open"][0] == src["open"][0]
    assert out["close"][-1] == src["close"][n // 4 * 4 - 1]
    assert out["high"][0] == max(src["high"][:4])
    assert out["low"][0] == min(src["low"][:4])
    assert out["volume"][0] == sum(src["volume"][:4])


def test_aggregate_candles_drops_partial_trailing() -> None:
    src = _make_uptrend(n=11, start=100.0, end=200.0)
    out = aggregate_candles(src, factor=4)
    assert len(out["close"]) == 2  # 11 // 4 = 2


@pytest.mark.parametrize("factor", [0, -1, 1.5, True])
def test_aggregate_candles_rejects_invalid_factor(factor) -> None:
    src = _make_uptrend(n=11, start=100.0, end=200.0)
    with pytest.raises(ValueError, match="factor must be an integer >= 1"):
        aggregate_candles(src, factor=factor)


def test_validate_candles_allows_missing_volume_when_ohlc_matches() -> None:
    candles = {
        "open": [1.0] * 60,
        "high": [2.0] * 60,
        "low": [0.5] * 60,
        "close": [1.5] * 60,
    }
    assert _validate_candles(candles) is True


def test_zones_overlap_at_price() -> None:
    z1 = {"low": 100.0, "high": 110.0}
    z2 = {"low": 105.0, "high": 115.0}
    z3 = {"low": 108.0, "high": 112.0}
    assert _zones_overlap_at_price([z1, z2, z3], 109.0) is True
    assert _zones_overlap_at_price([z1, z2, z3], 102.0) is False
    assert _zones_overlap_at_price([z1, z2, z3], 116.0) is False


def test_zones_intersection_returns_overlap_band() -> None:
    z1 = {"low": 100.0, "high": 110.0}
    z2 = {"low": 105.0, "high": 115.0}
    z3 = {"low": 108.0, "high": 112.0}
    out = _zones_intersection([z1, z2, z3])
    assert out == {"low": 108.0, "high": 110.0}


def test_zones_intersection_returns_none_when_disjoint() -> None:
    z1 = {"low": 100.0, "high": 105.0}
    z2 = {"low": 110.0, "high": 115.0}
    assert _zones_intersection([z1, z2]) is None


def test_compute_signal_nested_returns_none_for_insufficient_candles() -> None:
    short = {"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0], "volume": [1.0]}
    sig = compute_signal_nested(short, short, short, FibStrategyParams())
    assert sig.action == "NONE"
    assert sig.reason == "insufficient_candles"


def test_compute_signal_nested_no_mega_zone_touch() -> None:
    # Mega up-leg, but price is now far above mega zone
    n_up = 80
    closes = [40000.0 + (10000.0 / (n_up - 1)) * i for i in range(n_up)]
    closes += [closes[-1]] * 40  # pris stannar i toppen, ovanför zonen
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes, strict=False)]
    cs = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [10.0] * len(closes),
    }
    sig = compute_signal_nested(cs, cs, cs, FibStrategyParams(trend_filter_enabled=False))
    assert sig.action == "NONE"
    # Either mega-zone-miss or some downstream gate; never an entry on this shape
    assert sig.reason != "nested_confluence_confirmation"


def test_compute_signal_nested_trend_filter_blocks_counter_trend() -> None:
    # Build closes where a tiny down-leg appears at the end of a long uptrend
    closes = [40000.0 + i * 50.0 for i in range(120)]
    closes += [closes[-1] - 200.0 * i for i in range(1, 30)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 100.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 100.0 for o, c in zip(opens, closes, strict=False)]
    cs = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [10.0] * len(closes),
    }
    sig = compute_signal_nested(
        cs, cs, cs, FibStrategyParams(trend_filter_enabled=True, trend_filter_lookback=50)
    )
    if sig.htf_swing and sig.htf_swing["direction"] == "down":
        assert sig.action == "NONE"
        assert sig.reason == "trend_filter_reject"


def test_confluence_required_param_round_trips() -> None:
    p = FibStrategyParams(confluence_required=False)
    d = p.to_dict()
    assert d["confluence_required"] is False


def test_compute_signal_nested_uses_minor_close_as_entry() -> None:
    # Build a minor with a distinct, recent close
    n = 80
    closes = [40000.0 + i * 50.0 for i in range(n)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes, strict=False)]
    minor = {"open": opens, "high": highs, "low": lows, "close": closes, "volume": [1.0] * n}
    sig = compute_signal_nested(minor, minor, minor, FibStrategyParams(trend_filter_enabled=False))
    # entry, when populated, MUST equal minor's last close
    if sig.entry is not None:
        assert sig.entry == closes[-1]


def test_mega_zone_touch_required_default_true() -> None:
    p = FibStrategyParams()
    assert p.mega_zone_touch_required is True
    assert p.to_dict()["mega_zone_touch_required"] is True


def test_per_tier_atr_uses_native_btcusd_defaults() -> None:
    """Default per-tier ATR is tuned for native 1D+6h+1h on BTC/USD."""
    p = FibStrategyParams()
    assert p.resolve_mega_atr() == 6.0
    assert p.resolve_major_atr() == 5.5  # tuned for 6h
    assert p.resolve_minor_atr() == 6.0


def test_per_tier_atr_falls_back_when_explicitly_none() -> None:
    """Setting per-tier to None re-enables fall-back to global atr_depth."""
    p = FibStrategyParams(
        atr_depth=5.0,
        mega_atr_depth=None,
        major_atr_depth=None,
        minor_atr_depth=None,
    )
    assert p.resolve_mega_atr() == 5.0
    assert p.resolve_major_atr() == 5.0
    assert p.resolve_minor_atr() == 5.0


def test_per_tier_atr_overrides_apply_independently() -> None:
    p = FibStrategyParams(
        atr_depth=6.0,
        mega_atr_depth=7.0,
        major_atr_depth=4.0,
        minor_atr_depth=2.5,
    )
    assert p.resolve_mega_atr() == 7.0
    assert p.resolve_major_atr() == 4.0
    assert p.resolve_minor_atr() == 2.5
    d = p.to_dict()
    assert d["mega_atr_depth"] == 7.0
    assert d["major_atr_depth"] == 4.0
    assert d["minor_atr_depth"] == 2.5


def test_per_tier_atr_partial_override_keeps_other_defaults() -> None:
    """Overriding one tier leaves the others at their tuned defaults."""
    p = FibStrategyParams(atr_depth=6.0, minor_atr_depth=3.0)
    assert p.resolve_mega_atr() == 6.0  # default
    assert p.resolve_major_atr() == 5.5  # tuned default kept
    assert p.resolve_minor_atr() == 3.0  # overridden


def test_mega_zone_touch_off_skips_no_mega_zone_touch_reject() -> None:
    """With mega_zone_touch_required=False, a price outside the 1D zone
    should not produce a `no_mega_zone_touch` rejection."""
    # Build a long uptrend, then a tiny pullback that does NOT reach the 0.5
    # of the mega swing. Without the mega-zone-touch gate, evaluation should
    # progress past mega-zone and fail elsewhere (or reach a trade).
    n_up = 80
    closes = [40000.0 + (10000.0 / (n_up - 1)) * i for i in range(n_up)]
    closes += [closes[-1] - i * 20.0 for i in range(1, 80)]  # very shallow pullback
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes, strict=False)]
    cs = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [10.0] * len(closes),
    }

    sig_strict = compute_signal_nested(
        cs,
        cs,
        cs,
        FibStrategyParams(trend_filter_enabled=False, mega_zone_touch_required=True),
    )
    sig_loose = compute_signal_nested(
        cs,
        cs,
        cs,
        FibStrategyParams(trend_filter_enabled=False, mega_zone_touch_required=False),
    )
    # Strict should reject on mega zone
    assert sig_strict.reason == "no_mega_zone_touch"
    # Loose should bypass that gate (any other reason or even an entry is fine)
    assert sig_loose.reason != "no_mega_zone_touch"
