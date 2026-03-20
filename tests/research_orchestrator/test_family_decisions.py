from __future__ import annotations

import pytest

from core.research_orchestrator.family_decisions import (
    ComparisonDecision,
    ComparisonSampleKind,
    DecisionReason,
    FamilyComparisonInput,
    FamilyMetricSnapshot,
    FamilyStatus,
    FamilyStatusRecord,
    build_family_status_records,
    evaluate_family_promotion,
    family_status_records_to_dict,
)


def _snapshot(
    strategy_family: str | None,
    *,
    sample_kind: ComparisonSampleKind = ComparisonSampleKind.VALIDATION,
    profit_factor: float | None = 1.20,
    max_drawdown: float | None = 0.12,
    trades_per_year: float | None = 75.0,
    stability: float | None = 0.80,
    win_rate: float | None = 0.56,
) -> FamilyMetricSnapshot:
    return FamilyMetricSnapshot(
        strategy_family=strategy_family,
        sample_kind=sample_kind,
        profit_factor=profit_factor,
        max_drawdown=max_drawdown,
        trades_per_year=trades_per_year,
        stability=stability,
        win_rate=win_rate,
        artifact_refs=(f"artifact:{strategy_family}",) if strategy_family is not None else (),
    )


def _comparison(
    *,
    incumbent: FamilyMetricSnapshot | None = None,
    challenger: FamilyMetricSnapshot | None = None,
    explicit_override: bool = True,
    governance_signoff: bool = True,
    incumbent_status: FamilyStatus = FamilyStatus.ACTIVE,
    challenger_status: FamilyStatus = FamilyStatus.CHALLENGER,
) -> FamilyComparisonInput:
    return FamilyComparisonInput(
        incumbent=incumbent or _snapshot("legacy"),
        challenger=challenger
        or _snapshot(
            "ri",
            profit_factor=1.28,
            max_drawdown=0.10,
            trades_per_year=80.0,
            stability=0.85,
        ),
        incumbent_status=incumbent_status,
        challenger_status=challenger_status,
        explicit_override=explicit_override,
        governance_signoff=governance_signoff,
    )


def test_evaluate_family_promotion_promotes_ri_when_all_gates_pass() -> None:
    result = evaluate_family_promotion(_comparison())

    assert result.decision is ComparisonDecision.PROMOTE
    assert result.promotable_family == "ri"
    assert result.active_family == "ri"
    assert result.reasons == (DecisionReason.PROMOTION_APPROVED,)


def test_evaluate_family_promotion_returns_no_decision_for_train_only_comparison() -> None:
    result = evaluate_family_promotion(
        _comparison(
            incumbent=_snapshot("legacy", sample_kind=ComparisonSampleKind.TRAIN),
            challenger=_snapshot(
                "ri",
                sample_kind=ComparisonSampleKind.TRAIN,
                profit_factor=1.50,
                max_drawdown=0.05,
                trades_per_year=120.0,
                stability=0.95,
            ),
        )
    )

    assert result.decision is ComparisonDecision.NO_DECISION
    assert result.active_family == "legacy"
    assert result.reasons == (DecisionReason.VALIDATION_REQUIRED,)


def test_evaluate_family_promotion_keeps_incumbent_when_pf_margin_not_met() -> None:
    result = evaluate_family_promotion(
        _comparison(
            challenger=_snapshot(
                "ri",
                profit_factor=1.24,
                max_drawdown=0.10,
                trades_per_year=80.0,
                stability=0.85,
            )
        )
    )

    assert result.decision is ComparisonDecision.KEEP_INCUMBENT
    assert DecisionReason.PROMOTION_MARGIN_PF_NOT_MET in result.reasons
    assert DecisionReason.KEEP_INCUMBENT in result.reasons
    assert result.active_family == "legacy"


def test_evaluate_family_promotion_keeps_incumbent_when_drawdown_is_worse() -> None:
    result = evaluate_family_promotion(
        _comparison(
            challenger=_snapshot(
                "ri",
                profit_factor=1.30,
                max_drawdown=0.15,
                trades_per_year=80.0,
                stability=0.85,
            )
        )
    )

    assert result.decision is ComparisonDecision.KEEP_INCUMBENT
    assert DecisionReason.DRAWDOWN_WORSE_THAN_INCUMBENT in result.reasons
    assert result.active_family == "legacy"


def test_evaluate_family_promotion_keeps_incumbent_when_trade_threshold_not_met() -> None:
    result = evaluate_family_promotion(
        _comparison(
            challenger=_snapshot(
                "ri",
                profit_factor=1.40,
                max_drawdown=0.10,
                trades_per_year=49.0,
                stability=0.85,
            )
        )
    )

    assert result.decision is ComparisonDecision.KEEP_INCUMBENT
    assert DecisionReason.TRADE_THRESHOLD_NOT_MET in result.reasons
    assert DecisionReason.KEEP_INCUMBENT in result.reasons


def test_evaluate_family_promotion_is_invalid_without_override_or_signoff() -> None:
    result = evaluate_family_promotion(
        _comparison(explicit_override=False, governance_signoff=False)
    )

    assert result.decision is ComparisonDecision.INVALID
    assert DecisionReason.CROSS_FAMILY_OVERRIDE_REQUIRED in result.reasons
    assert DecisionReason.CROSS_FAMILY_GOVERNANCE_SIGNOFF_REQUIRED in result.reasons


@pytest.mark.parametrize(
    ("incumbent", "challenger", "expected_reason"),
    [
        pytest.param(_snapshot(None), _snapshot("ri"), DecisionReason.MISSING_INCUMBENT_FAMILY),
        pytest.param(
            _snapshot("legacy"),
            _snapshot(None),
            DecisionReason.MISSING_CHALLENGER_FAMILY,
        ),
        pytest.param(
            _snapshot("legacy", profit_factor=None),
            _snapshot("ri"),
            DecisionReason.MISSING_PROFIT_FACTOR,
        ),
        pytest.param(
            _snapshot("legacy"),
            _snapshot("ri", max_drawdown=None),
            DecisionReason.MISSING_MAX_DRAWDOWN,
        ),
        pytest.param(
            _snapshot("legacy"),
            _snapshot("ri", trades_per_year=None),
            DecisionReason.MISSING_TRADES_PER_YEAR,
        ),
        pytest.param(
            _snapshot("legacy"),
            _snapshot("ri", stability=None),
            DecisionReason.MISSING_STABILITY,
        ),
        pytest.param(
            _snapshot("legacy"),
            _snapshot("legacy"),
            DecisionReason.UNSUPPORTED_PROMOTION_PAIR,
        ),
    ],
)
def test_evaluate_family_promotion_rejects_malformed_or_unsupported_input(
    incumbent: FamilyMetricSnapshot,
    challenger: FamilyMetricSnapshot,
    expected_reason: DecisionReason,
) -> None:
    result = evaluate_family_promotion(_comparison(incumbent=incumbent, challenger=challenger))

    assert result.decision is ComparisonDecision.INVALID
    assert expected_reason in result.reasons


def test_evaluate_family_promotion_rejects_experimental_family_from_promotion_path() -> None:
    result = evaluate_family_promotion(_comparison(challenger_status=FamilyStatus.EXPERIMENTAL))

    assert result.decision is ComparisonDecision.INVALID
    assert DecisionReason.EXPERIMENTAL_FAMILY_ISOLATED in result.reasons


def test_build_family_status_records_is_explicit_and_deterministic() -> None:
    records = build_family_status_records(active_family="legacy", challenger_family="ri")

    assert records == (
        FamilyStatusRecord(strategy_family="legacy", status=FamilyStatus.ACTIVE),
        FamilyStatusRecord(strategy_family="ri", status=FamilyStatus.CHALLENGER),
    )
    assert family_status_records_to_dict(records) == [
        {"strategy_family": "legacy", "status": "active"},
        {"strategy_family": "ri", "status": "challenger"},
    ]


def test_family_comparison_result_to_dict_is_deterministic() -> None:
    result = evaluate_family_promotion(_comparison())

    assert result.to_dict() == {
        "decision": "promote",
        "incumbent_family": "legacy",
        "challenger_family": "ri",
        "active_family": "ri",
        "promotable_family": "ri",
        "reasons": ["promotion_approved"],
        "promotion_margin_pf": 0.05,
        "minimum_trade_threshold": 50.0,
    }
