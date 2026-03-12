"""
Traditional exit condition checks for BacktestEngine.

Extracted from engine.py — no behavior change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.backtest.position_tracker import PositionTracker


def check_traditional_exit_conditions(
    position_tracker: PositionTracker,
    current_price: float,
    result: dict,
    configs: dict,
) -> str | None:
    """Fallback traditional exit conditions."""
    position = position_tracker.position

    # Get exit config (top-level in merged configs)
    exit_cfg = configs.get("exit", {})
    stop_loss_pct = float(exit_cfg.get("stop_loss_pct", 0.02))
    take_profit_pct = float(exit_cfg.get("take_profit_pct", 0.05))
    exit_conf_threshold = float(exit_cfg.get("exit_conf_threshold", 0.45))

    # Emergency stop-loss
    pnl_pct = position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
    if pnl_pct <= -stop_loss_pct:
        return "EMERGENCY_SL"

    # Emergency take-profit (for very large moves)
    if pnl_pct >= take_profit_pct * 2:  # 2x normal TP
        return "EMERGENCY_TP"

    # Confidence drop (use direction-aware confidence if dict)
    conf_block = result.get("confidence_exit", result.get("confidence", 1.0))
    if isinstance(conf_block, dict):
        # Prefer confidence in the direction of the open position
        if position.side == "LONG":
            conf_value = float(conf_block.get("buy", conf_block.get("overall", 1.0) or 1.0))
        else:
            conf_value = float(conf_block.get("sell", conf_block.get("overall", 1.0) or 1.0))
    else:
        try:
            conf_value = float(conf_block)
        except Exception:
            conf_value = 1.0
    if conf_value < exit_conf_threshold:
        return "CONF_DROP"

    # Regime change
    regime = result.get("regime", "NEUTRAL")
    if position.side == "SHORT" and regime == "BULL":
        return "REGIME_CHANGE"
    if position.side == "LONG" and regime == "BEAR":
        return "REGIME_CHANGE"

    return None
