from __future__ import annotations

import asyncio
from typing import Any

import pytest

from core.agent.decision_record import DecisionRecord, append_decision


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_read_candles_rejects_unknown_timeframe(mcp_config) -> None:
    from mcp_server.trading_tools import read_candles

    result = _run(read_candles("tBTCUSD", "4h", 100, mcp_config))
    assert result["success"] is False
    assert result["error"] == "invalid_timeframe"


def test_read_candles_uses_public_candles(mcp_config, monkeypatch) -> None:
    from core.api import public as public_mod

    canned = {
        "open": [1.0, 2.0],
        "high": [1.1, 2.1],
        "low": [0.9, 1.9],
        "close": [1.05, 2.05],
        "volume": [10.0, 11.0],
    }

    async def fake_candles(symbol: str = "tBTCUSD", timeframe: str = "1m", limit: int = 120):
        return canned

    monkeypatch.setattr(public_mod, "public_candles", fake_candles)

    from mcp_server.trading_tools import read_candles

    result = _run(read_candles("tBTCUSD", "1h", 100, mcp_config))
    assert result["success"] is True
    assert result["close"] == [1.05, 2.05]
    assert result["timeframe"] == "1h"


def test_run_strategy_persists_record(
    mcp_config, monkeypatch, tmp_log_path, htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    from mcp_server.trading_tools import run_strategy

    result = _run(
        run_strategy(
            "tBTCUSD",
            "6h",
            "1h",
            mcp_config,
            htf_candles=htf_uptrend_pullback,
            ltf_candles=ltf_uptrend_pullback,
            risk_state={"current_equity_usd": 5000.0},
            persist=True,
        )
    )
    assert result["success"] is True, result
    assert "record" in result
    assert tmp_log_path.exists()


def test_run_strategy_persist_false(
    mcp_config, tmp_log_path, htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    from mcp_server.trading_tools import run_strategy

    result = _run(
        run_strategy(
            "tBTCUSD",
            "6h",
            "1h",
            mcp_config,
            htf_candles=htf_uptrend_pullback,
            ltf_candles=ltf_uptrend_pullback,
            persist=False,
        )
    )
    assert result["success"] is True
    assert not tmp_log_path.exists()


def test_run_strategy_rejects_invalid_timeframe(mcp_config) -> None:
    from mcp_server.trading_tools import run_strategy

    result = _run(run_strategy("tBTCUSD", "4h", "1h", mcp_config))
    assert result["success"] is False


def test_submit_paper_order_invalid_side(mcp_config) -> None:
    from mcp_server.trading_tools import submit_paper_order

    result = _run(submit_paper_order("tTESTBTC:TESTUSD", "BUY", 0.001, mcp_config))
    assert result["success"] is False
    assert result["error"] == "invalid_side"


def test_submit_paper_order_invalid_size(mcp_config) -> None:
    from mcp_server.trading_tools import submit_paper_order

    result = _run(submit_paper_order("tTESTBTC:TESTUSD", "LONG", 0.0, mcp_config))
    assert result["success"] is False
    assert result["error"] == "invalid_size"


def test_submit_paper_order_calls_paper_submit(mcp_config, monkeypatch) -> None:
    from core.api import paper as paper_mod

    captured: dict[str, Any] = {}

    async def fake_submit(payload: dict) -> dict:
        captured["payload"] = payload
        return {"ok": True, "exchange": "bitfinex", "request": payload, "response": {"id": 1}}

    monkeypatch.setattr(paper_mod, "paper_submit", fake_submit)

    from mcp_server.trading_tools import submit_paper_order

    result = _run(
        submit_paper_order("tTESTBTC:TESTUSD", "LONG", 0.001, mcp_config, force=True)
    )
    assert result["success"] is True
    assert result["submission"]["submitted"] is True
    assert captured["payload"]["side"] == "LONG"


def test_submit_paper_order_blocks_when_risk_failed(
    mcp_config, monkeypatch, tmp_log_path
) -> None:
    record = DecisionRecord(
        ts_utc="2026-05-07T00:00:00+00:00",
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        candles_hash={"htf": "h1", "ltf": "l1"},
        params_hash="p1",
        fib_signal={"action": "LONG"},
        risk_check={"passed": False, "reasons": ["daily_loss_breached"]},
    )
    append_decision(record)

    async def fake_submit(payload: dict) -> dict:
        raise AssertionError("paper_submit should not be called when risk blocked")

    from core.api import paper as paper_mod

    monkeypatch.setattr(paper_mod, "paper_submit", fake_submit)

    from mcp_server.trading_tools import submit_paper_order

    result = _run(
        submit_paper_order(
            "tTESTBTC:TESTUSD",
            "LONG",
            0.001,
            mcp_config,
            decision_id=record.decision_id,
        )
    )
    assert result["success"] is False
    assert result["error"] == "risk_blocked"


def test_submit_paper_order_force_overrides_block(
    mcp_config, monkeypatch, tmp_log_path
) -> None:
    record = DecisionRecord(
        ts_utc="2026-05-07T00:00:00+00:00",
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        candles_hash={"htf": "h1", "ltf": "l1"},
        params_hash="p1",
        fib_signal={"action": "LONG"},
        risk_check={"passed": False, "reasons": ["daily_loss_breached"]},
    )
    append_decision(record)

    calls: list[dict] = []

    async def fake_submit(payload: dict) -> dict:
        calls.append(payload)
        return {"ok": True, "request": payload, "response": {}}

    from core.api import paper as paper_mod

    monkeypatch.setattr(paper_mod, "paper_submit", fake_submit)

    from mcp_server.trading_tools import submit_paper_order

    result = _run(
        submit_paper_order(
            "tTESTBTC:TESTUSD",
            "LONG",
            0.001,
            mcp_config,
            decision_id=record.decision_id,
            force=True,
        )
    )
    assert result["success"] is True
    assert len(calls) == 1
    assert result["submission"]["force"] is True


def test_append_decision_log_validates_required_fields(mcp_config, tmp_log_path) -> None:
    from mcp_server.trading_tools import append_decision_log

    bad = _run(append_decision_log({"symbol": "tBTCUSD"}, mcp_config))
    assert bad["success"] is False
    assert bad["error"] == "missing_fields"


def test_append_decision_log_accepts_complete_record(mcp_config, tmp_log_path) -> None:
    from mcp_server.trading_tools import append_decision_log

    record = {
        "symbol": "tBTCUSD",
        "trend_tf": "6h",
        "entry_tf": "1h",
        "fib_signal": {"action": "NONE", "reason": "manual_marker"},
        "risk_check": {"passed": True, "reasons": []},
    }
    out = _run(append_decision_log(record, mcp_config))
    assert out["success"] is True
    assert tmp_log_path.exists()


def test_read_decision_log_filters_by_symbol(mcp_config, tmp_log_path) -> None:
    from mcp_server.trading_tools import read_decision_log

    rec_btc = DecisionRecord(
        ts_utc="2026-05-07T00:00:00+00:00",
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        candles_hash={"htf": "h1", "ltf": "l1"},
        params_hash="p1",
        fib_signal={"action": "LONG"},
        risk_check={"passed": True, "reasons": []},
    )
    rec_eth = DecisionRecord(
        ts_utc="2026-05-07T00:00:00+00:00",
        symbol="tETHUSD",
        trend_tf="6h",
        entry_tf="1h",
        candles_hash={"htf": "h1", "ltf": "l1"},
        params_hash="p1",
        fib_signal={"action": "SHORT"},
        risk_check={"passed": True, "reasons": []},
    )
    append_decision(rec_btc)
    append_decision(rec_eth)

    result = _run(read_decision_log(mcp_config, symbol="tBTCUSD"))
    assert result["success"] is True
    assert all(r["symbol"] == "tBTCUSD" for r in result["records"])
