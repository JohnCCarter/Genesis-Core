from __future__ import annotations

from core.strategy.prob_model import predict_proba


def test_prob_model_shapes_and_normalization():
    feats = {"ema": 0.2, "rsi": -0.1}
    out = predict_proba(
        feats, buy_w=[1.0, 0.5], buy_b=0.0, sell_w=[-0.8, 0.3], sell_b=0.0
    )
    assert set(out.keys()) == {"buy", "sell", "hold"}
    s = out["buy"] + out["sell"] + out["hold"]
    assert abs(s - 1.0) < 1e-9
    for v in out.values():
        assert 0.0 <= v <= 1.0


def test_prob_model_default_hold_when_no_weights():
    out = predict_proba({"ema": 0.0, "rsi": 0.0})
    # Utan vikter blir dot=bias=0 -> sigmoid(0)=0.5, p_hold=0
    # Men normaliserad simplex ger buy=sell=0.5, hold=0.0
    assert out["buy"] > 0 and out["sell"] > 0
    assert abs(out["buy"] + out["sell"] + out["hold"] - 1.0) < 1e-9

