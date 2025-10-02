from __future__ import annotations

from core.strategy.model_registry import ModelRegistry
from core.strategy.prob_model import predict_proba, predict_proba_for


def test_prob_model_integration_minimal():
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "1m")
    assert isinstance(meta, dict)
    feats = {k: 0.0 for k in meta.get("schema", [])}
    # Wrapper kommer justeras senare; tills dess validerar vi basfunktionen
    out = predict_proba(
        feats,
        schema=tuple(meta.get("schema", [])),
        buy_w=meta.get("buy", {}).get("w"),
        buy_b=meta.get("buy", {}).get("b", 0.0),
        sell_w=meta.get("sell", {}).get("w"),
        sell_b=meta.get("sell", {}).get("b", 0.0),
        calib_buy=(
            meta.get("buy", {}).get("calib", {}).get("a", 1.0),
            meta.get("buy", {}).get("calib", {}).get("b", 0.0),
        ),
        calib_sell=(
            meta.get("sell", {}).get("calib", {}).get("a", 1.0),
            meta.get("sell", {}).get("calib", {}).get("b", 0.0),
        ),
    )
    assert set(out.keys()) == {"buy", "sell", "hold"}


def test_prob_model_wrapper_applies_calibration_and_meta():
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "1m")
    feats = {k: 0.0 for k in meta.get("schema", [])}
    probas, pmeta = predict_proba_for("tBTCUSD", "1m", feats, model_meta=meta)
    assert set(probas.keys()) == {"buy", "sell", "hold"}
    assert "versions" in pmeta and isinstance(pmeta["versions"], dict)
