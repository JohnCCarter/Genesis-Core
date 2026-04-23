from __future__ import annotations

from core.strategy.features_asof_parts.context_bundle_utils import build_fibonacci_context_bundle
from core.strategy.features_asof_parts.fibonacci_context_utils import build_htf_fibonacci_context


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


def test_build_fibonacci_context_bundle_enables_htf_only_for_3h() -> None:
    calls = {"htf": 0, "ltf": 0}

    def _fake_htf(candles, highs, lows, closes, timeframe, symbol, config):
        calls["htf"] += 1
        assert candles == {"timestamp": [1, 2, 3]}
        assert highs == [10.0, 11.0]
        assert lows == [9.0, 10.0]
        assert closes == [9.5, 10.5]
        assert timeframe == "3h"
        assert symbol == "tBTCUSD"
        assert config == {"multi_timeframe": {"htf_selector": {"mode": "fixed"}}}
        return {"available": True, "source": "htf-3h"}, {"selected": "1D"}

    def _unexpected_ltf(*_args, **_kwargs):
        calls["ltf"] += 1
        raise AssertionError("LTF builder should remain disabled for 3h in this slice")

    bundle = build_fibonacci_context_bundle(
        candles={"timestamp": [1, 2, 3]},
        highs=[10.0, 11.0],
        lows=[9.0, 10.0],
        closes=[9.5, 10.5],
        timeframe="3h",
        symbol="tBTCUSD",
        config={"multi_timeframe": {"htf_selector": {"mode": "fixed"}}},
        atr_vals=[0.7, 0.8],
        build_htf_context_fn=_fake_htf,
        build_ltf_context_fn=_unexpected_ltf,
    )

    assert bundle.htf_fibonacci_context == {"available": True, "source": "htf-3h"}
    assert bundle.htf_selector_meta == {"selected": "1D"}
    assert bundle.ltf_fibonacci_context == {}
    assert calls == {"htf": 1, "ltf": 0}


def test_build_htf_fibonacci_context_forwards_data_source_policy_from_config() -> None:
    observed: dict[str, object] = {}

    def _as_config_dict(value):
        return value if isinstance(value, dict) else {}

    def _select_htf_timeframe(_timeframe, _selector_cfg):
        return "1D", {"selected": "1D"}

    def _fake_get_htf_fibonacci_context(candles, timeframe, symbol, htf_timeframe, **kwargs):
        observed["candles"] = candles
        observed["timeframe"] = timeframe
        observed["symbol"] = symbol
        observed["htf_timeframe"] = htf_timeframe
        observed["kwargs"] = kwargs
        return {"available": True}

    def _noop_log(*_args, **_kwargs):
        return None

    context, selector_meta = build_htf_fibonacci_context(
        candles={"timestamp": [1, 2, 3]},
        highs=[10.0, 11.0],
        lows=[9.0, 10.0],
        closes=[9.5, 10.5],
        timeframe="3h",
        symbol="tBTCUSD",
        config={"data_source_policy": "curated_only", "multi_timeframe": {}},
        as_config_dict_fn=_as_config_dict,
        select_htf_timeframe_fn=_select_htf_timeframe,
        get_htf_fibonacci_context_fn=_fake_get_htf_fibonacci_context,
        log_fib_flow_fn=_noop_log,
        logger=None,
    )

    assert context == {"available": True, "selector": {"selected": "1D"}}
    assert selector_meta == {"selected": "1D"}
    assert observed["timeframe"] == "3h"
    assert observed["symbol"] == "tBTCUSD"
    assert observed["htf_timeframe"] == "1D"
    assert observed["kwargs"] == {"data_source_policy": "curated_only"}
