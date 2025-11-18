"""
Optuna guard utilities for detecting potentially problematic trial configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ZeroTradeEstimate:
    """Result of zero-trade estimation check."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.optimizer.param_transforms import transform_parameters

from .canonical import canonicalize_config, fingerprint_config
from .trial_cache import TrialFingerprint, TrialResultCache


@dataclass(slots=True)
class ZeroTradeEstimate:
    ok: bool
    reason: str | None = None


def estimate_zero_trade(parameters: dict[str, Any]) -> ZeroTradeEstimate:
    """
    Estimate if parameters will likely result in zero trades.

    This is a preflight check to avoid running expensive backtests for
    configurations that are extremely unlikely to generate any trades.

    Args:
        parameters: Trial parameters to check

    Returns:
        ZeroTradeEstimate with ok=True if config looks reasonable,
        or ok=False with reason if it's likely to produce zero trades
    """
    # Check for extremely conservative entry thresholds
    entry_min = parameters.get("thresholds", {}).get("entry_min_confidence", 0.0)
    if entry_min > 0.99:
        return ZeroTradeEstimate(
            ok=False, reason=f"entry_min_confidence too high: {entry_min:.3f} (likely no entries)"
        )

    # Check for contradictory regime filters
    regime_cfg = parameters.get("gates", {}).get("regime", {})
    if regime_cfg.get("require_bullish") and regime_cfg.get("require_bearish"):
        return ZeroTradeEstimate(
            ok=False, reason="Cannot require both bullish and bearish regime simultaneously"
        )

    # Check for zero position sizing
    risk_cfg = parameters.get("risk", {})
    default_r = risk_cfg.get("R_default", 1.0)
    if default_r <= 0:
        return ZeroTradeEstimate(ok=False, reason=f"R_default must be positive, got {default_r}")

    # All checks passed
    return ZeroTradeEstimate(ok=True, reason=None)


__all__ = ["ZeroTradeEstimate", "estimate_zero_trade"]
def prepare_trial_params(params: dict[str, Any], *, precision: int = 6) -> TrialFingerprint:
    canonical_obj = canonicalize_config(params, precision=precision)
    canonical_json = json.dumps(canonical_obj, separators=(",", ":"), sort_keys=True)
    finger = fingerprint_config(canonical_obj, precision=precision)
    return TrialFingerprint(fingerprint=finger, canonical=canonical_json, raw=params)


def estimate_zero_trade(
    parameters: dict[str, Any],
    *,
    precision: int = 6,
) -> ZeroTradeEstimate:
    """Snabb heuristik: flagga konfigurationer som sannolikt ger 0 trades."""

    if not parameters:
        return ZeroTradeEstimate(ok=True)

    transformed, _ = transform_parameters(parameters)
    thresholds = transformed.get("thresholds") or {}
    entry_conf = thresholds.get("entry_conf_overall")

    entry_conf_value: float | None = None
    if isinstance(entry_conf, dict):
        raw = entry_conf.get("value")
        if raw is None:
            raw = entry_conf.get("default")
        try:
            entry_conf_value = float(raw) if raw is not None else None
        except (TypeError, ValueError):
            entry_conf_value = None
    elif entry_conf is not None:
        try:
            entry_conf_value = float(entry_conf)
        except (TypeError, ValueError):
            entry_conf_value = None

    if entry_conf_value is not None and entry_conf_value >= 0.98:
        return ZeroTradeEstimate(
            ok=False,
            reason=f"entry_conf_overall={entry_conf_value}>=0.98",
        )

    risk_cfg = transformed.get("risk") or {}
    risk_map = risk_cfg.get("risk_map")
    if isinstance(risk_map, list) and risk_map:
        total_size = sum(float(point[1]) for point in risk_map if isinstance(point, list | tuple))
        if total_size <= 0:
            return ZeroTradeEstimate(ok=False, reason="risk_map total size <= 0")

    return ZeroTradeEstimate(ok=True)


def evaluate_trial_with_cache(
    *,
    params: dict[str, Any],
    cache_dir: Path,
    executor: Callable[[], dict[str, Any]],
    zero_trade_penalty: float = -1e5,
    precision: int = 6,
) -> tuple[dict[str, Any], float | None, ZeroTradeEstimate]:
    """Kör trial med fingerprint-cache och zero-trade heuristik."""

    fingerprint = prepare_trial_params(params, precision=precision)
    cache = TrialResultCache(cache_dir)

    cached_payload = cache.lookup(fingerprint.fingerprint)
    if cached_payload:
        payload = dict(cached_payload)
        payload.setdefault("parameters", params)
        payload["from_cache"] = True
        return payload, cached_payload.get("score", {}).get("score"), ZeroTradeEstimate(ok=True)

    zero_trade = estimate_zero_trade(params, precision=precision)
    if not zero_trade.ok:
        payload = {
            "parameters": params,
            "skipped": True,
            "reason": "zero_trade_preflight",
            "details": zero_trade.reason,
            "score": {"score": zero_trade_penalty},
        }
        return payload, zero_trade_penalty, zero_trade

    payload = executor()
    if not payload.get("error"):
        snapshot = dict(payload)
        snapshot.setdefault("parameters", params)
        snapshot.pop("from_cache", None)
        cache.store(fingerprint.fingerprint, snapshot)
    return payload, payload.get("score", {}).get("score"), zero_trade
