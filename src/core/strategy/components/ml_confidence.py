"""
ML Confidence Component - Filters trades based on ML model confidence.
"""

from .base import ComponentResult, StrategyComponent


class MLConfidenceComponent(StrategyComponent):
    """
    Evaluates ML model confidence and blocks trades below threshold.

    This component wraps the existing ML confidence score and applies
    a simple threshold gate.
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initialize ML confidence component.

        Args:
            threshold: Minimum confidence required (0.0-1.0).
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be 0-1, got {threshold}")
        self.threshold = threshold

    def name(self) -> str:
        return "ml_confidence"

    def evaluate(self, context: dict) -> ComponentResult:
        """
        Evaluate ML confidence from context.

        Args:
            context: Must contain 'ml_confidence' key with float value.

        Returns:
            ComponentResult with allowed/confidence/reason.
        """
        if "ml_confidence" not in context:
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="ML_CONFIDENCE_MISSING",
                metadata={"threshold": self.threshold},
            )

        confidence = context["ml_confidence"]

        if not isinstance(confidence, int | float):
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="ML_CONFIDENCE_MISSING",
                metadata={"threshold": self.threshold},
            )

        allowed = confidence >= self.threshold

        return ComponentResult(
            allowed=allowed,
            confidence=float(confidence),
            reason=None if allowed else "ML_CONFIDENCE_LOW",
            metadata={"ml_confidence": confidence, "threshold": self.threshold},
        )
