"""
RegimeFilterComponent - Stateless entry veto based on market regime.

Allows entry only if the current regime is in the allowed list.
Phase 2 Component: Stateless, entry-only.
"""

from typing import Any

from core.strategy.components.base import ComponentResult, StrategyComponent


class RegimeFilterComponent(StrategyComponent):
    """
    Filter entries based on market regime.

    Allows entry only when regime matches one of the allowed regimes.
    Common regimes: "trending", "ranging", "balanced", "bull", "bear", "unknown"

    **Stateless**: Decision depends only on current bar context.
    **Entry-only**: Does not affect exits or position management.

    Configuration:
        allowed_regimes: List of regime strings that permit entry.
                         Example: ["trending", "bull"]

    Veto Reasons:
        - REGIME_NOT_ALLOWED: Current regime not in allowed list
        - REGIME_MISSING: Regime key missing from context
    """

    def __init__(self, allowed_regimes: list[str], name: str = "regime_filter"):
        """
        Initialize RegimeFilterComponent.

        Args:
            allowed_regimes: List of regime strings that permit entry.
                            Empty list blocks all entries.
            name: Component name for attribution.
        """
        self._name = name
        self.allowed_regimes = allowed_regimes if allowed_regimes else []

    def name(self) -> str:
        """Return component name for attribution."""
        return self._name

    def evaluate(self, context: dict[str, Any]) -> ComponentResult:
        """
        Evaluate regime filter.

        Args:
            context: Component context with "regime" key.

        Returns:
            ComponentResult with allowed=True if regime in allowed list,
            otherwise allowed=False with reason code.
        """
        regime = context.get("regime")

        # Missing regime: veto with metadata
        if regime is None:
            return ComponentResult(
                allowed=False,
                reason="REGIME_MISSING",
                confidence=0.0,
                metadata={
                    "component": self.name(),
                    "allowed_regimes": self.allowed_regimes,
                    "regime_found": None,
                },
            )

        # Regime not in allowed list: veto
        if regime not in self.allowed_regimes:
            return ComponentResult(
                allowed=False,
                reason="REGIME_NOT_ALLOWED",
                confidence=0.0,
                metadata={
                    "component": self.name(),
                    "allowed_regimes": self.allowed_regimes,
                    "regime_found": regime,
                },
            )

        # Regime allowed: pass through
        return ComponentResult(
            allowed=True,
            reason=None,
            confidence=1.0,
            metadata={
                "component": self.name(),
                "allowed_regimes": self.allowed_regimes,
                "regime_found": regime,
            },
        )
