from __future__ import annotations

import os
from typing import Any

from core.observability.metrics import metrics
from core.strategy.champion_loader import ChampionLoader
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features
from core.strategy.prob_model import predict_proba_for

champion_loader = ChampionLoader()


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, recursively merging nested dicts."""
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


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

    metrics_enabled = not bool(os.environ.get("GENESIS_DISABLE_METRICS"))
    if metrics_enabled:
        metrics.inc("pipeline_eval_invocations")

    timeframe = policy.get("timeframe", "1m")
    symbol = policy.get("symbol", "tBTCUSD")
    champion = champion_loader.load_cached(symbol, timeframe)
    champion_cfg = dict(champion.config or {})
    if configs:
        merged_cfg = _deep_merge(champion_cfg, configs)
        configs = merged_cfg
    else:
        configs = champion_cfg
    configs.setdefault("meta", {})["champion_source"] = champion.source

    feats, feats_meta = extract_features(
        candles, config=configs, timeframe=timeframe, symbol=symbol
    )
    if metrics_enabled:
        metrics.event("features_ok", {"keys": list(feats.keys())})

    # Detect regime BEFORE prediction (needed for regime-aware calibration)
    # Use unified regime detection (EMA-based, matches calibration analysis)
    from core.strategy.regime_unified import detect_regime_unified

    # Fast-path: use precomputed EMA50 if present
    pre = dict(configs.get("precomputed_features") or {})
    ema50 = pre.get("ema_50")
    closes = candles.get("close") if isinstance(candles, dict) else None
    if isinstance(ema50, list | tuple) and (closes is not None) and len(ema50) >= len(closes):
        current_price = float(closes[-1])
        current_ema = float(ema50[len(closes) - 1])
        if current_ema != 0:
            trend = (current_price - current_ema) / current_ema
            if trend > 0.02:
                current_regime = "bull"
            elif trend < -0.02:
                current_regime = "bear"
            else:
                current_regime = "ranging"
        else:
            current_regime = "balanced"
    else:
        current_regime = detect_regime_unified(candles, ema_period=50)

    # symbol/timeframe kan plockas från configs eller policy; defaulta till tBTCUSD/1m
    symbol = policy.get("symbol", "tBTCUSD")
    timeframe = policy.get("timeframe", "1m")
    probas, pmeta = predict_proba_for(symbol, timeframe, feats, regime=current_regime)
    if metrics_enabled:
        metrics.event(
            "proba_ok",
            {"schema": pmeta.get("schema", []), "versions": pmeta.get("versions", {})},
        )
    # Gauges för topproba
    if metrics_enabled:
        try:
            top = max(probas.values()) if isinstance(probas, dict) else 0.0
            metrics.set_gauge("proba_top", float(top))
        except Exception:  # nosec B110
            pass

    conf, conf_meta = compute_confidence(probas, config=configs.get("quality"))
    if metrics_enabled:
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
    if metrics_enabled:
        metrics.event("regime_ok", {"regime": regime})

    close_list = candles.get("close") if isinstance(candles, dict) else None
    last_close = None
    if close_list is not None:
        try:
            length = len(close_list)
        except Exception:
            length = 0
    else:
        length = 0
    if length > 0:
        try:
            last_close = float(close_list[-1])
        except (TypeError, ValueError):
            last_close = None

    htf_fib_data = feats_meta.get("htf_fibonacci")
    ltf_fib_data = feats_meta.get("ltf_fibonacci")

    # Diagnostik för fib-dataflöde
    from core.utils.logging_redaction import get_logger

    _eval_log = get_logger(__name__)
    _eval_log.info(
        "[FIB-FLOW] evaluate_pipeline state assembly: symbol=%s timeframe=%s htf_available=%s ltf_available=%s",
        symbol,
        timeframe,
        htf_fib_data.get("available") if isinstance(htf_fib_data, dict) else False,
        ltf_fib_data.get("available") if isinstance(ltf_fib_data, dict) else False,
    )

    state = {
        **state,
        "current_atr": feats.get("atr_14"),
        "atr_percentiles": feats_meta.get("atr_percentiles"),
        "htf_fib": htf_fib_data,
        "ltf_fib": ltf_fib_data,
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
    if metrics_enabled:
        metrics.event("decision_done", {"action": action, "size": action_meta.get("size", 0.0)})
    # Counters per action
    if metrics_enabled:
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
