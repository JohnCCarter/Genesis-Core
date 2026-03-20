from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal, TypeAlias

StrategyFamily: TypeAlias = Literal["legacy", "ri"]


class FamilyStatus(StrEnum):
    ACTIVE = "active"
    CHALLENGER = "challenger"
    EXPERIMENTAL = "experimental"


class ComparisonDecision(StrEnum):
    PROMOTE = "promote"
    KEEP_LEGACY = "keep_legacy"
    NO_PROMOTION = "no_promotion"
    INVALID = "invalid"


class DecisionReason(StrEnum):
    MISSING_STRATEGY_FAMILY = "missing_strategy_family"
    INVALID_STRATEGY_FAMILY = "invalid_strategy_family"
    UNSUPPORTED_FAMILY_COMBINATION = "unsupported_family_combination"
    MISSING_PROFIT_FACTOR = "missing_profit_factor"
    MISSING_MAX_DRAWDOWN = "missing_max_drawdown"
    MISSING_TRADES_PER_YEAR = "missing_trades_per_year"
    MISSING_STABILITY = "missing_stability"
    TRADE_THRESHOLD_NOT_MET = "trade_threshold_not_met"
    PROFIT_FACTOR_MARGIN_NOT_MET = "profit_factor_margin_not_met"
    DRAWDOWN_WORSE_THAN_LEGACY = "drawdown_worse_than_legacy"
    STABILITY_BELOW_LEGACY = "stability_below_legacy"
    OVERRIDE_REQUIRED = "override_required"
    SIGNOFF_REQUIRED = "signoff_required"
    PROMOTION_APPROVED = "promotion_approved"
    INCUMBENT_RETAINED = "incumbent_retained"


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    strategy_family: StrategyFamily | None
    profit_factor: float | None
    max_drawdown: float | None
    trades_per_year: float | None
    stability: float | None
    winrate: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy_family": self.strategy_family,
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "trades_per_year": self.trades_per_year,
            "stability": self.stability,
            "winrate": self.winrate,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    decision: ComparisonDecision
    reasons: tuple[DecisionReason, ...]
    legacy_metrics: MetricSnapshot
    ri_metrics: MetricSnapshot

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": str(self.decision),
            "reasons": [str(reason) for reason in self.reasons],
            "legacy_metrics": self.legacy_metrics.to_dict(),
            "ri_metrics": self.ri_metrics.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class PromotionResult:
    decision: ComparisonDecision
    reasons: tuple[DecisionReason, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": str(self.decision),
            "reasons": [str(reason) for reason in self.reasons],
        }
