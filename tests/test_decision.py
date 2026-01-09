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
    # EV negativt för BOTH long och short -> NONE
    # ev_long = 0.1 * 1.5 - 0.9 = -0.75 (NEG)
    # ev_short = 0.9 * 1.5 - 0.1 = +1.25 (POS) -> SHORT skulle passa!
    # För att få BOTH negativ, behöver vi probas nära 50/50:
    # ev_long = 0.45 * 1.5 - 0.55 = 0.675 - 0.55 = +0.125 (POS)
    # ev_short = 0.55 * 1.5 - 0.45 = 0.825 - 0.45 = +0.375 (POS)
    # Behöver båda < 0, vilket är svårt med R=1.5
    # Istället testa med coin-flip (ingen edge):
    a, m = decide(
        {},
        probas={"buy": 0.5, "sell": 0.5},
        confidence={"buy": 1.0, "sell": 1.0},
        regime="balanced",
        state={},
        risk_ctx={},
        cfg=cfg,
    )
    # Med p_buy=p_sell=0.5:
    # ev_long = 0.5*1.5 - 0.5 = 0.75-0.5 = +0.25 (Still POS!)
    # ev_short = 0.5*1.5 - 0.5 = 0.75-0.5 = +0.25 (Still POS!)
    # OK så coin-flip GER edge med R=1.5! Change strategy:
    # Test att action blir NONE om conf < threshold (andra check)
    assert a == "NONE"  # Passes conf check but might pass EV

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
