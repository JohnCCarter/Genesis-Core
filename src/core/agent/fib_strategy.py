from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.indicators.fibonacci import FibonacciConfig, detect_swing_points

DEFAULT_ENTRY_LOW = 0.5
DEFAULT_ENTRY_HIGH = 0.618
DEFAULT_EXTENSION_TARGETS: tuple[float, ...] = (1.272, 1.618)
DEFAULT_TARGET_FRACTIONS: tuple[float, float, float] = (0.333, 0.333, 0.334)
DEFAULT_ATR_DEPTH = 6.0
MIN_BARS_REQUIRED = 60


@dataclass(slots=True)
class FibStrategyParams:
    entry_zone_low: float = DEFAULT_ENTRY_LOW
    entry_zone_high: float = DEFAULT_ENTRY_HIGH
    extension_levels: tuple[float, ...] = DEFAULT_EXTENSION_TARGETS
    target_fractions: tuple[float, float, float] = DEFAULT_TARGET_FRACTIONS
    atr_depth: float = DEFAULT_ATR_DEPTH
    require_confirmation: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_zone_low": self.entry_zone_low,
            "entry_zone_high": self.entry_zone_high,
            "extension_levels": list(self.extension_levels),
            "target_fractions": list(self.target_fractions),
            "atr_depth": self.atr_depth,
            "require_confirmation": self.require_confirmation,
        }


@dataclass(slots=True)
class FibSignal:
    action: str  # "LONG" | "SHORT" | "NONE"
    reason: str
    htf_swing: dict[str, Any] | None = None
    htf_zone: dict[str, float] | None = None
    ltf_swing: dict[str, Any] | None = None
    ltf_zone: dict[str, float] | None = None
    entry: float | None = None
    stop: float | None = None
    targets: list[dict[str, Any]] = field(default_factory=list)
    size: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "htf_swing": self.htf_swing,
            "htf_zone": self.htf_zone,
            "ltf_swing": self.ltf_swing,
            "ltf_zone": self.ltf_zone,
            "entry": self.entry,
            "stop": self.stop,
            "targets": self.targets,
            "size": self.size,
        }


def _none(reason: str) -> FibSignal:
    return FibSignal(action="NONE", reason=reason)


def _validate_candles(candles: dict[str, Any]) -> bool:
    needed = ("open", "high", "low", "close")
    for key in needed:
        seq = candles.get(key)
        if not isinstance(seq, list) or len(seq) < MIN_BARS_REQUIRED:
            return False
    return True


def _latest_swing(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    atr_depth: float,
) -> tuple[str, int, int, float, float] | None:
    """Return (direction, idx_a, idx_b, price_a, price_b) of the most recent A→B leg.

    direction "up": A=swing-low, B=swing-high (swing-high is more recent)
    direction "down": A=swing-high, B=swing-low (swing-low is more recent)
    """
    cfg = FibonacciConfig(atr_depth=atr_depth)
    high_idx, low_idx, high_px, low_px = detect_swing_points(highs, lows, closes, cfg)
    if not high_idx or not low_idx:
        return None
    last_high_idx = high_idx[-1]
    last_low_idx = low_idx[-1]
    last_high_px = high_px[-1]
    last_low_px = low_px[-1]
    if last_high_idx > last_low_idx:
        return ("up", last_low_idx, last_high_idx, last_low_px, last_high_px)
    if last_low_idx > last_high_idx:
        return ("down", last_high_idx, last_low_idx, last_high_px, last_low_px)
    return None


def _retracement_zone(
    direction: str,
    price_a: float,
    price_b: float,
    zone_low: float,
    zone_high: float,
) -> dict[str, float]:
    """Compute fib retracement price zone between zone_low and zone_high fractions.

    For "up": A=low, B=high. Retracement = B - frac*(B-A). Higher frac → lower price.
    For "down": A=high, B=low. Retracement = B + frac*(A-B). Higher frac → higher price.
    """
    rng = abs(price_b - price_a)
    if direction == "up":
        # zone_high (e.g. 0.618) = deeper retrace = lower price
        upper = price_b - zone_low * rng
        lower = price_b - zone_high * rng
    else:
        lower = price_b + zone_low * rng
        upper = price_b + zone_high * rng
    return {"low": float(min(lower, upper)), "high": float(max(lower, upper))}


def _extension_prices(
    direction: str,
    price_a: float,
    price_b: float,
    levels: tuple[float, ...],
) -> list[float]:
    rng = abs(price_b - price_a)
    if direction == "up":
        return [float(price_b + (lvl - 1.0) * rng) for lvl in levels]
    return [float(price_b - (lvl - 1.0) * rng) for lvl in levels]


def _last_close_in_zone(closes: list[float], zone: dict[str, float]) -> bool:
    if not closes:
        return False
    last = float(closes[-1])
    return zone["low"] <= last <= zone["high"]


def _is_confirmation_candle(
    direction: str,
    opens: list[float],
    closes: list[float],
) -> bool:
    if not opens or not closes:
        return False
    o = float(opens[-1])
    c = float(closes[-1])
    if direction == "up":
        return c > o  # green candle for longs
    return c < o  # red candle for shorts


def _ltf_swing_within_htf_zone(
    htf_zone: dict[str, float],
    htf_direction: str,
    highs: list[float],
    lows: list[float],
    closes: list[float],
    atr_depth: float,
) -> tuple[str, int, int, float, float] | None:
    """Find the most recent LTF leg COUNTER to HTF direction with at least one
    extreme inside the HTF zone.

    For HTF-up: we expect a LTF down-leg (high→low) inside the zone — entry
    happens when price retraces back UP into the LTF 0.5–0.618 band.

    For HTF-down: we expect a LTF up-leg (low→high) — entry on retrace DOWN.

    Returns (ltf_leg_direction, a_idx, b_idx, a_price, b_price) where
    a is the start of the leg and b is the more recent extreme.
    """
    cfg = FibonacciConfig(atr_depth=atr_depth)
    high_idx, low_idx, high_px, low_px = detect_swing_points(highs, lows, closes, cfg)
    if not high_idx or not low_idx:
        return None

    if htf_direction == "up":
        # LTF down-leg: a swing-high followed by a more recent swing-low
        for i in range(len(low_idx) - 1, -1, -1):
            l_idx = low_idx[i]
            l_price = low_px[i]
            earlier_highs = [
                (hi, hp) for hi, hp in zip(high_idx, high_px) if hi < l_idx
            ]
            if not earlier_highs:
                continue
            h_idx, h_price = earlier_highs[-1]
            inside = (
                htf_zone["low"] <= l_price <= htf_zone["high"]
                or htf_zone["low"] <= h_price <= htf_zone["high"]
            )
            if not inside:
                continue
            return ("down", h_idx, l_idx, float(h_price), float(l_price))
        return None

    # htf_direction == "down": LTF up-leg = swing-low followed by a more recent swing-high
    for i in range(len(high_idx) - 1, -1, -1):
        h_idx = high_idx[i]
        h_price = high_px[i]
        earlier_lows = [(li, lp) for li, lp in zip(low_idx, low_px) if li < h_idx]
        if not earlier_lows:
            continue
        l_idx, l_price = earlier_lows[-1]
        inside = (
            htf_zone["low"] <= l_price <= htf_zone["high"]
            or htf_zone["low"] <= h_price <= htf_zone["high"]
        )
        if not inside:
            continue
        return ("up", l_idx, h_idx, float(l_price), float(h_price))
    return None


def compute_signal(
    htf_candles: dict[str, Any],
    ltf_candles: dict[str, Any],
    params: FibStrategyParams | None = None,
    *,
    equity_usd: float = 0.0,
    risk_pct: float = 0.01,
) -> FibSignal:
    p = params or FibStrategyParams()
    if not _validate_candles(htf_candles) or not _validate_candles(ltf_candles):
        return _none("insufficient_candles")

    htf_swing = _latest_swing(
        htf_candles["high"], htf_candles["low"], htf_candles["close"], p.atr_depth
    )
    if htf_swing is None:
        return _none("no_htf_swing")
    direction, a_idx, b_idx, a_px, b_px = htf_swing
    htf_zone = _retracement_zone(direction, a_px, b_px, p.entry_zone_low, p.entry_zone_high)

    if not _last_close_in_zone(htf_candles["close"], htf_zone):
        return FibSignal(
            action="NONE",
            reason="no_htf_zone_touch",
            htf_swing={"a": a_px, "b": b_px, "direction": direction},
            htf_zone=htf_zone,
        )

    ltf_swing = _ltf_swing_within_htf_zone(
        htf_zone,
        direction,
        ltf_candles["high"],
        ltf_candles["low"],
        ltf_candles["close"],
        p.atr_depth,
    )
    if ltf_swing is None:
        return FibSignal(
            action="NONE",
            reason="no_ltf_swing",
            htf_swing={"a": a_px, "b": b_px, "direction": direction},
            htf_zone=htf_zone,
        )

    ltf_dir, l_a_idx, l_b_idx, l_a_px, l_b_px = ltf_swing
    ltf_zone = _retracement_zone(ltf_dir, l_a_px, l_b_px, p.entry_zone_low, p.entry_zone_high)

    if not _last_close_in_zone(ltf_candles["close"], ltf_zone):
        return FibSignal(
            action="NONE",
            reason="no_ltf_zone_touch",
            htf_swing={"a": a_px, "b": b_px, "direction": direction},
            htf_zone=htf_zone,
            ltf_swing={"a": l_a_px, "b": l_b_px, "direction": ltf_dir},
            ltf_zone=ltf_zone,
        )

    if p.require_confirmation and not _is_confirmation_candle(
        direction, ltf_candles["open"], ltf_candles["close"]
    ):
        return FibSignal(
            action="NONE",
            reason="no_confirmation",
            htf_swing={"a": a_px, "b": b_px, "direction": direction},
            htf_zone=htf_zone,
            ltf_swing={"a": l_a_px, "b": l_b_px, "direction": ltf_dir},
            ltf_zone=ltf_zone,
        )

    entry = float(ltf_candles["close"][-1])
    # Stop sits beyond the LTF leg extreme (B = the more recent swing extreme).
    if direction == "up":
        # HTF-up + LTF down-leg: B = LTF swing-low, stop must be below it.
        stop = float(min(l_b_px, ltf_zone["low"]))
    else:
        # HTF-down + LTF up-leg: B = LTF swing-high, stop must be above it.
        stop = float(max(l_b_px, ltf_zone["high"]))
    stop_distance = abs(entry - stop)
    if stop_distance <= 0.0:
        return _none("invalid_stop_distance")

    extension_prices = _extension_prices(direction, a_px, b_px, p.extension_levels)
    targets: list[dict[str, Any]] = []
    fractions = list(p.target_fractions)
    for level, price, fraction in zip(p.extension_levels, extension_prices, fractions[:-1]):
        targets.append({"level": float(level), "price": float(price), "fraction": float(fraction)})
    targets.append({"level": "trailing", "fraction": float(fractions[-1])})

    size: float | None = None
    if equity_usd > 0 and risk_pct > 0:
        size = (equity_usd * risk_pct) / stop_distance

    action = "LONG" if direction == "up" else "SHORT"
    return FibSignal(
        action=action,
        reason="ltf_confirmation",
        htf_swing={"a": a_px, "b": b_px, "direction": direction},
        htf_zone=htf_zone,
        ltf_swing={"a": l_a_px, "b": l_b_px, "direction": ltf_dir},
        ltf_zone=ltf_zone,
        entry=entry,
        stop=stop,
        targets=targets,
        size=size,
    )
