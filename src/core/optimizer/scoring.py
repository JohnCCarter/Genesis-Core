from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class MetricThresholds:
    min_trades: int = 30
    min_profit_factor: float = 1.2
    max_max_dd: float = 0.15


def _extract_metric(name: str, container: dict[str, Any], default: float | None = None) -> float:
    value = container.get(name, default)
    if value is None:
        raise KeyError(f"Missing metric '{name}' in summary")
    return float(value)


def score_backtest(result: dict[str, Any], *, thresholds: MetricThresholds | None = None) -> dict[str, Any]:
    thresholds = thresholds or MetricThresholds()
    summary = result.get("summary") or {}
    trades: Iterable[dict[str, Any]] = result.get("trades") or []

    total_return = _extract_metric("total_return", summary, 0.0) / 100.0
    profit_factor = _extract_metric("profit_factor", summary, 0.0)
    max_drawdown = max(
        float(summary.get("max_drawdown", 0.0)) / 100.0,
        float(summary.get("max_dd", 0.0)),
    )
    win_rate = _extract_metric("win_rate", summary, 0.0) / 100.0
    num_trades = int(summary.get("num_trades", len(list(trades))))

    sharpe = float(summary.get("sharpe_ratio", 0.0))
    ret_ratio = total_return / max(0.0001, max_drawdown if max_drawdown > 0 else 0.0001)

    hard_failures: list[str] = []
    if num_trades < thresholds.min_trades:
        hard_failures.append(f"trades<{thresholds.min_trades}")
    if profit_factor < thresholds.min_profit_factor:
        hard_failures.append(f"pf<{thresholds.min_profit_factor}")
    if max_drawdown > thresholds.max_max_dd:
        hard_failures.append(f"max_dd>{thresholds.max_max_dd}")

    base_score = sharpe
    base_score += total_return
    base_score += ret_ratio * 0.25
    base_score += np.clip(win_rate - 0.4, -0.2, 0.2)

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
        },
        "hard_failures": hard_failures,
        "baseline": {
            "thresholds": thresholds,
        },
    }
