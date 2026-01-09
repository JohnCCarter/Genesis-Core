"""
Exit Fibonacci Calculator - Symmetrisk med Entry Logic

Detta modul beräknar exit-nivåer baserat på Fibonacci retracements,
men i MOTSATT riktning från entry-logiken.

ENTRY (LONG): Retracement nedåt från swing high
EXIT (LONG): Retracement nedåt från nya swing high (profit-taking)

Detta ger symmetrisk logik där samma Fibonacci-psykologi används
för både entry och exit, men med olika swing-referenser.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SwingContext:
    """Swing context för exit-beräkningar."""

    swing_high: float
    swing_low: float
    swing_timestamp: datetime | None = None
    bars_since_swing: int = 0
    is_valid: bool = True
    validation_reason: str = "OK"


def calculate_exit_fibonacci_levels(
    side: str, swing_high: float, swing_low: float, levels: list[float] | None = None
) -> dict[float, float]:
    """
    Beräkna exit Fibonacci-nivåer baserat på aktuell swing.

    SYMMETRISK LOGIK (Chamoun-modellen)
    -----------------------------------
    Entry- och exit-logiken använder samma Fibonacci-psykologi (0.382, 0.5, 0.618, 0.786)
    men tillämpas i motsatt riktning beroende på handels-sida.

    ▣ ENTRY (LONG)
        - Retracement NEDÅT från swing_low → swing_high (pullback)
        - Entry sker när priset rekylerar ned mot 0.5–0.618-zonen ("golden zone")

    ▣ EXIT (LONG)
        - Retracement NEDÅT från swing_high (profit-taking)
        - Pris rör sig nedåt från high, och nivåerna beräknas som:
            0.786 = swing_high - 0.786 * range   (tidig profit-taking)
            0.618 = swing_high - 0.618 * range   (golden zone – typisk TP)
            0.5   = swing_high - 0.5   * range   (50% retracement)
            0.382 = swing_high - 0.382 * range   (djup retracement)

    ▣ EXIT (SHORT)
        - Retracement UPPÅT från swing_low (profit-taking)
        - Pris rör sig uppåt från low, och nivåerna beräknas som:
            0.786 = swing_low + 0.786 * range    (tidig profit-taking)
            0.618 = swing_low + 0.618 * range    (golden zone – typisk TP)
            0.5   = swing_low + 0.5   * range    (50% retracement)
            0.382 = swing_low + 0.382 * range    (djup retracement)

    ▣ Sammanfattning
        LONG EXIT  → retracement DOWN från high (nivåer under high)
        SHORT EXIT → retracement UP från low  (nivåer över low)
        Samma formler används, men riktningen och referenspunkten skiljer sig.

    Args:
        side: "LONG" eller "SHORT"
        swing_high: högsta pris i swingen (måste vara > swing_low)
        swing_low: lägsta pris i swingen
        levels: lista av Fibonacci-nivåer (default: [0.786, 0.618, 0.5, 0.382])

    Returns:
        dict[float, float]: {nivå: pris}
        Exempel (LONG):
            {0.786: 102_140.0, 0.618: 103_820.0, 0.5: 105_000.0, 0.382: 106_180.0}

    Raises:
        ValueError: Om swing_high <= swing_low eller ogiltig 'side'
    """
    if levels is None:
        # INVERTERADE nivåer för exit (0.786 → 0.382)
        levels = [0.786, 0.618, 0.5, 0.382]

    # Validate inputs
    if swing_high <= swing_low:
        raise ValueError(f"Invalid swing: high ({swing_high}) must be > low ({swing_low})")

    if side not in ["LONG", "SHORT"]:
        raise ValueError(f"Invalid side: {side}. Must be 'LONG' or 'SHORT'")

    range_size = swing_high - swing_low
    exit_levels = {}

    if side == "LONG":
        # Exit nivåer moving DOWN från swing high (profit-taking när pris retraces)
        for level in levels:
            exit_levels[level] = swing_high - (level * range_size)

    else:  # SHORT
        # Exit nivåer moving UP från swing low (profit-taking när pris retraces)
        for level in levels:
            exit_levels[level] = swing_low + (level * range_size)

    return exit_levels


def validate_swing_for_exit(
    swing_high: float,
    swing_low: float,
    current_price: float,
    current_atr: float,
    min_swing_size_atr: float = 3.0,
    max_distance_atr: float = 8.0,
) -> tuple[bool, str]:
    """
    Validera att swing är lämplig för exit-beräkningar.

    Kontrollerar:
    1. Swing size är tillräckligt stor (min 3 ATR)
    2. Current price är inom rimligt avstånd från swing (max 8 ATR)
    3. Basic sanity checks (positive prices, valid range)

    Args:
        swing_high: Swing high price
        swing_low: Swing low price
        current_price: Nuvarande pris
        current_atr: Current ATR value
        min_swing_size_atr: Minimum swing size i ATR-termer
        max_distance_atr: Max avstånd från swing i ATR-termer

    Returns:
        (is_valid, reason)
    """
    # Check basic validity
    if swing_high <= 0 or swing_low <= 0:
        return False, "NEGATIVE_PRICES"

    if swing_high <= swing_low:
        return False, "INVALID_SWING_ORDER"

    if current_atr <= 0:
        return False, "INVALID_ATR"

    # Check swing size
    swing_size = swing_high - swing_low
    swing_size_atr = swing_size / current_atr

    if swing_size_atr < min_swing_size_atr:
        return False, f"SWING_TOO_SMALL_{swing_size_atr:.1f}_ATR"

    # Check distance from current price to swing
    distance_to_high = abs(current_price - swing_high)
    distance_to_low = abs(current_price - swing_low)
    nearest_distance = min(distance_to_high, distance_to_low)
    distance_atr = nearest_distance / current_atr

    if distance_atr > max_distance_atr:
        return False, f"SWING_TOO_FAR_{distance_atr:.1f}_ATR"

    return True, "OK"


def calculate_swing_improvement(
    old_swing_high: float,
    old_swing_low: float,
    new_swing_high: float,
    new_swing_low: float,
    side: str,
) -> float:
    """
    Beräkna hur mycket swing har förbättrats.

    För LONG: Förbättring = högre swing high (mer profit potential)
    För SHORT: Förbättring = lägre swing low (mer profit potential)

    Args:
        old_swing_high: Previous swing high
        old_swing_low: Previous swing low
        new_swing_high: New swing high
        new_swing_low: New swing low
        side: "LONG" or "SHORT"

    Returns:
        Improvement percentage (positive = better, negative = worse)
    """
    if side == "LONG":
        # För LONG: högre high är bättre
        if old_swing_high <= 0:
            return 0.0
        improvement = (new_swing_high - old_swing_high) / old_swing_high

    else:  # SHORT
        # För SHORT: lägre low är bättre
        if old_swing_low <= 0:
            return 0.0
        improvement = (old_swing_low - new_swing_low) / old_swing_low

    return improvement


def format_exit_levels_for_display(
    exit_levels: dict[float, float], side: str, current_price: float
) -> str:
    """
    Formatera exit-nivåer för display/logging.

    Args:
        exit_levels: Dictionary med {level: price}
        side: "LONG" or "SHORT"
        current_price: Current price för context

    Returns:
        Formatted string
    """
    lines = [f"Exit Levels ({side}):"]

    sorted_levels = sorted(exit_levels.items(), reverse=(side == "LONG"))

    for level, price in sorted_levels:
        distance = ((price - current_price) / current_price) * 100
        marker = "←" if abs(distance) < 1.0 else " "
        lines.append(f"  {level:.3f}: ${price:,.0f} ({distance:+.1f}%) {marker}")

    return "\n".join(lines)


def get_next_exit_level(
    exit_levels: dict[float, float],
    current_price: float,
    side: str,
    triggered_levels: set[float] | None = None,
) -> tuple[float | None, float | None]:
    """
    Hitta nästa exit-nivå som inte har triggats.

    Args:
        exit_levels: Dictionary med {level: price}
        current_price: Current price
        side: "LONG" or "SHORT"
        triggered_levels: Set av nivåer som redan triggats

    Returns:
        (next_level, next_price) eller (None, None) om inga kvar
    """
    if triggered_levels is None:
        triggered_levels = set()

    available_levels = [
        (level, price) for level, price in exit_levels.items() if level not in triggered_levels
    ]

    if not available_levels:
        return None, None

    if side == "LONG":
        # För LONG: närmaste nivå UNDER current price
        candidates = [(level, p) for level, p in available_levels if p < current_price]
        if candidates:
            # Högsta priset under current price
            return max(candidates, key=lambda x: x[1])

    else:  # SHORT
        # För SHORT: närmaste nivå ÖVER current price
        candidates = [(level, p) for level, p in available_levels if p > current_price]
        if candidates:
            # Lägsta priset över current price
            return min(candidates, key=lambda x: x[1])

    return None, None
