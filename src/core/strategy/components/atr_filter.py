"""
ATR Filter Component - Filters trades based on volatility (ATR ratio).
"""

from .base import ComponentResult, StrategyComponent


class ATRFilterComponent(StrategyComponent):
    """
    Evaluates volatility via ATR ratio and blocks trades in low volatility.

    This component compares current ATR against a moving average of ATR
    to detect volatility expansion/contraction.
    """

    def __init__(self, min_ratio: float = 1.0):
        """
        Initialize ATR filter component.

        Args:
            min_ratio: Minimum ATR/ATR_MA ratio required (typically >= 1.0).
        """
        if min_ratio < 0:
            raise ValueError(f"min_ratio must be >= 0, got {min_ratio}")
        self.min_ratio = min_ratio

    def name(self) -> str:
        return "atr_filter"

    def evaluate(self, context: dict) -> ComponentResult:
        """
        Evaluate ATR ratio from context.

        Args:
            context: Must contain 'atr' and 'atr_ma' keys with float values.

        Returns:
            ComponentResult with allowed/confidence/reason.
        """
        if "atr" not in context or "atr_ma" not in context:
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="ATR_DATA_MISSING",
                metadata={"min_ratio": self.min_ratio},
            )

        atr = context["atr"]
        atr_ma = context["atr_ma"]

        if not isinstance(atr, int | float) or not isinstance(atr_ma, int | float):
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="ATR_DATA_MISSING",
                metadata={"min_ratio": self.min_ratio},
            )

        if atr_ma <= 0:
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="ATR_MA_INVALID",
                metadata={"atr": atr, "atr_ma": atr_ma, "min_ratio": self.min_ratio},
            )

        ratio = atr / atr_ma
        allowed = ratio >= self.min_ratio

        confidence = min(ratio / 2.0, 1.0)

        return ComponentResult(
            allowed=allowed,
            confidence=confidence,
            reason=None if allowed else "ATR_TOO_LOW",
            metadata={
                "atr_ratio": ratio,
                "min_ratio": self.min_ratio,
                "atr": atr,
                "atr_ma": atr_ma,
            },
        )
