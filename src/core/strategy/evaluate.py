from __future__ import annotations

from typing import Any

from core.observability.metrics import metrics
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features import extract_features
from core.strategy.prob_model import predict_proba_for
from core.strategy.regime import classify_regime


def evaluate_pipeline(
    candles: dict[str, Any],
    *,
    policy: dict[str, Any] | None = None,
    configs: dict[str, Any] | None = None,
    state: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Tunn orkestrerare som komponerar pure‑modulerna (utan IO/logg).

    Returnerar (result, meta). Meta bör inkludera reasons/versions från delmodulerna.
    """
    policy = dict(policy or {})
    configs = dict(configs or {})
    state = dict(state or {})

    metrics.inc("pipeline_eval_invocations")

    feats, feats_meta = extract_features(candles, config=configs)
    metrics.event("features_ok", {"keys": list(feats.keys())})

    # symbol/timeframe kan plockas från configs eller policy; defaulta till tBTCUSD/1m
    symbol = policy.get("symbol", "tBTCUSD")
    timeframe = policy.get("timeframe", "1m")
    probas, pmeta = predict_proba_for(symbol, timeframe, feats)
    metrics.event(
        "proba_ok",
        {"schema": pmeta.get("schema", []), "versions": pmeta.get("versions", {})},
    )
    # Gauges för topproba
    try:
        top = max(probas.values()) if isinstance(probas, dict) else 0.0
        metrics.set_gauge("proba_top", float(top))
    except Exception:  # nosec B110
        pass

    conf, conf_meta = compute_confidence(probas, config=configs.get("quality"))
    metrics.event("confidence_ok", {})
    try:
        metrics.set_gauge("confidence_buy", float(conf.get("buy", 0.0)))
        metrics.set_gauge("confidence_sell", float(conf.get("sell", 0.0)))
    except Exception:  # nosec B110
        pass

    # HTF-features kan komma utifrån; här matar vi tomma för stub
    regime, regime_state = classify_regime({}, prev_state=state, config=configs)
    metrics.event("regime_ok", {"regime": regime})

    action, action_meta = decide(
        policy,
        probas=probas,
        confidence=conf,
        regime=regime,
        state=state,
        risk_ctx=configs.get("risk"),
        cfg=configs,
    )
    metrics.event("decision_done", {"action": action, "size": action_meta.get("size", 0.0)})
    # Counters per action
    try:
        if action in ("LONG", "SHORT", "NONE"):
            metrics.inc(f"decision_{action.lower()}")
    except Exception:  # nosec B110
        pass
    result: dict[str, Any] = {
        "features": feats,
        "probas": probas,
        "confidence": conf,
        "regime": regime,
        "action": action,
    }
    meta: dict[str, Any] = {
        "features": feats_meta,
        "proba": pmeta,
        "confidence": conf_meta,
        "regime": regime_state,
        "decision": action_meta,
    }
    return result, meta
