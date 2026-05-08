from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.indicators.fibonacci import FibonacciConfig, detect_swing_points

DEFAULT_ENTRY_LOW = 0.5
DEFAULT_ENTRY_HIGH = 0.786
DEFAULT_EXTENSION_TARGETS: tuple[float, ...] = (1.272, 1.618)
DEFAULT_TARGET_FRACTIONS: tuple[float, float, float] = (0.333, 0.333, 0.334)
DEFAULT_ATR_DEPTH = 6.0
# Per-tier defaults tuned for native Bitfinex 1D + 6h + 1h on BTC/USD.
# Stepwise ablation found major=5.5 removes one losing trade vs uniform 6.0
# without affecting winners (PF 1.15 → 1.44 on 24m of native data).
DEFAULT_MEGA_ATR_DEPTH = 6.0
DEFAULT_MAJOR_ATR_DEPTH = 5.5
DEFAULT_MINOR_ATR_DEPTH = 6.0
DEFAULT_TREND_LOOKBACK = 50  # bars (e.g. 1D-bars ≈ 50 days)
MIN_BARS_REQUIRED = 60


@dataclass(slots=True)
class FibStrategyParams:
    entry_zone_low: float = DEFAULT_ENTRY_LOW
    entry_zone_high: float = DEFAULT_ENTRY_HIGH
    extension_levels: tuple[float, ...] = DEFAULT_EXTENSION_TARGETS
    target_fractions: tuple[float, float, float] = DEFAULT_TARGET_FRACTIONS
    atr_depth: float = DEFAULT_ATR_DEPTH
    # Per-tier values for compute_signal_nested.
    # None = fall back to atr_depth. Defaults tuned for native 1D + 6h + 1h.
    mega_atr_depth: float | None = DEFAULT_MEGA_ATR_DEPTH
    major_atr_depth: float | None = DEFAULT_MAJOR_ATR_DEPTH
    minor_atr_depth: float | None = DEFAULT_MINOR_ATR_DEPTH
    require_confirmation: bool = True
    trend_filter_enabled: bool = True
    trend_filter_lookback: int = DEFAULT_TREND_LOOKBACK
    confluence_required: bool = True
    mega_zone_touch_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_zone_low": self.entry_zone_low,
            "entry_zone_high": self.entry_zone_high,
            "extension_levels": list(self.extension_levels),
            "target_fractions": list(self.target_fractions),
            "atr_depth": self.atr_depth,
            "mega_atr_depth": self.mega_atr_depth,
            "major_atr_depth": self.major_atr_depth,
            "minor_atr_depth": self.minor_atr_depth,
            "require_confirmation": self.require_confirmation,
            "trend_filter_enabled": self.trend_filter_enabled,
            "trend_filter_lookback": self.trend_filter_lookback,
            "confluence_required": self.confluence_required,
            "mega_zone_touch_required": self.mega_zone_touch_required,
        }

    def resolve_mega_atr(self) -> float:
        return self.mega_atr_depth if self.mega_atr_depth is not None else self.atr_depth

    def resolve_major_atr(self) -> float:
        return self.major_atr_depth if self.major_atr_depth is not None else self.atr_depth

    def resolve_minor_atr(self) -> float:
        return self.minor_atr_depth if self.minor_atr_depth is not None else self.atr_depth


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


def trend_aligned(direction: str, closes: list[float], lookback: int) -> bool:
    """Block counter-trend setups: a SHORT against a 50-day uptrend, or LONG against a downtrend.

    Compares closes[-1] to closes[-lookback]. If the long-horizon move opposes
    the immediate HTF swing direction, return False (reject).
    """
    if lookback <= 0 or len(closes) < lookback + 1:
        return True  # not enough history → fail-open
    recent = float(closes[-1])
    older = float(closes[-lookback])
    if direction == "up":
        return recent >= older
    return recent <= older


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

    if p.trend_filter_enabled and not trend_aligned(
        direction, htf_candles["close"], p.trend_filter_lookback
    ):
        return FibSignal(
            action="NONE",
            reason="trend_filter_reject",
            htf_swing={"a": a_px, "b": b_px, "direction": direction},
        )

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


# =============================================================================
# 3-tier nested fib strategy (mega → major → minor on same direction)
# =============================================================================
def aggregate_candles(candles: dict[str, Any], factor: int) -> dict[str, Any]:
    """Roll up `factor` adjacent bars into one (e.g. 1h × 4 → 4h).

    Drops the trailing partial group so we never emit a half-formed bar.
    """
    closes = candles.get("close") or []
    n_groups = len(closes) // factor
    if n_groups == 0:
        return {"open": [], "high": [], "low": [], "close": [], "volume": []}
    o, h, l, c, v = [], [], [], [], []
    opens = candles["open"]
    highs = candles["high"]
    lows = candles["low"]
    vols = candles.get("volume", [0.0] * len(closes))
    for i in range(n_groups):
        s = i * factor
        e = s + factor
        o.append(opens[s])
        c.append(closes[e - 1])
        h.append(max(highs[s:e]))
        l.append(min(lows[s:e]))
        v.append(sum(vols[s:e]))
    return {"open": o, "high": h, "low": l, "close": c, "volume": v}


def _latest_swing_in_direction(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    direction: str,
    atr_depth: float,
) -> tuple[str, int, int, float, float] | None:
    """Find the most recent swing in a specific direction (pro-trend leg).

    For "up": (a=swing-low, b=swing-high) where high is more recent.
    For "down": (a=swing-high, b=swing-low) where low is more recent.
    """
    cfg = FibonacciConfig(atr_depth=atr_depth)
    high_idx, low_idx, high_px, low_px = detect_swing_points(highs, lows, closes, cfg)
    if not high_idx or not low_idx:
        return None
    if direction == "up":
        last_high_idx = high_idx[-1]
        last_high_px = high_px[-1]
        earlier_lows = [(li, lp) for li, lp in zip(low_idx, low_px) if li < last_high_idx]
        if not earlier_lows:
            return None
        l_idx, l_px = earlier_lows[-1]
        return ("up", l_idx, last_high_idx, float(l_px), float(last_high_px))
    last_low_idx = low_idx[-1]
    last_low_px = low_px[-1]
    earlier_highs = [(hi, hp) for hi, hp in zip(high_idx, high_px) if hi < last_low_idx]
    if not earlier_highs:
        return None
    h_idx, h_px = earlier_highs[-1]
    return ("down", h_idx, last_low_idx, float(h_px), float(last_low_px))


def _zones_overlap_at_price(zones: list[dict[str, float]], price: float) -> bool:
    return all(z["low"] <= price <= z["high"] for z in zones)


def _zones_intersection(zones: list[dict[str, float]]) -> dict[str, float] | None:
    if not zones:
        return None
    lo = max(z["low"] for z in zones)
    hi = min(z["high"] for z in zones)
    if lo > hi:
        return None
    return {"low": lo, "high": hi}


def compute_signal_nested(
    mega_candles: dict[str, Any],
    major_candles: dict[str, Any],
    minor_candles: dict[str, Any],
    params: FibStrategyParams | None = None,
    *,
    equity_usd: float = 0.0,
    risk_pct: float = 0.01,
) -> FibSignal:
    """3-tier nested fib confluence strategy.

    All three swings (mega/major/minor) must be in the same direction. Entry
    happens when the current price sits inside all three retracement zones
    simultaneously (confluence) and a confirmation candle prints in the
    trend direction.
    """
    p = params or FibStrategyParams()
    if (
        not _validate_candles(mega_candles)
        or not _validate_candles(major_candles)
        or not _validate_candles(minor_candles)
    ):
        return _none("insufficient_candles")

    mega_swing = _latest_swing(
        mega_candles["high"], mega_candles["low"], mega_candles["close"],
        p.resolve_mega_atr(),
    )
    if mega_swing is None:
        return _none("no_mega_swing")
    direction, _, _, mega_a, mega_b = mega_swing

    if p.trend_filter_enabled and not trend_aligned(
        direction, mega_candles["close"], p.trend_filter_lookback
    ):
        return FibSignal(
            action="NONE",
            reason="trend_filter_reject",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
        )

    mega_zone = _retracement_zone(direction, mega_a, mega_b, p.entry_zone_low, p.entry_zone_high)

    last_close_minor = float(minor_candles["close"][-1])
    if p.mega_zone_touch_required and not (
        mega_zone["low"] <= last_close_minor <= mega_zone["high"]
    ):
        return FibSignal(
            action="NONE",
            reason="no_mega_zone_touch",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
        )

    major_swing = _latest_swing_in_direction(
        major_candles["high"], major_candles["low"], major_candles["close"],
        direction, p.resolve_major_atr(),
    )
    if major_swing is None:
        return FibSignal(
            action="NONE", reason="no_major_swing",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
        )
    _, _, _, major_a, major_b = major_swing
    major_zone = _retracement_zone(direction, major_a, major_b, p.entry_zone_low, p.entry_zone_high)

    if not (major_zone["low"] <= last_close_minor <= major_zone["high"]):
        return FibSignal(
            action="NONE", reason="no_major_zone_touch",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
            ltf_swing={"a": major_a, "b": major_b, "direction": direction},
            ltf_zone=major_zone,
        )

    minor_swing = _latest_swing_in_direction(
        minor_candles["high"], minor_candles["low"], minor_candles["close"],
        direction, p.resolve_minor_atr(),
    )
    if minor_swing is None:
        return FibSignal(
            action="NONE", reason="no_minor_swing",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
        )
    _, _, _, minor_a, minor_b = minor_swing
    minor_zone = _retracement_zone(direction, minor_a, minor_b, p.entry_zone_low, p.entry_zone_high)

    if not (minor_zone["low"] <= last_close_minor <= minor_zone["high"]):
        return FibSignal(
            action="NONE", reason="no_minor_zone_touch",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
            ltf_swing={"a": minor_a, "b": minor_b, "direction": direction},
            ltf_zone=minor_zone,
        )

    if p.confluence_required:
        # When mega zone-touch is not required, mega-zone may not contain the
        # current price; only check confluence on the zones that ARE required.
        confluence_zones = [major_zone, minor_zone]
        if p.mega_zone_touch_required:
            confluence_zones.insert(0, mega_zone)
        if not _zones_overlap_at_price(confluence_zones, last_close_minor):
            return FibSignal(
                action="NONE", reason="no_confluence",
                htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
                htf_zone=mega_zone,
                ltf_swing={"a": minor_a, "b": minor_b, "direction": direction},
                ltf_zone=minor_zone,
            )

    if p.require_confirmation and not _is_confirmation_candle(
        direction, minor_candles["open"], minor_candles["close"]
    ):
        return FibSignal(
            action="NONE", reason="no_confirmation",
            htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
            htf_zone=mega_zone,
            ltf_swing={"a": minor_a, "b": minor_b, "direction": direction},
            ltf_zone=minor_zone,
        )

    entry = last_close_minor
    if direction == "up":
        stop = float(min(minor_a, minor_zone["low"]))
    else:
        stop = float(max(minor_a, minor_zone["high"]))
    stop_distance = abs(entry - stop)
    if stop_distance <= 0.0:
        return _none("invalid_stop_distance")

    # Targets at MAJOR fib-extension (closer than mega; more reachable)
    extension_prices = _extension_prices(direction, major_a, major_b, p.extension_levels)
    targets: list[dict[str, Any]] = []
    fractions = list(p.target_fractions)
    for level, price, frac in zip(p.extension_levels, extension_prices, fractions[:-1]):
        targets.append({"level": float(level), "price": float(price), "fraction": float(frac)})
    targets.append({"level": "trailing", "fraction": float(fractions[-1])})

    size: float | None = None
    if equity_usd > 0 and risk_pct > 0:
        size = (equity_usd * risk_pct) / stop_distance

    action = "LONG" if direction == "up" else "SHORT"
    return FibSignal(
        action=action,
        reason="nested_confluence_confirmation",
        htf_swing={"a": mega_a, "b": mega_b, "direction": direction},
        htf_zone=mega_zone,
        ltf_swing={"a": minor_a, "b": minor_b, "direction": direction},
        ltf_zone=minor_zone,
        entry=entry,
        stop=stop,
        targets=targets,
        size=size,
    )
