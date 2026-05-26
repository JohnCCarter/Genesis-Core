# ruff: noqa: E402

from __future__ import annotations

import json
import math
import os
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_20260526 as local_envelope,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_20260526 as local_packet,
)
from scripts.run.run_backtest import GenesisPipeline, _deep_merge

os.environ["GENESIS_RANDOM_SEED"] = "42"
os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
os.environ["GENESIS_PRECOMPUTE_CACHE_WRITE"] = "0"
os.environ["GENESIS_MODE_EXPLICIT"] = "1"
os.environ["GENESIS_FAST_HASH"] = "0"
os.environ["GENESIS_SCORE_VERSION"] = "v2"

LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json"
)
LOCAL_ENVELOPE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json"
STATUS_OK = "continuation_release_hysteresis_local_action_position_equivalence_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_action_position_equivalence_fail_closed"
PACKET_STATUS_BOTH_ABSORBED = "candidate_and_control_asymmetry_absorbed_before_execution_surface"
PACKET_STATUS_CANDIDATE_ABSORBED = (
    "candidate_asymmetry_absorbed_before_execution_surface_while_control_reaches_execution_surface"
)
PACKET_STATUS_CANDIDATE_DIVERGES = "candidate_reaches_execution_surface_divergence"
FLOAT_TOLERANCE = 1e-9


class LocalActionPositionEquivalenceError(RuntimeError):
    pass


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _float_close(
    left: float | None, right: float | None, *, tolerance: float = FLOAT_TOLERANCE
) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    scale = max(1.0, abs(left), abs(right))
    return abs(left - right) <= tolerance * scale


def _label_counts(values: list[str]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [
        {"label": label, "count": count}
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _position_snapshot(position: Any) -> dict[str, Any]:
    if position is None:
        return {
            "has_position": False,
            "side": None,
            "current_size": None,
            "entry_time": None,
        }
    entry_time = position.entry_time
    if isinstance(entry_time, datetime):
        if entry_time.tzinfo is None:
            entry_time = entry_time.replace(tzinfo=UTC)
        entry_time_text = entry_time.astimezone(UTC).isoformat()
    else:
        entry_time_text = str(entry_time)
    return {
        "has_position": True,
        "side": str(position.side),
        "current_size": float(position.current_size),
        "entry_time": entry_time_text,
    }


def _run_case_with_action_position_rows(
    mode: str,
    *,
    start_date: str,
    end_date: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise LocalActionPositionEquivalenceError(
            f"Carrier does not expose enabled research_policy_router for {mode}"
        )

    if mode == "baseline":
        router_cfg.pop("continuation_release_hysteresis", None)
    elif mode == "release_zero":
        router_cfg["continuation_release_hysteresis"] = 0
    else:
        raise LocalActionPositionEquivalenceError(f"Unsupported mode {mode!r}")

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=local_packet.SYMBOL,
        timeframe=local_packet.TIMEFRAME,
        start_date=start_date,
        end_date=end_date,
        warmup_bars=local_packet.WARMUP,
        data_source_policy=local_packet.DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise LocalActionPositionEquivalenceError(f"BacktestEngine.load_data() failed for {mode}")

    rows: dict[str, dict[str, Any]] = {}
    continuation_release_timestamps: list[str] = []

    def capture(result: dict[str, Any], meta: dict[str, Any] | None, candles: dict[str, Any]):
        timestamps = candles.get("timestamp") or []
        if not timestamps:
            return result, meta
        timestamp = timestamps[-1]
        timestamp_text = str(
            timestamp.isoformat() if hasattr(timestamp, "isoformat") else timestamp
        )
        decision = (meta or {}).get("decision") or {}
        state_out = decision.get("state_out") or {}
        position_before = _position_snapshot(engine.position_tracker.position)
        row = {
            "action": result.get("action"),
            "reasons": decision.get("reasons"),
            "size": decision.get("size"),
            "router_state": state_out.get("research_policy_router_state"),
            "router_debug": state_out.get(local_packet.RESEARCH_POLICY_ROUTER_DEBUG_KEY),
            "position_before": position_before,
            "trade_event_count_before": len(engine.position_tracker.trades),
        }
        rows[timestamp_text] = local_packet._json_safe(row)
        debug = row.get("router_debug") or {}
        if debug.get("switch_control_mode") == "continuation_release":
            continuation_release_timestamps.append(timestamp_text)
        return result, meta

    engine.evaluation_hook = capture
    results = engine.run(
        policy={"symbol": local_packet.SYMBOL, "timeframe": local_packet.TIMEFRAME},
        configs=validated_cfg,
    )
    if "error" in results:
        raise LocalActionPositionEquivalenceError(
            f"Backtest run failed for {mode}: {results['error']}"
        )

    backtest_info = results.get("backtest_info") or {}
    execution_mode = backtest_info.get("execution_mode") or {}
    if not execution_mode.get("fast_window"):
        raise LocalActionPositionEquivalenceError(
            f"Execution mode drift for {mode}: fast_window false"
        )
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise LocalActionPositionEquivalenceError(
            f"Execution mode drift for {mode}: env_precompute_features != 1"
        )
    if not execution_mode.get("precompute_enabled"):
        raise LocalActionPositionEquivalenceError(
            f"Execution mode drift for {mode}: precompute_enabled false"
        )
    if str(execution_mode.get("mode_explicit")) != "1":
        raise LocalActionPositionEquivalenceError(
            f"Execution mode drift for {mode}: mode_explicit != 1"
        )

    return {
        "summary": local_packet._json_safe(results.get("summary")),
        "position_summary": local_packet._json_safe(results.get("position_summary")),
        "metrics": local_packet._json_safe(results.get("metrics")),
        "execution_mode": local_packet._json_safe(execution_mode),
        "bars_total": local_packet._json_safe(backtest_info.get("bars_total")),
        "bars_processed": local_packet._json_safe(backtest_info.get("bars_processed")),
        "effective_config_fingerprint": local_packet._json_safe(
            backtest_info.get("effective_config_fingerprint")
        ),
        "trades": local_packet._json_safe(results.get("trades")),
        "rows": rows,
        "continuation_release_timestamps": tuple(sorted(continuation_release_timestamps)),
    }


def _normalized_row(raw_row: dict[str, Any] | None) -> dict[str, Any]:
    row = local_packet._coerce_optional_dict(raw_row)
    debug = local_packet._coerce_optional_dict(row.get("router_debug"))
    position_before = local_packet._coerce_optional_dict(row.get("position_before"))
    size = local_packet._coerce_optional_float(row.get("size"))
    return {
        "action": local_packet._coerce_optional_str(row.get("action")) or "NONE",
        "size": size,
        "selected_policy": local_packet._coerce_optional_str(debug.get("selected_policy")),
        "switch_reason": local_packet._coerce_optional_str(debug.get("switch_reason")),
        "switch_control_mode": local_packet._coerce_optional_str(debug.get("switch_control_mode")),
        "bars_since_regime_change": local_packet._coerce_optional_float(
            debug.get("bars_since_regime_change")
        ),
        "zone": local_packet._coerce_optional_str(debug.get("zone")),
        "action_edge": local_packet._coerce_optional_float(debug.get("action_edge")),
        "confidence_gate": local_packet._coerce_optional_float(debug.get("confidence_gate")),
        "clarity_score": local_packet._coerce_optional_float(debug.get("clarity_score")),
        "position_before": {
            "has_position": bool(position_before.get("has_position", False)),
            "side": local_packet._coerce_optional_str(position_before.get("side")),
            "current_size": local_packet._coerce_optional_float(
                position_before.get("current_size")
            ),
            "entry_time": local_packet._coerce_optional_str(position_before.get("entry_time")),
        },
        "trade_event_count_before": int(
            local_packet._coerce_optional_float(row.get("trade_event_count_before")) or 0
        ),
    }


def _execution_effect(row: dict[str, Any]) -> dict[str, Any]:
    position_before = local_packet._coerce_dict(
        row.get("position_before"),
        field_name="execution_effect.position_before",
    )
    has_position = bool(position_before.get("has_position", False))
    side = local_packet._coerce_optional_str(position_before.get("side"))
    action = str(row.get("action") or "NONE")
    size = local_packet._coerce_optional_float(row.get("size")) or 0.0

    if not has_position:
        if action == "NONE" or size <= 0.0:
            return {"effect": "hold_flat", "side": None, "effective_size": 0.0}
        return {"effect": "open_position", "side": action, "effective_size": size}

    if action == "NONE" or size <= 0.0:
        return {"effect": "hold_existing", "side": side, "effective_size": 0.0}
    if action == side:
        return {"effect": "hold_existing", "side": side, "effective_size": 0.0}
    return {"effect": "reverse_position", "side": action, "effective_size": size}


def _position_equivalent(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_position = local_packet._coerce_dict(
        left.get("position_before"), field_name="left.position"
    )
    right_position = local_packet._coerce_dict(
        right.get("position_before"), field_name="right.position"
    )
    return (
        bool(left_position.get("has_position", False))
        == bool(right_position.get("has_position", False))
        and local_packet._coerce_optional_str(left_position.get("side"))
        == local_packet._coerce_optional_str(right_position.get("side"))
        and _float_close(
            local_packet._coerce_optional_float(left_position.get("current_size")),
            local_packet._coerce_optional_float(right_position.get("current_size")),
        )
        and local_packet._coerce_optional_str(left_position.get("entry_time"))
        == local_packet._coerce_optional_str(right_position.get("entry_time"))
    )


def _effect_equivalent(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        str(left.get("effect")) == str(right.get("effect"))
        and local_packet._coerce_optional_str(left.get("side"))
        == local_packet._coerce_optional_str(right.get("side"))
        and _float_close(
            local_packet._coerce_optional_float(left.get("effective_size")),
            local_packet._coerce_optional_float(right.get("effective_size")),
        )
    )


def _classify_row(
    *,
    row_changed: bool,
    action_changed: bool,
    size_changed: bool,
    selected_policy_changed: bool,
    switch_reason_changed: bool,
    position_equivalent: bool,
    effect_equivalent: bool,
    baseline_row: dict[str, Any],
    release_zero_row: dict[str, Any],
    baseline_effect: dict[str, Any],
    release_zero_effect: dict[str, Any],
) -> str:
    if not row_changed:
        return "identical"

    baseline_position = local_packet._coerce_dict(
        baseline_row.get("position_before"), field_name="classification.baseline_position"
    )
    release_zero_position = local_packet._coerce_dict(
        release_zero_row.get("position_before"), field_name="classification.release_position"
    )
    same_locked_position = (
        position_equivalent
        and bool(baseline_position.get("has_position", False))
        and bool(release_zero_position.get("has_position", False))
    )

    if effect_equivalent and position_equivalent and not action_changed and not size_changed:
        if selected_policy_changed or switch_reason_changed:
            return "router_internal_only"
        return "execution_equivalent_other"

    if effect_equivalent and same_locked_position and size_changed and not action_changed:
        return "size_diff_absorbed_by_locked_position"

    if effect_equivalent and same_locked_position and action_changed:
        return "action_diff_absorbed_by_locked_position"

    if not position_equivalent:
        return "position_context_divergence"

    if not effect_equivalent:
        baseline_effect_label = str(baseline_effect.get("effect"))
        release_zero_effect_label = str(release_zero_effect.get("effect"))
        effect_pair = {baseline_effect_label, release_zero_effect_label}
        if effect_pair == {"hold_flat", "open_position"}:
            return "flat_entry_divergence"
        if "reverse_position" in effect_pair:
            return "reverse_candidate_divergence"
        return "execution_divergence_other"

    return "execution_equivalent_other"


def _serialize_effect(effect: dict[str, Any]) -> dict[str, Any]:
    return {
        "effect": str(effect.get("effect")),
        "side": local_packet._coerce_optional_str(effect.get("side")),
        "effective_size": _round_or_none(
            local_packet._coerce_optional_float(effect.get("effective_size"))
        ),
    }


def _serialize_row(
    row: dict[str, Any],
    *,
    effect: dict[str, Any],
) -> dict[str, Any]:
    position_before = local_packet._coerce_dict(
        row.get("position_before"), field_name="serialize_row.position_before"
    )
    return {
        "action": str(row.get("action") or "NONE"),
        "size": _round_or_none(local_packet._coerce_optional_float(row.get("size"))),
        "selected_policy": local_packet._coerce_optional_str(row.get("selected_policy")),
        "switch_reason": local_packet._coerce_optional_str(row.get("switch_reason")),
        "switch_control_mode": local_packet._coerce_optional_str(row.get("switch_control_mode")),
        "bars_since_regime_change": _round_or_none(
            local_packet._coerce_optional_float(row.get("bars_since_regime_change"))
        ),
        "zone": local_packet._coerce_optional_str(row.get("zone")),
        "action_edge": _round_or_none(local_packet._coerce_optional_float(row.get("action_edge"))),
        "confidence_gate": _round_or_none(
            local_packet._coerce_optional_float(row.get("confidence_gate"))
        ),
        "clarity_score": _round_or_none(
            local_packet._coerce_optional_float(row.get("clarity_score"))
        ),
        "position_before": {
            "has_position": bool(position_before.get("has_position", False)),
            "side": local_packet._coerce_optional_str(position_before.get("side")),
            "current_size": _round_or_none(
                local_packet._coerce_optional_float(position_before.get("current_size"))
            ),
            "entry_time": local_packet._coerce_optional_str(position_before.get("entry_time")),
        },
        "trade_event_count_before": int(
            local_packet._coerce_optional_float(row.get("trade_event_count_before")) or 0
        ),
        "execution_effect": _serialize_effect(effect),
    }


def _analyze_envelope_row(
    timestamp: str,
    baseline_raw: dict[str, Any] | None,
    release_zero_raw: dict[str, Any] | None,
) -> dict[str, Any]:
    baseline_row = _normalized_row(baseline_raw)
    release_zero_row = _normalized_row(release_zero_raw)
    baseline_effect = _execution_effect(baseline_row)
    release_zero_effect = _execution_effect(release_zero_row)

    row_changed = baseline_raw != release_zero_raw
    action_changed = str(baseline_row.get("action")) != str(release_zero_row.get("action"))
    size_changed = not _float_close(
        local_packet._coerce_optional_float(baseline_row.get("size")),
        local_packet._coerce_optional_float(release_zero_row.get("size")),
    )
    selected_policy_changed = local_packet._coerce_optional_str(
        baseline_row.get("selected_policy")
    ) != local_packet._coerce_optional_str(release_zero_row.get("selected_policy"))
    switch_reason_changed = local_packet._coerce_optional_str(
        baseline_row.get("switch_reason")
    ) != local_packet._coerce_optional_str(release_zero_row.get("switch_reason"))
    position_equivalent = _position_equivalent(baseline_row, release_zero_row)
    effect_equivalent = _effect_equivalent(baseline_effect, release_zero_effect)

    classification = _classify_row(
        row_changed=row_changed,
        action_changed=action_changed,
        size_changed=size_changed,
        selected_policy_changed=selected_policy_changed,
        switch_reason_changed=switch_reason_changed,
        position_equivalent=position_equivalent,
        effect_equivalent=effect_equivalent,
        baseline_row=baseline_row,
        release_zero_row=release_zero_row,
        baseline_effect=baseline_effect,
        release_zero_effect=release_zero_effect,
    )

    return {
        "timestamp": timestamp,
        "row_changed": row_changed,
        "action_changed": action_changed,
        "size_changed": size_changed,
        "selected_policy_changed": selected_policy_changed,
        "switch_reason_changed": switch_reason_changed,
        "position_before_equivalent": position_equivalent,
        "execution_effect_equivalent": effect_equivalent,
        "classification": classification,
        "baseline": _serialize_row(baseline_row, effect=baseline_effect),
        "release_zero": _serialize_row(release_zero_row, effect=release_zero_effect),
    }


def _row_summary(row_analyses: list[dict[str, Any]]) -> dict[str, Any]:
    classifications = [str(row["classification"]) for row in row_analyses]
    diff_rows = [row for row in row_analyses if bool(row["row_changed"])]
    return {
        "envelope_row_count": len(row_analyses),
        "identical_row_count": len([row for row in row_analyses if not bool(row["row_changed"])]),
        "diff_row_count": len(diff_rows),
        "action_diff_rows": len([row for row in row_analyses if bool(row["action_changed"])]),
        "size_diff_rows": len([row for row in row_analyses if bool(row["size_changed"])]),
        "selected_policy_diff_rows": len(
            [row for row in row_analyses if bool(row["selected_policy_changed"])]
        ),
        "switch_reason_diff_rows": len(
            [row for row in row_analyses if bool(row["switch_reason_changed"])]
        ),
        "position_before_diff_rows": len(
            [row for row in row_analyses if not bool(row["position_before_equivalent"])]
        ),
        "execution_effect_diff_rows": len(
            [row for row in row_analyses if not bool(row["execution_effect_equivalent"])]
        ),
        "router_internal_only_rows": len(
            [row for row in row_analyses if str(row["classification"]) == "router_internal_only"]
        ),
        "size_diff_absorbed_by_locked_position_rows": len(
            [
                row
                for row in row_analyses
                if str(row["classification"]) == "size_diff_absorbed_by_locked_position"
            ]
        ),
        "action_diff_absorbed_by_locked_position_rows": len(
            [
                row
                for row in row_analyses
                if str(row["classification"]) == "action_diff_absorbed_by_locked_position"
            ]
        ),
        "execution_divergence_rows": len(
            [
                row
                for row in row_analyses
                if str(row["classification"])
                in {
                    "flat_entry_divergence",
                    "reverse_candidate_divergence",
                    "position_context_divergence",
                    "execution_divergence_other",
                }
            ]
        ),
        "all_diff_rows_execution_equivalent": all(
            bool(row["execution_effect_equivalent"]) for row in diff_rows
        ),
        "classification_counts": _label_counts(classifications),
    }


def _subject_payload(
    spec: local_envelope.EnvelopeSubjectSpec,
    *,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    baseline = _run_case_with_action_position_rows(
        "baseline",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = _run_case_with_action_position_rows(
        "release_zero",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    observed_baseline_timestamps = tuple(baseline["continuation_release_timestamps"])
    observed_release_zero_timestamps = tuple(release_zero["continuation_release_timestamps"])
    if observed_baseline_timestamps != spec.baseline_timestamps:
        raise LocalActionPositionEquivalenceError(
            f"Baseline continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.baseline_timestamps}, actual={observed_baseline_timestamps}"
        )
    if observed_release_zero_timestamps != spec.release_zero_timestamps:
        raise LocalActionPositionEquivalenceError(
            f"Release-zero continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.release_zero_timestamps}, actual={observed_release_zero_timestamps}"
        )

    baseline_summary = local_packet._coerce_dict(
        baseline.get("summary"), field_name=f"{spec.subject_id}.baseline.summary"
    )
    release_zero_summary = local_packet._coerce_dict(
        release_zero.get("summary"), field_name=f"{spec.subject_id}.release_zero.summary"
    )
    total_return_diff = local_packet._coerce_float(
        release_zero_summary.get("total_return"),
        field_name=f"{spec.subject_id}.release_zero.total_return",
    ) - local_packet._coerce_float(
        baseline_summary.get("total_return"),
        field_name=f"{spec.subject_id}.baseline.total_return",
    )
    final_capital_diff = local_packet._coerce_float(
        release_zero_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.release_zero.final_capital",
    ) - local_packet._coerce_float(
        baseline_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.baseline.final_capital",
    )
    if not math.isclose(total_return_diff, spec.inventory_total_return_diff, abs_tol=1e-12):
        raise LocalActionPositionEquivalenceError(
            f"Monthly total return diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_total_return_diff}, actual={total_return_diff}"
        )
    if not math.isclose(final_capital_diff, spec.inventory_final_capital_diff, abs_tol=1e-9):
        raise LocalActionPositionEquivalenceError(
            f"Monthly final capital diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_final_capital_diff}, actual={final_capital_diff}"
        )

    baseline_rows = local_packet._coerce_dict(
        baseline.get("rows"), field_name=f"{spec.subject_id}.baseline.rows"
    )
    release_zero_rows = local_packet._coerce_dict(
        release_zero.get("rows"), field_name=f"{spec.subject_id}.release_zero.rows"
    )

    envelope_timestamps = [
        timestamp
        for timestamp in sorted(set(baseline_rows) | set(release_zero_rows))
        if spec.envelope_start <= str(timestamp) <= spec.envelope_end
    ]
    if len(envelope_timestamps) != spec.envelope_row_count:
        raise LocalActionPositionEquivalenceError(
            f"Envelope row-count drift for {spec.subject_id}: expected={spec.envelope_row_count}, actual={len(envelope_timestamps)}"
        )

    row_analyses = [
        _analyze_envelope_row(
            str(timestamp),
            baseline_rows.get(str(timestamp)),
            release_zero_rows.get(str(timestamp)),
        )
        for timestamp in envelope_timestamps
    ]
    row_summary = _row_summary(row_analyses)

    return {
        "subject_id": spec.subject_id,
        "role": spec.role,
        "month_window": {
            "start": spec.month_start,
            "end": spec.month_end,
            "inventory_total_return_diff": _round_or_none(spec.inventory_total_return_diff),
            "inventory_final_capital_diff": _round_or_none(spec.inventory_final_capital_diff),
        },
        "envelope_window": {
            "start": spec.envelope_start,
            "end": spec.envelope_end,
            "row_count": spec.envelope_row_count,
            "span_hours": _round_or_none(
                (
                    local_packet._parse_timestamp(spec.envelope_end)
                    - local_packet._parse_timestamp(spec.envelope_start)
                ).total_seconds()
                / 3600.0
            ),
        },
        "continuation_release_timestamp_validation": {
            "baseline_matches_local_packet": True,
            "release_zero_matches_local_packet": True,
        },
        "monthly_reproduction": {
            "top_line_sign": local_packet._sign_label(total_return_diff),
            "rerun_total_return_diff": _round_or_none(total_return_diff),
            "rerun_final_capital_diff": _round_or_none(final_capital_diff),
            "matches_local_packet_total_return_diff": True,
            "matches_local_packet_final_capital_diff": True,
        },
        "row_summary": row_summary,
        "envelope_row_analysis": row_analyses,
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = local_packet._coerce_dict(
        subject_payloads.get("2021-04"), field_name="equivalence.subject_payloads.2021-04"
    )
    control = local_packet._coerce_dict(
        subject_payloads.get("2023-05"), field_name="equivalence.subject_payloads.2023-05"
    )
    candidate_summary = local_packet._coerce_dict(
        candidate.get("row_summary"), field_name="candidate.row_summary"
    )
    control_summary = local_packet._coerce_dict(
        control.get("row_summary"), field_name="control.row_summary"
    )

    candidate_execution_divergence_rows = int(
        local_packet._coerce_float(
            candidate_summary.get("execution_divergence_rows"),
            field_name="candidate.execution_divergence_rows",
        )
    )
    control_execution_divergence_rows = int(
        local_packet._coerce_float(
            control_summary.get("execution_divergence_rows"),
            field_name="control.execution_divergence_rows",
        )
    )
    candidate_locked_size_rows = int(
        local_packet._coerce_float(
            candidate_summary.get("size_diff_absorbed_by_locked_position_rows"),
            field_name="candidate.size_diff_absorbed_by_locked_position_rows",
        )
    )
    control_locked_size_rows = int(
        local_packet._coerce_float(
            control_summary.get("size_diff_absorbed_by_locked_position_rows"),
            field_name="control.size_diff_absorbed_by_locked_position_rows",
        )
    )
    candidate_router_internal_rows = int(
        local_packet._coerce_float(
            candidate_summary.get("router_internal_only_rows"),
            field_name="candidate.router_internal_only_rows",
        )
    )
    control_router_internal_rows = int(
        local_packet._coerce_float(
            control_summary.get("router_internal_only_rows"),
            field_name="control.router_internal_only_rows",
        )
    )

    if candidate_execution_divergence_rows == 0 and control_execution_divergence_rows == 0:
        status = PACKET_STATUS_BOTH_ABSORBED
        inference = (
            "Both `2021-04` and `2023-05` keep the same execution-effect class on every envelope row. "
            "The candidate's extra negative-like structure therefore lives before execution, mainly as locked-"
            "position size/policy asymmetry rather than action or trade-path divergence."
        )
    elif candidate_execution_divergence_rows == 0:
        status = PACKET_STATUS_CANDIDATE_ABSORBED
        inference = (
            "`2021-04` stays absorbed before execution surface even though the control shows execution-surface "
            "divergence. The candidate's retained asymmetry remains pre-execution rather than economic."
        )
    else:
        status = PACKET_STATUS_CANDIDATE_DIVERGES
        inference = (
            "`2021-04` reaches execution-surface divergence inside the bounded envelope, so the retained local "
            "asymmetry is no longer confined to router-internal or locked-position state alone."
        )

    return {
        "status": status,
        "candidate_subject_id": "2021-04",
        "control_subject_id": "2023-05",
        "candidate_execution_divergence_rows": candidate_execution_divergence_rows,
        "control_execution_divergence_rows": control_execution_divergence_rows,
        "candidate_locked_position_size_diff_rows": candidate_locked_size_rows,
        "control_locked_position_size_diff_rows": control_locked_size_rows,
        "candidate_router_internal_only_rows": candidate_router_internal_rows,
        "control_router_internal_only_rows": control_router_internal_rows,
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a candidate-only local replay around the rows where "
            "locked-position size asymmetry persists, to test whether the negative-like signal is purely dormant or "
            "whether another non-economic state surface still separates it from the control."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "local_envelope_artifact": str(LOCAL_ENVELOPE_RELATIVE),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in local_packet.SUBJECT_DEFINITIONS],
            "focus_surface": "action, size, and pre-execution position equivalence inside the exact local envelope",
        },
    }


def run_local_action_position_equivalence() -> dict[str, Any]:
    envelope_specs = local_envelope._load_local_packet_specs()
    base_cfg, carrier_cfg, authority = local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: _subject_payload(
            envelope_specs[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in local_packet.SUBJECT_DEFINITIONS
    }
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-action-position-equivalence-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed local packet, rerun on the same carrier and "
                "compared only on action, size, and pre-execution position equivalence"
            ),
            "question": (
                "Inside the exact `2021-04` and `2023-05` local envelopes, do the retained baseline-vs-release_zero "
                "differences actually reach execution surface, or are they absorbed while both runs face the same "
                "pre-execution position context?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "local_envelope_artifact": str(LOCAL_ENVELOPE_RELATIVE),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in local_packet.SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "focus_surface": "action, size, router labels, and pre-execution position state",
            },
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_local_action_position_equivalence()
    except LocalActionPositionEquivalenceError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("packet_summary", {}).get("status", result.get("status")),
        "candidate_execution_divergence_rows": result.get("packet_summary", {}).get(
            "candidate_execution_divergence_rows"
        ),
        "control_execution_divergence_rows": result.get("packet_summary", {}).get(
            "control_execution_divergence_rows"
        ),
        "candidate_subject_id": result.get("packet_summary", {}).get("candidate_subject_id"),
        "control_subject_id": result.get("packet_summary", {}).get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
