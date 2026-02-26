"""
Base classes for composable strategy components.

Defines the core interfaces and contracts for component-based strategy evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ComponentResult:
    """
    Result from a strategy component evaluation.

    Attributes:
        allowed: Whether component allows the trade (veto power).
        confidence: Component confidence score (0.0-1.0).
        reason: Optional veto reason code (e.g., "ML_CONFIDENCE_LOW").
        metadata: Additional debugging/attribution data.
    """

    allowed: bool
    confidence: float
    reason: str | None = None
    metadata: dict | None = None

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")


class StrategyComponent(ABC):
    """
    Abstract base class for strategy decision components.

    Each component evaluates a single aspect of trade decision logic
    (e.g., ML confidence, HTF regime, volatility filter) and returns
    a ComponentResult indicating whether the trade is allowed and
    what confidence level the component assigns.
    """

    @abstractmethod
    def name(self) -> str:
        """Return component identifier (used for attribution tracking)."""
        pass

    @abstractmethod
    def evaluate(self, context: dict) -> ComponentResult:
        """
        Evaluate component logic against provided context.

        Args:
            context: Dictionary containing market data, features, indicators, etc.

        Returns:
            ComponentResult with allowed/confidence/reason/metadata.
        """
        pass
