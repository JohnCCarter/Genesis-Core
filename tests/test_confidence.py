from __future__ import annotations

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
