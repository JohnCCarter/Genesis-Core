from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeAlias

from core.strategy.family_registry import (
    STRATEGY_FAMILY_LEGACY,
    STRATEGY_FAMILY_RI,
    StrategyFamily,
    StrategyFamilyValidationError,
    validate_strategy_family_name,
)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

PROMOTION_MARGIN_PF = 0.05
MINIMUM_TRADE_THRESHOLD = 50.0


class FamilyStatus(StrEnum):
    ACTIVE = "active"
    CHALLENGER = "challenger"
    EXPERIMENTAL = "experimental"


class ComparisonDecision(StrEnum):
    PROMOTE = "promote"
    KEEP_INCUMBENT = "keep_incumbent"
    NO_DECISION = "no_decision"
    INVALID = "invalid"


class ComparisonSampleKind(StrEnum):
    VALIDATION = "validation"
    TRAIN = "train"


class DecisionReason(StrEnum):
    PROMOTION_APPROVED = "promotion_approved"
    KEEP_INCUMBENT = "keep_incumbent"
    VALIDATION_REQUIRED = "validation_required"
    MISSING_INCUMBENT_FAMILY = "missing_incumbent_family"
    MISSING_CHALLENGER_FAMILY = "missing_challenger_family"
    INVALID_INCUMBENT_FAMILY = "invalid_incumbent_family"
    INVALID_CHALLENGER_FAMILY = "invalid_challenger_family"
    INCUMBENT_STATUS_MUST_BE_ACTIVE = "incumbent_status_must_be_active"
    CHALLENGER_STATUS_MUST_BE_CHALLENGER = "challenger_status_must_be_challenger"
    EXPERIMENTAL_FAMILY_ISOLATED = "experimental_family_isolated"
    UNSUPPORTED_PROMOTION_PAIR = "unsupported_promotion_pair"
    MISSING_PROFIT_FACTOR = "missing_profit_factor"
    MISSING_MAX_DRAWDOWN = "missing_max_drawdown"
    MISSING_TRADES_PER_YEAR = "missing_trades_per_year"
    MISSING_STABILITY = "missing_stability"
    CROSS_FAMILY_OVERRIDE_REQUIRED = "cross_family_override_required"
    CROSS_FAMILY_GOVERNANCE_SIGNOFF_REQUIRED = "cross_family_governance_signoff_required"
    PROMOTION_MARGIN_PF_NOT_MET = "promotion_margin_pf_not_met"
    DRAWDOWN_WORSE_THAN_INCUMBENT = "drawdown_worse_than_incumbent"
    TRADE_THRESHOLD_NOT_MET = "trade_threshold_not_met"
    STABILITY_BELOW_INCUMBENT = "stability_below_incumbent"


@dataclass(frozen=True, slots=True)
class FamilyMetricSnapshot:
    strategy_family: StrategyFamily | str | None
    sample_kind: ComparisonSampleKind
    profit_factor: float | None
    max_drawdown: float | None
    trades_per_year: float | None
    stability: float | None
    win_rate: float | None = None
    artifact_refs: tuple[str, ...] = ()
    metadata: JsonObject = field(default_factory=dict)

    def to_dict(self) -> JsonObject:
        return {
            "strategy_family": (
                str(self.strategy_family) if self.strategy_family is not None else None
            ),
            "sample_kind": str(self.sample_kind),
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "trades_per_year": self.trades_per_year,
            "stability": self.stability,
            "win_rate": self.win_rate,
            "artifact_refs": list(self.artifact_refs),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class FamilyStatusRecord:
    strategy_family: StrategyFamily
    status: FamilyStatus

    def to_dict(self) -> JsonObject:
        return {
            "strategy_family": str(self.strategy_family),
            "status": str(self.status),
        }


@dataclass(frozen=True, slots=True)
class FamilyComparisonInput:
    incumbent: FamilyMetricSnapshot
    challenger: FamilyMetricSnapshot
    incumbent_status: FamilyStatus
    challenger_status: FamilyStatus
    explicit_override: bool = False
    governance_signoff: bool = False
    promotion_margin_pf: float = PROMOTION_MARGIN_PF
    minimum_trade_threshold: float = MINIMUM_TRADE_THRESHOLD

    def to_dict(self) -> JsonObject:
        return {
            "incumbent": self.incumbent.to_dict(),
            "challenger": self.challenger.to_dict(),
            "incumbent_status": str(self.incumbent_status),
            "challenger_status": str(self.challenger_status),
            "explicit_override": self.explicit_override,
            "governance_signoff": self.governance_signoff,
            "promotion_margin_pf": self.promotion_margin_pf,
            "minimum_trade_threshold": self.minimum_trade_threshold,
        }


@dataclass(frozen=True, slots=True)
class FamilyComparisonResult:
    decision: ComparisonDecision
    incumbent_family: StrategyFamily | None
    challenger_family: StrategyFamily | None
    active_family: StrategyFamily | None
    promotable_family: StrategyFamily | None
    reasons: tuple[DecisionReason, ...]
    promotion_margin_pf: float
    minimum_trade_threshold: float

    def to_dict(self) -> JsonObject:
        return {
            "decision": str(self.decision),
            "incumbent_family": self.incumbent_family,
            "challenger_family": self.challenger_family,
            "active_family": self.active_family,
            "promotable_family": self.promotable_family,
            "reasons": [str(reason) for reason in self.reasons],
            "promotion_margin_pf": self.promotion_margin_pf,
            "minimum_trade_threshold": self.minimum_trade_threshold,
        }


class FamilyDecisionValidationError(ValueError):
    """Raised when family decision inputs violate explicit governance contracts."""


def _append_unique_reason(
    reasons: list[DecisionReason],
    reason: DecisionReason,
) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _normalize_strategy_family(
    value: StrategyFamily | str | None,
    *,
    missing_reason: DecisionReason,
    invalid_reason: DecisionReason,
) -> tuple[StrategyFamily | None, tuple[DecisionReason, ...]]:
    if value is None:
        return None, (missing_reason,)
    try:
        return validate_strategy_family_name(value), ()
    except StrategyFamilyValidationError:
        return None, (invalid_reason,)


def _validate_comparison_input(
    comparison: FamilyComparisonInput,
) -> tuple[StrategyFamily | None, StrategyFamily | None, tuple[DecisionReason, ...]]:
    reasons: list[DecisionReason] = []

    incumbent_family, incumbent_reasons = _normalize_strategy_family(
        comparison.incumbent.strategy_family,
        missing_reason=DecisionReason.MISSING_INCUMBENT_FAMILY,
        invalid_reason=DecisionReason.INVALID_INCUMBENT_FAMILY,
    )
    challenger_family, challenger_reasons = _normalize_strategy_family(
        comparison.challenger.strategy_family,
        missing_reason=DecisionReason.MISSING_CHALLENGER_FAMILY,
        invalid_reason=DecisionReason.INVALID_CHALLENGER_FAMILY,
    )
    for reason in incumbent_reasons + challenger_reasons:
        _append_unique_reason(reasons, reason)

    if comparison.incumbent.profit_factor is None or comparison.challenger.profit_factor is None:
        _append_unique_reason(reasons, DecisionReason.MISSING_PROFIT_FACTOR)
    if comparison.incumbent.max_drawdown is None or comparison.challenger.max_drawdown is None:
        _append_unique_reason(reasons, DecisionReason.MISSING_MAX_DRAWDOWN)
    if (
        comparison.incumbent.trades_per_year is None
        or comparison.challenger.trades_per_year is None
    ):
        _append_unique_reason(reasons, DecisionReason.MISSING_TRADES_PER_YEAR)
    if comparison.incumbent.stability is None or comparison.challenger.stability is None:
        _append_unique_reason(reasons, DecisionReason.MISSING_STABILITY)

    if comparison.incumbent_status is not FamilyStatus.ACTIVE:
        _append_unique_reason(reasons, DecisionReason.INCUMBENT_STATUS_MUST_BE_ACTIVE)
    if comparison.challenger_status is FamilyStatus.EXPERIMENTAL:
        _append_unique_reason(reasons, DecisionReason.EXPERIMENTAL_FAMILY_ISOLATED)
    elif comparison.challenger_status is not FamilyStatus.CHALLENGER:
        _append_unique_reason(reasons, DecisionReason.CHALLENGER_STATUS_MUST_BE_CHALLENGER)

    if incumbent_family is not None and challenger_family is not None:
        if not (
            incumbent_family == STRATEGY_FAMILY_LEGACY and challenger_family == STRATEGY_FAMILY_RI
        ):
            _append_unique_reason(reasons, DecisionReason.UNSUPPORTED_PROMOTION_PAIR)

    if not comparison.explicit_override:
        _append_unique_reason(reasons, DecisionReason.CROSS_FAMILY_OVERRIDE_REQUIRED)
    if not comparison.governance_signoff:
        _append_unique_reason(reasons, DecisionReason.CROSS_FAMILY_GOVERNANCE_SIGNOFF_REQUIRED)

    return incumbent_family, challenger_family, tuple(reasons)


def _invalid_result(
    comparison: FamilyComparisonInput,
    incumbent_family: StrategyFamily | None,
    challenger_family: StrategyFamily | None,
    *reasons: DecisionReason,
) -> FamilyComparisonResult:
    return FamilyComparisonResult(
        decision=ComparisonDecision.INVALID,
        incumbent_family=incumbent_family,
        challenger_family=challenger_family,
        active_family=incumbent_family,
        promotable_family=None,
        reasons=tuple(reasons),
        promotion_margin_pf=comparison.promotion_margin_pf,
        minimum_trade_threshold=comparison.minimum_trade_threshold,
    )


def evaluate_family_promotion(comparison: FamilyComparisonInput) -> FamilyComparisonResult:
    incumbent_family, challenger_family, invalid_reasons = _validate_comparison_input(comparison)
    if invalid_reasons:
        return _invalid_result(
            comparison,
            incumbent_family,
            challenger_family,
            *invalid_reasons,
        )

    assert incumbent_family is not None
    assert challenger_family is not None
    assert comparison.incumbent.profit_factor is not None
    assert comparison.challenger.profit_factor is not None
    assert comparison.incumbent.max_drawdown is not None
    assert comparison.challenger.max_drawdown is not None
    assert comparison.challenger.trades_per_year is not None
    assert comparison.incumbent.stability is not None
    assert comparison.challenger.stability is not None

    if (
        comparison.incumbent.sample_kind is not ComparisonSampleKind.VALIDATION
        or comparison.challenger.sample_kind is not ComparisonSampleKind.VALIDATION
    ):
        return FamilyComparisonResult(
            decision=ComparisonDecision.NO_DECISION,
            incumbent_family=incumbent_family,
            challenger_family=challenger_family,
            active_family=incumbent_family,
            promotable_family=None,
            reasons=(DecisionReason.VALIDATION_REQUIRED,),
            promotion_margin_pf=comparison.promotion_margin_pf,
            minimum_trade_threshold=comparison.minimum_trade_threshold,
        )

    reasons: list[DecisionReason] = []
    required_profit_factor = comparison.incumbent.profit_factor + comparison.promotion_margin_pf
    if comparison.challenger.profit_factor < required_profit_factor:
        _append_unique_reason(reasons, DecisionReason.PROMOTION_MARGIN_PF_NOT_MET)
    if comparison.challenger.max_drawdown > comparison.incumbent.max_drawdown:
        _append_unique_reason(reasons, DecisionReason.DRAWDOWN_WORSE_THAN_INCUMBENT)
    if comparison.challenger.trades_per_year < comparison.minimum_trade_threshold:
        _append_unique_reason(reasons, DecisionReason.TRADE_THRESHOLD_NOT_MET)
    if comparison.challenger.stability < comparison.incumbent.stability:
        _append_unique_reason(reasons, DecisionReason.STABILITY_BELOW_INCUMBENT)

    if reasons:
        _append_unique_reason(reasons, DecisionReason.KEEP_INCUMBENT)
        return FamilyComparisonResult(
            decision=ComparisonDecision.KEEP_INCUMBENT,
            incumbent_family=incumbent_family,
            challenger_family=challenger_family,
            active_family=incumbent_family,
            promotable_family=None,
            reasons=tuple(reasons),
            promotion_margin_pf=comparison.promotion_margin_pf,
            minimum_trade_threshold=comparison.minimum_trade_threshold,
        )

    return FamilyComparisonResult(
        decision=ComparisonDecision.PROMOTE,
        incumbent_family=incumbent_family,
        challenger_family=challenger_family,
        active_family=challenger_family,
        promotable_family=challenger_family,
        reasons=(DecisionReason.PROMOTION_APPROVED,),
        promotion_margin_pf=comparison.promotion_margin_pf,
        minimum_trade_threshold=comparison.minimum_trade_threshold,
    )


def build_family_status_records(
    *,
    active_family: StrategyFamily,
    challenger_family: StrategyFamily,
    experimental_families: tuple[StrategyFamily, ...] = (),
) -> tuple[FamilyStatusRecord, ...]:
    ordered_statuses: dict[StrategyFamily, FamilyStatus] = {
        active_family: FamilyStatus.ACTIVE,
        challenger_family: FamilyStatus.CHALLENGER,
    }
    for family in experimental_families:
        if family in ordered_statuses:
            raise FamilyDecisionValidationError("family_status_conflict")
        ordered_statuses[family] = FamilyStatus.EXPERIMENTAL
    return tuple(
        FamilyStatusRecord(strategy_family=family, status=ordered_statuses[family])
        for family in sorted(ordered_statuses)
    )


def family_status_records_to_dict(
    records: tuple[FamilyStatusRecord, ...],
) -> list[JsonObject]:
    return [record.to_dict() for record in records]


__all__ = [
    "ComparisonDecision",
    "ComparisonSampleKind",
    "DecisionReason",
    "FamilyComparisonInput",
    "FamilyComparisonResult",
    "FamilyDecisionValidationError",
    "FamilyMetricSnapshot",
    "FamilyStatus",
    "FamilyStatusRecord",
    "MINIMUM_TRADE_THRESHOLD",
    "PROMOTION_MARGIN_PF",
    "build_family_status_records",
    "evaluate_family_promotion",
    "family_status_records_to_dict",
]
