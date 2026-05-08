from __future__ import annotations

from core.agent.fib_strategy import (
    FibStrategyParams,
    _retracement_zone,
    _validate_candles,
    compute_signal,
)


def test_retracement_zone_uptrend_orders_levels_correctly() -> None:
    # A=low=100, B=high=200. 0.5 retracement = 150. 0.618 = 138.2.
    zone = _retracement_zone("up", 100.0, 200.0, 0.5, 0.618)
    assert abs(zone["high"] - 150.0) < 1e-6
    assert abs(zone["low"] - 138.2) < 1e-6


def test_retracement_zone_downtrend_orders_levels_correctly() -> None:
    # A=high=200, B=low=100. 0.5 retracement = 150. 0.618 = 161.8.
    zone = _retracement_zone("down", 200.0, 100.0, 0.5, 0.618)
    assert abs(zone["low"] - 150.0) < 1e-6
    assert abs(zone["high"] - 161.8) < 1e-6


def test_compute_signal_insufficient_candles_returns_none() -> None:
    short = {"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0], "volume": [1.0]}
    sig = compute_signal(short, short)
    assert sig.action == "NONE"
    assert sig.reason == "insufficient_candles"


def test_validate_candles_rejects_mismatched_ohlc_lengths() -> None:
    candles = {
        "open": [1.0] * 60,
        "high": [1.0] * 60,
        "low": [1.0] * 59,
        "close": [1.0] * 60,
    }
    assert _validate_candles(candles) is False


def test_compute_signal_flat_market_no_zone_touch(flat_candles) -> None:
    # Flat market: any swing yields a zone, but pullback won't enter the 0.5–0.618 band
    sig = compute_signal(flat_candles, flat_candles)
    assert sig.action == "NONE"
    # Allowed reasons: no_htf_swing or no_htf_zone_touch
    assert sig.reason in {
        "no_htf_swing",
        "no_htf_zone_touch",
        "no_ltf_swing",
        "no_ltf_zone_touch",
        "no_confirmation",
    }


def test_compute_signal_uptrend_pullback_yields_long(
    htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    sig = compute_signal(
        htf_uptrend_pullback,
        ltf_uptrend_pullback,
        FibStrategyParams(trend_filter_enabled=False),
        equity_usd=10000.0,
        risk_pct=0.01,
    )
    # Strict assertion: synthetic data is constructed for this scenario
    assert sig.action == "LONG", f"got {sig.action} reason={sig.reason}"
    assert sig.htf_zone is not None
    assert sig.ltf_zone is not None
    assert sig.entry is not None
    assert sig.stop is not None
    assert sig.entry > sig.stop  # long: stop below entry
    assert sig.size is not None and sig.size > 0
    assert len(sig.targets) == 3
    assert sig.targets[0]["level"] == 1.272
    assert sig.targets[1]["level"] == 1.618
    assert sig.targets[2]["level"] == "trailing"


def test_compute_signal_downtrend_pullback_yields_short(
    htf_downtrend_pullback, ltf_downtrend_pullback
) -> None:
    sig = compute_signal(
        htf_downtrend_pullback,
        ltf_downtrend_pullback,
        FibStrategyParams(trend_filter_enabled=False),
        equity_usd=10000.0,
        risk_pct=0.01,
    )
    assert sig.action == "SHORT", f"got {sig.action} reason={sig.reason}"
    assert sig.entry is not None and sig.stop is not None
    assert sig.stop > sig.entry  # short: stop above entry


def test_compute_signal_size_zero_when_no_equity(
    htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    sig = compute_signal(htf_uptrend_pullback, ltf_uptrend_pullback, equity_usd=0.0)
    if sig.action != "NONE":
        assert sig.size is None


def test_fibstrategy_params_to_dict_round_trip() -> None:
    p = FibStrategyParams(entry_zone_low=0.4, entry_zone_high=0.7)
    d = p.to_dict()
    assert d["entry_zone_low"] == 0.4
    assert d["entry_zone_high"] == 0.7
    assert d["extension_levels"] == [1.272, 1.618]
    assert d["trend_filter_enabled"] is True
    assert d["trend_filter_lookback"] == 50
    assert d["confluence_required"] is True


def test_default_entry_zone_high_is_0786() -> None:
    p = FibStrategyParams()
    assert p.entry_zone_high == 0.786


def test_trend_aligned_helper_passes_with_too_little_data() -> None:
    from core.agent.fib_strategy import trend_aligned

    closes = [100.0, 101.0, 102.0]
    assert trend_aligned("up", closes, lookback=200) is True
    assert trend_aligned("down", closes, lookback=200) is True


def test_trend_aligned_helper_blocks_counter_trend() -> None:
    from core.agent.fib_strategy import trend_aligned

    closes = list(range(100, 400))  # 300 ascending closes
    # Direction "down" against an uptrend over lookback=200 → reject
    assert trend_aligned("down", closes, lookback=200) is False
    # Direction "up" aligned with the uptrend → pass
    assert trend_aligned("up", closes, lookback=200) is True


def test_compute_signal_trend_filter_rejects_short_in_uptrend() -> None:
    # 250 ascending closes → uptrend over 50-bar lookback
    closes = [40000.0 + i * 50.0 for i in range(250)]
    # Now drop sharply at the end so a recent HTF swing flips to "down"
    closes += [closes[-1] - i * 200.0 for i in range(1, 30)]
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 100.0 for o, c in zip(opens, closes, strict=False)]
    lows = [min(o, c) - 100.0 for o, c in zip(opens, closes, strict=False)]
    htf = {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [10.0] * len(closes),
    }
    sig_with = compute_signal(htf, htf, FibStrategyParams(trend_filter_enabled=True))
    sig_without = compute_signal(htf, htf, FibStrategyParams(trend_filter_enabled=False))
    if sig_with.htf_swing and sig_with.htf_swing["direction"] == "down":
        assert sig_with.action == "NONE"
        assert sig_with.reason == "trend_filter_reject"
    assert sig_without.reason != "trend_filter_reject"
