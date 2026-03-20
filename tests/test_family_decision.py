from __future__ import annotations

from core.decision.comparison import compare_families
from core.decision.models import (
    ComparisonDecision,
    DecisionReason,
    FamilyStatus,
    MetricSnapshot,
)
from core.decision.promotion import apply_promotion


def _metrics(
    strategy_family: str | None,
    *,
    profit_factor: float,
    max_drawdown: float,
    trades_per_year: float,
    stability: float,
    winrate: float = 0.55,
) -> MetricSnapshot:
    return MetricSnapshot(
        strategy_family=strategy_family,
        profit_factor=profit_factor,
        max_drawdown=max_drawdown,
        trades_per_year=trades_per_year,
        stability=stability,
        winrate=winrate,
    )


def test_models_expose_explicit_status_enum() -> None:
    assert FamilyStatus.ACTIVE == "active"
    assert FamilyStatus.CHALLENGER == "challenger"
    assert FamilyStatus.EXPERIMENTAL == "experimental"


def test_ri_wins_and_can_be_promoted() -> None:
    legacy = _metrics(
        "legacy",
        profit_factor=1.20,
        max_drawdown=0.12,
        trades_per_year=80.0,
        stability=0.80,
    )
    ri = _metrics(
        "ri",
        profit_factor=1.26,
        max_drawdown=0.10,
        trades_per_year=90.0,
        stability=0.85,
    )

    comparison = compare_families(legacy, ri)
    promotion = apply_promotion(comparison, override_flag=True, signoff_flag=True)

    assert comparison.decision is ComparisonDecision.PROMOTE
    assert promotion.decision is ComparisonDecision.PROMOTE
    assert promotion.reasons == (DecisionReason.PROMOTION_APPROVED,)


def test_ri_slightly_better_but_below_margin_results_in_no_promotion() -> None:
    legacy = _metrics(
        "legacy",
        profit_factor=1.20,
        max_drawdown=0.12,
        trades_per_year=80.0,
        stability=0.80,
    )
    ri = _metrics(
        "ri",
        profit_factor=1.24,
        max_drawdown=0.10,
        trades_per_year=90.0,
        stability=0.85,
    )

    comparison = compare_families(legacy, ri)
    promotion = apply_promotion(comparison, override_flag=True, signoff_flag=True)

    assert comparison.decision is ComparisonDecision.KEEP_LEGACY
    assert DecisionReason.PROFIT_FACTOR_MARGIN_NOT_MET in comparison.reasons
    assert promotion.decision is ComparisonDecision.NO_PROMOTION


def test_ri_worse_drawdown_is_rejected() -> None:
    legacy = _metrics(
        "legacy",
        profit_factor=1.20,
        max_drawdown=0.12,
        trades_per_year=80.0,
        stability=0.80,
    )
    ri = _metrics(
        "ri",
        profit_factor=1.30,
        max_drawdown=0.13,
        trades_per_year=90.0,
        stability=0.85,
    )

    comparison = compare_families(legacy, ri)
    promotion = apply_promotion(comparison, override_flag=True, signoff_flag=True)

    assert comparison.decision is ComparisonDecision.KEEP_LEGACY
    assert DecisionReason.DRAWDOWN_WORSE_THAN_LEGACY in comparison.reasons
    assert promotion.decision is ComparisonDecision.NO_PROMOTION


def test_low_trades_returns_invalid() -> None:
    legacy = _metrics(
        "legacy",
        profit_factor=1.20,
        max_drawdown=0.12,
        trades_per_year=80.0,
        stability=0.80,
    )
    ri = _metrics(
        "ri",
        profit_factor=1.30,
        max_drawdown=0.10,
        trades_per_year=49.0,
        stability=0.85,
    )

    comparison = compare_families(legacy, ri)

    assert comparison.decision is ComparisonDecision.INVALID
    assert comparison.reasons == (DecisionReason.TRADE_THRESHOLD_NOT_MET,)


def test_missing_override_rejects_promotion() -> None:
    legacy = _metrics(
        "legacy",
        profit_factor=1.20,
        max_drawdown=0.12,
        trades_per_year=80.0,
        stability=0.80,
    )
    ri = _metrics(
        "ri",
        profit_factor=1.30,
        max_drawdown=0.10,
        trades_per_year=90.0,
        stability=0.85,
    )

    comparison = compare_families(legacy, ri)
    promotion = apply_promotion(comparison, override_flag=False, signoff_flag=True)

    assert comparison.decision is ComparisonDecision.PROMOTE
    assert promotion.decision is ComparisonDecision.NO_PROMOTION
    assert promotion.reasons == (DecisionReason.OVERRIDE_REQUIRED,)
