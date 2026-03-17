from __future__ import annotations

import math
from dataclasses import dataclass

from core.intelligence.events.models import JsonValue
from core.intelligence.parameter.interface import (
    ApprovedParameterSet,
    ParameterAnalysisRequest,
    ParameterAnalysisResult,
    ParameterIntelligenceAnalyzer,
    ParameterRecommendation,
)

PREFERRED_THRESHOLD = 0.7
REVIEW_THRESHOLD = 0.5
_ALLOWED_DISPOSITIONS = frozenset({"preferred", "review", "defer"})


class ParameterAnalysisValidationError(ValueError):
    """Raised when parameter-intelligence inputs violate deterministic requirements."""


def _validate_json_value(value: JsonValue, *, path: str) -> None:
    if isinstance(value, str | bool) or value is None or isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ParameterAnalysisValidationError(f"{path} must contain finite floats only")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ParameterAnalysisValidationError(f"{path} keys must be strings")
            _validate_json_value(item, path=f"{path}.{key}")
        return
    raise ParameterAnalysisValidationError(f"{path} contains unsupported JSON value")


def _clamp01(value: float, *, field_name: str) -> float:
    if not math.isfinite(value):
        raise ParameterAnalysisValidationError(f"{field_name} must be finite")
    return max(0.0, min(1.0, float(value)))


def _validate_parameter_set(parameter_set: ApprovedParameterSet, *, seen_ids: set[str]) -> None:
    if not parameter_set.parameter_set_id.strip():
        raise ParameterAnalysisValidationError("parameter_set_id must be non-empty")
    if parameter_set.parameter_set_id in seen_ids:
        raise ParameterAnalysisValidationError("parameter_set_id values must be unique")
    seen_ids.add(parameter_set.parameter_set_id)
    if not parameter_set.parameters:
        raise ParameterAnalysisValidationError("parameters must be non-empty")
    _validate_json_value(
        parameter_set.parameters, path=f"{parameter_set.parameter_set_id}.parameters"
    )
    _clamp01(parameter_set.sensitivity_score, field_name="sensitivity_score")
    _clamp01(parameter_set.stability_score, field_name="stability_score")
    _clamp01(parameter_set.consistency_score, field_name="consistency_score")
    if not math.isfinite(parameter_set.baseline_weight) or parameter_set.baseline_weight <= 0.0:
        raise ParameterAnalysisValidationError("baseline_weight must be positive and finite")
    if not math.isfinite(parameter_set.risk_multiplier) or parameter_set.risk_multiplier <= 0.0:
        raise ParameterAnalysisValidationError("risk_multiplier must be positive and finite")
    for entity_id in parameter_set.source_ledger_entity_ids:
        if not entity_id.strip():
            raise ParameterAnalysisValidationError("source_ledger_entity_ids must be non-empty")


def _validate_request(request: ParameterAnalysisRequest) -> None:
    if not request.evaluations:
        raise ParameterAnalysisValidationError("evaluations must not be empty")
    if not request.approved_parameter_sets:
        raise ParameterAnalysisValidationError("approved_parameter_sets must not be empty")

    seen_event_ids: set[str] = set()
    for evaluation in request.evaluations:
        if not evaluation.event_id.strip():
            raise ParameterAnalysisValidationError("evaluation event_id must be non-empty")
        if evaluation.event_id in seen_event_ids:
            raise ParameterAnalysisValidationError("evaluation event_id values must be unique")
        seen_event_ids.add(evaluation.event_id)
        if not math.isfinite(evaluation.score):
            raise ParameterAnalysisValidationError("evaluation scores must be finite")

    seen_ids: set[str] = set()
    for parameter_set in request.approved_parameter_sets:
        _validate_parameter_set(parameter_set, seen_ids=seen_ids)


def _evaluation_support(request: ParameterAnalysisRequest) -> tuple[float, float, tuple[str, ...]]:
    scores = tuple(
        _clamp01(item.score, field_name="evaluation.score") for item in request.evaluations
    )
    avg_score = sum(scores) / len(scores)
    high_priority_share = sum(
        1 for item in request.evaluations if item.disposition == "high_priority"
    ) / len(request.evaluations)
    event_ids = tuple(item.event_id for item in request.evaluations)
    return round(avg_score, 6), round(high_priority_share, 6), event_ids


def _disposition_for_score(score: float) -> str:
    if score >= PREFERRED_THRESHOLD:
        return "preferred"
    if score >= REVIEW_THRESHOLD:
        return "review"
    return "defer"


def _weighting_suggestion(
    parameter_set: ApprovedParameterSet,
    *,
    stability_score: float,
    high_priority_share: float,
) -> float:
    suggestion = parameter_set.baseline_weight * (
        0.85 + (0.30 * stability_score) + (0.10 * high_priority_share)
    )
    return round(max(0.1, min(3.0, suggestion)), 6)


def _risk_multiplier_suggestion(
    parameter_set: ApprovedParameterSet,
    *,
    inverse_sensitivity: float,
    consistency_score: float,
) -> float:
    suggestion = parameter_set.risk_multiplier * (
        0.70 + (0.20 * consistency_score) + (0.10 * inverse_sensitivity)
    )
    return round(max(0.1, min(2.0, suggestion)), 6)


def _recommendation(
    parameter_set: ApprovedParameterSet,
    *,
    evaluation_support: float,
    high_priority_share: float,
    supporting_event_ids: tuple[str, ...],
) -> ParameterRecommendation:
    sensitivity_score = _clamp01(parameter_set.sensitivity_score, field_name="sensitivity_score")
    stability_score = _clamp01(parameter_set.stability_score, field_name="stability_score")
    consistency_score = _clamp01(parameter_set.consistency_score, field_name="consistency_score")
    inverse_sensitivity = 1.0 - sensitivity_score

    advisory_score = round(
        (0.35 * stability_score)
        + (0.25 * consistency_score)
        + (0.20 * inverse_sensitivity)
        + (0.20 * evaluation_support),
        6,
    )
    advisory_disposition = _disposition_for_score(advisory_score)
    if advisory_disposition not in _ALLOWED_DISPOSITIONS:
        raise ParameterAnalysisValidationError("advisory disposition must remain advisory-only")

    weighting_suggestion = _weighting_suggestion(
        parameter_set,
        stability_score=stability_score,
        high_priority_share=high_priority_share,
    )
    risk_multiplier_suggestion = _risk_multiplier_suggestion(
        parameter_set,
        inverse_sensitivity=inverse_sensitivity,
        consistency_score=consistency_score,
    )
    rationale = (
        f"evaluation_support={evaluation_support:.6f};"
        f"sensitivity_score={sensitivity_score:.6f};"
        f"stability_score={stability_score:.6f};"
        f"consistency_score={consistency_score:.6f};"
        f"advisory_score={advisory_score:.6f};"
        f"advisory_disposition={advisory_disposition}"
    )
    return ParameterRecommendation(
        parameter_set_id=parameter_set.parameter_set_id,
        advisory_score=advisory_score,
        sensitivity_score=sensitivity_score,
        stability_score=stability_score,
        consistency_score=consistency_score,
        weighting_suggestion=weighting_suggestion,
        risk_multiplier_suggestion=risk_multiplier_suggestion,
        advisory_disposition=advisory_disposition,
        rationale=rationale,
        supporting_event_ids=supporting_event_ids,
        source_ledger_entity_ids=parameter_set.source_ledger_entity_ids,
    )


def analyze_parameter_sets(request: ParameterAnalysisRequest) -> ParameterAnalysisResult:
    """Analyze approved parameter sets using deterministic, advisory-only intelligence inputs."""

    _validate_request(request)
    evaluation_support, high_priority_share, supporting_event_ids = _evaluation_support(request)
    recommendations = tuple(
        _recommendation(
            parameter_set,
            evaluation_support=evaluation_support,
            high_priority_share=high_priority_share,
            supporting_event_ids=supporting_event_ids,
        )
        for parameter_set in request.approved_parameter_sets
    )
    return tuple(
        sorted(
            recommendations,
            key=lambda item: (
                -item.advisory_score,
                -item.stability_score,
                -item.consistency_score,
                item.parameter_set_id,
            ),
        )
    )


@dataclass(frozen=True, slots=True)
class DeterministicParameterIntelligenceAnalyzer(ParameterIntelligenceAnalyzer):
    def analyze(self, request: ParameterAnalysisRequest) -> ParameterAnalysisResult:
        return analyze_parameter_sets(request)
