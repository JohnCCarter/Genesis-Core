from __future__ import annotations

from pathlib import Path
from typing import Any

from core.optimizer.champion import ChampionCandidate


def _extract_results_path_from_log(log_content: str) -> Path | None:
    """Extract the backtest result JSON path from subprocess logs."""

    import re

    from core.optimizer import runner as runner_module

    patterns = [
        r"^\s*results:\s*(.+?\.json)\s*$",
        r"^\s*json:\s*(.+?\.json)\s*$",
        r"^\[SAVED\]\s*Results:\s*(.+?\.json)\s*$",
    ]

    for pat in patterns:
        matches = re.findall(pat, log_content, flags=re.MULTILINE)
        if not matches:
            continue
        candidate = Path(str(matches[-1]).strip())
        if not candidate.is_absolute():
            candidate = runner_module.PROJECT_ROOT / candidate
        if candidate.exists():
            return candidate
    return None


def _candidate_from_result(result: dict[str, Any]) -> ChampionCandidate | None:
    if result.get("error") or result.get("skipped"):
        return None
    score_block = result.get("score") or {}
    constraints_block = result.get("constraints") or {}
    hard_failures = list(score_block.get("hard_failures") or [])
    constraints_ok = bool(constraints_block.get("ok"))
    if not constraints_ok or hard_failures:
        return None
    try:
        score_value = float(score_block.get("score"))
    except (TypeError, ValueError):
        return None
    return ChampionCandidate(
        parameters=dict(result.get("parameters") or {}),
        score=score_value,
        metrics=dict(score_block.get("metrics") or {}),
        constraints_ok=constraints_ok,
        constraints=dict(constraints_block),
        hard_failures=hard_failures,
        trial_id=str(result.get("trial_id", "")),
        results_path=str(result.get("results_path", "")),
        merged_config=result.get("merged_config"),
    )


def _extract_num_trades(payload: dict[str, Any]) -> int | None:
    """Best effort extraction of num_trades from nested payloads."""

    def _coerce(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    score_block = payload.get("score")
    if isinstance(score_block, dict):
        metrics = score_block.get("metrics")
        if isinstance(metrics, dict):
            coerced = _coerce(metrics.get("num_trades"))
            if coerced is not None:
                return coerced

    summary_block = payload.get("summary")
    if isinstance(summary_block, dict):
        coerced = _coerce(summary_block.get("num_trades"))
        if coerced is not None:
            return coerced

    metrics_block = payload.get("metrics")
    if isinstance(metrics_block, dict):
        coerced = _coerce(metrics_block.get("num_trades"))
        if coerced is not None:
            return coerced

    return None


def _check_abort_heuristic(
    backtest_results: dict[str, Any], trial_params: dict[str, Any]
) -> dict[str, Any]:
    """Check if trial should be aborted post-backtest based on heuristic."""

    metrics = backtest_results.get("metrics", {})
    num_trades = metrics.get("num_trades", 0)

    if num_trades == 0:
        thresholds = trial_params.get("thresholds", {})
        entry_conf = thresholds.get("entry_conf_overall", 0.0)
        signal_adapt = thresholds.get("signal_adaptation", {})
        zones = signal_adapt.get("zones", {})
        low_zone = zones.get("low", {})
        low_entry = low_zone.get("entry_conf_overall", 0.0)
        min_edge = thresholds.get("min_edge", 0.0)

        if entry_conf >= 0.35 or low_entry >= 0.28 or min_edge >= 0.015:
            return {
                "ok": False,
                "reason": "zero_trades_high_thresholds",
                "details": f"entry={entry_conf:.3f}, low_zone={low_entry:.3f}, min_edge={min_edge:.4f}",
                "penalty": -500.0,
            }

    if 0 < num_trades <= 3:
        return {
            "ok": False,
            "reason": "very_few_trades",
            "details": f"only {num_trades} trades",
            "penalty": -250.0,
        }

    return {"ok": True, "reason": "", "details": "", "penalty": 0.0}
