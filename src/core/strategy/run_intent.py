from __future__ import annotations

from typing import Any, Literal

RunIntent = Literal["research_slice", "candidate", "promotion_compare", "champion_freeze"]

RUN_INTENT_RESEARCH_SLICE: RunIntent = "research_slice"
RUN_INTENT_CANDIDATE: RunIntent = "candidate"
RUN_INTENT_PROMOTION_COMPARE: RunIntent = "promotion_compare"
RUN_INTENT_CHAMPION_FREEZE: RunIntent = "champion_freeze"

_ALLOWED_RUN_INTENTS = frozenset(
    {
        RUN_INTENT_RESEARCH_SLICE,
        RUN_INTENT_CANDIDATE,
        RUN_INTENT_PROMOTION_COMPARE,
        RUN_INTENT_CHAMPION_FREEZE,
    }
)


class RunIntentValidationError(ValueError):
    """Raised when a run_intent is missing or invalid."""


def validate_run_intent_name(value: Any) -> RunIntent:
    if value is None:
        raise RunIntentValidationError("missing_run_intent")
    normalized = str(value).strip().lower()
    if normalized in _ALLOWED_RUN_INTENTS:
        return normalized  # type: ignore[return-value]
    raise RunIntentValidationError("invalid_run_intent")


__all__ = [
    "RUN_INTENT_CANDIDATE",
    "RUN_INTENT_CHAMPION_FREEZE",
    "RUN_INTENT_PROMOTION_COMPARE",
    "RUN_INTENT_RESEARCH_SLICE",
    "RunIntent",
    "RunIntentValidationError",
    "validate_run_intent_name",
]
