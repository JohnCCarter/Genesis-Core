from __future__ import annotations

import math

from core.risk.guards import breached_max_drawdown, within_daily_loss_limit


def test_breached_max_drawdown_basic():
    # peak 1000, current 850 => drop 15%
    assert breached_max_drawdown(1000.0, 850.0, 10.0) is True
    # peak 1000, current 900 => drop 10% < 15% => inte bruten
    assert breached_max_drawdown(1000.0, 900.0, 15.0) is False
    assert breached_max_drawdown(1000.0, 900.0, 20.0) is False


def test_within_daily_loss_limit():
    # limit 100 => ok down to -100
    assert within_daily_loss_limit(0.0, 100.0) is True
    assert within_daily_loss_limit(-50.0, 100.0) is True
    assert within_daily_loss_limit(-100.0, 100.0) is True
    assert within_daily_loss_limit(-100.01, 100.0) is False
