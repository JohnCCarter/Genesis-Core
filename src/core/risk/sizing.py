from __future__ import annotations

from typing import Final


def capped_position_size(
    account_equity_usd: float,
    risk_fraction: float,
    position_cap_pct: float,
) -> float:
    """Beräkna positionsstorlek som min(account_equity*risk_fraction, cap).

    - account_equity_usd: total kontovärde i USD
    - risk_fraction: andel av equity per trade (t.ex. 0.01)
    - position_cap_pct: hårt cap (% av equity), t.ex. 20 => 0.2
    """
    if account_equity_usd <= 0:
        return 0.0
    if risk_fraction <= 0:
        return 0.0
    cap: Final[float] = (
        max(0.0, min(1.0, position_cap_pct / 100.0)) * account_equity_usd
    )
    desired = account_equity_usd * risk_fraction
    return float(min(desired, cap))
