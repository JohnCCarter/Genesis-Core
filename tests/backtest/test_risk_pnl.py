from __future__ import annotations

from core.risk.pnl import breached_daily_loss, daily_pnl_usd


def test_daily_pnl_usd():
    assert daily_pnl_usd(1000.0, 1050.0) == 50.0
    assert daily_pnl_usd(1000.0, 950.0) == -50.0


def test_breached_daily_loss_abs_and_pct():
    # Absolut loss
    assert breached_daily_loss(1000.0, 900.0, max_abs_loss_usd=50.0) is True
    assert breached_daily_loss(1000.0, 960.0, max_abs_loss_usd=50.0) is False

    # Procentuell loss
    assert breached_daily_loss(1000.0, 850.0, max_loss_pct=10.0) is True  # -15% <= -10%
    assert breached_daily_loss(1000.0, 950.0, max_loss_pct=10.0) is False  # -5% > -10%

    # OR-logik när båda anges
    assert breached_daily_loss(1000.0, 940.0, max_abs_loss_usd=100.0, max_loss_pct=3.0) is True
