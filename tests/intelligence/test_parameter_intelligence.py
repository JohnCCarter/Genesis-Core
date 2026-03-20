from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict

import pytest

from core.intelligence.evaluation import IntelligenceEvaluation
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
    ParameterAnalysisRequest,
    ParameterAnalysisValidationError,
    analyze_parameter_sets,
)


def _evaluation(
    index: int,
    *,
    disposition: str = "review",
    score: float = 0.6,
) -> IntelligenceEvaluation:
    return IntelligenceEvaluation(
        event_id=f"intel-tbtcusd-20260317-{index:04d}",
        disposition=disposition,
        score=score,
        rationale=f"Evaluation {index}",
    )


def _parameter_set(
    parameter_set_id: str,
    *,
    sensitivity_score: float,
    stability_score: float,
    consistency_score: float,
    baseline_weight: float = 1.0,
    risk_multiplier: float = 1.0,
    strategy_family: str | None = None,
) -> ApprovedParameterSet:
    parameters = {
        "ema_fast": 9,
        "ema_slow": 21,
        "stop_loss_atr": 1.5,
        "parameter_set_id": parameter_set_id,
    }
    if strategy_family is not None:
        parameters["strategy_family"] = strategy_family
    return ApprovedParameterSet(
        parameter_set_id=parameter_set_id,
        parameters=parameters,
        sensitivity_score=sensitivity_score,
        stability_score=stability_score,
        consistency_score=consistency_score,
        source_ledger_entity_ids=(f"ART-2026-{parameter_set_id[-1:] or '0'}001",),
        baseline_weight=baseline_weight,
        risk_multiplier=risk_multiplier,
    )


def test_parameter_package_exports_are_available() -> None:
    assert DeterministicParameterIntelligenceAnalyzer.__name__ == (
        "DeterministicParameterIntelligenceAnalyzer"
    )
    assert analyze_parameter_sets.__name__ == "analyze_parameter_sets"
    assert ApprovedParameterSet.__name__ == "ApprovedParameterSet"


def test_parameter_analysis_is_deterministic_and_non_mutating() -> None:
    request = ParameterAnalysisRequest(
        evaluations=(
            _evaluation(1, disposition="high_priority", score=0.8),
            _evaluation(2, disposition="review", score=0.4),
        ),
        approved_parameter_sets=(
            _parameter_set(
                "ps-b",
                sensitivity_score=0.5,
                stability_score=0.7,
                consistency_score=0.65,
                baseline_weight=0.9,
                risk_multiplier=1.1,
            ),
            _parameter_set(
                "ps-a",
                sensitivity_score=0.2,
                stability_score=0.9,
                consistency_score=0.8,
                baseline_weight=1.0,
                risk_multiplier=1.2,
            ),
        ),
    )
    before_request = deepcopy(asdict(request))

    first = analyze_parameter_sets(request)
    second = DeterministicParameterIntelligenceAnalyzer().analyze(request)

    assert first == second
    assert tuple(item.parameter_set_id for item in first) == ("ps-a", "ps-b")
    assert first[0].advisory_score == 0.795
    assert first[0].weighting_suggestion == 1.17
    assert first[0].risk_multiplier_suggestion == 1.128
    assert first[0].advisory_disposition == "preferred"
    assert tuple(item.supporting_event_ids for item in first) == (
        ("intel-tbtcusd-20260317-0001", "intel-tbtcusd-20260317-0002"),
        ("intel-tbtcusd-20260317-0001", "intel-tbtcusd-20260317-0002"),
    )
    assert asdict(request) == before_request


def test_parameter_analysis_uses_stable_tie_breaking_by_parameter_set_id() -> None:
    request = ParameterAnalysisRequest(
        evaluations=(_evaluation(1, disposition="review", score=0.6),),
        approved_parameter_sets=(
            _parameter_set(
                "ps-z",
                sensitivity_score=0.3,
                stability_score=0.8,
                consistency_score=0.7,
            ),
            _parameter_set(
                "ps-a",
                sensitivity_score=0.3,
                stability_score=0.8,
                consistency_score=0.7,
            ),
        ),
    )

    result = analyze_parameter_sets(request)

    assert tuple(item.parameter_set_id for item in result) == ("ps-a", "ps-z")


def test_parameter_analysis_outputs_are_advisory_only_and_json_serializable() -> None:
    request = ParameterAnalysisRequest(
        evaluations=(_evaluation(1, disposition="review", score=0.55),),
        approved_parameter_sets=(
            _parameter_set(
                "ps-review",
                sensitivity_score=0.45,
                stability_score=0.62,
                consistency_score=0.58,
            ),
        ),
    )

    result = analyze_parameter_sets(request)
    payload = json.dumps([asdict(item) for item in result], sort_keys=True, allow_nan=False)

    assert result[0].advisory_disposition in {"preferred", "review", "defer"}
    assert result[0].advisory_disposition == "review"
    assert "advisory_disposition=review" in result[0].rationale
    assert isinstance(payload, str)


def test_parameter_analysis_appends_strategy_family_to_rationale_when_declared_consistently() -> (
    None
):
    request = ParameterAnalysisRequest(
        evaluations=(
            _evaluation(1, disposition="high_priority", score=0.8),
            _evaluation(2, disposition="review", score=0.4),
        ),
        approved_parameter_sets=(
            _parameter_set(
                "ps-a",
                sensitivity_score=0.2,
                stability_score=0.9,
                consistency_score=0.8,
                baseline_weight=1.0,
                risk_multiplier=1.2,
                strategy_family="legacy",
            ),
        ),
    )

    result = analyze_parameter_sets(request)

    assert result[0].advisory_score == 0.795
    assert result[0].advisory_disposition == "preferred"
    assert result[0].supporting_event_ids == (
        "intel-tbtcusd-20260317-0001",
        "intel-tbtcusd-20260317-0002",
    )
    assert "strategy_family=legacy" in result[0].rationale


@pytest.mark.parametrize(
    "approved_parameter_sets",
    [
        (
            _parameter_set(
                "ps-missing",
                sensitivity_score=0.2,
                stability_score=0.9,
                consistency_score=0.8,
            ),
        ),
        (
            _parameter_set(
                "ps-legacy",
                sensitivity_score=0.2,
                stability_score=0.9,
                consistency_score=0.8,
                strategy_family="legacy",
            ),
            _parameter_set(
                "ps-ri",
                sensitivity_score=0.3,
                stability_score=0.8,
                consistency_score=0.7,
                strategy_family="ri",
            ),
        ),
        (
            ApprovedParameterSet(
                parameter_set_id="ps-invalid",
                parameters={
                    "ema_fast": 9,
                    "ema_slow": 21,
                    "stop_loss_atr": 1.5,
                    "parameter_set_id": "ps-invalid",
                    "strategy_family": "legacy-ish",
                },
                sensitivity_score=0.2,
                stability_score=0.9,
                consistency_score=0.8,
                source_ledger_entity_ids=("ART-2026-X001",),
            ),
        ),
    ],
)
def test_parameter_analysis_does_not_append_strategy_family_for_non_canonical_metadata(
    approved_parameter_sets: tuple[ApprovedParameterSet, ...],
) -> None:
    request = ParameterAnalysisRequest(
        evaluations=(_evaluation(1, disposition="review", score=0.55),),
        approved_parameter_sets=approved_parameter_sets,
    )

    result = analyze_parameter_sets(request)

    assert "strategy_family=" not in result[0].rationale
    assert result[0].advisory_disposition in {"preferred", "review", "defer"}


@pytest.mark.parametrize(
    ("analysis_request", "message"),
    [
        (
            ParameterAnalysisRequest(
                evaluations=(),
                approved_parameter_sets=(
                    _parameter_set(
                        "ps-a",
                        sensitivity_score=0.2,
                        stability_score=0.9,
                        consistency_score=0.8,
                    ),
                ),
            ),
            "evaluations",
        ),
        (
            ParameterAnalysisRequest(
                evaluations=(_evaluation(1),),
                approved_parameter_sets=(
                    _parameter_set(
                        "dup",
                        sensitivity_score=0.2,
                        stability_score=0.9,
                        consistency_score=0.8,
                    ),
                    _parameter_set(
                        "dup",
                        sensitivity_score=0.3,
                        stability_score=0.8,
                        consistency_score=0.7,
                    ),
                ),
            ),
            "unique",
        ),
        (
            ParameterAnalysisRequest(
                evaluations=(
                    _evaluation(1),
                    IntelligenceEvaluation(
                        event_id="intel-tbtcusd-20260317-0001",
                        disposition="review",
                        score=0.7,
                        rationale="Duplicate event",
                    ),
                ),
                approved_parameter_sets=(
                    _parameter_set(
                        "ps-a",
                        sensitivity_score=0.2,
                        stability_score=0.9,
                        consistency_score=0.8,
                    ),
                ),
            ),
            "unique",
        ),
        (
            ParameterAnalysisRequest(
                evaluations=(_evaluation(1),),
                approved_parameter_sets=(
                    ApprovedParameterSet(
                        parameter_set_id="ps-empty",
                        parameters={},
                        sensitivity_score=0.2,
                        stability_score=0.9,
                        consistency_score=0.8,
                    ),
                ),
            ),
            "parameters",
        ),
        (
            ParameterAnalysisRequest(
                evaluations=(_evaluation(1),),
                approved_parameter_sets=(
                    ApprovedParameterSet(
                        parameter_set_id="ps-non-mapping",
                        parameters=[],
                        sensitivity_score=0.2,
                        stability_score=0.9,
                        consistency_score=0.8,
                    ),
                ),
            ),
            "mapping",
        ),
    ],
)
def test_parameter_analysis_rejects_invalid_or_incomplete_inputs(
    analysis_request: ParameterAnalysisRequest,
    message: str,
) -> None:
    with pytest.raises(ParameterAnalysisValidationError, match=message):
        analyze_parameter_sets(analysis_request)
