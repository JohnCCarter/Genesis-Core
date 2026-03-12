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
from core.backtest.htf_exit_partials import evaluate_partial_exits
from core.backtest.htf_exit_structure import detect_structure_break
from core.backtest.htf_exit_swing_updates import (
    check_swing_updates,
    initialize_position_exit_levels,
    resolve_valid_exit_context,
)
from core.backtest.htf_exit_trailing import (
    calculate_fallback_trailing_stop,
    calculate_trailing_stop,
)
from core.backtest.position_tracker import Position


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
                - partial_3_pct: Percentage to close at TP3 (default: 0.20)
                - partial_4_pct: Percentage to close at TP4 (default: 0.10)
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
        self.partial_3_pct = config.get("partial_3_pct", 0.20)  # 20% @ TP3
        self.partial_4_pct = config.get("partial_4_pct", 0.10)  # 10% @ TP4
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
        position.exit_ctx["swing_id"]
        resolved_exit_context = resolve_valid_exit_context(position.exit_ctx)

        # Invariants (fångar statisk/dynamisk-mismatch direkt)
        if resolved_exit_context is None:
            return self._fallback_exits(position, current_bar, indicators)
        fib_levels, _swing_bounds = resolved_exit_context

        # Step 2: Check for swing updates (if strategy allows)
        if self.swing_strategy != SwingUpdateStrategy.FIXED and htf_fib_context:
            self._check_swing_updates(position, htf_fib_context, current_bar, indicators)

            # If the swing was updated, we must refresh and re-validate the frozen context.
            if position.exit_ctx:
                resolved_exit_context = resolve_valid_exit_context(position.exit_ctx)
                if resolved_exit_context is None:
                    return self._fallback_exits(position, current_bar, indicators)
                fib_levels, _swing_bounds = resolved_exit_context

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
        # Get adaptive thresholds based on current market conditions
        current_price = current_bar["close"]
        atr_thr, pct_thr = self._adaptive_thresholds(current_price, htf_levels, atr)
        partial_candidates = evaluate_partial_exits(
            position_side=position.side,
            current_size=position.current_size,
            current_bar=current_bar,
            atr=atr,
            htf_levels=htf_levels,
            triggered_exits=self.triggered_exits[position_id],
            partial_pcts=(
                self.partial_1_pct,
                self.partial_2_pct,
                self.partial_3_pct,
                self.partial_4_pct,
            ),
            pct_thr=pct_thr,
            atr_thr=atr_thr,
            near_with_adaptive=self._near_with_adaptive,
        )
        return [
            ExitAction(action="PARTIAL", size=candidate.size, reason=candidate.reason)
            for candidate in partial_candidates
        ]

    def _check_trailing_stop(
        self,
        position: Position,
        current_price: float,
        ema50: float,
        atr: float,
        htf_levels: dict[float, float],
    ) -> ExitAction | None:
        """Calculate dynamic trailing stop with HTF promotion."""
        trail_stop = calculate_trailing_stop(
            position_side=position.side,
            current_price=current_price,
            ema50=ema50,
            atr=atr,
            htf_levels=htf_levels,
            trail_atr_multiplier=self.trail_atr_multiplier,
        )
        return ExitAction(action="TRAIL_UPDATE", stop_price=trail_stop, reason="TRAIL_STOP")

    def _check_structure_break(
        self,
        position: Position,
        current_price: float,
        htf_levels: dict[float, float],
        ema_slope50_z: float,
    ) -> ExitAction | None:
        """Check for structure break → full exit."""
        reason = detect_structure_break(
            position_side=position.side,
            current_price=current_price,
            htf_levels=htf_levels,
            ema_slope50_z=ema_slope50_z,
        )
        if reason is None:
            return None
        return ExitAction(action="FULL_EXIT", reason=reason)

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
        atr = indicators.get("atr", 100)
        ema50 = indicators.get("ema50", current_bar["close"])
        trail_stop = calculate_fallback_trailing_stop(
            position_side=position.side,
            ema50=ema50,
            atr=atr,
            trail_atr_multiplier=self.trail_atr_multiplier,
        )

        return [ExitAction(action="TRAIL_UPDATE", stop_price=trail_stop, reason="FALLBACK_TRAIL")]

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
        initialize_position_exit_levels(
            position=position,
            htf_fib_context=htf_fib_context,
            indicators=indicators,
            min_swing_size_atr=self.swing_params.min_swing_size_atr,
            max_distance_atr=self.swing_params.max_distance_atr,
        )

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
        check_swing_updates(
            position=position,
            htf_fib_context=htf_fib_context,
            current_bar=current_bar,
            swing_decider=self.swing_decider,
            swing_params=self.swing_params,
            triggered_exits=self.triggered_exits,
            swing_update_log=self.swing_update_log,
        )
