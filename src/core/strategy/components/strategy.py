"""
ComposableStrategy - Combines multiple strategy components.

Evaluates components in sequence and applies veto/confidence aggregation logic.
"""

from dataclasses import dataclass

from .base import ComponentResult, StrategyComponent


@dataclass
class StrategyDecision:
    """
    Final strategy decision after evaluating all components.

    Attributes:
        allowed: Whether trade is allowed (all components must approve).
        confidence: Aggregated confidence score.
        veto_component: Name of component that vetoed, if any.
        veto_reason: Reason code from vetoing component.
        component_results: Individual results from each component.
    """

    allowed: bool
    confidence: float
    veto_component: str | None = None
    veto_reason: str | None = None
    component_results: dict[str, ComponentResult] | None = None


class ComposableStrategy:
    """
    Combines multiple StrategyComponents into a single decision pipeline.

    Components are evaluated in order. First veto blocks the trade.
    Confidence is aggregated using min() (weakest link principle).
    """

    def __init__(self, components: list[StrategyComponent]):
        """
        Initialize composable strategy.

        Args:
            components: List of components to evaluate (order matters for veto).
        """
        if not components:
            raise ValueError("At least one component required")
        self.components = components

    def evaluate(self, context: dict) -> StrategyDecision:
        """
        Evaluate all components and produce final decision.

        Args:
            context: Market data/features/indicators dictionary.

        Returns:
            StrategyDecision with aggregated result.
        """
        component_results = {}
        confidences = []

        for component in self.components:
            result = component.evaluate(context)
            component_results[component.name()] = result
            confidences.append(result.confidence)

            if not result.allowed:
                return StrategyDecision(
                    allowed=False,
                    confidence=min(confidences),
                    veto_component=component.name(),
                    veto_reason=result.reason,
                    component_results=component_results,
                )

        return StrategyDecision(
            allowed=True,
            confidence=min(confidences),
            veto_component=None,
            veto_reason=None,
            component_results=component_results,
        )
