from __future__ import annotations

import os
from typing import Any

from core.config.authority_mode_resolver import (
    AUTHORITY_MODE_REGIME_MODULE,
)
from core.config.authority_mode_resolver import (
    resolve_authority_mode_with_source_permissive as _resolve_authority_mode_with_source,
)
from core.config.merge_policy import resolve_champion_merge_for_evaluate
from core.intelligence.regime.authority import (
    detect_authoritative_regime_legacy as _detect_intelligence_authoritative_regime_legacy,
)
from core.intelligence.regime.authority import (
    normalize_authoritative_regime as _normalize_intelligence_authoritative_regime,
)
from core.intelligence.regime.htf import (
    compute_htf_regime as _compute_intelligence_htf_regime,
)
from core.observability.metrics import metrics
from core.strategy.champion_loader import ChampionLoader
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features_backtest, extract_features_live
from core.strategy.fib_logging import log_fib_flow
from core.strategy.prob_model import predict_proba_for
from core.utils.dict_merge import deep_merge_dicts
from core.utils.env_flags import env_flag_enabled

champion_loader = ChampionLoader()


def _metrics_enabled() -> bool:
    """Return whether observability metrics should be emitted for this process.

    Note: `GENESIS_DISABLE_METRICS` is a *disable* flag.
    """

    return not env_flag_enabled(os.getenv("GENESIS_DISABLE_METRICS"), default=False)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _volume_score_from_candles(
    candles: dict[str, Any],
    *,
    window: int = 50,
    cap_ratio: float = 3.0,
) -> float | None:
    """Return a stable volume_score in [0,1] (None if unavailable).

    Definition (simple, robust):
    - ratio = v_now / median(v_recent)
    - score = clamp(ratio, 0, 1)

    Rationale:
    - Normal volume (ratio≈1) should be treated as *good* quality → score≈1.
    - Only unusually low volume should reduce quality.
    """
    vols = None
    if isinstance(candles, dict):
        vols = candles.get("volume")
        if vols is None:
            vols = candles.get("vol")
    # In backtests, fast_window can pass numpy arrays. Accept any sequence-like.
    if vols is None or not hasattr(vols, "__len__") or len(vols) == 0:
        return None

    try:
        v_now = float(vols[-1])
    except Exception:
        return None

    if v_now <= 0:
        return 0.0

    start = max(0, len(vols) - int(window))
    recent = []
    for v in vols[start:]:
        vf = _safe_float(v)
        if vf is not None and vf > 0:
            recent.append(vf)
    if not recent:
        return 0.0

    recent_sorted = sorted(recent)
    median = recent_sorted[len(recent_sorted) // 2]
    if median <= 0:
        return 0.0

    ratio = v_now / median
    cap_ratio = float(cap_ratio) if cap_ratio is not None else 3.0
    # cap_ratio is an outlier cap; values below 1 would artificially penalize
    # normal/median volume and violate the intended semantics.
    cap_ratio = 1.0 if cap_ratio < 1.0 else cap_ratio
    # Cap extreme outliers but don't penalize typical/median volume.
    ratio = min(ratio, cap_ratio)
    score = ratio
    if score != score:  # NaN
        return None
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return float(score)


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, recursively merging nested dicts."""
    return deep_merge_dicts(base, override)


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    """Compatibility wrapper for HTF regime logic.

    Keep this symbol local in evaluate.py for tests/monkeypatching parity.
    """

    return _compute_intelligence_htf_regime(
        htf_fib_data,
        current_price=current_price,
    )


def _detect_shadow_regime_from_regime_module(candles: dict[str, Any]) -> str | None:
    """Compatibility wrapper for shadow observer logic.

    Keep this symbol local in evaluate.py for tests/monkeypatching parity.
    """

    try:
        from core.strategy.regime import detect_regime_from_candles

        return str(detect_regime_from_candles(candles))
    except Exception:
        return None


def _detect_authoritative_regime(candles: dict[str, Any], configs: dict[str, Any]) -> str:
    """Compatibility wrapper for authoritative regime detection.

    Authority remains `regime_unified.detect_regime_unified` inside the delegated module path.
    """

    authority_mode, _source = _resolve_authority_mode_with_source(configs)
    if authority_mode == AUTHORITY_MODE_REGIME_MODULE:
        observed = _detect_shadow_regime_from_regime_module(candles)
        return _normalize_intelligence_authoritative_regime(observed)

    from core.strategy import regime_unified as _regime_unified

    return _detect_intelligence_authoritative_regime_legacy(
        candles,
        configs,
        fallback_detect_regime_unified=lambda fallback_candles: _regime_unified.detect_regime_unified(
            fallback_candles,
            ema_period=50,
        ),
    )


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

    metrics_enabled = _metrics_enabled()
    if metrics_enabled:
        metrics.inc("pipeline_eval_invocations")

    # Backtests/optimizer runs inject `_global_index` on every bar. In that mode,
    # treat `configs` as the *authoritative* config. Do NOT merge in the active
    # champion, otherwise results become dependent on whichever champion file is
    # currently active (non-reproducible and extremely confusing).
    merge_resolution = resolve_champion_merge_for_evaluate(configs)
    force_backtest_mode = not merge_resolution.should_merge

    timeframe = policy.get("timeframe", "1m")
    symbol = policy.get("symbol", "tBTCUSD")
    champion = champion_loader.load_cached(symbol, timeframe)

    if force_backtest_mode:
        configs.setdefault("meta", {})["champion_source"] = "explicit_backtest_config"
    else:
        champion_cfg = dict(champion.config or {})
        if configs:
            configs = _deep_merge(champion_cfg, configs)
        else:
            configs = champion_cfg
        configs.setdefault("meta", {})["champion_source"] = champion.source

    closes = candles.get("close") if isinstance(candles, dict) else None
    total_bars = len(closes) if closes is not None else 0
    now_index = total_bars if force_backtest_mode and total_bars > 0 else None

    # Avoid deprecated compatibility wrapper (`features_asof.extract_features`) in core runtime code.
    # Semantics must remain identical:
    # - Live: last bar is forming -> use last CLOSED bar (len-2)
    # - Backtest/optimizer: all bars closed -> use last bar (len-1)
    if now_index is None:
        feats, feats_meta = extract_features_live(
            candles,
            config=configs,
            timeframe=timeframe,
            symbol=symbol,
        )
    else:
        feats, feats_meta = extract_features_backtest(
            candles,
            total_bars - 1,
            config=configs,
            timeframe=timeframe,
            symbol=symbol,
        )
    if metrics_enabled:
        metrics.event("features_ok", {"keys": list(feats.keys())})

    # Detect regime BEFORE prediction (needed for regime-aware calibration).
    # Authority path is config-gated in delegated regime_intelligence module.
    authority_mode, authority_mode_source = _resolve_authority_mode_with_source(configs)
    authoritative_source = (
        "regime.detect_regime_from_candles"
        if authority_mode == AUTHORITY_MODE_REGIME_MODULE
        else "regime_unified.detect_regime_unified"
    )
    current_regime = _detect_authoritative_regime(candles, configs)

    # Shadow-only observer path (T2): compute regime.py signal for observability only.
    # Authority for decision path remains `detect_regime_unified` above.
    shadow_regime = _detect_shadow_regime_from_regime_module(candles)
    shadow_regime_mismatch: bool | None = None
    if shadow_regime is not None:
        shadow_regime_mismatch = str(shadow_regime) != str(current_regime)

    # symbol/timeframe kan plockas från configs eller policy; defaulta till tBTCUSD/1m
    symbol = policy.get("symbol", "tBTCUSD")
    timeframe = policy.get("timeframe", "1m")
    meta_cfg = dict(configs.get("meta") or {})
    research_model_meta_path = meta_cfg.get("research_model_meta_path")
    if (
        research_model_meta_path is not None
        and meta_cfg.get("run_intent") != "research_code_experiment"
    ):
        raise ValueError("research_model_meta_path_requires_research_code_experiment")
    predict_kwargs: dict[str, Any] = {"regime": current_regime}
    if research_model_meta_path is not None:
        predict_kwargs["research_model_meta_path"] = str(research_model_meta_path)
    probas, pmeta = predict_proba_for(symbol, timeframe, feats, **predict_kwargs)
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

    # --- Market quality inputs for confidence (fail-safe: None => neutral) ---
    last_close = None
    if closes is not None:
        try:
            if len(closes) > 0:
                last_close = float(closes[-1])
        except Exception:
            last_close = None

    current_atr = _safe_float(feats_meta.get("current_atr_used"))
    if current_atr is None:
        current_atr = _safe_float(feats.get("atr_14"))
    atr_pct = None
    if current_atr is not None and last_close is not None and last_close > 0:
        atr_pct = float(current_atr / last_close)

    quality_cfg = dict(configs.get("quality") or {})
    pipeline_cfg = dict(quality_cfg.get("pipeline") or {})

    spread_bp = _safe_float(pipeline_cfg.get("spread_bp"))

    volume_score = _volume_score_from_candles(
        candles,
        window=int(pipeline_cfg.get("volume_window", 50) or 50),
        cap_ratio=float(pipeline_cfg.get("volume_cap_ratio", 3.0) or 3.0),
    )

    # data_quality in [0,1]; keep it conservative and deterministic
    data_quality = 1.0
    if last_close is None:
        data_quality = 0.0
    elif current_atr is None or current_atr <= 0:
        data_quality = 0.5
    if volume_score is not None and volume_score <= 0.0:
        data_quality = min(data_quality, 0.5)

    # Optional staleness check (timestamp deltas). If unavailable, stay neutral.
    ts = candles.get("timestamp") if isinstance(candles, dict) else None
    if isinstance(ts, list | tuple) and len(ts) >= 2:
        t1 = _safe_float(ts[-1])
        t0 = _safe_float(ts[-2])
        if t1 is not None and t0 is not None:
            dt = float(t1) - float(t0)
            if dt > 0:
                # Detect ms vs seconds by magnitude of delta.
                dt_seconds = dt / 1000.0 if dt > 10_000 else dt
                expected: float | None = None
                try:
                    from core.strategy.htf_selector import TIMEFRAME_TO_MINUTES

                    minutes = TIMEFRAME_TO_MINUTES.get(str(timeframe))
                    if minutes is not None:
                        expected = float(minutes) * 60.0
                except Exception:
                    expected = None

                # If we can estimate expected, penalize if too stale.
                if expected is not None:
                    factor = _safe_float(pipeline_cfg.get("stale_threshold_factor"))
                    factor = 3.0 if factor is None or factor <= 0 else float(factor)
                    if dt_seconds > expected * factor:
                        data_quality = min(data_quality, 0.5)

    conf_scaled, conf_meta = compute_confidence(
        probas,
        atr_pct=atr_pct,
        spread_bp=spread_bp,
        volume_score=volume_score,
        data_quality=data_quality,
        config=quality_cfg,
    )

    # Exit-safety: keep a *raw* (unscaled) confidence view for traditional exits.
    # We intentionally do NOT apply market-quality scaling here, otherwise a benign
    # quality dip can trigger CONF_DROP churn.
    conf_exit, conf_exit_meta = compute_confidence(
        probas,
        data_quality=data_quality,
        config={"enabled": False},
    )

    # Quality application mode:
    # - both (default): scaled confidence affects both entry gating and sizing.
    # - sizing_only: raw confidence gates entries, but scaled confidence is used for sizing.
    quality_apply = str(quality_cfg.get("apply") or "both").strip().lower()
    conf_for_decide = conf_scaled
    if quality_apply in {"sizing_only", "sizing", "size_only"}:
        # Keep entry gating behavior identical to the baseline (raw confidence),
        # while still letting market-quality reduce/increase position sizing.
        conf_for_decide = dict(conf_exit)
        conf_for_decide["buy_scaled"] = float(conf_scaled.get("buy", 0.0))
        conf_for_decide["sell_scaled"] = float(conf_scaled.get("sell", 0.0))
        conf_for_decide["overall_scaled"] = float(conf_scaled.get("overall", 0.0))
        conf_for_decide["quality_apply"] = "sizing_only"
    if metrics_enabled:
        metrics.event("confidence_ok", {})
        try:
            metrics.set_gauge("confidence_buy", float(conf_scaled.get("buy", 0.0)))
            metrics.set_gauge("confidence_sell", float(conf_scaled.get("sell", 0.0)))
        except Exception:  # nosec B110
            pass

    # Use already detected regime (from candles-based detection)
    # Note: classify_regime with hysteresis could be added later for stability
    regime = current_regime
    regime_state = {"regime": regime, "steps": 0, "candidate": regime}
    if metrics_enabled:
        metrics.event("regime_ok", {"regime": regime})

    if closes is not None:
        try:
            total_bars = len(closes)
        except Exception:
            total_bars = 0
    else:
        total_bars = 0

    htf_fib_data = feats_meta.get("htf_fibonacci")
    ltf_fib_data = feats_meta.get("ltf_fibonacci")

    # Compute HTF regime for defensive position sizing
    # This provides "early warning" when 1D structure is bearish
    htf_regime = compute_htf_regime(htf_fib_data, current_price=last_close)

    log_fib_flow(
        "[FIB-FLOW] evaluate_pipeline state assembly: symbol=%s timeframe=%s htf_available=%s ltf_available=%s htf_regime=%s",
        symbol,
        timeframe,
        htf_fib_data.get("available") if isinstance(htf_fib_data, dict) else False,
        ltf_fib_data.get("available") if isinstance(ltf_fib_data, dict) else False,
        htf_regime,
    )

    state = {
        **state,
        "current_atr": current_atr,
        "atr_percentiles": feats_meta.get("atr_percentiles"),
        "htf_fib": htf_fib_data,
        "ltf_fib": ltf_fib_data,
        "last_close": last_close,
        "htf_regime": htf_regime,
    }

    action, action_meta = decide(
        policy,
        probas=probas,
        confidence=conf_for_decide,
        regime=regime,
        htf_regime=htf_regime,
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
        "confidence": conf_for_decide,
        "confidence_exit": conf_exit,
        "regime": regime,
        "htf_regime": htf_regime,
        "action": action,
    }
    meta: dict[str, Any] = {
        "features": feats_meta,
        "proba": pmeta,
        "confidence": conf_meta,
        "confidence_exit": conf_exit_meta,
        "regime": regime_state,
        "htf_regime": htf_regime,
        "decision": action_meta,
        "champion": {
            "source": configs.get("meta", {}).get("champion_source"),
        },
        "observability": {
            "shadow_regime": {
                "authoritative_source": authoritative_source,
                "shadow_source": "regime.detect_regime_from_candles",
                "authority_mode": authority_mode,
                "authority_mode_source": authority_mode_source,
                "authority": regime,
                "shadow": shadow_regime,
                "mismatch": shadow_regime_mismatch,
                "decision_input": False,
            }
        },
    }
    return result, meta
