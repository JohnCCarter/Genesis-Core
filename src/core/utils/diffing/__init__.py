"""
Diffing utilities for comparing backtest results and metrics.
"""

from __future__ import annotations

from typing import Any


def summarize_metrics_diff(metrics_diff: dict[str, Any]) -> str:
    """
    Generate a human-readable summary of metric differences.
    
    Args:
        metrics_diff: Dictionary with metric name as key and delta information
        
    Returns:
        Human-readable summary string, or empty string if no significant changes
    """
    if not metrics_diff:
        return ""
    
    lines = []
    for metric_name, delta_info in sorted(metrics_diff.items()):
        if isinstance(delta_info, dict):
            old_val = delta_info.get("old")
            new_val = delta_info.get("new")
            delta = delta_info.get("delta")
            
            if delta is not None and abs(delta) > 1e-9:
                change_pct = ""
                if old_val is not None and abs(old_val) > 1e-9:
                    pct = (delta / old_val) * 100
                    change_pct = f" ({pct:+.1f}%)"
                lines.append(f"  {metric_name}: {old_val:.4f} → {new_val:.4f} (Δ{delta:+.4f}){change_pct}")
    
    return "\n".join(lines) if lines else ""


__all__ = ["summarize_metrics_diff"]
