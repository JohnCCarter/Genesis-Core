from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PartialExitCandidate:
    """Computed partial-exit candidate before engine-level action wrapping."""

    size: float
    reason: str


@dataclass(frozen=True)
class PartialExitSpec:
    """Declarative spec for a single partial-exit trigger."""

    trigger_id: str
    level_key: float
    pct: float
    uses_padding: bool = False


LONG_PARTIAL_SPECS: tuple[PartialExitSpec, ...] = (
    PartialExitSpec("TP1_0382", 0.382, 1.0, uses_padding=True),
    PartialExitSpec("TP2_05", 0.5, 1.0),
    PartialExitSpec("TP3_0618", 0.618, 1.0),
    PartialExitSpec("TP4_0786", 0.786, 1.0),
)

SHORT_PARTIAL_SPECS: tuple[PartialExitSpec, ...] = (
    PartialExitSpec("TP1_0618", 0.618, 1.0),
    PartialExitSpec("TP2_05", 0.5, 1.0),
    PartialExitSpec("TP3_0382", 0.382, 1.0),
    PartialExitSpec("TP4_0786", 0.786, 1.0),
)


def evaluate_partial_exits(
    *,
    position_side: str,
    current_size: float,
    current_bar: dict[str, Any],
    atr: float,
    htf_levels: dict[float, float],
    triggered_exits: set[str],
    partial_pcts: tuple[float, float, float, float],
    pct_thr: float,
    atr_thr: float,
    near_with_adaptive: Callable[[float, float, float, float, float], bool],
) -> list[PartialExitCandidate]:
    """Evaluate partial-exit candidates while preserving trigger order and semantics."""
    current_price = current_bar["close"]
    specs = LONG_PARTIAL_SPECS if position_side == "LONG" else SHORT_PARTIAL_SPECS
    actions: list[PartialExitCandidate] = []

    for spec, pct in zip(specs, partial_pcts, strict=True):
        target = htf_levels.get(spec.level_key)
        if not target or spec.trigger_id in triggered_exits:
            continue

        if spec.uses_padding:
            tp1_pad = max(0.05 * max(atr, 1e-9), 0.0005 * target)
            if (current_bar["low"] - tp1_pad) <= target <= (current_bar["high"] + tp1_pad):
                actions.append(
                    PartialExitCandidate(size=current_size * pct, reason=spec.trigger_id)
                )
                triggered_exits.add(spec.trigger_id)
            continue

        if near_with_adaptive(current_price, target, atr, pct_thr, atr_thr):
            actions.append(PartialExitCandidate(size=current_size * pct, reason=spec.trigger_id))
            triggered_exits.add(spec.trigger_id)

    return actions
