from __future__ import annotations


def daily_pnl_usd(baseline_equity_usd: float, current_equity_usd: float) -> float:
    """Beräkna dagens PnL i USD som current - baseline.

    Baslinjen avser equity vid dagens start; justera upstream om insättningar/uttag sker.
    """
    return float(current_equity_usd - baseline_equity_usd)


def breached_daily_loss(
    baseline_equity_usd: float,
    current_equity_usd: float,
    *,
    max_abs_loss_usd: float | None = None,
    max_loss_pct: float | None = None,
) -> bool:
    """True om dagens PnL underskrider max tillåten förlust (absolut eller procent).

    Minsta konfiguration: ange antingen max_abs_loss_usd eller max_loss_pct.
    Om båda anges triggar breach när någon av dem bryts (OR).
    """
    pnl = daily_pnl_usd(baseline_equity_usd, current_equity_usd)
    breaches = []
    if max_abs_loss_usd is not None:
        breaches.append(pnl <= -abs(max_abs_loss_usd))
    if max_loss_pct is not None and baseline_equity_usd > 0:
        threshold = -abs(max_loss_pct) / 100.0 * baseline_equity_usd
        breaches.append(pnl <= threshold)
    return any(breaches) if breaches else False
