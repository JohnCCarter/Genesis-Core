from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
WAVE_DISCRIMINATOR_RELATIVE = Path(
    "results/evaluation/ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json"
)
TAXONOMY_PASS_RELATIVE = Path(
    "results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json"
)
ACTION_DIFF_2017_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "2017_enabled_vs_absent_action_diffs.json"
)
LOCAL_WINDOW_2017_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_clean_continuation_holdout_generalization_pass_2026-05-25.json"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
MAX_ADJACENCY_GAP = timedelta(hours=24)
STATUS_FAIL_CLOSED = "holdout_generalization_fail_closed"
STATUS_FALSIFIED = "absolute_clean_continuation_age_split_falsified_on_holdouts"
STATUS_PARTIAL = "absolute_clean_continuation_age_split_partial_overlap_on_holdouts"


class HoldoutGeneralizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class NormalizedDecisionRow:
    timestamp: datetime
    bars_since_regime_change: float
    action_edge: float
    confidence_gate: float
    clarity_score: float
    zone: str
    selected_policy: str | None
    switch_reason: str | None
    previous_policy: str | None
    phase_label: str | None


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HoldoutGeneralizationError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise HoldoutGeneralizationError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise HoldoutGeneralizationError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_optional_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise HoldoutGeneralizationError(f"Expected string-or-null for {field_name}, got {value!r}")
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise HoldoutGeneralizationError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _parse_timestamp(raw: Any, *, field_name: str) -> datetime:
    timestamp = _coerce_str(raw, field_name=field_name)
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HoldoutGeneralizationError(
            f"Invalid timestamp for {field_name}: {timestamp!r}"
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _git_head_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        raise HoldoutGeneralizationError("Expected at least one numeric value to summarize")
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "mean": _round_or_none(sum(values) / len(values)),
        "max": _round_or_none(max(values)),
        "gt_zero_share": _round_or_none(sum(value > 0 for value in values) / len(values)),
    }


def _label_counts(values: list[str | None]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for value in values:
        label = value if value is not None else "<missing>"
        counts[label] = counts.get(label, 0) + 1
    return [
        {"label": label, "count": count}
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _group_adjacent_rows(rows: list[NormalizedDecisionRow]) -> list[list[NormalizedDecisionRow]]:
    if not rows:
        return []
    grouped: list[list[NormalizedDecisionRow]] = [[rows[0]]]
    for row in rows[1:]:
        if row.timestamp - grouped[-1][-1].timestamp <= MAX_ADJACENCY_GAP:
            grouped[-1].append(row)
        else:
            grouped.append([row])
    return grouped


def _serialize_window(window: list[NormalizedDecisionRow]) -> dict[str, Any]:
    start = window[0].timestamp
    end = window[-1].timestamp
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "row_count": len(window),
        "span_hours": _round_or_none((end - start).total_seconds() / 3600.0),
        "bars_since_regime_change": _numeric_summary(
            [row.bars_since_regime_change for row in window]
        ),
        "timestamps": [row.timestamp.isoformat() for row in window],
    }


def _normalize_taxonomy_row(row: dict[str, Any]) -> NormalizedDecisionRow:
    return NormalizedDecisionRow(
        timestamp=_parse_timestamp(row.get("timestamp"), field_name="taxonomy.timestamp"),
        bars_since_regime_change=_coerce_float(
            row.get("bars_since_regime_change"),
            field_name="taxonomy.bars_since_regime_change",
        ),
        action_edge=_coerce_float(row.get("action_edge"), field_name="taxonomy.action_edge"),
        confidence_gate=_coerce_float(
            row.get("confidence_gate"),
            field_name="taxonomy.confidence_gate",
        ),
        clarity_score=_coerce_float(
            row.get("clarity_score"),
            field_name="taxonomy.clarity_score",
        ),
        zone=_coerce_str(row.get("zone"), field_name="taxonomy.zone"),
        selected_policy=_coerce_optional_str(
            row.get("selected_policy"),
            field_name="taxonomy.selected_policy",
        ),
        switch_reason=_coerce_optional_str(
            row.get("switch_reason"),
            field_name="taxonomy.switch_reason",
        ),
        previous_policy=_coerce_optional_str(
            row.get("previous_policy"),
            field_name="taxonomy.previous_policy",
        ),
        phase_label=_coerce_optional_str(
            row.get("phase_label"),
            field_name="taxonomy.phase_label",
        ),
    )


def _load_taxonomy_subject_rows(subject_id: str) -> list[NormalizedDecisionRow]:
    payload = _coerce_dict(_load_json(TAXONOMY_PASS_RELATIVE), field_name="taxonomy_payload")
    subjects = _coerce_dict(payload.get("subjects"), field_name="taxonomy_payload.subjects")
    subject = _coerce_dict(subjects.get(subject_id), field_name=f"taxonomy.subjects.{subject_id}")
    rows = _coerce_list(subject.get("rows"), field_name=f"taxonomy.subjects.{subject_id}.rows")
    normalized = [
        _normalize_taxonomy_row(_coerce_dict(row, field_name="taxonomy.row")) for row in rows
    ]
    if not normalized:
        raise HoldoutGeneralizationError(f"No taxonomy rows materialized for subject {subject_id}")
    return sorted(normalized, key=lambda row: row.timestamp)


def _normalize_annual_2017_row(row: dict[str, Any]) -> NormalizedDecisionRow | None:
    timestamp = _parse_timestamp(row.get("timestamp"), field_name="annual_2017.timestamp")
    if (timestamp.year, timestamp.month) != (2017, 3):
        return None

    enabled = _coerce_dict(row.get("enabled"), field_name="annual_2017.enabled")
    absent = _coerce_dict(row.get("absent"), field_name="annual_2017.absent")
    enabled_action = _coerce_str(enabled.get("action"), field_name="annual_2017.enabled.action")
    absent_action = _coerce_str(absent.get("action"), field_name="annual_2017.absent.action")
    if (absent_action, enabled_action) != ("NONE", "LONG"):
        return None

    router_debug = _coerce_dict(
        enabled.get("router_debug"),
        field_name="annual_2017.enabled.router_debug",
    )
    zone = _coerce_str(router_debug.get("zone"), field_name="annual_2017.zone")
    switch_reason = _coerce_str(
        router_debug.get("switch_reason"),
        field_name="annual_2017.switch_reason",
    )
    if zone != "low" or switch_reason != "stable_continuation_state":
        return None

    return NormalizedDecisionRow(
        timestamp=timestamp,
        bars_since_regime_change=_coerce_float(
            router_debug.get("bars_since_regime_change"),
            field_name="annual_2017.bars_since_regime_change",
        ),
        action_edge=_coerce_float(
            router_debug.get("action_edge"),
            field_name="annual_2017.action_edge",
        ),
        confidence_gate=_coerce_float(
            router_debug.get("confidence_gate"),
            field_name="annual_2017.confidence_gate",
        ),
        clarity_score=_coerce_float(
            router_debug.get("clarity_score"),
            field_name="annual_2017.clarity_score",
        ),
        zone=zone,
        selected_policy=_coerce_optional_str(
            router_debug.get("selected_policy"),
            field_name="annual_2017.selected_policy",
        ),
        switch_reason=switch_reason,
        previous_policy=_coerce_optional_str(
            router_debug.get("previous_policy"),
            field_name="annual_2017.previous_policy",
        ),
        phase_label=_coerce_optional_str(
            router_debug.get("phase_label"),
            field_name="annual_2017.phase_label",
        ),
    )


def _load_2017_continuation_rows() -> list[NormalizedDecisionRow]:
    payload = _coerce_list(_load_json(ACTION_DIFF_2017_RELATIVE), field_name="annual_2017_payload")
    rows: list[NormalizedDecisionRow] = []
    for item in payload:
        normalized = _normalize_annual_2017_row(_coerce_dict(item, field_name="annual_2017.row"))
        if normalized is not None:
            rows.append(normalized)
    rows = sorted(rows, key=lambda row: row.timestamp)
    if not rows:
        raise HoldoutGeneralizationError("No March 2017 continuation-family rows materialized")
    return rows


def _feature_overlap(
    subject_summary: dict[str, Any], reference_summary: dict[str, Any]
) -> dict[str, Any]:
    subject_min = float(subject_summary["min"])
    subject_max = float(subject_summary["max"])
    reference_min = float(reference_summary["min"])
    reference_max = float(reference_summary["max"])
    overlap = not (subject_max < reference_min or subject_min > reference_max)
    within = subject_min >= reference_min and subject_max <= reference_max
    if subject_max < reference_min:
        position = "below_reference_range"
        distance = reference_min - subject_max
    elif subject_min > reference_max:
        position = "above_reference_range"
        distance = subject_min - reference_max
    else:
        position = "overlaps_reference_range"
        distance = 0.0
    return {
        "overlaps_reference_range": overlap,
        "within_reference_range": within,
        "position": position,
        "distance_to_reference_range": _round_or_none(distance),
    }


def _holdout_transport_verdict(
    bars_summary: dict[str, Any],
    *,
    reference_range: dict[str, Any],
    threshold: float,
) -> dict[str, Any]:
    bars_min = float(bars_summary["min"])
    bars_max = float(bars_summary["max"])
    threshold_overlap = not (bars_max < threshold or bars_min > threshold)
    wave_one_side_count = int(sum(value <= threshold for value in bars_summary["values"]))
    wave_two_side_count = int(sum(value > threshold for value in bars_summary["values"]))
    boundary_count = int(sum(value == threshold for value in bars_summary["values"]))
    overlap_summary = _feature_overlap(bars_summary, reference_range)
    if overlap_summary["position"] == "below_reference_range":
        verdict = "outside_reference_envelope_lower"
    elif overlap_summary["position"] == "above_reference_range":
        verdict = "outside_reference_envelope_higher"
    elif wave_one_side_count and wave_two_side_count:
        verdict = "crosses_reference_boundary"
    elif wave_one_side_count:
        verdict = "overlaps_reference_wave_one_side_only"
    else:
        verdict = "overlaps_reference_wave_two_side_only"
    return {
        "verdict": verdict,
        "threshold": _round_or_none(threshold),
        "threshold_overlap": threshold_overlap,
        "wave_one_side_count": wave_one_side_count,
        "wave_two_side_count": wave_two_side_count,
        "boundary_count": boundary_count,
        "reference_range_overlap": overlap_summary,
    }


def _decision_time_summary(rows: list[NormalizedDecisionRow]) -> dict[str, Any]:
    return {
        "bars_since_regime_change": _numeric_summary(
            [row.bars_since_regime_change for row in rows]
        ),
        "action_edge": _numeric_summary([row.action_edge for row in rows]),
        "confidence_gate": _numeric_summary([row.confidence_gate for row in rows]),
        "clarity_score": _numeric_summary([row.clarity_score for row in rows]),
        "zone_counts": _label_counts([row.zone for row in rows]),
        "selected_policy_counts": _label_counts([row.selected_policy for row in rows]),
        "switch_reason_counts": _label_counts([row.switch_reason for row in rows]),
        "previous_policy_counts": _label_counts([row.previous_policy for row in rows]),
        "phase_label_counts": _label_counts([row.phase_label for row in rows]),
    }


def _reference_rule() -> dict[str, Any]:
    payload = _coerce_dict(_load_json(WAVE_DISCRIMINATOR_RELATIVE), field_name="wave_discriminator")
    numeric_features = _coerce_dict(
        _coerce_dict(
            payload.get("decision_time_comparison"),
            field_name="wave_discriminator.decision_time_comparison",
        ).get("numeric_features"),
        field_name="wave_discriminator.numeric_features",
    )
    bars_feature = _coerce_dict(
        numeric_features.get("bars_since_regime_change"),
        field_name="wave_discriminator.numeric_features.bars_since_regime_change",
    )
    best_rules = _coerce_list(
        _coerce_dict(
            payload.get("single_feature_rule_search"),
            field_name="wave_discriminator.single_feature_rule_search",
        ).get("best_rule_per_feature"),
        field_name="wave_discriminator.best_rule_per_feature",
    )
    selected_rule: dict[str, Any] | None = None
    for item in best_rules:
        rule = _coerce_dict(item, field_name="wave_discriminator.rule")
        if rule.get("feature") == "bars_since_regime_change":
            selected_rule = rule
            break
    if selected_rule is None:
        raise HoldoutGeneralizationError(
            "Wave discriminator artifact does not contain a bars_since_regime_change rule"
        )

    wave_one_summary = _coerce_dict(
        bars_feature.get("wave_one"), field_name="bars_feature.wave_one"
    )
    wave_two_summary = _coerce_dict(
        bars_feature.get("wave_two"), field_name="bars_feature.wave_two"
    )
    combined_summary = {
        "min": min(float(wave_one_summary["min"]), float(wave_two_summary["min"])),
        "max": max(float(wave_one_summary["max"]), float(wave_two_summary["max"])),
    }
    return {
        "feature": "bars_since_regime_change",
        "operator": _coerce_str(selected_rule.get("operator"), field_name="rule.operator"),
        "threshold": _coerce_float(selected_rule.get("threshold"), field_name="rule.threshold"),
        "positive_wave": _coerce_str(
            selected_rule.get("positive_wave"),
            field_name="rule.positive_wave",
        ),
        "accuracy": _coerce_float(selected_rule.get("accuracy"), field_name="rule.accuracy"),
        "reference_envelopes": {
            "wave_one": {
                "count": int(wave_one_summary["count"]),
                "min": _round_or_none(float(wave_one_summary["min"])),
                "mean": _round_or_none(float(wave_one_summary["mean"])),
                "max": _round_or_none(float(wave_one_summary["max"])),
            },
            "wave_two": {
                "count": int(wave_two_summary["count"]),
                "min": _round_or_none(float(wave_two_summary["min"])),
                "mean": _round_or_none(float(wave_two_summary["mean"])),
                "max": _round_or_none(float(wave_two_summary["max"])),
            },
            "combined": {
                "min": _round_or_none(combined_summary["min"]),
                "max": _round_or_none(combined_summary["max"]),
            },
        },
    }


def _combined_reference_feature_ranges() -> dict[str, dict[str, Any]]:
    payload = _coerce_dict(_load_json(WAVE_DISCRIMINATOR_RELATIVE), field_name="wave_discriminator")
    numeric_features = _coerce_dict(
        _coerce_dict(
            payload.get("decision_time_comparison"),
            field_name="wave_discriminator.decision_time_comparison",
        ).get("numeric_features"),
        field_name="wave_discriminator.numeric_features",
    )
    combined: dict[str, dict[str, Any]] = {}
    for feature_name in (
        "bars_since_regime_change",
        "action_edge",
        "confidence_gate",
        "clarity_score",
    ):
        feature_payload = _coerce_dict(
            numeric_features.get(feature_name),
            field_name=f"wave_discriminator.numeric_features.{feature_name}",
        )
        wave_one = _coerce_dict(
            feature_payload.get("wave_one"), field_name=f"{feature_name}.wave_one"
        )
        wave_two = _coerce_dict(
            feature_payload.get("wave_two"), field_name=f"{feature_name}.wave_two"
        )
        combined[feature_name] = {
            "min": _round_or_none(min(float(wave_one["min"]), float(wave_two["min"]))),
            "max": _round_or_none(max(float(wave_one["max"]), float(wave_two["max"]))),
        }
    return combined


def _subject_summary(
    subject_id: str,
    rows: list[NormalizedDecisionRow],
    *,
    source_kind: str,
    reference_rule: dict[str, Any],
    reference_feature_ranges: dict[str, dict[str, Any]],
    support_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision_time_state = _decision_time_summary(rows)
    bars_values = [row.bars_since_regime_change for row in rows]
    bars_summary = dict(decision_time_state["bars_since_regime_change"])
    bars_summary["values"] = bars_values
    windows = [_serialize_window(window) for window in _group_adjacent_rows(rows)]
    window_sizes_desc = [
        int(window["row_count"])
        for window in sorted(
            windows,
            key=lambda window: (-int(window["row_count"]), str(window["start"])),
        )
    ]
    feature_transport = {
        feature_name: _feature_overlap(
            _coerce_dict(
                decision_time_state[feature_name], field_name=f"decision_time_state.{feature_name}"
            ),
            reference_range,
        )
        for feature_name, reference_range in reference_feature_ranges.items()
    }
    return {
        "subject_id": subject_id,
        "source_kind": source_kind,
        "row_count": len(rows),
        "decision_time_state": decision_time_state,
        "feature_transport_vs_reference": feature_transport,
        "threshold_transport": _holdout_transport_verdict(
            bars_summary,
            reference_range=_coerce_dict(
                reference_rule["reference_envelopes"]["combined"],
                field_name="reference_rule.reference_envelopes.combined",
            ),
            threshold=float(reference_rule["threshold"]),
        ),
        "window_count": len(windows),
        "window_size_sequence_desc": window_sizes_desc,
        "largest_windows": sorted(
            windows,
            key=lambda window: (-int(window["row_count"]), str(window["start"])),
        )[:3],
        "visible_family_match": {
            "absent_action": "NONE",
            "enabled_action": "LONG",
            "zone": decision_time_state["zone_counts"],
            "switch_reason": decision_time_state["switch_reason_counts"],
        },
        "support_context": support_context,
    }


def _load_2017_support_context() -> dict[str, Any]:
    payload = _coerce_dict(_load_json(LOCAL_WINDOW_2017_RELATIVE), field_name="local_window_2017")
    subject_summaries = _coerce_dict(
        payload.get("subject_summaries"),
        field_name="local_window_2017.subject_summaries",
    )
    march = _coerce_dict(
        subject_summaries.get("2017-03"), field_name="local_window_2017.subject_summaries.2017-03"
    )
    return {
        "source_artifact": str(LOCAL_WINDOW_2017_RELATIVE),
        "continuation_row_count": int(march["continuation_row_count"]),
        "window_count": int(march["window_count"]),
        "largest_window": _coerce_dict(
            march.get("largest_window"), field_name="local_window_2017.largest_window"
        ),
        "top_two_window_share": _coerce_float(
            march.get("top_two_window_share"),
            field_name="local_window_2017.top_two_window_share",
        ),
    }


def _transport_summary(holdouts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    bars_overlap_count = sum(
        bool(
            _coerce_dict(
                holdout["feature_transport_vs_reference"]["bars_since_regime_change"],
                field_name="holdout.feature_transport_vs_reference.bars_since_regime_change",
            )["overlaps_reference_range"]
        )
        for holdout in holdouts.values()
    )
    non_age_feature_overlap_counts = {}
    for feature_name in ("action_edge", "confidence_gate", "clarity_score"):
        non_age_feature_overlap_counts[feature_name] = sum(
            bool(
                _coerce_dict(
                    holdout["feature_transport_vs_reference"][feature_name],
                    field_name=f"holdout.feature_transport_vs_reference.{feature_name}",
                )["overlaps_reference_range"]
            )
            for holdout in holdouts.values()
        )
    if bars_overlap_count == 0:
        status = STATUS_FALSIFIED
    else:
        status = STATUS_PARTIAL
    return {
        "status": status,
        "holdouts_evaluated": list(holdouts.keys()),
        "bars_overlap_holdout_count": bars_overlap_count,
        "non_age_feature_overlap_counts": non_age_feature_overlap_counts,
        "inference": (
            "The learned clean-continuation split remains carrier-local in absolute regime-age terms; "
            "holdouts can preserve the visible continuation shell while living far below the 2023-12 "
            "absolute bars_since_regime_change envelope."
        ),
        "next_hypothesis": (
            "A transportable phase-age discriminator likely needs subject-local normalization "
            "instead of a raw absolute bars_since_regime_change threshold."
        ),
    }


def run_holdout_generalization_pass() -> dict[str, Any]:
    reference_rule = _reference_rule()
    reference_feature_ranges = _combined_reference_feature_ranges()
    wave_one_rows = _load_taxonomy_subject_rows("continuation_2023_wave_one")
    wave_two_rows = _load_taxonomy_subject_rows("continuation_2023_wave_two")
    harmful_displacement_rows = _load_taxonomy_subject_rows("harmful_2024_displacement")
    continuation_2017_rows = _load_2017_continuation_rows()

    reference_subjects = {
        "continuation_2023_wave_one": _subject_summary(
            "continuation_2023_wave_one",
            wave_one_rows,
            source_kind="taxonomy_clean_continuation_reference",
            reference_rule=reference_rule,
            reference_feature_ranges=reference_feature_ranges,
        ),
        "continuation_2023_wave_two": _subject_summary(
            "continuation_2023_wave_two",
            wave_two_rows,
            source_kind="taxonomy_clean_continuation_reference",
            reference_rule=reference_rule,
            reference_feature_ranges=reference_feature_ranges,
        ),
    }
    holdout_subjects = {
        "harmful_2024_displacement": _subject_summary(
            "harmful_2024_displacement",
            harmful_displacement_rows,
            source_kind="taxonomy_clean_continuation_holdout",
            reference_rule=reference_rule,
            reference_feature_ranges=reference_feature_ranges,
        ),
        "2017_03_continuation_family": _subject_summary(
            "2017_03_continuation_family",
            continuation_2017_rows,
            source_kind="annual_enabled_vs_absent_continuation_family_holdout",
            reference_rule=reference_rule,
            reference_feature_ranges=reference_feature_ranges,
            support_context=_load_2017_support_context(),
        ),
    }

    return {
        "audit_version": "ri-policy-router-clean-continuation-holdout-generalization-pass-2026-05-25",
        "base_sha": _git_head_sha(),
        "observational_only": True,
        "non_authoritative": True,
        "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        "inputs": {
            "reference_rule_artifact": str(WAVE_DISCRIMINATOR_RELATIVE),
            "taxonomy_artifact": str(TAXONOMY_PASS_RELATIVE),
            "annual_2017_action_diff_surface": str(ACTION_DIFF_2017_RELATIVE),
            "continuation_local_window_reference_2017": str(LOCAL_WINDOW_2017_RELATIVE),
        },
        "reference_rule": reference_rule,
        "reference_subjects": reference_subjects,
        "holdout_subjects": holdout_subjects,
        "transport_summary": _transport_summary(holdout_subjects),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-clean-continuation-holdout-generalization-pass-2026-05-25",
        "base_sha": _git_head_sha(),
        "observational_only": True,
        "non_authoritative": True,
        "status": STATUS_FAIL_CLOSED,
        "failure_reason": reason,
        "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        "inputs": {
            "reference_rule_artifact": str(WAVE_DISCRIMINATOR_RELATIVE),
            "taxonomy_artifact": str(TAXONOMY_PASS_RELATIVE),
            "annual_2017_action_diff_surface": str(ACTION_DIFF_2017_RELATIVE),
            "continuation_local_window_reference_2017": str(LOCAL_WINDOW_2017_RELATIVE),
        },
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_holdout_generalization_pass()
    except HoldoutGeneralizationError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("transport_summary", {}).get("status", result.get("status")),
        "reference_threshold": result.get("reference_rule", {}).get("threshold"),
        "holdout_bars_ranges": {
            subject_id: holdout["decision_time_state"]["bars_since_regime_change"]
            for subject_id, holdout in result.get("holdout_subjects", {}).items()
        },
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
