from __future__ import annotations

import os
from typing import Any

from core.observability.metrics import metrics
from core.strategy.champion_loader import ChampionLoader
from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features_backtest, extract_features_live
from core.strategy.fib_logging import log_fib_flow
from core.strategy.prob_model import predict_proba_for
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
    cap_ratio = 1.0 if cap_ratio <= 0 else cap_ratio
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
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    """Compute regime from HTF (1D) Fibonacci context for defensive sizing.

    This function derives a regime classification from the HTF swing structure
    to enable position size adjustments when the higher timeframe is bearish.

    The regime is determined by the relationship between current price and
    HTF Fibonacci levels:
    - "bull": Price above 0.618 retracement (strong uptrend structure)
    - "bear": Price below 0.382 retracement (strong downtrend structure)
    - "ranging": Price between 0.382 and 0.618 (consolidation)
    - "unknown": Insufficient HTF data available

    Args:
        htf_fib_data: HTF Fibonacci context dict from features_asof, containing
            keys like 'swing_high', 'swing_low', 'levels', 'available'.
        current_price: Current LTF close price for regime determination.

    Returns:
        Regime string: "bull", "bear", "ranging", or "unknown".

    Note:
        This is intentionally separate from LTF regime detection (EMA-based).
        HTF regime changes slowly (~days) and provides "early warning" for
        position sizing adjustments before LTF signals deteriorate.

    Example:
        >>> htf_data = {"available": True, "swing_high": 100000, "swing_low": 80000}
        >>> compute_htf_regime(htf_data, current_price=95000)
        'bull'  # Price in upper part of swing range

    See also:
        - decision.py: htf_regime_size_multipliers config
        - decision.py: volatility_sizing config
        - AGENTS.md: Section "HTF-Regim + Volatilitet styr Sizing"
    """
    if not htf_fib_data or not isinstance(htf_fib_data, dict):
        return "unknown"

    if not htf_fib_data.get("available"):
        return "unknown"

    if current_price is None or current_price <= 0:
        return "unknown"

    # Extract swing bounds from HTF context
    swing_high = _safe_float(htf_fib_data.get("swing_high"))
    swing_low = _safe_float(htf_fib_data.get("swing_low"))

    if swing_high is None or swing_low is None:
        return "unknown"

    if swing_high <= swing_low:
        return "unknown"

    # Calculate position within swing range (0 = at low, 1 = at high)
    swing_range = swing_high - swing_low
    position_in_range = (current_price - swing_low) / swing_range

    # Classify based on position in swing range
    # These thresholds align with Fibonacci retracement levels
    if position_in_range >= 0.618:
        return "bull"
    elif position_in_range <= 0.382:
        return "bear"
    else:
        return "ranging"


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
    force_backtest_mode = "_global_index" in configs

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

    # Detect regime BEFORE prediction (needed for regime-aware calibration)
    # Use unified regime detection (EMA-based, matches calibration analysis)
    from core.strategy.regime_unified import detect_regime_unified

    # Fast-path: use precomputed EMA50 if present.
    # IMPORTANT: In backtests/optimizer we feed a *windowed* candles dict (e.g. last 200 bars)
    # but `precomputed_features` contains full-series arrays. In that mode, index EMA by
    # `_global_index` (injected by BacktestEngine) rather than `len(closes)-1`.
    pre = dict(configs.get("precomputed_features") or {})
    ema50 = pre.get("ema_50")
    closes = candles.get("close") if isinstance(candles, dict) else None

    ema_idx: int | None = None
    if "_global_index" in configs:
        try:
            ema_idx = int(configs.get("_global_index"))
        except (TypeError, ValueError):
            ema_idx = None
    if ema_idx is None and closes is not None:
        ema_idx = len(closes) - 1

    if (
        isinstance(ema50, list | tuple)
        and (closes is not None)
        and (ema_idx is not None)
        and 0 <= ema_idx < len(ema50)
    ):
        current_price = float(closes[-1])
        current_ema = float(ema50[ema_idx])
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
    }
    return result, meta
