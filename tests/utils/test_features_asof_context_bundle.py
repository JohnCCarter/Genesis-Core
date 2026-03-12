from __future__ import annotations

from core.strategy.features_asof_parts.context_bundle_utils import build_fibonacci_context_bundle


def test_build_fibonacci_context_bundle_skips_builders_for_ineligible_timeframe() -> None:
    calls = {"htf": 0, "ltf": 0}

    def _unexpected_htf(*_args, **_kwargs):
        calls["htf"] += 1
        raise AssertionError("HTF builder should not be called")

    def _unexpected_ltf(*_args, **_kwargs):
        calls["ltf"] += 1
        raise AssertionError("LTF builder should not be called")

    bundle = build_fibonacci_context_bundle(
        candles={"timestamp": [1, 2, 3]},
        highs=[1.0, 2.0],
        lows=[0.5, 1.5],
        closes=[0.8, 1.8],
        timeframe="4h",
        symbol="tBTCUSD",
        config={"x": 1},
        atr_vals=[0.1, 0.2],
        build_htf_context_fn=_unexpected_htf,
        build_ltf_context_fn=_unexpected_ltf,
    )

    assert bundle.htf_fibonacci_context == {}
    assert bundle.ltf_fibonacci_context == {}
    assert bundle.htf_selector_meta is None
    assert calls == {"htf": 0, "ltf": 0}


def test_build_fibonacci_context_bundle_preserves_selector_and_atr_passthrough() -> None:
    observed = {}

    def _fake_htf(candles, highs, lows, closes, timeframe, symbol, config):
        observed["htf"] = {
            "candles": candles,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "timeframe": timeframe,
            "symbol": symbol,
            "config": config,
        }
        return {"available": True, "source": "htf"}, {"selected": "6h"}

    def _fake_ltf(candles, highs, lows, closes, timeframe, atr_vals, symbol):
        observed["ltf"] = {
            "candles": candles,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "timeframe": timeframe,
            "atr_vals": atr_vals,
            "symbol": symbol,
        }
        return {"available": True, "source": "ltf"}

    candles = {"timestamp": [1, 2, 3]}
    highs = [10.0, 11.0]
    lows = [9.0, 10.0]
    closes = [9.5, 10.5]
    atr_vals = [0.7, 0.8]
    config = {"multi_timeframe": {"htf_selector": {"mode": "fixed"}}}

    bundle = build_fibonacci_context_bundle(
        candles=candles,
        highs=highs,
        lows=lows,
        closes=closes,
        timeframe="1h",
        symbol="tBTCUSD",
        config=config,
        atr_vals=atr_vals,
        build_htf_context_fn=_fake_htf,
        build_ltf_context_fn=_fake_ltf,
    )

    assert bundle.htf_fibonacci_context == {"available": True, "source": "htf"}
    assert bundle.htf_selector_meta == {"selected": "6h"}
    assert bundle.ltf_fibonacci_context == {"available": True, "source": "ltf"}
    assert observed["htf"]["timeframe"] == "1h"
    assert observed["htf"]["symbol"] == "tBTCUSD"
    assert observed["htf"]["config"] is config
    assert observed["ltf"]["atr_vals"] is atr_vals
    assert observed["ltf"]["timeframe"] == "1h"
    assert observed["ltf"]["symbol"] == "tBTCUSD"
