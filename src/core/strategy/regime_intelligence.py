from __future__ import annotations

from typing import Any

_AUTHORITY_MODE_LEGACY = "legacy"
_AUTHORITY_MODE_REGIME_MODULE = "regime_module"
_ALLOWED_AUTHORITY_MODES = {_AUTHORITY_MODE_LEGACY, _AUTHORITY_MODE_REGIME_MODULE}
_AUTHORITY_MODE_SOURCE_CANONICAL = "multi_timeframe.regime_intelligence.authority_mode"
_AUTHORITY_MODE_SOURCE_ALIAS = "regime_unified.authority_mode"
_AUTHORITY_MODE_SOURCE_DEFAULT = "default_legacy"
_AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK = "canonical_invalid_fallback_legacy"
_AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK = "alias_invalid_fallback_legacy"


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def compute_htf_regime(
    htf_fib_data: dict[str, Any] | None,
    current_price: float | None = None,
) -> str:
    """Compute regime from HTF (1D) Fibonacci context for defensive sizing."""
    if not htf_fib_data or not isinstance(htf_fib_data, dict):
        return "unknown"

    if not htf_fib_data.get("available"):
        return "unknown"

    if current_price is None or current_price <= 0:
        return "unknown"

    swing_high = _safe_float(htf_fib_data.get("swing_high"))
    swing_low = _safe_float(htf_fib_data.get("swing_low"))

    if swing_high is None or swing_low is None:
        return "unknown"

    if swing_high <= swing_low:
        return "unknown"

    swing_range = swing_high - swing_low
    position_in_range = (current_price - swing_low) / swing_range

    if position_in_range >= 0.618:
        return "bull"
    elif position_in_range <= 0.382:
        return "bear"
    else:
        return "ranging"


def detect_shadow_regime_from_regime_module(candles: dict[str, Any]) -> str | None:
    """Compute regime.py observer value in shadow-only mode."""
    try:
        from core.strategy.regime import detect_regime_from_candles

        return str(detect_regime_from_candles(candles))
    except Exception:
        return None


def _normalize_authority_mode(value: Any) -> str | None:
    normalized = str(value).strip().lower() if value is not None else _AUTHORITY_MODE_LEGACY
    return normalized if normalized in _ALLOWED_AUTHORITY_MODES else None


def resolve_authority_mode_with_source(configs: dict[str, Any] | None) -> tuple[str, str]:
    """Resolve authority mode + source with deterministic precedence.

    Precedence contract:
    1) `multi_timeframe.regime_intelligence.authority_mode` (canonical)
    2) `regime_unified.authority_mode` (compatibility alias)
    3) default legacy fallback

    If canonical key is present but invalid, fallback is always legacy even when alias is valid.
    """

    cfg = dict(configs or {})

    mtf = cfg.get("multi_timeframe")
    regime_intelligence_cfg = mtf.get("regime_intelligence") if isinstance(mtf, dict) else None
    canonical_present = isinstance(regime_intelligence_cfg, dict) and (
        "authority_mode" in regime_intelligence_cfg
    )
    if canonical_present:
        canonical_mode = _normalize_authority_mode(regime_intelligence_cfg.get("authority_mode"))
        if canonical_mode is not None:
            return canonical_mode, _AUTHORITY_MODE_SOURCE_CANONICAL
        return _AUTHORITY_MODE_LEGACY, _AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK

    alias_cfg = cfg.get("regime_unified")
    alias_present = isinstance(alias_cfg, dict) and ("authority_mode" in alias_cfg)
    if alias_present:
        alias_mode = _normalize_authority_mode(alias_cfg.get("authority_mode"))
        if alias_mode is not None:
            return alias_mode, _AUTHORITY_MODE_SOURCE_ALIAS
        return _AUTHORITY_MODE_LEGACY, _AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK

    return _AUTHORITY_MODE_LEGACY, _AUTHORITY_MODE_SOURCE_DEFAULT


def resolve_authority_mode(configs: dict[str, Any] | None) -> str:
    """Resolve configured regime authority mode with safe legacy fallback."""

    mode, _source = resolve_authority_mode_with_source(configs)
    return mode


def _detect_authoritative_regime_legacy(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str:
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
                return "bull"
            elif trend < -0.02:
                return "bear"
            else:
                return "ranging"
        return "balanced"

    from core.strategy import regime_unified as _regime_unified

    return _regime_unified.detect_regime_unified(candles, ema_period=50)


def detect_authoritative_regime(
    candles: dict[str, Any],
    configs: dict[str, Any],
) -> str:
    """Return authoritative regime for evaluate decision path.

    Default authority path is legacy (precomputed EMA50 / regime_unified).
    When configured with `multi_timeframe.regime_intelligence.authority_mode=regime_module`
    (or compatibility alias `regime_unified.authority_mode=regime_module`),
    authority switches explicitly to `regime.detect_regime_from_candles`.
    """
    authority_mode = resolve_authority_mode(configs)
    if authority_mode == _AUTHORITY_MODE_REGIME_MODULE:
        observed = detect_shadow_regime_from_regime_module(candles)
        normalized = str(observed).strip().lower() if observed is not None else ""
        if normalized in {"bull", "bear", "ranging", "balanced"}:
            return normalized
        return "balanced"

    return _detect_authoritative_regime_legacy(candles, configs)
