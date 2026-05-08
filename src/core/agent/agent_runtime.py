from __future__ import annotations

import datetime as dt
from dataclasses import fields
from pathlib import Path
from typing import Any

from core.risk.guards import breached_max_drawdown, within_daily_loss_limit
from core.risk.pnl import daily_pnl_usd

from .decision_record import (
    DecisionRecord,
    append_decision,
    candles_hash,
    canonical_hash,
)
from .fib_strategy import FibStrategyParams, compute_signal, compute_signal_nested


def _coerce_params(params: dict[str, Any] | FibStrategyParams | None) -> FibStrategyParams:
    if params is None:
        return FibStrategyParams()
    if isinstance(params, FibStrategyParams):
        return params
    allowed = {field.name for field in fields(FibStrategyParams)}
    kwargs: dict[str, Any] = {}
    for key, value in params.items():
        if key not in allowed:
            continue
        if key in {"extension_levels", "target_fractions"} and isinstance(value, list):
            kwargs[key] = tuple(value)
        else:
            kwargs[key] = value
    return FibStrategyParams(**kwargs)


def _evaluate_risk(risk_state: dict[str, Any] | None) -> dict[str, Any]:
    state = risk_state or {}
    baseline = float(state.get("baseline_equity_usd") or 0.0)
    current = float(state.get("current_equity_usd") or baseline)
    peak = float(state.get("equity_peak_usd") or baseline)
    max_dd = float(state.get("max_dd_pct") or 0.0)
    max_loss = float(state.get("max_daily_loss_usd") or 0.0)
    pnl = daily_pnl_usd(baseline, current) if baseline > 0 else 0.0
    reasons: list[str] = []
    if max_loss > 0 and not within_daily_loss_limit(pnl, max_loss):
        reasons.append("daily_loss_breached")
    if peak > 0 and max_dd > 0 and breached_max_drawdown(peak, current, max_dd):
        reasons.append("max_drawdown_breached")
    return {
        "passed": not reasons,
        "reasons": reasons,
        "baseline_equity_usd": baseline,
        "current_equity_usd": current,
        "daily_pnl_usd": pnl,
        "equity_peak_usd": peak,
        "max_dd_pct": max_dd,
        "max_daily_loss_usd": max_loss,
    }


def evaluate_and_record(
    *,
    htf_candles: dict[str, Any],
    ltf_candles: dict[str, Any],
    symbol: str,
    trend_tf: str,
    entry_tf: str,
    params: dict[str, Any] | FibStrategyParams | None = None,
    risk_state: dict[str, Any] | None = None,
    risk_pct: float = 0.01,
    persist: bool = True,
    log_path: Path | None = None,
    mid_candles: dict[str, Any] | None = None,
    mid_tf: str | None = None,
) -> DecisionRecord:
    """Evaluate strategy and emit a DecisionRecord.

    Two modes (auto-selected):
      - 2-tier (legacy): when mid_candles is None. HTF trend + LTF counter-leg.
      - 3-tier (nested confluence): when mid_candles is provided. Mega/major/minor
        all in same direction; entry on confluence overlap.
    """
    fib_params = _coerce_params(params)
    risk_check = _evaluate_risk(risk_state)
    equity = float(risk_check.get("current_equity_usd") or 0.0)

    if mid_candles is not None:
        signal = compute_signal_nested(
            htf_candles,
            mid_candles,
            ltf_candles,
            fib_params,
            equity_usd=equity,
            risk_pct=risk_pct,
        )
        candles_hashes = {
            "mega": candles_hash(htf_candles),
            "major": candles_hash(mid_candles),
            "minor": candles_hash(ltf_candles),
        }
    else:
        signal = compute_signal(
            htf_candles,
            ltf_candles,
            fib_params,
            equity_usd=equity,
            risk_pct=risk_pct,
        )
        candles_hashes = {
            "htf": candles_hash(htf_candles),
            "ltf": candles_hash(ltf_candles),
        }

    record = DecisionRecord(
        ts_utc=dt.datetime.now(dt.UTC).isoformat(),
        symbol=symbol,
        trend_tf=trend_tf,
        mid_tf=mid_tf,
        entry_tf=entry_tf,
        candles_hash=candles_hashes,
        params_hash=canonical_hash(fib_params.to_dict()),
        fib_signal=signal.to_dict(),
        risk_check=risk_check,
    )

    if persist:
        append_decision(record, path=log_path)
    return record
