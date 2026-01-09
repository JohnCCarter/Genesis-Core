"""
Exit Swing Update Strategies

Definierar olika strategier för hur exit Fibonacci-nivåer uppdateras
när nya HTF swings detekteras under en öppen position.

FIXED: Swing fastställs vid entry, uppdateras aldrig
DYNAMIC: Uppdatera vid varje ny validerad swing
HYBRID: Uppdatera endast om swing förbättras enligt kriterier
"""

from dataclasses import dataclass
from enum import Enum


class SwingUpdateStrategy(Enum):
    """Strategies för hur exit swing-nivåer uppdateras."""

    FIXED = "fixed"  # Aldrig uppdatera efter position open
    DYNAMIC = "dynamic"  # Uppdatera vid varje ny validerad swing
    HYBRID = "hybrid"  # Uppdatera endast om "bättre" swing


@dataclass
class SwingUpdateParams:
    """Parameters för swing update logic."""

    strategy: SwingUpdateStrategy = SwingUpdateStrategy.FIXED
    min_improvement_pct: float = 0.02  # 2% improvement krävs för update
    max_age_bars: int = 30  # Max ålder på swing i bars
    allow_worse_swing: bool = False  # Tillåt update till sämre swing?
    min_swing_size_atr: float = 3.0  # Minimum swing size
    max_distance_atr: float = 8.0  # Max distance från price till swing
    log_updates: bool = True  # Logga alla updates för analys


class SwingUpdateDecider:
    """Beslutar om swing ska uppdateras baserat på strategy."""

    def should_update_swing(
        self, current_swing: dict, new_swing: dict, position_side: str, params: SwingUpdateParams
    ) -> tuple[bool, str]:
        """
        Besluta om swing ska uppdateras.

        Args:
            current_swing: Nuvarande swing context
            new_swing: Ny swing context
            position_side: "LONG" or "SHORT"
            params: Strategy parameters

        Returns:
            (should_update, reason)
        """
        # FIXED: Uppdatera aldrig
        if params.strategy == SwingUpdateStrategy.FIXED:
            return False, "STRATEGY_FIXED"

        # DYNAMIC: Uppdatera alltid (om valid)
        if params.strategy == SwingUpdateStrategy.DYNAMIC:
            return self._check_dynamic_update(new_swing)

        # HYBRID: Uppdatera om bättre
        if params.strategy == SwingUpdateStrategy.HYBRID:
            return self._check_hybrid_update(current_swing, new_swing, position_side, params)

        return False, "UNKNOWN_STRATEGY"

    def _check_dynamic_update(self, new_swing: dict) -> tuple[bool, str]:
        """
        Dynamic strategy: Uppdatera alltid vid ny validerad swing.

        Args:
            new_swing: Ny swing context

        Returns:
            (should_update, reason)
        """
        if not new_swing.get("is_valid", False):
            return False, "SWING_NOT_VALID"

        return True, "NEW_VALID_SWING"

    def _check_hybrid_update(
        self, current_swing: dict, new_swing: dict, position_side: str, params: SwingUpdateParams
    ) -> tuple[bool, str]:
        """
        Hybrid strategy: Uppdatera endast om swing är "bättre".

        Kriterier:
        1. Swing måste vara valid
        2. Swing måste vara tillräckligt förbättrad (min_improvement_pct)
        3. Swing får inte vara för gammal (max_age_bars)
        4. Om allow_worse_swing=False, ingen update till sämre swing

        Args:
            current_swing: Nuvarande swing context
            new_swing: Ny swing context
            position_side: "LONG" or "SHORT"
            params: Strategy parameters

        Returns:
            (should_update, reason)
        """
        # 1. Check validity
        if not new_swing.get("is_valid", False):
            return False, "SWING_NOT_VALID"

        # 2. Check swing age
        swing_age = new_swing.get("bars_since_swing", 0)
        if swing_age > params.max_age_bars:
            return False, f"SWING_TOO_OLD_{swing_age}_BARS"

        # 3. Calculate improvement
        current_high = current_swing.get("swing_high", 0)
        current_low = current_swing.get("swing_low", 0)
        new_high = new_swing.get("swing_high", 0)
        new_low = new_swing.get("swing_low", 0)

        if position_side == "LONG":
            # För LONG: högre high är bättre (mer profit potential)
            if current_high <= 0:
                improvement = 0.0
            else:
                improvement = (new_high - current_high) / current_high

        else:  # SHORT
            # För SHORT: lägre low är bättre (mer profit potential)
            if current_low <= 0:
                improvement = 0.0
            else:
                improvement = (current_low - new_low) / current_low

        # 4. Check if improvement meets threshold
        if improvement >= params.min_improvement_pct:
            return True, f"SWING_IMPROVED_{improvement:.2%}"

        # 5. Check if worse swing (negative improvement)
        if improvement < 0:
            if not params.allow_worse_swing:
                return False, f"SWING_WORSE_{improvement:.2%}"
            else:
                return True, f"SWING_WORSE_ALLOWED_{improvement:.2%}"

        # 6. Improvement too small
        return False, f"NO_SIGNIFICANT_IMPROVEMENT_{improvement:.2%}"

    def format_update_log_entry(
        self,
        position_id: str,
        timestamp,
        reason: str,
        old_swing: tuple[float, float],
        new_swing: tuple[float, float],
        improvement: float,
        old_triggered: set,
        update_count: int,
    ) -> dict:
        """
        Formatera en log-entry för swing update.

        Args:
            position_id: Position identifier
            timestamp: Timestamp för update
            reason: Anledning till update
            old_swing: (old_high, old_low)
            new_swing: (new_high, new_low)
            improvement: Improvement percentage
            old_triggered: Set av tidigare triggade exits
            update_count: Antal updates för denna position

        Returns:
            Dictionary med log-entry
        """
        return {
            "position_id": position_id,
            "timestamp": timestamp,
            "update_count": update_count,
            "reason": reason,
            "old_swing": {
                "high": old_swing[0],
                "low": old_swing[1],
                "range": old_swing[0] - old_swing[1],
            },
            "new_swing": {
                "high": new_swing[0],
                "low": new_swing[1],
                "range": new_swing[0] - new_swing[1],
            },
            "improvement_pct": improvement,
            "old_triggered_exits": list(old_triggered),
            "exits_reset": len(old_triggered) > 0,
        }
