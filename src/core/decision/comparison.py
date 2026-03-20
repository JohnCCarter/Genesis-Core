from __future__ import annotations

from core.decision.models import (
    ComparisonDecision,
    ComparisonResult,
    DecisionReason,
    MetricSnapshot,
)
from core.decision.validation import (
    DEFAULT_TRADE_THRESHOLD,
    enforce_trade_threshold,
    validate_metrics,
)

PROMOTION_MARGIN_PF = 0.05


def compare_families(
    legacy_metrics: MetricSnapshot,
    ri_metrics: MetricSnapshot,
    *,
    promotion_margin: float = PROMOTION_MARGIN_PF,
    minimum_trade_threshold: float = DEFAULT_TRADE_THRESHOLD,
) -> ComparisonResult:
    reasons = list(validate_metrics(legacy_metrics, expected_family="legacy"))
    reasons.extend(validate_metrics(ri_metrics, expected_family="ri"))

    if reasons:
        return ComparisonResult(
            decision=ComparisonDecision.INVALID,
            reasons=tuple(dict.fromkeys(reasons)),
            legacy_metrics=legacy_metrics,
            ri_metrics=ri_metrics,
        )

    trade_reasons = list(enforce_trade_threshold(ri_metrics, threshold=minimum_trade_threshold))
    if trade_reasons:
        return ComparisonResult(
            decision=ComparisonDecision.INVALID,
            reasons=tuple(dict.fromkeys(trade_reasons)),
            legacy_metrics=legacy_metrics,
            ri_metrics=ri_metrics,
        )

    assert legacy_metrics.profit_factor is not None
    assert ri_metrics.profit_factor is not None
    assert legacy_metrics.max_drawdown is not None
    assert ri_metrics.max_drawdown is not None
    assert legacy_metrics.stability is not None
    assert ri_metrics.stability is not None

    comparison_reasons: list[DecisionReason] = []
    if ri_metrics.profit_factor < legacy_metrics.profit_factor + promotion_margin:
        comparison_reasons.append(DecisionReason.PROFIT_FACTOR_MARGIN_NOT_MET)
    if ri_metrics.max_drawdown > legacy_metrics.max_drawdown:
        comparison_reasons.append(DecisionReason.DRAWDOWN_WORSE_THAN_LEGACY)
    if ri_metrics.stability < legacy_metrics.stability:
        comparison_reasons.append(DecisionReason.STABILITY_BELOW_LEGACY)

    if comparison_reasons:
        comparison_reasons.append(DecisionReason.INCUMBENT_RETAINED)
        return ComparisonResult(
            decision=ComparisonDecision.KEEP_LEGACY,
            reasons=tuple(dict.fromkeys(comparison_reasons)),
            legacy_metrics=legacy_metrics,
            ri_metrics=ri_metrics,
        )

    return ComparisonResult(
        decision=ComparisonDecision.PROMOTE,
        reasons=(DecisionReason.PROMOTION_APPROVED,),
        legacy_metrics=legacy_metrics,
        ri_metrics=ri_metrics,
    )
