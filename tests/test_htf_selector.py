from core.strategy.htf_selector import select_htf_timeframe


def test_select_htf_timeframe_prefers_explicit_mapping():
    selector = {"mode": "fixed", "per_timeframe": {"1h": {"timeframe": "12h"}}}
    timeframe, meta = select_htf_timeframe("1h", selector)
    assert timeframe == "12h"
    assert meta["decision_path"][0]["success"] is True


def test_select_htf_timeframe_supports_multiplier_rules():
    selector = {"mode": "fixed", "per_timeframe": {"1h": {"multiplier": 6}}}
    timeframe, _ = select_htf_timeframe("1h", selector)
    assert timeframe == "6h"


def test_select_htf_timeframe_uses_fallback():
    selector = {
        "mode": "fixed",
        "per_timeframe": {},
        "fallback_timeframe": "1D",
    }
    timeframe, meta = select_htf_timeframe("30m", selector)
    assert timeframe == "1D"
    assert meta["decision_path"][-1]["source"] == "fallback"


def test_select_htf_timeframe_defaults_to_static_map():
    timeframe, meta = select_htf_timeframe("1h", None)
    assert timeframe == "6h"
    assert meta["selected"] == "6h"
