from __future__ import annotations


def breached_max_drawdown(
    equity_peak_usd: float, current_equity_usd: float, max_dd_pct: float
) -> bool:
    if equity_peak_usd <= 0:
        return False
    drop_pct = (
        (equity_peak_usd - max(current_equity_usd, 0.0)) / equity_peak_usd * 100.0
    )
    return drop_pct >= max(0.0, max_dd_pct)


def within_daily_loss_limit(daily_pnl_usd: float, max_daily_loss_usd: float) -> bool:
    return daily_pnl_usd >= -abs(max_daily_loss_usd)
