from __future__ import annotations

import pytest

from core.strategy.confidence import compute_confidence


def test_compute_confidence_stub_shapes():
    probs = {"buy": 0.4, "sell": 0.3, "hold": 0.3}
    conf, meta = compute_confidence(probs)
    assert isinstance(conf, dict) and isinstance(meta, dict)
    assert "versions" in meta and "reasons" in meta


def test_compute_confidence_monotonicity_and_clamp():
    probs_a = {"buy": 0.6, "sell": 0.3, "hold": 0.1}
    probs_b = {"buy": 0.7, "sell": 0.2, "hold": 0.1}
    conf_a, _ = compute_confidence(probs_a, data_quality=0.8)
    conf_b, _ = compute_confidence(probs_b, data_quality=0.8)
    # Monotoni: högre p_buy ska inte få lägre confidence
    assert conf_b["buy"] >= conf_a["buy"]
    # Clamp: värden ligger inom [0,1]
    assert 0.0 <= conf_a["buy"] <= 1.0 and 0.0 <= conf_a["sell"] <= 1.0


def test_compute_confidence_v2_spread_penalty_reduces_confidence():
    probs = {"buy": 0.6, "sell": 0.2, "hold": 0.2}
    cfg = {
        "enabled": True,
        "clamp": {"min_quality": 0.20},
        "components": {
            "data_quality": {"enabled": True, "floor": 0.50, "exponent": 1.0},
            "spread": {"enabled": True, "ref_bp": 5.0, "max_bp": 50.0, "floor": 0.25},
            "atr": {"enabled": False},
            "volume": {"enabled": False},
        },
    }
    conf_low, meta_low = compute_confidence(probs, spread_bp=2.0, data_quality=1.0, config=cfg)
    conf_high, meta_high = compute_confidence(probs, spread_bp=80.0, data_quality=1.0, config=cfg)
    assert meta_low["quality"]["version"] == "v2"
    assert meta_high["quality"]["version"] == "v2"
    assert conf_high["buy"] < conf_low["buy"]
    assert conf_high["sell"] < conf_low["sell"]


def test_compute_confidence_v2_atr_pct_penalty_reduces_confidence():
    probs = {"buy": 0.6, "sell": 0.2, "hold": 0.2}
    cfg = {
        "enabled": True,
        "clamp": {"min_quality": 0.20},
        "components": {
            "data_quality": {"enabled": False},
            "spread": {"enabled": False},
            "atr": {"enabled": True, "ref_pct": 0.008, "max_pct": 0.04, "floor": 0.40},
            "volume": {"enabled": False},
        },
    }
    conf_low, _ = compute_confidence(probs, atr_pct=0.005, config=cfg)
    conf_high, _ = compute_confidence(probs, atr_pct=0.10, config=cfg)
    assert conf_high["buy"] < conf_low["buy"]
    assert conf_high["sell"] < conf_low["sell"]


def test_compute_confidence_v2_volume_penalty_reduces_confidence():
    probs = {"buy": 0.6, "sell": 0.2, "hold": 0.2}
    cfg = {
        "enabled": True,
        "clamp": {"min_quality": 0.20},
        "components": {
            "data_quality": {"enabled": False},
            "spread": {"enabled": False},
            "atr": {"enabled": False},
            "volume": {"enabled": True, "floor": 0.40, "exponent": 1.0},
        },
    }
    conf_good, _ = compute_confidence(probs, volume_score=1.0, config=cfg)
    conf_bad, _ = compute_confidence(probs, volume_score=0.0, config=cfg)
    assert conf_bad["buy"] < conf_good["buy"]
    assert conf_bad["sell"] < conf_good["sell"]


def test_compute_confidence_v2_component_scope_sizing_only_does_not_affect_gate() -> None:
    probs = {"buy": 0.80, "sell": 0.10, "hold": 0.10}
    cfg = {
        "enabled": True,
        "clamp": {"min_quality": 0.20},
        "components": {
            "data_quality": {"enabled": False},
            "spread": {"enabled": False},
            "atr": {
                "enabled": True,
                "scope": "sizing",
                "ref_pct": 0.010,
                "max_pct": 0.050,
                "floor": 0.40,
                "exponent": 1.0,
            },
            "volume": {"enabled": True, "scope": "sizing", "floor": 0.40, "exponent": 0.8},
        },
    }

    conf, meta = compute_confidence(probs, atr_pct=0.040, volume_score=0.10, config=cfg)

    # Gate confidence should be unscaled (quality_gate == 1.0).
    assert conf["buy"] == pytest.approx(probs["buy"])
    assert conf["sell"] == pytest.approx(probs["sell"])

    # Scaled confidences should exist and be reduced.
    assert "buy_scaled" in conf
    assert conf["buy_scaled"] < conf["buy"]

    q = meta["quality"]
    assert q["version"] == "v2"
    assert q["quality_factor_gate"] == pytest.approx(1.0)
    assert q["quality_factor_size"] < 1.0
    assert q["component_scopes"]["atr"] == "sizing"
    assert q["component_scopes"]["volume"] == "sizing"


def test_compute_confidence_v2_preserves_buy_sell_order_when_not_saturated():
    probs = {"buy": 0.7, "sell": 0.3, "hold": 0.0}
    cfg = {
        "enabled": True,
        "clamp": {"min_quality": 0.20},
        "components": {
            "data_quality": {"enabled": True, "floor": 0.50, "exponent": 1.0},
            "spread": {"enabled": False},
            "atr": {"enabled": False},
            "volume": {"enabled": False},
        },
    }
    conf, _ = compute_confidence(probs, data_quality=0.8, config=cfg)
    # Since both are scaled by same Q, buy should remain >= sell (no inversion)
    assert conf["buy"] >= conf["sell"]
