from __future__ import annotations

from core.agent.fib_strategy import (
    FibStrategyParams,
    aggregate_candles,
    compute_signal_nested,
    _zones_intersection,
    _zones_overlap_at_price,
)


def _make_uptrend(n: int = 80, start: float = 40000.0, end: float = 50000.0) -> dict:
    closes = [start + (end - start) * i / (n - 1) for i in range(n)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes)]
    return {"open": opens, "high": highs, "low": lows, "close": closes,
            "volume": [10.0] * n}


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
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes)]
    cs = {"open": opens, "high": highs, "low": lows, "close": closes,
          "volume": [10.0] * len(closes)}
    sig = compute_signal_nested(cs, cs, cs, FibStrategyParams(trend_filter_enabled=False))
    assert sig.action == "NONE"
    # Either mega-zone-miss or some downstream gate; never an entry on this shape
    assert sig.reason != "nested_confluence_confirmation"


def test_compute_signal_nested_trend_filter_blocks_counter_trend() -> None:
    # Build closes where a tiny down-leg appears at the end of a long uptrend
    closes = [40000.0 + i * 50.0 for i in range(120)]
    closes += [closes[-1] - 200.0 * i for i in range(1, 30)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 100.0 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 100.0 for o, c in zip(opens, closes)]
    cs = {"open": opens, "high": highs, "low": lows, "close": closes,
          "volume": [10.0] * len(closes)}
    sig = compute_signal_nested(cs, cs, cs,
                                 FibStrategyParams(trend_filter_enabled=True,
                                                   trend_filter_lookback=50))
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
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes)]
    minor = {"open": opens, "high": highs, "low": lows, "close": closes,
             "volume": [1.0] * n}
    sig = compute_signal_nested(minor, minor, minor,
                                 FibStrategyParams(trend_filter_enabled=False))
    # entry, when populated, MUST equal minor's last close
    if sig.entry is not None:
        assert sig.entry == closes[-1]


def test_mega_zone_touch_required_default_true() -> None:
    p = FibStrategyParams()
    assert p.mega_zone_touch_required is True
    assert p.to_dict()["mega_zone_touch_required"] is True


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
    highs = [max(o, c) + 50.0 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 50.0 for o, c in zip(opens, closes)]
    cs = {"open": opens, "high": highs, "low": lows, "close": closes,
          "volume": [10.0] * len(closes)}

    sig_strict = compute_signal_nested(
        cs, cs, cs,
        FibStrategyParams(trend_filter_enabled=False, mega_zone_touch_required=True),
    )
    sig_loose = compute_signal_nested(
        cs, cs, cs,
        FibStrategyParams(trend_filter_enabled=False, mega_zone_touch_required=False),
    )
    # Strict should reject on mega zone
    assert sig_strict.reason == "no_mega_zone_touch"
    # Loose should bypass that gate (any other reason or even an entry is fine)
    assert sig_loose.reason != "no_mega_zone_touch"
