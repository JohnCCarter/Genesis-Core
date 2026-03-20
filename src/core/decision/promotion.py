from __future__ import annotations

from core.decision.models import (
    ComparisonDecision,
    ComparisonResult,
    DecisionReason,
    PromotionResult,
)


def apply_promotion(
    decision: ComparisonResult,
    override_flag: bool,
    signoff_flag: bool,
) -> PromotionResult:
    if decision.decision is ComparisonDecision.INVALID:
        return PromotionResult(
            decision=ComparisonDecision.INVALID,
            reasons=decision.reasons,
        )

    if decision.decision is not ComparisonDecision.PROMOTE:
        return PromotionResult(
            decision=ComparisonDecision.NO_PROMOTION,
            reasons=decision.reasons,
        )

    reasons: list[DecisionReason] = []
    if not override_flag:
        reasons.append(DecisionReason.OVERRIDE_REQUIRED)
    if not signoff_flag:
        reasons.append(DecisionReason.SIGNOFF_REQUIRED)

    if reasons:
        return PromotionResult(
            decision=ComparisonDecision.NO_PROMOTION,
            reasons=tuple(reasons),
        )

    return PromotionResult(
        decision=ComparisonDecision.PROMOTE,
        reasons=(DecisionReason.PROMOTION_APPROVED,),
    )
