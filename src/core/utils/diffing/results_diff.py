"""Results diffing utilities for comparing backtest outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "MetricDelta",
    "diff_metrics",
    "diff_backtest_results",
    "diff_backtest_files",
    "check_backtest_comparability",
    "format_comparability_issues",
    "summarize_metric_deltas",
    "summarize_metrics_diff",
]


@dataclass(slots=True)
class MetricDelta:
    old: float | int | None
    new: float | int | None
    delta: float | int | None
    regression: bool = False


def _compute_delta(old_value: Any, new_value: Any) -> MetricDelta:
    if old_value is None and new_value is None:
        return MetricDelta(old=None, new=None, delta=None, regression=False)

    try:
        old_num = float(old_value) if old_value is not None else 0.0
        new_num = float(new_value) if new_value is not None else 0.0
        return MetricDelta(old=old_value, new=new_value, delta=new_num - old_num, regression=False)
    except (TypeError, ValueError):
        regression = old_value != new_value
        return MetricDelta(old=old_value, new=new_value, delta=None, regression=regression)


def diff_metrics(
    old_metrics: dict[str, Any],
    new_metrics: dict[str, Any],
    *,
    regression_thresholds: dict[str, float | int] | None = None,
) -> dict[str, MetricDelta]:
    regression_thresholds = regression_thresholds or {}
    diff: dict[str, MetricDelta] = {}
    keys = set(old_metrics.keys()) | set(new_metrics.keys())
    for key in sorted(keys):
        delta = _compute_delta(old_metrics.get(key), new_metrics.get(key))
        if delta.delta is not None:
            threshold = regression_thresholds.get(key)
            if threshold is not None and delta.delta <= threshold:
                delta.regression = True
        diff[key] = delta
    return diff


def diff_backtest_results(
    old_results: dict[str, Any],
    new_results: dict[str, Any],
) -> dict[str, Any]:
    old_metrics = (
        (old_results.get("summary") or {}).get("metrics") or old_results.get("metrics") or {}
    )
    new_metrics = (
        (new_results.get("summary") or {}).get("metrics") or new_results.get("metrics") or {}
    )
    metric_diff = diff_metrics(old_metrics, new_metrics)

    trades_old = len(old_results.get("trades") or [])
    trades_new = len(new_results.get("trades") or [])
    trade_delta = MetricDelta(old=trades_old, new=trades_new, delta=trades_new - trades_old)

    metrics_serialized = {
        key: {
            "old": delta.old,
            "new": delta.new,
            "delta": delta.delta,
            "regression": delta.regression,
        }
        for key, delta in metric_diff.items()
    }
    trade_serialized = {
        "old": trade_delta.old,
        "new": trade_delta.new,
        "delta": trade_delta.delta,
        "regression": trade_delta.regression,
    }

    return {
        "metrics": metrics_serialized,
        "trades": trade_serialized,
    }


def diff_backtest_files(old_path: Path | str, new_path: Path | str) -> dict[str, Any]:
    with (
        Path(old_path).open("r", encoding="utf-8") as f_old,
        Path(new_path).open("r", encoding="utf-8") as f_new,
    ):
        old_data = json.load(f_old)
        new_data = json.load(f_new)
    return diff_backtest_results(old_data, new_data)


def summarize_metric_deltas(diff: dict[str, MetricDelta]) -> str:
    lines = []
    for key, delta in diff.items():
        if delta.delta is not None:
            lines.append(f"{key}: {delta.delta:+.4f} (old={delta.old}, new={delta.new})")
        elif delta.regression:
            lines.append(f"{key}: changed from {delta.old} to {delta.new}")
    return "\n".join(lines)


def summarize_metrics_diff(serialized_diff: dict[str, Any]) -> str:
    lines = []
    for key, payload in serialized_diff.items():
        delta = payload.get("delta")
        if delta is not None:
            lines.append(
                f"{key}: {delta:+.4f} (old={payload.get('old')}, new={payload.get('new')})"
            )
        elif payload.get("regression"):
            lines.append(f"{key}: changed from {payload.get('old')} to {payload.get('new')}")
    return "\n".join(lines)


def _dig(mapping: dict[str, Any], dotted_path: str) -> Any:
    cur: Any = mapping
    for part in dotted_path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        return v or None
    return None


def _extract_score_version(results: dict[str, Any]) -> str | None:
    score_block = results.get("score")
    if isinstance(score_block, dict):
        return _coerce_optional_str(score_block.get("score_version"))
    return None


def check_backtest_comparability(
    old_results: dict[str, Any],
    new_results: dict[str, Any],
    *,
    warn_only: bool = False,
    context: str = "compare",
) -> list[str]:
    """Enforce apples-to-apples guardrails for backtest comparisons.

    Policy (STRICT default):
    - Fail-fast ONLY when both values are known and differ.
    - score_version: fail-fast only when both are known and differ; otherwise warn-only.
    - HTF status + git_hash + seed + initial_capital: warn-only.

    Returns:
        List of warnings (strings). Raises ValueError on fail-fast errors unless warn_only=True.
    """

    old_info = old_results.get("backtest_info")
    new_info = new_results.get("backtest_info")
    old_info = old_info if isinstance(old_info, dict) else {}
    new_info = new_info if isinstance(new_info, dict) else {}

    warnings: list[str] = []
    errors: list[str] = []

    fail_fast_fields = [
        "symbol",
        "timeframe",
        "start_date",
        "end_date",
        "warmup_bars",
        "commission_rate",
        "slippage_rate",
        "effective_config_fingerprint",
        "execution_mode.fast_window",
        "execution_mode.env_precompute_features",
    ]
    for path in fail_fast_fields:
        a = _dig(old_info, path)
        b = _dig(new_info, path)
        if a is None or b is None:
            if a is None and b is None:
                continue
            warnings.append(f"missing:{path} old={a!r} new={b!r}")
            continue
        if a != b:
            errors.append(f"{path} old={a!r} new={b!r}")

    # runtime_version lives at top-level in results payloads.
    old_runtime = old_results.get("runtime_version")
    new_runtime = new_results.get("runtime_version")
    if old_runtime is None or new_runtime is None:
        if not (old_runtime is None and new_runtime is None):
            warnings.append(f"missing:runtime_version old={old_runtime!r} new={new_runtime!r}")
    elif old_runtime != new_runtime:
        errors.append(f"runtime_version old={old_runtime!r} new={new_runtime!r}")

    # score_version: only fail-fast if both known and differ.
    old_sv = _extract_score_version(old_results)
    new_sv = _extract_score_version(new_results)
    if old_sv and new_sv and old_sv != new_sv:
        errors.append(f"score_version old={old_sv!r} new={new_sv!r}")
    elif (old_sv is None) != (new_sv is None):
        warnings.append(f"missing:score_version old={old_sv!r} new={new_sv!r}")

    warn_only_fields = [
        "execution_mode.mode_explicit",
        "git_hash",
        "seed",
        "initial_capital",
        "htf.env_htf_exits",
        "htf.use_new_exit_engine",
        "htf.htf_candles_loaded",
        "htf.htf_context_seen",
    ]
    for path in warn_only_fields:
        a = _dig(old_info, path)
        b = _dig(new_info, path)
        if a is None or b is None:
            continue
        if a != b:
            warnings.append(f"{path} old={a!r} new={b!r}")

    if errors and not warn_only:
        raise ValueError(
            f"Inkompatibla backtest-resultat ({context}): "
            + "; ".join(errors[:8])
            + ("; ..." if len(errors) > 8 else "")
        )

    return warnings


def format_comparability_issues(issues: list[str], *, max_items: int = 6) -> str:
    if not issues:
        return ""
    max_items = max(1, max_items)  # Ensure at least one item is shown
    preview = "; ".join(issues[:max_items])
    suffix = "; ..." if len(issues) > max_items else ""
    return f"{preview}{suffix}"
