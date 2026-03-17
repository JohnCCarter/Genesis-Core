from __future__ import annotations

from core.intelligence.evaluation.interface import (
    EvaluationRequest,
    EvaluationResult,
    IntelligenceEvaluation,
    IntelligenceEvaluator,
)
from core.intelligence.features.interface import IntelligenceFeatureSet

HIGH_PRIORITY_THRESHOLD = 0.75
MONITOR_THRESHOLD = 0.45


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _score_feature_set(feature_set: IntelligenceFeatureSet) -> float:
    features = feature_set.features
    confidence = _clamp01(float(features.get("confidence", 0.0)))
    reference_bonus = min(int(features.get("reference_count", 0)), 3) * 0.05
    summary_bonus = min(int(features.get("summary_word_count", 0)), 20) / 20.0 * 0.05
    score = confidence * 0.9 + reference_bonus + summary_bonus
    return round(_clamp01(score), 6)


def _disposition_for_score(score: float) -> str:
    if score >= HIGH_PRIORITY_THRESHOLD:
        return "high_priority"
    if score >= MONITOR_THRESHOLD:
        return "monitor"
    return "ignore"


def _rationale(feature_set: IntelligenceFeatureSet, score: float, disposition: str) -> str:
    features = feature_set.features
    return (
        f"namespace={feature_set.feature_namespace};"
        f"confidence={float(features.get('confidence', 0.0)):.6f};"
        f"reference_count={int(features.get('reference_count', 0))};"
        f"summary_word_count={int(features.get('summary_word_count', 0))};"
        f"score={score:.6f};"
        f"disposition={disposition}"
    )


def evaluate_feature_sets(
    feature_sets: tuple[IntelligenceFeatureSet, ...],
) -> EvaluationResult:
    """Evaluate deterministic feature sets with stable score/disposition semantics."""

    results: list[IntelligenceEvaluation] = []
    for feature_set in feature_sets:
        score = _score_feature_set(feature_set)
        disposition = _disposition_for_score(score)
        results.append(
            IntelligenceEvaluation(
                event_id=feature_set.event_id,
                disposition=disposition,
                score=score,
                rationale=_rationale(feature_set, score, disposition),
            )
        )
    return tuple(results)


class DeterministicIntelligenceEvaluator(IntelligenceEvaluator):
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        return evaluate_feature_sets(request.feature_sets)
