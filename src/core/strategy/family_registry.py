from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from core.config.authority_mode_resolver import (
    AUTHORITY_MODE_REGIME_MODULE,
    resolve_authority_mode_permissive,
)

StrategyFamily = Literal["legacy", "ri"]

STRATEGY_FAMILY_LEGACY: StrategyFamily = "legacy"
STRATEGY_FAMILY_RI: StrategyFamily = "ri"
STRATEGY_FAMILY_SOURCE = "family_registry_v1"


class StrategyFamilyValidationError(ValueError):
    """Raised when a config violates deterministic strategy-family rules."""


@dataclass(frozen=True, slots=True)
class StrategyFamilyDefinition:
    name: StrategyFamily
    required_parameters: tuple[str, ...]
    validation_rules: tuple[str, ...]
    required_authority_mode: str | None
    required_atr_period: int | None
    required_gates: tuple[int, int] | None
    threshold_cluster: dict[str, float]


_RI_THRESHOLD_CLUSTER: dict[str, float] = {
    "thresholds.entry_conf_overall": 0.25,
    "thresholds.regime_proba.balanced": 0.36,
    "thresholds.signal_adaptation.zones.low.entry_conf_overall": 0.16,
    "thresholds.signal_adaptation.zones.low.regime_proba": 0.33,
    "thresholds.signal_adaptation.zones.mid.entry_conf_overall": 0.40,
    "thresholds.signal_adaptation.zones.mid.regime_proba": 0.51,
    "thresholds.signal_adaptation.zones.high.entry_conf_overall": 0.32,
    "thresholds.signal_adaptation.zones.high.regime_proba": 0.57,
}

_RI_REQUIRED_PARAMETERS: tuple[str, ...] = (
    "strategy_family",
    "multi_timeframe.regime_intelligence.authority_mode",
    "thresholds.signal_adaptation.atr_period",
    "gates.hysteresis_steps",
    "gates.cooldown_bars",
    *tuple(_RI_THRESHOLD_CLUSTER.keys()),
)

FAMILY_REGISTRY: dict[StrategyFamily, StrategyFamilyDefinition] = {
    STRATEGY_FAMILY_LEGACY: StrategyFamilyDefinition(
        name=STRATEGY_FAMILY_LEGACY,
        required_parameters=("strategy_family",),
        validation_rules=(
            "strategy_family is mandatory",
            "legacy may not use authority_mode=regime_module",
        ),
        required_authority_mode="legacy",
        required_atr_period=None,
        required_gates=None,
        threshold_cluster={},
    ),
    STRATEGY_FAMILY_RI: StrategyFamilyDefinition(
        name=STRATEGY_FAMILY_RI,
        required_parameters=_RI_REQUIRED_PARAMETERS,
        validation_rules=(
            "strategy_family is mandatory",
            "ri requires authority_mode=regime_module",
            "ri requires thresholds.signal_adaptation.atr_period=14",
            "ri requires gates.hysteresis_steps=3 and gates.cooldown_bars=2",
            "ri requires the canonical RI threshold cluster",
        ),
        required_authority_mode=AUTHORITY_MODE_REGIME_MODULE,
        required_atr_period=14,
        required_gates=(3, 2),
        threshold_cluster=_RI_THRESHOLD_CLUSTER,
    ),
}

_ALLOWED_STRATEGY_FAMILIES = frozenset(FAMILY_REGISTRY.keys())


def _get_nested_value(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _normalize_declared_strategy_family(value: Any) -> StrategyFamily | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in _ALLOWED_STRATEGY_FAMILIES:
        return normalized  # type: ignore[return-value]
    raise StrategyFamilyValidationError("invalid_strategy_family")


def _float_equals(actual: Any, expected: float) -> bool:
    try:
        return abs(float(actual) - expected) <= 1e-9
    except (TypeError, ValueError):
        return False


def matches_threshold_cluster(config: dict[str, Any], cluster: dict[str, float]) -> bool:
    return all(
        _float_equals(_get_nested_value(config, path), expected)
        for path, expected in cluster.items()
    )


def matches_ri_cluster(config: dict[str, Any]) -> bool:
    authority_mode = resolve_authority_mode_permissive(config)
    atr_period = _get_nested_value(config, "thresholds.signal_adaptation.atr_period")
    hysteresis_steps = _get_nested_value(config, "gates.hysteresis_steps")
    cooldown_bars = _get_nested_value(config, "gates.cooldown_bars")
    ri_definition = FAMILY_REGISTRY[STRATEGY_FAMILY_RI]
    return (
        authority_mode == AUTHORITY_MODE_REGIME_MODULE
        and atr_period == ri_definition.required_atr_period
        and (hysteresis_steps, cooldown_bars) == ri_definition.required_gates
        and matches_threshold_cluster(config, ri_definition.threshold_cluster)
    )


def has_ri_signature_markers(config: dict[str, Any]) -> bool:
    ri_definition = FAMILY_REGISTRY[STRATEGY_FAMILY_RI]
    atr_period = _get_nested_value(config, "thresholds.signal_adaptation.atr_period")
    gates = (
        _get_nested_value(config, "gates.hysteresis_steps"),
        _get_nested_value(config, "gates.cooldown_bars"),
    )
    return (
        atr_period == ri_definition.required_atr_period
        or gates == ri_definition.required_gates
        or matches_threshold_cluster(config, ri_definition.threshold_cluster)
    )


def classify_strategy_family(config: dict[str, Any]) -> StrategyFamily:
    authority_mode = resolve_authority_mode_permissive(config)
    if authority_mode == AUTHORITY_MODE_REGIME_MODULE:
        if matches_ri_cluster(config):
            return STRATEGY_FAMILY_RI
        raise StrategyFamilyValidationError("invalid_strategy_family:hybrid_regime_module")
    if has_ri_signature_markers(config):
        raise StrategyFamilyValidationError("invalid_strategy_family:hybrid_legacy_signature")
    return STRATEGY_FAMILY_LEGACY


def validate_strategy_family_name(value: Any) -> StrategyFamily:
    normalized = _normalize_declared_strategy_family(value)
    if normalized is None:
        raise StrategyFamilyValidationError("missing_strategy_family")
    return normalized


def validate_strategy_family_config(config: dict[str, Any]) -> StrategyFamily:
    family = validate_strategy_family_name(config.get("strategy_family"))
    authority_mode = resolve_authority_mode_permissive(config)
    ri_definition = FAMILY_REGISTRY[STRATEGY_FAMILY_RI]

    if family == STRATEGY_FAMILY_LEGACY:
        if authority_mode == AUTHORITY_MODE_REGIME_MODULE:
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_regime_module")
        if has_ri_signature_markers(config):
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_hybrid_signature")
        return family

    if authority_mode != AUTHORITY_MODE_REGIME_MODULE:
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_requires_regime_module")

    atr_period = _get_nested_value(config, "thresholds.signal_adaptation.atr_period")
    if atr_period != ri_definition.required_atr_period:
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_requires_atr_14")

    gates = (
        _get_nested_value(config, "gates.hysteresis_steps"),
        _get_nested_value(config, "gates.cooldown_bars"),
    )
    if gates != ri_definition.required_gates:
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_requires_canonical_gates")

    if not matches_threshold_cluster(config, ri_definition.threshold_cluster):
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_threshold_cluster_mismatch")

    return family


def validate_strategy_family_identity_config(config: dict[str, Any]) -> StrategyFamily:
    family = validate_strategy_family_name(config.get("strategy_family"))
    authority_mode = resolve_authority_mode_permissive(config)

    if family == STRATEGY_FAMILY_LEGACY:
        if authority_mode == AUTHORITY_MODE_REGIME_MODULE:
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_regime_module")
        if has_ri_signature_markers(config):
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_hybrid_signature")
        return family

    if authority_mode != AUTHORITY_MODE_REGIME_MODULE:
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_requires_regime_module")

    return family


def resolve_strategy_family(config: dict[str, Any]) -> StrategyFamily:
    return validate_strategy_family_config(config)


def inject_strategy_family(config: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(config or {})
    normalized["strategy_family"] = classify_strategy_family(normalized)
    return normalized


def build_strategy_family_metadata(config: dict[str, Any]) -> dict[str, str]:
    family = validate_strategy_family_config(config)
    return {
        "strategy_family": family,
        "strategy_family_source": STRATEGY_FAMILY_SOURCE,
    }


def validate_cross_family_promotion(
    source_family: StrategyFamily,
    target_family: StrategyFamily,
    *,
    explicit_override: bool = False,
    governance_signoff: bool = False,
) -> None:
    if source_family == target_family:
        return
    if explicit_override and governance_signoff:
        return
    raise StrategyFamilyValidationError("cross_family_promotion_requires_override_and_signoff")


__all__ = [
    "FAMILY_REGISTRY",
    "STRATEGY_FAMILY_LEGACY",
    "STRATEGY_FAMILY_RI",
    "STRATEGY_FAMILY_SOURCE",
    "StrategyFamily",
    "StrategyFamilyDefinition",
    "StrategyFamilyValidationError",
    "build_strategy_family_metadata",
    "classify_strategy_family",
    "has_ri_signature_markers",
    "inject_strategy_family",
    "matches_ri_cluster",
    "matches_threshold_cluster",
    "resolve_strategy_family",
    "validate_cross_family_promotion",
    "validate_strategy_family_config",
    "validate_strategy_family_identity_config",
    "validate_strategy_family_name",
]
