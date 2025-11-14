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
