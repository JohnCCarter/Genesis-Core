from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np

from core.backtest.metrics import calculate_metrics


@dataclass(slots=True)
class MetricThresholds:
    min_trades: int = 10  # Sänkt för korta perioder
    min_profit_factor: float = 1.0  # Sänkt för korta perioder
    max_max_dd: float = 0.20  # Ökat för korta perioder


def _extract_metric(name: str, container: dict[str, Any], default: float | None = None) -> float:
    value = container.get(name, default)
    if value is None:
        raise KeyError(f"Missing metric '{name}' in summary")
    return float(value)


def _resolve_score_version(score_version: str | None) -> str:
    raw = (score_version or os.environ.get("GENESIS_SCORE_VERSION") or "v1").strip().lower()
    if raw in {"1", "v1", "legacy", "default"}:
        return "v1"
    if raw in {"2", "v2", "sharpe"}:
        return "v2"
    raise ValueError(f"Unknown score_version: {score_version!r}")


def _score_v1(
    *,
    sharpe: float,
    total_return: float,
    ret_ratio: float,
    win_rate: float,
) -> tuple[float, dict[str, float]]:
    win_term = float(np.clip(win_rate - 0.4, -0.2, 0.2))
    base_score = float(sharpe) + float(total_return) + float(ret_ratio) * 0.25 + win_term
    return base_score, {
        "sharpe": float(sharpe),
        "return": float(total_return),
        "return_to_dd": float(ret_ratio) * 0.25,
        "win_rate_term": win_term,
    }


def _score_v2(
    *,
    sharpe: float,
    total_return: float,
    profit_factor: float,
    win_rate: float,
) -> tuple[float, dict[str, float]]:
    """Sharpe-first scoring with clipped bonuses.

    Rationale (high-level):
    - Sharpe is the backbone.
    - Return contributes as a small, capped bonus (log-scaled).
    - Profit factor contributes as a small, capped bonus (log-scaled).
    - Win rate is only a tie-breaker.

    All inputs are expected to be in normalized units:
    - total_return as fraction (e.g. 0.05 for +5%)
    - win_rate in [0, 1]
    """

    sharpe_term = float(np.clip(sharpe, -1.0, 3.0))

    # Capped return bonus (keeps sign, avoids large-return domination)
    ret_clipped = float(np.clip(total_return, -0.50, 0.50))
    ret_term = float(np.log1p(ret_clipped))  # safe since ret_clipped > -1.0

    # Capped PF bonus (PF=1 => 0), negative for PF<1
    pf = float(profit_factor)
    pf_clipped = float(np.clip(pf, 0.25, 5.0))
    pf_term = float(np.log(pf_clipped))

    # Win-rate tie-breaker
    wr_term = float(np.clip(win_rate - 0.50, -0.10, 0.10))

    # Weights intentionally small for bonuses; Sharpe is the backbone.
    base_score = sharpe_term + (0.15 * ret_term) + (0.10 * pf_term) + (0.05 * wr_term)
    return float(base_score), {
        "sharpe_clipped": sharpe_term,
        "return_log1p": ret_term,
        "pf_log": pf_term,
        "win_rate_term": wr_term,
    }


def score_backtest(
    result: dict[str, Any],
    *,
    thresholds: MetricThresholds | None = None,
    score_version: str | None = None,
) -> dict[str, Any]:
    thresholds = thresholds or MetricThresholds()
    score_version_resolved = _resolve_score_version(score_version)

    # Robust metrics: compute from trades/equity (with equity fallback) instead of trusting summary
    mt = calculate_metrics(result, prefer_summary=False)

    # Cost / churn telemetry (used by constraints and optional scoring heuristics)
    summary = result.get("summary") if isinstance(result, dict) else None
    if not isinstance(summary, dict):
        summary = {}
    try:
        initial_capital = float(summary.get("initial_capital", 10000.0) or 10000.0)
    except (TypeError, ValueError):
        initial_capital = 10000.0

    trades = result.get("trades") if isinstance(result, dict) else None
    total_commission = 0.0
    if isinstance(trades, list):
        for t in trades:
            if not isinstance(t, dict):
                continue
            try:
                total_commission += float(t.get("commission", 0.0) or 0.0)
            except (TypeError, ValueError):
                continue
    total_commission_pct = total_commission / initial_capital if initial_capital > 0 else 0.0

    # Metrics from calculate_metrics() are in percent where applicable
    total_return = float(mt.get("total_return", 0.0)) / 100.0
    profit_factor = float(mt.get("profit_factor", 0.0))
    max_drawdown_pct = float(mt.get("max_drawdown", 0.0))  # percent
    max_drawdown = max_drawdown_pct / 100.0
    win_rate = float(mt.get("win_rate", 0.0)) / 100.0
    num_trades = int(mt.get("num_trades", 0))
    sharpe = float(mt.get("sharpe_ratio", 0.0))

    # Guard against zero-DD cases to avoid exploding return_to_dd
    ret_ratio = total_return / max(0.0001, max_drawdown if max_drawdown > 0 else 0.0001)

    hard_failures: list[str] = []
    if num_trades < thresholds.min_trades:
        hard_failures.append(f"trades<{thresholds.min_trades}")
    if profit_factor < thresholds.min_profit_factor:
        hard_failures.append(f"pf<{thresholds.min_profit_factor}")
    if max_drawdown > thresholds.max_max_dd:
        hard_failures.append(f"max_dd>{thresholds.max_max_dd}")

    if score_version_resolved == "v1":
        base_score, score_components = _score_v1(
            sharpe=sharpe,
            total_return=total_return,
            ret_ratio=ret_ratio,
            win_rate=win_rate,
        )
    elif score_version_resolved == "v2":
        base_score, score_components = _score_v2(
            sharpe=sharpe,
            total_return=total_return,
            profit_factor=profit_factor,
            win_rate=win_rate,
        )
    else:  # pragma: no cover - _resolve_score_version constrains values
        raise ValueError(f"Unhandled score_version: {score_version_resolved!r}")

    penalty = 0.0
    if hard_failures:
        penalty = 100.0

    score = base_score - penalty

    return {
        "score": score,
        "metrics": {
            "total_return": total_return,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "num_trades": num_trades,
            "sharpe_ratio": sharpe,
            "return_to_dd": ret_ratio,
            "total_commission": total_commission,
            "total_commission_pct": total_commission_pct,
        },
        "hard_failures": hard_failures,
        "baseline": {
            "thresholds": thresholds,
            "score_version": score_version_resolved,
            "score_components": score_components,
        },
    }
