"""MCP tools for the Bitfinex paper-trading agent (research-evidence lane).

All handlers are async and return ``{"success": bool, ...}``.

Strategy logic lives in ``src.core.agent.fib_strategy`` /
``src.core.agent.agent_runtime``. These tools are intentionally thin shims so
that a future WebSocket scheduler can call the same underlying functions
directly without the MCP layer.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Genesis-Core uses src-layout. Ensure src/ is importable when running the MCP
# server as ``python -m mcp_server.server`` (without installing the package).
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core.agent.agent_runtime import evaluate_and_record  # noqa: E402
from core.agent.decision_record import (  # noqa: E402
    DEFAULT_LOG_PATH,
    SCHEMA_VERSION,
    DecisionRecord,
    append_decision,
    append_followup,
    find_decision,
    read_decisions,
)

from .config import MCPConfig  # noqa: E402

ALLOWED_TIMEFRAMES = {
    "1m",
    "5m",
    "15m",
    "30m",
    "1h",
    "3h",
    "6h",
    "12h",
    "1D",
    "1W",
    "14D",
    "1M",
}

MAX_CANDLES = 1000
MAX_LOG_LIMIT = 500


def _err(msg: str, **extra: Any) -> dict[str, Any]:
    return {"success": False, "error": msg, **extra}


async def read_account_state(config: MCPConfig) -> dict[str, Any]:
    """Read Bitfinex wallets, positions, and open orders.

    Returns empty lists when API credentials are missing instead of raising —
    this keeps the tool usable for inspection without auth.
    """
    try:
        from core.config.settings import get_settings
        from core.io.bitfinex import read_helpers as bfx_read
    except Exception as exc:  # pragma: no cover - import-only path
        return _err(f"import_failed: {exc}")

    try:
        settings = get_settings()
    except Exception as exc:
        return _err(f"settings_unavailable: {exc}")

    has_keys = bool(getattr(settings, "BITFINEX_API_KEY", None)) and bool(
        getattr(settings, "BITFINEX_API_SECRET", None)
    )
    if not has_keys:
        return {
            "success": True,
            "wallets": [],
            "positions": [],
            "orders": [],
            "usd_available": 0.0,
            "equity_estimate_usd": 0.0,
            "note": "no_api_keys_configured",
        }

    wallets_raw: Any = []
    positions_raw: Any = []
    orders_raw: Any = []
    try:
        wallets_raw = await bfx_read.get_wallets()
    except Exception as exc:
        logger.warning("get_wallets failed: %s", exc)
    try:
        positions_raw = await bfx_read.get_positions()
    except Exception as exc:
        logger.warning("get_positions failed: %s", exc)
    try:
        orders_raw = await bfx_read.get_orders()
    except Exception as exc:
        logger.warning("get_orders failed: %s", exc)

    wallets: list[dict[str, Any]] = []
    usd_available = 0.0
    equity_estimate = 0.0
    if isinstance(wallets_raw, list):
        for row in wallets_raw:
            if isinstance(row, list) and len(row) >= 5:
                wtype = str(row[0])
                ccy = str(row[1]).upper()
                balance = float(row[2] or 0.0)
                available = float(row[4] or 0.0)
                wallets.append(
                    {
                        "type": wtype,
                        "currency": ccy,
                        "balance": balance,
                        "available": available,
                    }
                )
                if ccy in {"USD", "TESTUSD"}:
                    usd_available += max(0.0, available)
                    equity_estimate += max(0.0, balance)

    positions: list[dict[str, Any]] = []
    if isinstance(positions_raw, list):
        for row in positions_raw:
            if isinstance(row, list) and len(row) >= 4:
                positions.append(
                    {
                        "symbol": str(row[0]),
                        "status": str(row[1]) if len(row) > 1 else None,
                        "amount": float(row[2] or 0.0),
                        "base_price": float(row[3]) if row[3] is not None else None,
                    }
                )

    orders: list[dict[str, Any]] = []
    if isinstance(orders_raw, list):
        for row in orders_raw:
            if isinstance(row, list) and len(row) >= 4:
                orders.append({"id": row[0], "symbol": str(row[3])})

    return {
        "success": True,
        "wallets": wallets,
        "positions": positions,
        "orders": orders,
        "usd_available": usd_available,
        "equity_estimate_usd": equity_estimate,
    }


async def read_candles(
    symbol: str,
    timeframe: str,
    limit: int,
    config: MCPConfig,
) -> dict[str, Any]:
    if not symbol:
        return _err("missing_symbol")
    if timeframe not in ALLOWED_TIMEFRAMES:
        return _err(
            "invalid_timeframe",
            allowed=sorted(ALLOWED_TIMEFRAMES),
        )
    safe_limit = max(1, min(int(limit or 300), MAX_CANDLES))
    try:
        from core.api.public import public_candles
    except Exception as exc:  # pragma: no cover
        return _err(f"import_failed: {exc}")
    try:
        data = await public_candles(symbol=symbol, timeframe=timeframe, limit=safe_limit)
    except Exception as exc:
        return _err(f"candles_fetch_failed: {exc}")
    return {"success": True, "symbol": symbol, "timeframe": timeframe, **data}


async def run_strategy(
    symbol: str,
    trend_tf: str,
    entry_tf: str,
    config: MCPConfig,
    *,
    htf_candles: dict[str, Any] | None = None,
    ltf_candles: dict[str, Any] | None = None,
    mid_candles: dict[str, Any] | None = None,
    mid_tf: str | None = None,
    params: dict[str, Any] | None = None,
    risk_state: dict[str, Any] | None = None,
    risk_pct: float = 0.01,
    persist: bool = True,
    candle_limit: int = 300,
) -> dict[str, Any]:
    """Evaluate the fib agent.

    If mid_tf is provided (e.g. native "6h"), runs the 3-tier
    nested-confluence strategy. Otherwise falls back to 2-tier.
    """
    if not symbol:
        return _err("missing_symbol")
    if trend_tf not in ALLOWED_TIMEFRAMES or entry_tf not in ALLOWED_TIMEFRAMES:
        return _err("invalid_timeframe", allowed=sorted(ALLOWED_TIMEFRAMES))
    if mid_tf is not None and mid_tf not in ALLOWED_TIMEFRAMES:
        return _err(
            "invalid_mid_timeframe",
            mid_tf=mid_tf,
            allowed=sorted(ALLOWED_TIMEFRAMES),
            note="Bitfinex has no native 4h; use 6h instead.",
        )

    if htf_candles is None:
        htf = await read_candles(symbol, trend_tf, candle_limit, config)
        if not htf.get("success"):
            return _err("htf_candles_failed", detail=htf)
        htf_candles = {k: htf.get(k, []) for k in ("open", "high", "low", "close", "volume")}
    if ltf_candles is None:
        ltf = await read_candles(symbol, entry_tf, candle_limit, config)
        if not ltf.get("success"):
            return _err("ltf_candles_failed", detail=ltf)
        ltf_candles = {k: ltf.get(k, []) for k in ("open", "high", "low", "close", "volume")}

    if mid_tf is not None and mid_candles is None:
        mid_resp = await read_candles(symbol, mid_tf, candle_limit, config)
        if not mid_resp.get("success"):
            return _err("mid_candles_failed", detail=mid_resp)
        mid_candles = {k: mid_resp.get(k, []) for k in ("open", "high", "low", "close", "volume")}

    try:
        record = evaluate_and_record(
            htf_candles=htf_candles,
            ltf_candles=ltf_candles,
            mid_candles=mid_candles,
            mid_tf=mid_tf,
            symbol=symbol,
            trend_tf=trend_tf,
            entry_tf=entry_tf,
            params=params,
            risk_state=risk_state,
            risk_pct=float(risk_pct or 0.01),
            persist=persist,
        )
    except Exception as exc:
        logger.exception("evaluate_and_record failed")
        return _err(f"strategy_failed: {exc}")

    return {"success": True, "record": asdict(record)}


async def submit_paper_order(
    symbol: str,
    side: str,
    size: float,
    config: MCPConfig,
    *,
    type: str = "MARKET",
    price: float | None = None,
    decision_id: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    if side not in {"LONG", "SHORT"}:
        return _err("invalid_side", side=side)
    try:
        size = float(size)
    except (TypeError, ValueError):
        return _err("invalid_size")
    if size <= 0:
        return _err("invalid_size")

    record = None
    if decision_id:
        record = find_decision(decision_id)
        if record is None:
            return _err("decision_not_found", decision_id=decision_id)
    if record is not None and not force:
        if not record.get("risk_check", {}).get("passed", False):
            return _err(
                "risk_blocked",
                decision_id=decision_id,
                reasons=record["risk_check"].get("reasons", []),
            )

    try:
        from core.api.paper import paper_submit
    except Exception as exc:  # pragma: no cover
        return _err(f"import_failed: {exc}")

    payload: dict[str, Any] = {"symbol": symbol, "side": side, "size": size, "type": type}
    if price is not None:
        payload["price"] = float(price)

    try:
        response = await paper_submit(payload)
    except Exception as exc:
        return _err(f"submit_failed: {exc}")

    submission_record = {
        "submitted": bool(response.get("ok")),
        "request": payload,
        "response": response,
        "force": bool(force),
    }
    if decision_id:
        try:
            append_followup(decision_id=decision_id, submission=submission_record)
        except Exception as exc:
            logger.warning("append_followup failed: %s", exc)

    return {
        "success": True,
        "submission": submission_record,
        "audit_path": str(DEFAULT_LOG_PATH),
    }


async def read_decision_log(
    config: MCPConfig,
    *,
    symbol: str | None = None,
    decision_id: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    safe_limit = max(1, min(int(limit or 50), MAX_LOG_LIMIT))
    try:
        records = read_decisions(symbol=symbol, decision_id=decision_id, limit=safe_limit)
    except Exception as exc:
        return _err(f"read_log_failed: {exc}")
    return {"success": True, "records": records, "path": str(DEFAULT_LOG_PATH)}


async def append_decision_log(
    record: dict[str, Any],
    config: MCPConfig,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return _err("invalid_record_type")
    required = {"symbol", "trend_tf", "entry_tf", "fib_signal", "risk_check"}
    missing = required - set(record.keys())
    if missing:
        return _err("missing_fields", missing=sorted(missing))
    record.setdefault("schema_version", SCHEMA_VERSION)
    try:
        path = append_decision(record)
    except Exception as exc:
        return _err(f"append_failed: {exc}")
    return {"success": True, "appended": True, "path": str(path)}


__all__ = [
    "read_account_state",
    "read_candles",
    "run_strategy",
    "submit_paper_order",
    "read_decision_log",
    "append_decision_log",
    "DecisionRecord",
]
