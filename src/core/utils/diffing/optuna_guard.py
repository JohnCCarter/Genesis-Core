"""
Optuna guard utilities for detecting potentially problematic trial configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ZeroTradeEstimate:
    """Result of zero-trade estimation check."""
    
    ok: bool
    reason: str | None = None


def estimate_zero_trade(parameters: dict[str, Any]) -> ZeroTradeEstimate:
    """
    Estimate if parameters will likely result in zero trades.
    
    This is a preflight check to avoid running expensive backtests for
    configurations that are extremely unlikely to generate any trades.
    
    Args:
        parameters: Trial parameters to check
        
    Returns:
        ZeroTradeEstimate with ok=True if config looks reasonable,
        or ok=False with reason if it's likely to produce zero trades
    """
    # Check for extremely conservative entry thresholds
    entry_min = parameters.get("thresholds", {}).get("entry_min_confidence", 0.0)
    if entry_min > 0.99:
        return ZeroTradeEstimate(
            ok=False,
            reason=f"entry_min_confidence too high: {entry_min:.3f} (likely no entries)"
        )
    
    # Check for contradictory regime filters
    regime_cfg = parameters.get("gates", {}).get("regime", {})
    if regime_cfg.get("require_bullish") and regime_cfg.get("require_bearish"):
        return ZeroTradeEstimate(
            ok=False,
            reason="Cannot require both bullish and bearish regime simultaneously"
        )
    
    # Check for zero position sizing
    risk_cfg = parameters.get("risk", {})
    default_r = risk_cfg.get("R_default", 1.0)
    if default_r <= 0:
        return ZeroTradeEstimate(
            ok=False,
            reason=f"R_default must be positive, got {default_r}"
        )
    
    # All checks passed
    return ZeroTradeEstimate(ok=True, reason=None)


__all__ = ["ZeroTradeEstimate", "estimate_zero_trade"]
