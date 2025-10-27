from __future__ import annotations

from typing import Any

from core.observability.metrics import metrics
from core.strategy.champion_loader import ChampionLoader
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features
from core.strategy.prob_model import predict_proba_for

champion_loader = ChampionLoader()


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

    timeframe = policy.get("timeframe", "1m")
    symbol = policy.get("symbol", "tBTCUSD")
    champion = champion_loader.load_cached(symbol, timeframe)
    champion_cfg = dict(champion.config or {})
    if configs:
        merged_cfg = champion_cfg
        merged_cfg.update(configs)
        configs = merged_cfg
    else:
        configs = champion_cfg
    configs.setdefault("meta", {})["champion_source"] = champion.source

    feats, feats_meta = extract_features(
        candles, config=configs, timeframe=timeframe, symbol=symbol
    )
    metrics.event("features_ok", {"keys": list(feats.keys())})

    # Detect regime BEFORE prediction (needed for regime-aware calibration)
    # Use unified regime detection (EMA-based, matches calibration analysis)
    from core.strategy.regime_unified import detect_regime_unified

    current_regime = detect_regime_unified(candles, ema_period=50)

    # symbol/timeframe kan plockas från configs eller policy; defaulta till tBTCUSD/1m
    symbol = policy.get("symbol", "tBTCUSD")
    timeframe = policy.get("timeframe", "1m")
    probas, pmeta = predict_proba_for(symbol, timeframe, feats, regime=current_regime)
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

    # Use already detected regime (from candles-based detection)
    # Note: classify_regime with hysteresis could be added later for stability
    regime = current_regime
    regime_state = {"regime": regime, "steps": 0, "candidate": regime}
    metrics.event("regime_ok", {"regime": regime})

    close_list = candles.get("close") if isinstance(candles, dict) else None
    last_close = None
    if close_list:
        try:
            last_close = float(close_list[-1])
        except (TypeError, ValueError):
            last_close = None

    state = {
        **state,
        "current_atr": feats.get("atr_14"),
        "atr_percentiles": feats_meta.get("atr_percentiles"),
        "htf_fib": feats_meta.get("htf_fibonacci"),
        "ltf_fib": feats_meta.get("ltf_fibonacci"),
        "last_close": last_close,
    }

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
        "champion": {
            "source": configs.get("meta", {}).get("champion_source"),
        },
    }
    return result, meta
