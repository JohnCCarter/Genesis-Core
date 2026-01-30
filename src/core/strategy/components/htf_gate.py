"""
HTF Gate Component - Filters trades based on higher timeframe regime.
"""

from .base import ComponentResult, StrategyComponent


class HTFGateComponent(StrategyComponent):
    """
    Evaluates higher timeframe regime and blocks trades in unfavorable regimes.

    This component allows specification of which HTF regimes are acceptable
    for taking trades.
    """

    def __init__(self, required_regimes: list[str] | None = None):
        """
        Initialize HTF gate component.

        Args:
            required_regimes: List of acceptable regime strings
                            (e.g., ['trending', 'bull']).
                            If None, defaults to ['trending', 'bull'].
        """
        self.required_regimes = required_regimes or ["trending", "bull"]

    def name(self) -> str:
        return "htf_gate"

    def evaluate(self, context: dict) -> ComponentResult:
        """
        Evaluate HTF regime from context.

        Args:
            context: Must contain 'htf_regime' key with string value.

        Returns:
            ComponentResult with allowed/confidence/reason.
        """
        htf_regime = context.get("htf_regime", "unknown")

        if not isinstance(htf_regime, str):
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="HTF_REGIME_MISSING",
                metadata={"required": self.required_regimes},
            )

        allowed = htf_regime in self.required_regimes

        return ComponentResult(
            allowed=allowed,
            confidence=1.0 if allowed else 0.0,
            reason=None if allowed else f"HTF_REGIME_{htf_regime.upper()}",
            metadata={"htf_regime": htf_regime, "required": self.required_regimes},
        )
