from __future__ import annotations

from typing import Any

from core.backtest.position_tracker import Position
from core.indicators.exit_fibonacci import (
    calculate_exit_fibonacci_levels,
    validate_swing_for_exit,
)


def resolve_valid_exit_context(
    exit_ctx: dict[str, Any] | None,
) -> tuple[dict[float, float], tuple[float, float]] | None:
    """Validate and return the frozen exit context if it is internally consistent."""
    if not exit_ctx:
        return None

    fib_levels = exit_ctx.get("fib")
    swing_bounds = exit_ctx.get("swing_bounds")
    if not fib_levels or not swing_bounds:
        return None

    lo, hi = swing_bounds
    if hi <= lo:
        return None

    levels = list(fib_levels.values())
    if not levels or min(levels) < lo - 1e-9 or max(levels) > hi + 1e-9:
        return None

    return fib_levels, (lo, hi)


def initialize_position_exit_levels(
    *,
    position: Position,
    htf_fib_context: dict[str, Any],
    indicators: dict[str, float],
    min_swing_size_atr: float,
    max_distance_atr: float,
) -> None:
    """Initialize position exit levels from producer-style HTF swing context."""
    htf_levels = htf_fib_context.get("levels", {})
    current_price = indicators.get("ema50", position.entry_price)
    current_atr = indicators.get("atr", 100.0)

    swing_high, swing_low = coerce_swing_bounds(
        htf_levels=htf_levels,
        swing_high=htf_fib_context.get("swing_high"),
        swing_low=htf_fib_context.get("swing_low"),
    )

    if swing_high <= swing_low or swing_high <= 0 or swing_low <= 0:
        return

    exit_levels = calculate_exit_fibonacci_levels(
        side=position.side,
        swing_high=swing_high,
        swing_low=swing_low,
        levels=[0.786, 0.618, 0.5, 0.382],
    )

    is_valid, _reason = validate_swing_for_exit(
        swing_high=swing_high,
        swing_low=swing_low,
        current_price=current_price,
        current_atr=current_atr,
        min_swing_size_atr=min_swing_size_atr,
        max_distance_atr=max_distance_atr,
    )

    if is_valid:
        position.exit_fib_levels = exit_levels
        position.exit_swing_high = swing_high
        position.exit_swing_low = swing_low
        position.exit_swing_timestamp = htf_fib_context.get("last_update") or htf_fib_context.get(
            "timestamp"
        )
        position.exit_swing_updated = 0


def check_swing_updates(
    *,
    position: Position,
    htf_fib_context: dict[str, Any],
    current_bar: dict[str, Any],
    swing_decider: Any,
    swing_params: Any,
    triggered_exits: dict[str, set[str]],
    swing_update_log: list[Any],
) -> None:
    """Apply swing-update policy while preserving frozen-context mutation behavior."""
    if not htf_fib_context.get("available"):
        return

    htf_levels = htf_fib_context.get("levels", {})
    new_swing_high, new_swing_low = coerce_swing_bounds(
        htf_levels=htf_levels,
        swing_high=htf_fib_context.get("swing_high"),
        swing_low=htf_fib_context.get("swing_low"),
    )

    if new_swing_high <= new_swing_low or new_swing_high <= 0:
        return

    current_swing = {
        "swing_high": position.exit_swing_high,
        "swing_low": position.exit_swing_low,
        "swing_timestamp": position.exit_swing_timestamp,
        "bars_since_swing": htf_fib_context.get("swing_age_bars", 0),
        "is_valid": True,
    }
    new_swing = {
        "swing_high": new_swing_high,
        "swing_low": new_swing_low,
        "swing_timestamp": htf_fib_context.get("last_update")
        or htf_fib_context.get("timestamp")
        or current_bar.get("timestamp"),
        "bars_since_swing": int(htf_fib_context.get("swing_age_bars", 0)),
        "is_valid": True,
    }

    should_update, reason = swing_decider.should_update_swing(
        current_swing=current_swing,
        new_swing=new_swing,
        position_side=position.side,
        params=swing_params,
    )

    if not should_update:
        return

    old_swing = (position.exit_swing_high, position.exit_swing_low)
    position.exit_swing_high = new_swing_high
    position.exit_swing_low = new_swing_low
    position.exit_swing_timestamp = new_swing.get("swing_timestamp")
    position.exit_swing_updated += 1

    new_exit_levels = calculate_exit_fibonacci_levels(
        side=position.side,
        swing_high=new_swing_high,
        swing_low=new_swing_low,
        levels=[0.786, 0.618, 0.5, 0.382],
    )
    position.exit_fib_levels = new_exit_levels

    if position.exit_ctx is not None:
        position.exit_ctx["fib"] = dict(new_exit_levels)
        position.exit_ctx["swing_bounds"] = (new_swing_low, new_swing_high)
        position.exit_ctx["swing_id"] = f"swing_update_{position.exit_swing_updated}"

    position_id = f"{position.symbol}_{position.entry_time.isoformat()}"
    old_triggered = triggered_exits.get(position_id, set()).copy()
    triggered_exits[position_id] = set()

    if swing_params.log_updates:
        log_entry = swing_decider.format_update_log_entry(
            position_id=position_id,
            timestamp=current_bar.get("timestamp"),
            reason=reason,
            old_swing=old_swing,
            new_swing=(new_swing_high, new_swing_low),
            improvement=(
                (new_swing_high - old_swing[0]) / old_swing[0]
                if position.side == "LONG"
                else (old_swing[1] - new_swing_low) / old_swing[1]
            ),
            old_triggered=old_triggered,
            update_count=position.exit_swing_updated,
        )
        swing_update_log.append(log_entry)


def coerce_swing_bounds(
    *, htf_levels: dict[float, float], swing_high: Any, swing_low: Any
) -> tuple[float, float]:
    """Coerce explicit or inferred swing bounds to floats, preserving existing fallback rules."""
    if (swing_high is None or swing_low is None) and isinstance(htf_levels, dict):
        if 1.0 in htf_levels and 0.0 in htf_levels:
            swing_high = htf_levels.get(1.0)
            swing_low = htf_levels.get(0.0)

    high = float(swing_high) if swing_high is not None else 0.0
    low = float(swing_low) if swing_low is not None else 0.0
    return high, low
