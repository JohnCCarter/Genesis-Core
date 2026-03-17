from __future__ import annotations

from typing import Any


def compute_risk_state_multiplier(
    *,
    cfg: dict[str, Any],
    equity_drawdown_pct: float,
    bars_since_regime_change: int,
) -> dict[str, Any]:
    """Compute position size multiplier based on current RI risk state."""
    if not cfg or not bool(cfg.get("enabled", False)):
        return {
            "enabled": False,
            "multiplier": 1.0,
            "drawdown_mult": 1.0,
            "transition_mult": 1.0,
            "equity_drawdown_pct": equity_drawdown_pct,
            "bars_since_regime_change": bars_since_regime_change,
        }

    dd_cfg = dict(cfg.get("drawdown_guard") or {})
    soft_thr = float(dd_cfg.get("soft_threshold", 0.03))
    hard_thr = float(dd_cfg.get("hard_threshold", 0.06))
    soft_mult = float(dd_cfg.get("soft_mult", 0.70))
    hard_mult = float(dd_cfg.get("hard_mult", 0.40))

    dd = float(equity_drawdown_pct)
    if dd <= 0.0:
        drawdown_mult = 1.0
    elif dd >= hard_thr:
        drawdown_mult = hard_mult
    elif dd >= soft_thr:
        t = (dd - soft_thr) / max(hard_thr - soft_thr, 1e-9)
        drawdown_mult = soft_mult + t * (hard_mult - soft_mult)
    else:
        t = dd / max(soft_thr, 1e-9)
        drawdown_mult = 1.0 + t * (soft_mult - 1.0)

    tr_cfg = dict(cfg.get("transition_guard") or {})
    transition_mult = 1.0
    if bool(tr_cfg.get("enabled", True)):
        guard_bars = int(tr_cfg.get("guard_bars", 4))
        if 0 < bars_since_regime_change <= guard_bars:
            transition_mult = float(tr_cfg.get("mult", 0.60))

    multiplier = max(0.05, min(1.0, drawdown_mult * transition_mult))

    return {
        "enabled": True,
        "multiplier": multiplier,
        "drawdown_mult": drawdown_mult,
        "transition_mult": transition_mult,
        "equity_drawdown_pct": dd,
        "bars_since_regime_change": bars_since_regime_change,
    }
