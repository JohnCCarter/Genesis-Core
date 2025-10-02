from __future__ import annotations

from core.strategy.decision import decide


def test_decide_stub_shapes():
    action, meta = decide(
        {},
        probas={"buy": 0.4, "sell": 0.3, "hold": 0.3},
        confidence={"buy": 0.4, "sell": 0.3},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg={},
    )
    assert action in ("LONG", "SHORT", "NONE")
    assert isinstance(meta, dict)


def test_decide_gate_order_and_fail_safe():
    cfg = {
        "ev": {"R_default": 1.5},
        "thresholds": {"entry_conf_overall": 0.6, "regime_proba": {"balanced": 0.55}},
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 1},
        "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
    }
    # EV negativt -> NONE
    a, m = decide(
        {},
        probas={"buy": 0.1, "sell": 0.2},
        confidence={"buy": 1.0, "sell": 1.0},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE" and "EV_NEG" in m.get("reasons", [])

    # Proba under tröskel -> NONE
    a, m = decide(
        {},
        probas={"buy": 0.54, "sell": 0.2},
        confidence={"buy": 1.0, "sell": 1.0},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "NONE"

    # Över proba + conf -> LONG, cooldown träder i kraft i state_out
    a, m = decide(
        {},
        probas={"buy": 0.7, "sell": 0.2},
        confidence={"buy": 0.7, "sell": 0.2},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    assert a == "LONG"
    assert m.get("state_out", {}).get("cooldown_remaining") == 1

    # Nästa beslut under cooldown -> NONE
    a2, m2 = decide(
        {},
        probas={"buy": 0.7, "sell": 0.2},
        confidence={"buy": 0.7, "sell": 0.2},
        regime="balanced",
        state=m.get("state_out", {}),
        risk_ctx={},
        cfg=cfg,
    )
    assert a2 == "NONE" and "COOLDOWN_ACTIVE" in m2.get("reasons", [])
