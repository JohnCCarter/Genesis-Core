from __future__ import annotations

from core.decision.models import DecisionReason, MetricSnapshot, StrategyFamily

VALID_FAMILIES: tuple[StrategyFamily, ...] = ("legacy", "ri")
DEFAULT_TRADE_THRESHOLD = 50.0


def validate_metrics(
    snapshot: MetricSnapshot,
    *,
    expected_family: StrategyFamily | None = None,
) -> tuple[DecisionReason, ...]:
    reasons: list[DecisionReason] = []

    if snapshot.strategy_family is None:
        reasons.append(DecisionReason.MISSING_STRATEGY_FAMILY)
    elif snapshot.strategy_family not in VALID_FAMILIES:
        reasons.append(DecisionReason.INVALID_STRATEGY_FAMILY)
    elif expected_family is not None and snapshot.strategy_family != expected_family:
        reasons.append(DecisionReason.UNSUPPORTED_FAMILY_COMBINATION)

    if snapshot.profit_factor is None:
        reasons.append(DecisionReason.MISSING_PROFIT_FACTOR)
    if snapshot.max_drawdown is None:
        reasons.append(DecisionReason.MISSING_MAX_DRAWDOWN)
    if snapshot.trades_per_year is None:
        reasons.append(DecisionReason.MISSING_TRADES_PER_YEAR)
    if snapshot.stability is None:
        reasons.append(DecisionReason.MISSING_STABILITY)

    return tuple(dict.fromkeys(reasons))


def enforce_trade_threshold(
    snapshot: MetricSnapshot,
    *,
    threshold: float = DEFAULT_TRADE_THRESHOLD,
) -> tuple[DecisionReason, ...]:
    if snapshot.trades_per_year is None:
        return (DecisionReason.MISSING_TRADES_PER_YEAR,)
    if snapshot.trades_per_year < threshold:
        return (DecisionReason.TRADE_THRESHOLD_NOT_MET,)
    return ()
