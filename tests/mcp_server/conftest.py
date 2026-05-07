from __future__ import annotations

import math
from typing import Any

import pytest


def _build_candles(
    closes: list[float],
    *,
    high_offset: float = 50.0,
    low_offset: float = 50.0,
) -> dict[str, Any]:
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + high_offset for o, c in zip(opens, closes)]
    lows = [min(o, c) - low_offset for o, c in zip(opens, closes)]
    volumes = [10.0] * len(closes)
    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


@pytest.fixture()
def htf_uptrend_pullback() -> dict[str, Any]:
    """Synthetic HTF series: rises from 40000 to 50000, then pulls back into 0.5–0.618 zone."""
    n_up = 80
    closes = [40000.0 + (10000.0 / (n_up - 1)) * i for i in range(n_up)]
    n_down = 40
    peak = closes[-1]
    target = 50000.0 - 0.55 * (50000.0 - 40000.0)
    closes += [peak - ((peak - target) / (n_down - 1)) * i for i in range(1, n_down)]
    return _build_candles(closes, high_offset=80.0, low_offset=80.0)


@pytest.fixture()
def ltf_uptrend_pullback() -> dict[str, Any]:
    """Synthetic LTF series with a small pullback inside the HTF zone, then a green confirm.

    Target the confirmation close to land mid-LTF-zone (≈0.55 retrace UP from the LTF low).
    """
    base = 50000.0 - 0.55 * (50000.0 - 40000.0)
    closes: list[float] = []
    n_up = 30
    for i in range(n_up):
        closes.append(base + 200.0 + (300.0 / (n_up - 1)) * i)
    n_down = 25
    peak = closes[-1]
    bottom = base - 50.0
    for i in range(1, n_down):
        closes.append(peak - ((peak - bottom) / (n_down - 1)) * i)
    n_confirm = 10
    last = closes[-1]
    # Mid of LTF 0.5–0.618 zone, anchored on LTF low/high (not HTF base)
    target = bottom + 0.55 * (peak - bottom)
    for i in range(1, n_confirm):
        closes.append(last + ((target - last) / (n_confirm - 1)) * i)
    return _build_candles(closes, high_offset=40.0, low_offset=40.0)


@pytest.fixture()
def htf_downtrend_pullback() -> dict[str, Any]:
    n_down = 80
    closes = [50000.0 - (10000.0 / (n_down - 1)) * i for i in range(n_down)]
    n_up = 40
    bottom = closes[-1]
    target = 40000.0 + 0.55 * (50000.0 - 40000.0)
    closes += [bottom + ((target - bottom) / (n_up - 1)) * i for i in range(1, n_up)]
    return _build_candles(closes, high_offset=80.0, low_offset=80.0)


@pytest.fixture()
def ltf_downtrend_pullback() -> dict[str, Any]:
    """LTF up-leg followed by a red-confirm retrace mid-LTF-zone."""
    base = 40000.0 + 0.55 * (50000.0 - 40000.0)
    closes: list[float] = []
    n_down = 30
    for i in range(n_down):
        closes.append(base - 200.0 - (300.0 / (n_down - 1)) * i)
    n_up = 25
    bottom = closes[-1]
    top = base + 50.0
    for i in range(1, n_up):
        closes.append(bottom + ((top - bottom) / (n_up - 1)) * i)
    n_confirm = 10
    last = closes[-1]
    # Mid of LTF 0.5–0.618 zone, anchored on LTF top (retrace DOWN from top)
    target = top - 0.55 * (top - bottom)
    for i in range(1, n_confirm):
        closes.append(last + ((target - last) / (n_confirm - 1)) * i)
    return _build_candles(closes, high_offset=40.0, low_offset=40.0)


@pytest.fixture()
def flat_candles() -> dict[str, Any]:
    closes = [50000.0 + math.sin(i * 0.1) * 5.0 for i in range(120)]
    return _build_candles(closes, high_offset=20.0, low_offset=20.0)


@pytest.fixture()
def tmp_log_path(tmp_path, monkeypatch):
    """Redirect agent_decisions.jsonl writes to a temporary file."""
    log_file = tmp_path / "agent_decisions.jsonl"
    from core.agent import decision_record as dr_mod

    monkeypatch.setattr(dr_mod, "DEFAULT_LOG_PATH", log_file)
    from mcp_server import trading_tools as tt_mod

    monkeypatch.setattr(tt_mod, "DEFAULT_LOG_PATH", log_file)
    return log_file


@pytest.fixture()
def mcp_config():
    from mcp_server.config import MCPConfig

    return MCPConfig()
