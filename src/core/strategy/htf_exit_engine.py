"""
HTF Fibonacci Exit Engine.

This module implements the logic for exiting positions based on Higher Timeframe (HTF)
Fibonacci levels and market structure. It replaces or augments fixed TP/SL.

Key Features:
- Partial Exits at key Fib levels (0.382, 0.5, 0.618).
- Structure-based Trailing Stop: Moves stop loss based on HTF structure breaks.
- Conflict Resolution: Prioritizes HTF signals over LTF noise.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


@dataclass
class ExitSignal:
    action: Literal["HOLD", "PARTIAL_EXIT", "FULL_EXIT", "UPDATE_STOP"]
    quantity_pct: float = 0.0  # 0.0 to 1.0
    reason: str = ""
    new_stop_price: float | None = None
    price_target: float | None = None


class HTFFibonacciExitEngine:
    """
    Engine for managing exits based on HTF Fibonacci levels.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        # Defaults
        self.partial_1_pct = self.config.get("partial_1_pct", 0.33)
        self.partial_2_pct = self.config.get("partial_2_pct", 0.50)  # of remaining

        # Thresholds (in ATR units)
        self.fib_threshold_atr = self.config.get("fib_threshold_atr", 0.3)
        self.trail_atr_multiplier = self.config.get("trail_atr_multiplier", 1.5)

        # State tracking per position
        # We need to track which TPs have been hit for the current position
        self.position_state = {
            "tp1_hit": False,
            "tp2_hit": False,
            "max_favorable_excursion": 0.0,
            "highest_structure_level": 0.0,  # Highest fib level closed above/below
        }

    def reset_state(self):
        """Reset state for a new position."""
        self.position_state = {
            "tp1_hit": False,
            "tp2_hit": False,
            "max_favorable_excursion": 0.0,
            "highest_structure_level": 0.0,
        }

    def check_exits(
        self,
        current_price: float,
        position_size: float,
        entry_price: float,
        side: int,  # 1 for Long, -1 for Short
        current_atr: float,
        htf_data: pd.Series,  # Row containing htf_fib_0382, etc.
    ) -> ExitSignal:
        """
        Evaluate exit conditions for a single bar.

        Args:
            current_price: Current close price (or high/low depending on pessimism)
            position_size: Current position size
            entry_price: Entry price of the position
            side: 1 (Long) or -1 (Short)
            current_atr: Current ATR (LTF)
            htf_data: Series with HTF Fib levels (already mapped/aligned)

        Returns:
            ExitSignal
        """
        if position_size == 0:
            return ExitSignal("HOLD")

        # 1. Helpers
        def is_near(target, threshold_atr=self.fib_threshold_atr):
            if target is None:
                return False
            return abs(current_price - target) <= (current_atr * threshold_atr)

        # 2. Extract HTF Levels
        # Use get() and float() conversion to ensure safety from numpy/pandas types
        try:
            fib_382 = float(htf_data.get("htf_fib_0382"))
            fib_500 = float(htf_data.get("htf_fib_05"))
            fib_618 = float(htf_data.get("htf_fib_0618"))
        except (ValueError, TypeError):
            return ExitSignal("HOLD", reason="Invalid HTF Data")

        # Handle nan
        if np.isnan(fib_382) or np.isnan(fib_500) or np.isnan(fib_618):
            return ExitSignal("HOLD", reason="Missing HTF Data")

        # 3. Determine Sorted Levels (Price Proximity from Entry)
        levels_sorted = []
        if side == 1:  # Long
            # Filter levels above entry
            candidates = [p for p in [fib_382, fib_500, fib_618] if p > entry_price]
            candidates.sort()  # Ascending: Lowest first (closest to current price moving up)
            levels_sorted = candidates
        else:  # Short
            # Filter levels below entry
            candidates = [p for p in [fib_382, fib_500, fib_618] if p < entry_price]
            candidates.sort(
                reverse=True
            )  # Descending: Highest first (closest to current price moving down)
            levels_sorted = candidates

        # 4. Partial Exits (TP1, TP2)
        # TP1 Check
        if not self.position_state["tp1_hit"] and len(levels_sorted) > 0:
            tp1_price = levels_sorted[0]
            # Success if we crossed it or are at/above it (Long) / at/below it (Short)
            if (side == 1 and current_price >= tp1_price) or (
                side == -1 and current_price <= tp1_price
            ):
                self.position_state["tp1_hit"] = True
                return ExitSignal(
                    "PARTIAL_EXIT",
                    quantity_pct=self.partial_1_pct,
                    reason=f"TP1 Hit ({tp1_price:.2f})",
                )

        # TP2 Check
        if not self.position_state["tp2_hit"] and len(levels_sorted) > 1:
            tp2_price = levels_sorted[1]
            if (side == 1 and current_price >= tp2_price) or (
                side == -1 and current_price <= tp2_price
            ):
                self.position_state["tp2_hit"] = True
                return ExitSignal(
                    "PARTIAL_EXIT",
                    quantity_pct=self.partial_2_pct,
                    reason=f"TP2 Hit ({tp2_price:.2f})",
                )

        # 5. Structure-Based Trailing Stop
        current_sl_target = None

        # Logic:
        # If TP1 hit -> Move SL to Breakeven (Entry).
        # If TP2 hit -> Move SL to TP1.

        if self.position_state["tp2_hit"]:
            # If we hit TP2, our stop should be at least at TP1
            if len(levels_sorted) > 0:
                target = levels_sorted[0]  # TP1
                current_sl_target = target
        elif self.position_state["tp1_hit"]:
            # If we hit TP1, move to Breakeven
            current_sl_target = entry_price

        if current_sl_target is not None:
            # Return UPDATE_STOP with the proposed new level.
            # The caller is responsible for checking if this new stop is actually 'tighter' than current stop.
            # (i.e. if Long: new > current; if Short: new < current).
            return ExitSignal(
                "UPDATE_STOP", new_stop_price=current_sl_target, reason="Structure Trail"
            )

        return ExitSignal("HOLD")
