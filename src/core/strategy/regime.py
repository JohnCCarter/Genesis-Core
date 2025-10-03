from __future__ import annotations

from typing import Any, Literal

Regime = Literal["trend", "range", "balanced"]


def classify_regime(
    htf_features: dict[str, float],
    *,
    prev_state: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[Regime, dict[str, Any]]:
    """Klassificera regim (pure) utifrån HTF‑features med hysteresis.

    htf_features: {"adx_norm", "atr_pct", "ema_slope"}
    Hysteresis: kräv N på varandra följande observationer för regimskifte.
    """
    adx = float(htf_features.get("adx_norm", 0.0))
    # atr_pct = float(htf_features.get("atr_pct", 0.0))  # TODO: Implement ATR-based regime logic
    ema_slope = float(htf_features.get("ema_slope", 0.0))

    cfg = dict(config or {})
    hysteresis_steps = int((cfg.get("gates") or {}).get("hysteresis_steps") or 2)

    # Enkel heuristik: stark trend om hög adx och lutning ≠ 0; range annars.
    candidate: Regime
    if adx >= 0.5 and abs(ema_slope) > 0.0:
        candidate = "trend"
    elif adx <= 0.2 and abs(ema_slope) < 0.005:
        candidate = "range"
    else:
        candidate = "balanced"

    ps = dict(prev_state or {})
    current = ps.get("regime", "balanced")
    steps = int(ps.get("steps", 0))

    if candidate == current:
        steps = 0
        regime = current  # type: ignore[assignment]
    else:
        steps += 1
        if steps >= hysteresis_steps:
            regime = candidate
            steps = 0
        else:
            regime = current  # hold tills hysteresis uppfylls

    state: dict[str, Any] = {"regime": regime, "steps": steps}
    return regime, state
