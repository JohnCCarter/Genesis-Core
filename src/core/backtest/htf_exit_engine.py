"""
HTF Fibonacci Exit Engine for Genesis-Core

HTF-strukturbaserad exit logik som använder:
1. HTF-swing Fibonacci nivåer (1D → 6h → 1h)
2. Partial exits vid Fib confluence
3. Trail promotion vid strukturbrott
4. AS-OF semantik (no lookahead)
"""

from dataclasses import dataclass
from typing import Any

from core.backtest.exit_strategies import SwingUpdateDecider, SwingUpdateParams, SwingUpdateStrategy
from core.backtest.position_tracker import Position
from core.indicators.exit_fibonacci import (
    calculate_exit_fibonacci_levels,
    validate_swing_for_exit,
)


def crossed_target(
    high: float,
    low: float,
    target: float,
    atr: float,
    pct_pad: float = 0.0005,
    atr_pad: float = 0.05,
) -> bool:
    """
    Check if price crossed target level with padding.

    Args:
        high: Bar high price
        low: Bar low price
        target: Target level to check
        atr: Current ATR for padding
        pct_pad: Percentage padding (default 0.05%)
        atr_pad: ATR-based padding (default 0.05 ATR)

    Returns:
        True if target was crossed within padding
    """
    pad = max(atr_pad * max(atr, 1e-9), pct_pad * target)
    return (low - pad) <= target <= (high + pad)


@dataclass
class ExitAction:
    """Represents an exit action to be executed."""

    action: str  # "PARTIAL", "TRAIL_UPDATE", "FULL_EXIT"
    size: float = 0.0  # For PARTIAL
    stop_price: float = 0.0  # For TRAIL_UPDATE
    reason: str = ""  # Exit reason


class HTFFibonacciExitEngine:
    """
    HTF-strukturbaserad exit logik.

    Principles:
    1. HTF-swing drives exits (1D → 6h → 1h)
    2. Partial exits at Fib confluence zones
    3. Trail promotion vid strukturbrott
    4. AS-OF semantics (no lookahead)
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize HTF Exit Engine.

        Args:
            config: Exit configuration with parameters:
                - partial_1_pct: Percentage to close at TP1 (default: 0.40)
                - partial_2_pct: Percentage to close at TP2 (default: 0.30)
                - fib_threshold_atr: ATR threshold for Fib proximity (default: 0.3)
                - trail_atr_multiplier: ATR multiplier for trailing stop (default: 1.3)
                - enable_partials: Enable partial exits (default: True)
                - enable_trailing: Enable trailing stops (default: True)
                - enable_structure_breaks: Enable structure break exits (default: True)
                - swing_update_strategy: "FIXED", "DYNAMIC", or "HYBRID" (default: "FIXED")
                - swing_update_params: Parameters for swing update logic
        """
        self.partial_1_pct = config.get("partial_1_pct", 0.40)  # 40% @ TP1
        self.partial_2_pct = config.get("partial_2_pct", 0.30)  # 30% @ TP2
        self.fib_threshold_atr = config.get("fib_threshold_atr", 0.3)  # 30% ATR
        self.trail_atr_multiplier = config.get("trail_atr_multiplier", 1.3)  # 1.3x ATR

        # Feature flags
        self.enable_partials = config.get("enable_partials", True)
        self.enable_trailing = config.get("enable_trailing", True)
        self.enable_structure_breaks = config.get("enable_structure_breaks", True)

        # Swing update strategy
        swing_strategy = config.get("swing_update_strategy", "fixed")
        self.swing_strategy = SwingUpdateStrategy(swing_strategy.lower())

        swing_params = config.get("swing_update_params", {})
        self.swing_params = SwingUpdateParams(
            strategy=self.swing_strategy,
            min_improvement_pct=swing_params.get("min_improvement_pct", 0.02),
            max_age_bars=swing_params.get("max_age_bars", 30),
            allow_worse_swing=swing_params.get("allow_worse_swing", False),
            min_swing_size_atr=swing_params.get("min_swing_size_atr", 3.0),
            max_distance_atr=swing_params.get("max_distance_atr", 8.0),
            log_updates=swing_params.get("log_updates", True),
        )

        self.swing_decider = SwingUpdateDecider()

        # State tracking
        self.triggered_exits: dict[str, set] = {}  # Track triggered exits per position
        self.swing_update_log: list = []  # Log all swing updates for analysis

    def check_exits(
        self,
        position: Position,
        current_bar: dict[str, Any],
        htf_fib_context: dict[str, Any],
        indicators: dict[str, float],
    ) -> list[ExitAction]:
        """
        Check all exit conditions for a position using position-specific exit levels.

        Args:
            position: Current position (with exit_fib_levels)
            current_bar: Current price bar with OHLC data
            htf_fib_context: HTF Fibonacci context from meta (for swing updates)
            indicators: Technical indicators (atr, ema50, ema_slope50_z)

        Returns:
            List of exit actions to execute
        """
        actions = []
        current_price = current_bar["close"]
        atr = indicators.get("atr", 100.0)

        # Step 1: Check if position has frozen exit context
        if not position.exit_ctx:
            # Position needs frozen exit context - this should be set at position open
            return self._fallback_exits(position, current_bar, indicators)

        # Use frozen exit context (en referens per trade)
        fib_levels = position.exit_ctx["fib"]
        swing_bounds = position.exit_ctx["swing_bounds"]
        position.exit_ctx["swing_id"]

        # Invariants (fångar statisk/dynamisk-mismatch direkt)
        if not fib_levels or not swing_bounds:
            return self._fallback_exits(position, current_bar, indicators)

        lo, hi = swing_bounds
        if hi <= lo:
            return self._fallback_exits(position, current_bar, indicators)

        levels = list(fib_levels.values())
        if not levels or min(levels) < lo - 1e-9 or max(levels) > hi + 1e-9:
            return self._fallback_exits(position, current_bar, indicators)

        # Step 2: Check for swing updates (if strategy allows)
        if self.swing_strategy != SwingUpdateStrategy.FIXED and htf_fib_context:
            self._check_swing_updates(position, htf_fib_context, current_bar, indicators)

        # Step 3: Reachability guard + tydlig orsak
        nearest = min(abs(current_price - v) for v in fib_levels.values()) if fib_levels else 999.0
        if nearest > 8 * max(atr, 1e-9):
            # Log why no exits trigger
            return [
                ExitAction(
                    action="DEBUG", reason=f"levels_out_of_reach_{nearest/atr:.1f}_ATR", size=0.0
                )
            ]

        # Get position ID for tracking triggered exits
        position_id = f"{position.symbol}_{position.entry_time.isoformat()}"
        if position_id not in self.triggered_exits:
            self.triggered_exits[position_id] = set()

        # === PARTIAL EXITS ===
        if self.enable_partials:
            partial_actions = self._check_partial_exits(
                position, current_bar, atr, fib_levels, position_id
            )
            actions.extend(partial_actions)

        # === TRAILING STOP ===
        if self.enable_trailing:
            ema50 = indicators.get("ema50", current_price)
            trail_action = self._check_trailing_stop(
                position, current_price, ema50, atr, fib_levels
            )
            if trail_action:
                actions.append(trail_action)

        # === STRUCTURE BREAK (Full Exit) ===
        if self.enable_structure_breaks:
            ema_slope50_z = indicators.get("ema_slope50_z", 0.0)
            structure_action = self._check_structure_break(
                position, current_price, fib_levels, ema_slope50_z
            )
            if structure_action:
                actions.append(structure_action)

        return actions

    def _check_partial_exits(
        self,
        position: Position,
        current_bar: dict[str, Any],
        atr: float,
        htf_levels: dict[float, float],
        position_id: str,
    ) -> list[ExitAction]:
        """Check for partial exit opportunities with adaptive thresholds."""
        actions = []

        # Get adaptive thresholds based on current market conditions
        current_price = current_bar["close"]
        atr_thr, pct_thr = self._adaptive_thresholds(current_price, htf_levels, atr)

        if position.side == "LONG":
            # TP1: Near 0.382 (HTF)?
            if (
                htf_levels.get(0.382)
                and crossed_target(current_bar["high"], current_bar["low"], htf_levels[0.382], atr)
                and "TP1_0382" not in self.triggered_exits[position_id]
            ):

                actions.append(
                    ExitAction(
                        action="PARTIAL",
                        size=position.current_size * self.partial_1_pct,
                        reason="TP1_0382",
                    )
                )
                self.triggered_exits[position_id].add("TP1_0382")

            # TP2: Near 0.5 (HTF)?
            if (
                htf_levels.get(0.5)
                and self._near_with_adaptive(current_price, htf_levels[0.5], atr, pct_thr, atr_thr)
                and "TP2_05" not in self.triggered_exits[position_id]
            ):

                actions.append(
                    ExitAction(
                        action="PARTIAL",
                        size=position.current_size * self.partial_2_pct,
                        reason="TP2_05",
                    )
                )
                self.triggered_exits[position_id].add("TP2_05")

        else:  # SHORT position
            # TP1: Near 0.618 (HTF)? (SHORT targets lower Fib levels)
            if (
                htf_levels.get(0.618)
                and self._near_with_adaptive(
                    current_price, htf_levels[0.618], atr, pct_thr, atr_thr
                )
                and "TP1_0618" not in self.triggered_exits[position_id]
            ):

                actions.append(
                    ExitAction(
                        action="PARTIAL",
                        size=position.current_size * self.partial_1_pct,
                        reason="TP1_0618",
                    )
                )
                self.triggered_exits[position_id].add("TP1_0618")

            # TP2: Near 0.5 (HTF)?
            if (
                htf_levels.get(0.5)
                and self._near_with_adaptive(current_price, htf_levels[0.5], atr, pct_thr, atr_thr)
                and "TP2_05" not in self.triggered_exits[position_id]
            ):

                actions.append(
                    ExitAction(
                        action="PARTIAL",
                        size=position.current_size * self.partial_2_pct,
                        reason="TP2_05",
                    )
                )
                self.triggered_exits[position_id].add("TP2_05")

        return actions

    def _check_trailing_stop(
        self,
        position: Position,
        current_price: float,
        ema50: float,
        atr: float,
        htf_levels: dict[float, float],
    ) -> ExitAction | None:
        """Calculate dynamic trailing stop with HTF promotion."""

        if position.side == "LONG":
            # Base trail
            base_trail = ema50 - (self.trail_atr_multiplier * atr)

            # Promotion: if price > 0.618 (HTF), lock against 0.5
            fib_05 = htf_levels.get(0.5)
            fib_0618 = htf_levels.get(0.618)

            if fib_05 and fib_0618 and current_price > fib_0618:
                promoted_trail = fib_05  # Lock against 0.5 as support
                trail_stop = max(base_trail, promoted_trail)
            else:
                trail_stop = base_trail

        else:  # SHORT
            # Base trail
            base_trail = ema50 + (self.trail_atr_multiplier * atr)

            # Promotion: if price < 0.382 (HTF), lock against 0.5
            fib_05 = htf_levels.get(0.5)
            fib_0382 = htf_levels.get(0.382)

            if fib_05 and fib_0382 and current_price < fib_0382:
                promoted_trail = fib_05  # Lock against 0.5 as resistance
                trail_stop = min(base_trail, promoted_trail)
            else:
                trail_stop = base_trail

        return ExitAction(action="TRAIL_UPDATE", stop_price=trail_stop, reason="TRAIL_STOP")

    def _check_structure_break(
        self,
        position: Position,
        current_price: float,
        htf_levels: dict[float, float],
        ema_slope50_z: float,
    ) -> ExitAction | None:
        """Check for structure break → full exit."""

        if position.side == "LONG":
            # Long structure break: price < 0.618 AND downward momentum
            fib_0618 = htf_levels.get(0.618)
            if (
                fib_0618 and current_price < fib_0618 and ema_slope50_z < -0.5
            ):  # Stronger momentum filter
                return ExitAction(action="FULL_EXIT", reason="STRUCTURE_BREAK_DOWN")

        else:  # SHORT
            # Short structure break: price > 0.382 AND upward momentum
            fib_0382 = htf_levels.get(0.382)
            if (
                fib_0382 and current_price > fib_0382 and ema_slope50_z > 0.5
            ):  # Stronger momentum filter
                return ExitAction(action="FULL_EXIT", reason="STRUCTURE_BREAK_UP")

        return None

    def _is_near_level(self, price: float, level: float, atr: float) -> bool:
        """Check if price is near Fib level (ATR-normalized)."""
        if not level or atr <= 0:
            return False
        distance_atr = abs(price - level) / atr
        return distance_atr <= self.fib_threshold_atr

    def _validate_fib_window(self, htf_levels: dict[float, float]) -> tuple[bool, str]:
        """
        Validate that Fibonacci levels are within reasonable bounds.

        Returns:
            (is_valid, reason) - True if valid, False with reason if not
        """
        if not htf_levels:
            return False, "NO_LEVELS"

        # Get swing high/low from levels
        # Note: levels dict contains calculated Fib levels, not the raw swing bounds
        # We can infer bounds from the levels themselves
        level_values = [v for v in htf_levels.values() if v is not None]
        if not level_values:
            return False, "INVALID_LEVELS"

        # Basic sanity check: all levels should be positive and reasonable
        if any(v <= 0 for v in level_values):
            return False, "NEGATIVE_LEVELS"

        return True, "OK"

    def _fib_reachability_flag(
        self, price: float, htf_levels: dict[float, float], atr: float, pad_atr: float = 8.0
    ) -> tuple[bool, str, float]:
        """
        Check if ANY Fib level is within reachable distance.

        Args:
            price: Current price
            htf_levels: Fibonacci levels dict
            atr: Current ATR
            pad_atr: Maximum distance in ATR units (default 8.0)

        Returns:
            (is_reachable, reason, nearest_distance_atr)
        """
        if atr <= 0:
            return False, "INVALID_ATR", 999.0

        # Calculate envelope around current price
        envelope_lo = price - (pad_atr * atr)
        envelope_hi = price + (pad_atr * atr)

        # Check if any level is within envelope
        reachable_levels = []
        all_distances = []

        for level_key, level_price in htf_levels.items():
            if level_price is None:
                continue

            distance_atr = abs(price - level_price) / atr
            all_distances.append(distance_atr)

            if envelope_lo <= level_price <= envelope_hi:
                reachable_levels.append((level_key, distance_atr))

        nearest_distance = min(all_distances) if all_distances else 999.0

        if reachable_levels:
            return True, "REACHABLE", nearest_distance
        else:
            return False, "LEVELS_OUT_OF_REACH", nearest_distance

    def _adaptive_thresholds(
        self, price: float, htf_levels: dict[float, float], atr: float
    ) -> tuple[float, float]:
        """
        Calculate adaptive thresholds for Fib proximity.

        Combines ATR-based and percentage-based thresholds.
        Widens thresholds when price is far from all Fib levels.

        Returns:
            (atr_threshold, pct_threshold)
        """
        # Base thresholds
        atr_thr = 0.20  # Start at 0.20 ATR (more generous than 0.50)
        pct_thr = 0.0015  # 0.15% in price terms

        # Calculate distance to nearest Fib level
        if atr > 0 and htf_levels:
            distances = []
            for level_price in htf_levels.values():
                if level_price is not None:
                    dist_atr = abs(price - level_price) / atr
                    distances.append(dist_atr)

            if distances:
                nearest = min(distances)

                # Adaptively widen thresholds if far from all levels
                if nearest > 4.0:
                    # Price is >4 ATR from nearest level - widen thresholds
                    atr_thr = min(0.35, atr_thr + 0.10)  # Cap at 0.35 ATR
                    pct_thr = min(0.0030, pct_thr + 0.0008)  # Cap at 0.30%

        return atr_thr, pct_thr

    def _near_with_adaptive(
        self, price: float, target: float, atr: float, pct_thr: float, atr_thr: float
    ) -> bool:
        """
        Check if price is near target using BOTH ATR and percentage thresholds.

        Returns True if EITHER condition is met (more lenient).
        """
        if target is None or atr <= 0:
            return False

        distance = abs(price - target)

        # ATR-based check
        atr_check = (distance / atr) <= atr_thr

        # Percentage-based check
        pct_check = (distance / max(price, 1.0)) <= pct_thr

        # Return True if EITHER threshold is met
        return atr_check or pct_check

    def _fallback_exits(
        self, position: Position, current_bar: dict[str, Any], indicators: dict[str, float]
    ) -> list[ExitAction]:
        """
        Fallback exit logic when HTF context unavailable.

        Uses simple trailing stop based on EMA.
        """
        current_price = current_bar["close"]
        atr = indicators.get("atr", 100)
        ema50 = indicators.get("ema50", current_price)

        # Simple trailing stop
        if position.side == "LONG":
            trail_stop = ema50 - (self.trail_atr_multiplier * atr)
        else:  # SHORT
            trail_stop = ema50 + (self.trail_atr_multiplier * atr)

        return [ExitAction(action="TRAIL_UPDATE", stop_price=trail_stop, reason="FALLBACK_TRAIL")]

    def cleanup_position(self, position_id: str):
        """Clean up tracking data when position is closed."""
        if position_id in self.triggered_exits:
            del self.triggered_exits[position_id]

    def _initialize_position_exit_levels(
        self, position: Position, htf_fib_context: dict[str, Any], indicators: dict[str, float]
    ) -> None:
        """
        Initialize position's exit Fibonacci levels from HTF context.

        Args:
            position: Position to initialize
            htf_fib_context: HTF Fibonacci context
            indicators: Technical indicators
        """
        htf_levels = htf_fib_context.get("levels", {})
        current_price = indicators.get("ema50", 0.0)  # Use EMA as reference price
        current_atr = indicators.get("atr", 100.0)

        # Extract swing from HTF context
        swing_high = htf_levels.get("htf_fib_100", 0.0)  # 1.0 level = swing high
        swing_low = htf_levels.get("htf_fib_0", 0.0)  # 0.0 level = swing low

        if swing_high <= swing_low or swing_high <= 0 or swing_low <= 0:
            # Invalid swing - use fallback levels
            return

        # Calculate exit Fibonacci levels using symmetric logic
        exit_levels = calculate_exit_fibonacci_levels(
            side=position.side,
            swing_high=swing_high,
            swing_low=swing_low,
            levels=[0.382, 0.5, 0.618],
        )

        # Validate swing for exit
        is_valid, reason = validate_swing_for_exit(
            swing_high=swing_high,
            swing_low=swing_low,
            current_price=current_price,
            current_atr=current_atr,
            min_swing_size_atr=self.swing_params.min_swing_size_atr,
            max_distance_atr=self.swing_params.max_distance_atr,
        )

        if is_valid:
            # Initialize position with exit levels
            position.exit_fib_levels = exit_levels
            position.exit_swing_high = swing_high
            position.exit_swing_low = swing_low
            position.exit_swing_timestamp = htf_fib_context.get("timestamp")
            position.exit_swing_updated = 0

    def _check_swing_updates(
        self,
        position: Position,
        htf_fib_context: dict[str, Any],
        current_bar: dict[str, Any],
        indicators: dict[str, float],
    ) -> None:
        """
        Check if swing should be updated based on strategy.

        Args:
            position: Current position
            htf_fib_context: New HTF Fibonacci context
            current_bar: Current bar data
            indicators: Technical indicators
        """
        if not htf_fib_context.get("available"):
            return

        htf_levels = htf_fib_context.get("levels", {})
        new_swing_high = htf_levels.get("htf_fib_100", 0.0)
        new_swing_low = htf_levels.get("htf_fib_0", 0.0)

        if new_swing_high <= new_swing_low or new_swing_high <= 0:
            return

        # Create current and new swing contexts
        current_swing = {
            "swing_high": position.exit_swing_high,
            "swing_low": position.exit_swing_low,
            "swing_timestamp": position.exit_swing_timestamp,
            "bars_since_swing": position.exit_swing_updated,
            "is_valid": True,
        }

        new_swing = {
            "swing_high": new_swing_high,
            "swing_low": new_swing_low,
            "swing_timestamp": htf_fib_context.get("timestamp"),
            "bars_since_swing": 0,
            "is_valid": True,
        }

        # Decide if swing should be updated
        should_update, reason = self.swing_decider.should_update_swing(
            current_swing=current_swing,
            new_swing=new_swing,
            position_side=position.side,
            params=self.swing_params,
        )

        if should_update:
            # Update position's swing and recalculate exit levels
            old_swing = (position.exit_swing_high, position.exit_swing_low)

            position.exit_swing_high = new_swing_high
            position.exit_swing_low = new_swing_low
            position.exit_swing_timestamp = htf_fib_context.get("timestamp")
            position.exit_swing_updated += 1

            # Recalculate exit levels
            new_exit_levels = calculate_exit_fibonacci_levels(
                side=position.side,
                swing_high=new_swing_high,
                swing_low=new_swing_low,
                levels=[0.382, 0.5, 0.618],
            )

            position.exit_fib_levels = new_exit_levels

            # Reset triggered exits (new swing = fresh opportunity)
            position_id = f"{position.symbol}_{position.entry_time.isoformat()}"
            old_triggered = self.triggered_exits.get(position_id, set()).copy()
            self.triggered_exits[position_id] = set()

            # Log the update if enabled
            if self.swing_params.log_updates:
                log_entry = self.swing_decider.format_update_log_entry(
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
                self.swing_update_log.append(log_entry)
