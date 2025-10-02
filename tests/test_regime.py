from __future__ import annotations

from core.strategy.regime import classify_regime


def test_classify_regime_stub_shapes():
    regime, state = classify_regime({"adx_norm": 0.5, "atr_pct": 0.2, "ema_slope": 0.01})
    assert regime in ("trend", "range", "balanced")
    assert isinstance(state, dict)


def test_regime_hysteresis_three_steps():
    cfg = {"gates": {"hysteresis_steps": 2}}
    state = {"regime": "balanced", "steps": 0}

    # Första kandidat: trend (steget 1) – inget skifte än
    r1, state = classify_regime(
        {"adx_norm": 0.7, "atr_pct": 0.2, "ema_slope": 0.02},
        prev_state=state,
        config=cfg,
    )
    assert state["regime"] == "balanced"

    # Andra kandidat i rad: trend – nu ska skiftet ske
    r2, state = classify_regime(
        {"adx_norm": 0.8, "atr_pct": 0.2, "ema_slope": 0.03},
        prev_state=state,
        config=cfg,
    )
    assert state["regime"] == "trend"

    # Kandidat byter tillbaka till balanced men hysteresis låser kvar tills två steg
    r3, state = classify_regime(
        {"adx_norm": 0.3, "atr_pct": 0.2, "ema_slope": 0.0},
        prev_state=state,
        config=cfg,
    )
    assert state["regime"] == "trend"
