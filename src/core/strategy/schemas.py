"""Shared strategy schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

FIB_KEYS: tuple[float, ...] = (0.382, 0.5, 0.618, 0.786)


class HtfFibContext(BaseModel):
    """Standardiserad HTF-fib-kontext för exit-motorn."""

    available: bool = False
    levels: dict[float, float] = Field(default_factory=dict)
    swing_high: float | None = None
    swing_low: float | None = None
    swing_age_bars: int | None = None
    source: str = "unknown"
    timestamp: str | None = None

    @field_validator("levels", mode="before")
    @classmethod
    def _coerce_levels(_cls, value: object) -> dict[float, float]:
        """Tillåt både str- och float-nycklar och filtrera bort ogiltiga värden."""
        out: dict[float, float] = {}
        if isinstance(value, dict):
            for key, val in value.items():
                try:
                    fib_key = float(key)
                    fib_value = float(val)
                except (TypeError, ValueError):
                    continue
                out[fib_key] = fib_value
        return {fib_key: out[fib_key] for fib_key in FIB_KEYS if fib_key in out}

    def is_usable(self) -> bool:
        """Returnera True om kontexten är komplett och användbar för HTF-exits."""
        if not self.available:
            return False
        if not all(
            fib_key in self.levels and isinstance(self.levels[fib_key], float)
            for fib_key in FIB_KEYS
        ):
            return False
        if self.swing_high is None or self.swing_low is None:
            return False
        return self.swing_high > self.swing_low
