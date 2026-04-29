from __future__ import annotations

from typing import Any

from core.config.authority_mode_resolver import AUTHORITY_MODE_REGIME_MODULE
from core.strategy.family_registry import (
    FAMILY_REGISTRY,
    STRATEGY_FAMILY_LEGACY,
    STRATEGY_FAMILY_RI,
    StrategyFamily,
    StrategyFamilyValidationError,
    matches_ri_cluster,
    validate_strategy_family_identity_config,
    validate_strategy_family_name,
)
from core.strategy.run_intent import (
    RUN_INTENT_RESEARCH_SLICE,
    RunIntent,
    RunIntentValidationError,
    validate_run_intent_name,
)


class StrategyFamilyAdmissionError(ValueError):
    """Raised when family admission fails for a given run_intent."""


def _get_nested_value(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _get_parameters_mapping(opt_cfg: dict[str, Any]) -> dict[str, Any] | None:
    params_spec = opt_cfg.get("parameters", {})
    return params_spec if isinstance(params_spec, dict) else None


def _get_param_spec(params_spec: dict[str, Any], path: str) -> dict[str, Any] | None:
    direct = params_spec.get(path)
    if isinstance(direct, dict):
        return direct

    keys = path.split(".")
    current: Any = params_spec
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current if isinstance(current, dict) else None


def _spec_allows_value(spec: dict[str, Any] | None, expected: Any) -> bool:
    if not isinstance(spec, dict):
        return False
    param_type = spec.get("type")
    if param_type == "fixed":
        return spec.get("value") == expected
    if param_type == "grid":
        return expected in tuple(spec.get("values") or ())
    if param_type in {"float", "int"}:
        low = spec.get("low")
        high = spec.get("high")
        if low is None or high is None:
            return False
        try:
            expected_value = float(expected)
            return float(low) <= expected_value <= float(high)
        except (TypeError, ValueError):
            return False
    return False


def _spec_requires_exact_value(spec: dict[str, Any] | None, expected: Any) -> bool:
    if not isinstance(spec, dict):
        return False
    param_type = spec.get("type")
    if param_type == "fixed":
        return spec.get("value") == expected
    if param_type == "grid":
        return tuple(spec.get("values") or ()) == (expected,)
    return False


def _optimizer_has_ri_signature_markers(params_spec: dict[str, Any]) -> bool:
    ri_definition = FAMILY_REGISTRY[STRATEGY_FAMILY_RI]
    atr_marker = _spec_requires_exact_value(
        _get_param_spec(params_spec, "thresholds.signal_adaptation.atr_period"),
        ri_definition.required_atr_period,
    )
    gates_marker = _spec_requires_exact_value(
        _get_param_spec(params_spec, "gates.hysteresis_steps"),
        ri_definition.required_gates[0],
    ) and _spec_requires_exact_value(
        _get_param_spec(params_spec, "gates.cooldown_bars"),
        ri_definition.required_gates[1],
    )
    threshold_cluster_marker = all(
        _spec_requires_exact_value(_get_param_spec(params_spec, path), expected)
        for path, expected in ri_definition.threshold_cluster.items()
    )
    return atr_marker or gates_marker or threshold_cluster_marker


def _optimizer_matches_canonical_ri_cluster(params_spec: dict[str, Any]) -> bool:
    ri_definition = FAMILY_REGISTRY[STRATEGY_FAMILY_RI]
    return (
        _spec_requires_exact_value(
            _get_param_spec(params_spec, "multi_timeframe.regime_intelligence.authority_mode"),
            AUTHORITY_MODE_REGIME_MODULE,
        )
        and _spec_requires_exact_value(
            _get_param_spec(params_spec, "thresholds.signal_adaptation.atr_period"),
            ri_definition.required_atr_period,
        )
        and _spec_requires_exact_value(
            _get_param_spec(params_spec, "gates.hysteresis_steps"),
            ri_definition.required_gates[0],
        )
        and _spec_requires_exact_value(
            _get_param_spec(params_spec, "gates.cooldown_bars"),
            ri_definition.required_gates[1],
        )
        and all(
            _spec_allows_value(_get_param_spec(params_spec, path), expected)
            for path, expected in ri_definition.threshold_cluster.items()
        )
    )


def extract_optimizer_run_intent(opt_cfg: dict[str, Any]) -> RunIntent | None:
    raw = ((opt_cfg.get("meta") or {}).get("runs") or {}).get("run_intent")
    if raw is None:
        return None
    return validate_run_intent_name(raw)


def validate_optimizer_strategy_family_identity(opt_cfg: dict[str, Any]) -> StrategyFamily:
    family = validate_strategy_family_name(opt_cfg.get("strategy_family"))
    params_spec = _get_parameters_mapping(opt_cfg)
    if params_spec is None:
        raise StrategyFamilyValidationError("invalid_optimizer_parameters_mapping")

    authority_spec = _get_param_spec(
        params_spec, "multi_timeframe.regime_intelligence.authority_mode"
    )
    authority_is_regime_module = _spec_allows_value(authority_spec, AUTHORITY_MODE_REGIME_MODULE)
    authority_is_exact_regime_module = _spec_requires_exact_value(
        authority_spec,
        AUTHORITY_MODE_REGIME_MODULE,
    )

    if family == STRATEGY_FAMILY_LEGACY:
        if authority_is_regime_module:
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_regime_module")
        if _optimizer_has_ri_signature_markers(params_spec):
            raise StrategyFamilyValidationError("invalid_strategy_family:legacy_hybrid_signature")
        return family

    if not authority_is_exact_regime_module:
        raise StrategyFamilyValidationError("invalid_strategy_family:ri_requires_regime_module")

    return family


def validate_strategy_family_admission(
    config: dict[str, Any],
    *,
    run_intent: Any,
    family: StrategyFamily | None = None,
) -> tuple[StrategyFamily, RunIntent]:
    resolved_family = family or validate_strategy_family_identity_config(config)
    resolved_run_intent = validate_run_intent_name(run_intent)

    if resolved_family == STRATEGY_FAMILY_LEGACY:
        return resolved_family, resolved_run_intent

    if resolved_run_intent == RUN_INTENT_RESEARCH_SLICE:
        return resolved_family, resolved_run_intent

    if not matches_ri_cluster(config):
        raise StrategyFamilyAdmissionError(
            f"invalid_family_admission:ri_requires_canonical_cluster:{resolved_run_intent}"
        )

    return resolved_family, resolved_run_intent


def validate_optimizer_family_admission(
    opt_cfg: dict[str, Any]
) -> tuple[StrategyFamily, RunIntent | None]:
    resolved_family = validate_optimizer_strategy_family_identity(opt_cfg)
    run_intent = extract_optimizer_run_intent(opt_cfg)

    if resolved_family == STRATEGY_FAMILY_LEGACY:
        return resolved_family, run_intent

    if run_intent is None:
        raise RunIntentValidationError("missing_run_intent")

    if run_intent == RUN_INTENT_RESEARCH_SLICE:
        return resolved_family, run_intent

    params_spec = _get_parameters_mapping(opt_cfg)
    if params_spec is None:
        raise StrategyFamilyValidationError("invalid_optimizer_parameters_mapping")

    if not _optimizer_matches_canonical_ri_cluster(params_spec):
        raise StrategyFamilyAdmissionError(
            f"invalid_family_admission:ri_requires_canonical_cluster:{run_intent}"
        )

    return resolved_family, run_intent


__all__ = [
    "StrategyFamilyAdmissionError",
    "extract_optimizer_run_intent",
    "validate_optimizer_family_admission",
    "validate_optimizer_strategy_family_identity",
    "validate_strategy_family_admission",
]
