"""
EVGateComponent - Stateless entry veto based on expected value.

Allows entry only if expected value meets or exceeds threshold.
Phase 2 Component: Stateless, entry-only, binary veto.
"""

from typing import Any

from core.strategy.components.base import ComponentResult, StrategyComponent


class EVGateComponent(StrategyComponent):
    """
    Filter entries based on expected value (EV).

    Allows entry only when EV >= min_ev threshold.
    EV is calculated from probabilities: EV = proba * reward - (1-proba) * risk

    **Stateless**: Decision depends only on current bar context.
    **Entry-only**: Does not affect exits or position management.
    **Binary veto**: No confidence modification (per Phase 2 spec).

    Configuration:
        min_ev: Minimum expected value required for entry.
                Typical range: [-1.0, 1.0]
                Example: 0.0 (require non-negative EV)

    Veto Reasons:
        - EV_BELOW_THRESHOLD: EV < min_ev
        - EV_MISSING: expected_value key missing from context
    """

    def __init__(self, min_ev: float = 0.0, name: str = "ev_gate"):
        """
        Initialize EVGateComponent.

        Args:
            min_ev: Minimum expected value threshold.
                   Common values:
                   - 0.0: Require non-negative EV (default)
                   - 0.1: Require +10% edge
                   - -0.5: Allow some negative EV (very permissive)
            name: Component name for attribution.
        """
        self._name = name
        self.min_ev = min_ev

    def name(self) -> str:
        """Return component name for attribution."""
        return self._name

    def evaluate(self, context: dict[str, Any]) -> ComponentResult:
        """
        Evaluate EV gate.

        Args:
            context: Component context with "expected_value" key.

        Returns:
            ComponentResult with allowed=True if EV >= min_ev,
            otherwise allowed=False with reason code.
        """
        ev = context.get("expected_value")

        # Missing EV: veto with metadata
        if ev is None:
            return ComponentResult(
                allowed=False,
                reason="EV_MISSING",
                confidence=0.0,
                metadata={
                    "component": self.name(),
                    "min_ev": self.min_ev,
                    "ev_value": None,
                },
            )

        # Convert to float (defensive)
        try:
            ev_float = float(ev)
        except (TypeError, ValueError):
            return ComponentResult(
                allowed=False,
                reason="EV_MISSING",
                confidence=0.0,
                metadata={
                    "component": self.name(),
                    "min_ev": self.min_ev,
                    "ev_value": None,
                    "ev_raw": str(ev),
                },
            )

        # EV below threshold: veto
        if ev_float < self.min_ev:
            return ComponentResult(
                allowed=False,
                reason="EV_BELOW_THRESHOLD",
                confidence=0.0,
                metadata={
                    "component": self.name(),
                    "min_ev": self.min_ev,
                    "ev_value": ev_float,
                },
            )

        # EV meets or exceeds threshold: allow
        return ComponentResult(
            allowed=True,
            reason=None,
            confidence=1.0,
            metadata={
                "component": self.name(),
                "min_ev": self.min_ev,
                "ev_value": ev_float,
            },
        )
