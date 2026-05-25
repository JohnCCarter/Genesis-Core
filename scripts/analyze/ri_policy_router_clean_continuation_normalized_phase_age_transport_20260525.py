from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
TAXONOMY_PASS_RELATIVE = Path(
    "results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json"
)
WAVE_DISCRIMINATOR_RELATIVE = Path(
    "results/evaluation/ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json"
)
PRIOR_HOLDOUT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_clean_continuation_holdout_generalization_pass_2026-05-25.json"
)
ACTION_DIFF_2017_RELATIVE = Path(
    "results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/"
    "2017_enabled_vs_absent_action_diffs.json"
)
LOCAL_WINDOW_2017_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json"
)
CHRONOLOGY_REFERENCE_RELATIVE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_clean_continuation_normalized_phase_age_transport_2026-05-25.json"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
EXPECTED_STATE_LABEL = "clean_continuation"
MAX_ADJACENCY_GAP = timedelta(hours=24)
STATUS_OK = "normalized_phase_age_transport_check_generated"
STATUS_FAIL_CLOSED = "normalized_phase_age_transport_check_fail_closed"
TRANSPORT_STATUS_PARTIAL = "subject_relative_normalized_phase_age_partially_recovers_transport"
TRANSPORT_STATUS_FAIL = "subject_relative_normalized_phase_age_not_materialized"
FEATURE_FAMILIES = {
    "baseline": ("bars_since_regime_change",),
    "subject_relative": (
        "subject_offset_from_floor",
        "subject_progress_pct",
        "subject_rank_pct",
    ),
    "window_relative": (
        "window_offset_from_start",
        "window_progress_pct",
        "window_rank_pct",
    ),
}
FEATURES = tuple(feature for family in FEATURE_FAMILIES.values() for feature in family)


class NormalizedPhaseAgeTransportError(RuntimeError):
    pass


@dataclass(frozen=True)
class DecisionRow:
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
    cohort_label: str | None


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise NormalizedPhaseAgeTransportError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise NormalizedPhaseAgeTransportError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise NormalizedPhaseAgeTransportError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_optional_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise NormalizedPhaseAgeTransportError(
            f"Expected string-or-null for {field_name}, got {value!r}"
        )
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise NormalizedPhaseAgeTransportError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _parse_timestamp(raw: Any, *, field_name: str) -> datetime:
    timestamp = _coerce_str(raw, field_name=field_name)
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise NormalizedPhaseAgeTransportError(
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
        raise NormalizedPhaseAgeTransportError("Expected at least one numeric value to summarize")
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "mean": _round_or_none(fmean(values)),
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


def _group_adjacent_rows(rows: list[DecisionRow]) -> list[list[DecisionRow]]:
    if not rows:
        return []
    grouped: list[list[DecisionRow]] = [[rows[0]]]
    for row in rows[1:]:
        if row.timestamp - grouped[-1][-1].timestamp <= MAX_ADJACENCY_GAP:
            grouped[-1].append(row)
        else:
            grouped.append([row])
    return grouped


def _normalize_taxonomy_row(row: dict[str, Any]) -> DecisionRow:
    return DecisionRow(
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
        cohort_label=_coerce_optional_str(
            row.get("cohort_label"),
            field_name="taxonomy.cohort_label",
        ),
    )


def _load_taxonomy_subject_rows(subject_id: str) -> tuple[list[DecisionRow], dict[str, Any]]:
    payload = _coerce_dict(_load_json(TAXONOMY_PASS_RELATIVE), field_name="taxonomy_payload")
    subjects = _coerce_dict(payload.get("subjects"), field_name="taxonomy_payload.subjects")
    subject = _coerce_dict(subjects.get(subject_id), field_name=f"taxonomy.subjects.{subject_id}")
    if subject.get("dominant_state_label") != EXPECTED_STATE_LABEL:
        raise NormalizedPhaseAgeTransportError(
            f"Taxonomy subject {subject_id!r} is not locked as clean_continuation"
        )
    rows = _coerce_list(subject.get("rows"), field_name=f"taxonomy.subjects.{subject_id}.rows")
    normalized = [
        _normalize_taxonomy_row(_coerce_dict(row, field_name="taxonomy.row")) for row in rows
    ]
    if not normalized:
        raise NormalizedPhaseAgeTransportError(
            f"No rows materialized for taxonomy subject {subject_id}"
        )
    return sorted(normalized, key=lambda row: row.timestamp), subject


def _normalize_annual_2017_row(row: dict[str, Any]) -> DecisionRow | None:
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
        enabled.get("router_debug"), field_name="annual_2017.enabled.router_debug"
    )
    zone = _coerce_str(router_debug.get("zone"), field_name="annual_2017.zone")
    switch_reason = _coerce_str(
        router_debug.get("switch_reason"), field_name="annual_2017.switch_reason"
    )
    if zone != "low" or switch_reason != "stable_continuation_state":
        return None

    return DecisionRow(
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
        cohort_label=None,
    )


def _load_2017_continuation_rows() -> list[DecisionRow]:
    payload = _coerce_list(_load_json(ACTION_DIFF_2017_RELATIVE), field_name="annual_2017_payload")
    rows: list[DecisionRow] = []
    for item in payload:
        normalized = _normalize_annual_2017_row(_coerce_dict(item, field_name="annual_2017.row"))
        if normalized is not None:
            rows.append(normalized)
    rows = sorted(rows, key=lambda row: row.timestamp)
    if not rows:
        raise NormalizedPhaseAgeTransportError(
            "No March 2017 continuation-family rows materialized"
        )
    return rows


def _load_prior_holdout_status() -> str:
    payload = _coerce_dict(_load_json(PRIOR_HOLDOUT_RELATIVE), field_name="prior_holdout_payload")
    transport_summary = _coerce_dict(
        payload.get("transport_summary"), field_name="prior_holdout_payload.transport_summary"
    )
    return _coerce_str(transport_summary.get("status"), field_name="prior_holdout_status")


def _load_named_2017_window_specs() -> dict[str, dict[str, Any]]:
    payload = _coerce_dict(_load_json(LOCAL_WINDOW_2017_RELATIVE), field_name="local_window_2017")
    subject_summaries = _coerce_dict(
        payload.get("subject_summaries"), field_name="local_window_2017.subject_summaries"
    )
    march = _coerce_dict(subject_summaries.get("2017-03"), field_name="local_window_2017.2017-03")
    chronological_windows = _coerce_list(
        march.get("chronological_windows"), field_name="local_window_2017.chronological_windows"
    )
    retained = [
        _coerce_dict(window, field_name="local_window_2017.window")
        for window in chronological_windows
        if int(_coerce_float(window.get("row_count"), field_name="local_window_2017.row_count"))
        >= 3
    ]
    retained = sorted(retained, key=lambda window: str(window["start"]))
    if len(retained) < 3:
        raise NormalizedPhaseAgeTransportError(
            "Could not recover the three retained 2017-03 chronology windows"
        )
    names = (
        "2017_03_early_anchor",
        "2017_03_late_revisit",
        "2017_03_month_end_revisit",
    )
    return dict(zip(names, retained[:3], strict=True))


def _window_timestamp_set(window_spec: dict[str, Any]) -> set[datetime]:
    timestamps = _coerce_list(window_spec.get("timestamps"), field_name="window_spec.timestamps")
    return {
        _parse_timestamp(timestamp, field_name="window_spec.timestamp") for timestamp in timestamps
    }


def _extract_named_2017_windows(rows: list[DecisionRow]) -> dict[str, list[DecisionRow]]:
    grouped = _group_adjacent_rows(rows)
    grouped_by_signature = {
        tuple(window_row.timestamp.isoformat() for window_row in window): window
        for window in grouped
    }
    named_specs = _load_named_2017_window_specs()
    extracted: dict[str, list[DecisionRow]] = {}
    for name, spec in named_specs.items():
        timestamps = tuple(
            sorted(timestamp.isoformat() for timestamp in _window_timestamp_set(spec))
        )
        window = grouped_by_signature.get(timestamps)
        if window is None:
            raise NormalizedPhaseAgeTransportError(
                f"Named 2017 holdout window {name!r} could not be recovered from the annual surface"
            )
        extracted[name] = window
    return extracted


def _extract_named_2017_augmented_windows(
    augmented_rows: list[dict[str, Any]],
    raw_windows: dict[str, list[DecisionRow]],
) -> dict[str, list[dict[str, Any]]]:
    rows_by_timestamp = {str(row["timestamp"]): row for row in augmented_rows}
    extracted: dict[str, list[dict[str, Any]]] = {}
    for name, window in raw_windows.items():
        extracted[name] = [
            {**rows_by_timestamp[row.timestamp.isoformat()], "subject_id": name} for row in window
        ]
    return extracted


def _augment_rows(rows: list[DecisionRow], *, subject_id: str) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: row.timestamp)
    grouped = _group_adjacent_rows(ordered)
    subject_min = min(row.bars_since_regime_change for row in ordered)
    subject_max = max(row.bars_since_regime_change for row in ordered)
    subject_span = subject_max - subject_min
    subject_count = len(ordered)
    window_membership: dict[datetime, dict[str, Any]] = {}
    for window_index, window in enumerate(grouped):
        window_min = min(row.bars_since_regime_change for row in window)
        window_max = max(row.bars_since_regime_change for row in window)
        window_span = window_max - window_min
        for position, row in enumerate(window):
            window_membership[row.timestamp] = {
                "window_index": window_index,
                "window_min": window_min,
                "window_max": window_max,
                "window_span": window_span,
                "window_count": len(window),
                "window_position": position,
                "window_start": window[0].timestamp.isoformat(),
                "window_end": window[-1].timestamp.isoformat(),
            }

    augmented: list[dict[str, Any]] = []
    for subject_position, row in enumerate(ordered):
        membership = window_membership[row.timestamp]
        subject_offset = row.bars_since_regime_change - subject_min
        window_offset = row.bars_since_regime_change - float(membership["window_min"])
        augmented.append(
            {
                "subject_id": subject_id,
                "timestamp": row.timestamp.isoformat(),
                "bars_since_regime_change": _round_or_none(row.bars_since_regime_change),
                "action_edge": _round_or_none(row.action_edge),
                "confidence_gate": _round_or_none(row.confidence_gate),
                "clarity_score": _round_or_none(row.clarity_score),
                "zone": row.zone,
                "selected_policy": row.selected_policy,
                "switch_reason": row.switch_reason,
                "previous_policy": row.previous_policy,
                "phase_label": row.phase_label,
                "cohort_label": row.cohort_label,
                "subject_offset_from_floor": _round_or_none(subject_offset),
                "subject_progress_pct": _round_or_none(
                    0.0 if subject_span == 0 else subject_offset / subject_span
                ),
                "subject_rank_pct": _round_or_none(
                    0.0 if subject_count == 1 else subject_position / (subject_count - 1)
                ),
                "window_offset_from_start": _round_or_none(window_offset),
                "window_progress_pct": _round_or_none(
                    0.0
                    if float(membership["window_span"]) == 0.0
                    else window_offset / float(membership["window_span"])
                ),
                "window_rank_pct": _round_or_none(
                    0.0
                    if int(membership["window_count"]) == 1
                    else int(membership["window_position"]) / (int(membership["window_count"]) - 1)
                ),
                "window_index": int(membership["window_index"]),
                "window_position": int(membership["window_position"]),
                "window_start": membership["window_start"],
                "window_end": membership["window_end"],
            }
        )
    return augmented


def _reference_wave_rows(
    combined_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    wave_one = [row for row in combined_rows if row.get("cohort_label") == "continuation_wave_one"]
    wave_two = [row for row in combined_rows if row.get("cohort_label") == "continuation_wave_two"]
    if not wave_one or not wave_two:
        raise NormalizedPhaseAgeTransportError(
            "Combined 2023 clean-continuation subject could not be split into wave_one and wave_two"
        )
    return wave_one, wave_two


def _numeric_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if isinstance(row.get(key), int | float)]


def _describe_numeric_feature(
    wave_one_rows: list[dict[str, Any]],
    wave_two_rows: list[dict[str, Any]],
    *,
    feature: str,
) -> dict[str, Any]:
    wave_one_values = _numeric_values(wave_one_rows, feature)
    wave_two_values = _numeric_values(wave_two_rows, feature)
    if not wave_one_values or not wave_two_values:
        raise NormalizedPhaseAgeTransportError(
            f"Numeric feature {feature!r} missing on one of the reference waves"
        )

    wave_one_min = min(wave_one_values)
    wave_one_max = max(wave_one_values)
    wave_two_min = min(wave_two_values)
    wave_two_max = max(wave_two_values)
    disjoint = wave_one_max < wave_two_min or wave_two_max < wave_one_min
    separating_interval = None
    if disjoint:
        left_max = min(max(wave_one_values), max(wave_two_values))
        right_min = max(min(wave_one_values), min(wave_two_values))
        separating_interval = {
            "lower_exclusive": _round_or_none(left_max),
            "upper_exclusive": _round_or_none(right_min),
        }

    return {
        "wave_one": {
            "count": len(wave_one_values),
            "mean": _round_or_none(fmean(wave_one_values)),
            "min": _round_or_none(wave_one_min),
            "max": _round_or_none(wave_one_max),
        },
        "wave_two": {
            "count": len(wave_two_values),
            "mean": _round_or_none(fmean(wave_two_values)),
            "min": _round_or_none(wave_two_min),
            "max": _round_or_none(wave_two_max),
        },
        "mean_gap_wave_two_minus_wave_one": _round_or_none(
            fmean(wave_two_values) - fmean(wave_one_values)
        ),
        "range_overlap": not disjoint,
        "separating_interval": separating_interval,
    }


def _evaluate_rule(
    rows: list[dict[str, Any]],
    *,
    feature: str,
    threshold: float,
    operator: str,
    positive_wave: str,
) -> dict[str, Any]:
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    for row in rows:
        value = float(row[feature])
        is_positive = str(row["wave_label"]) == positive_wave
        predicted_positive = value >= threshold if operator == ">=" else value <= threshold
        if predicted_positive and is_positive:
            true_positive += 1
        elif predicted_positive and not is_positive:
            false_positive += 1
        elif not predicted_positive and is_positive:
            false_negative += 1
        else:
            true_negative += 1
    total = len(rows)
    accuracy = (true_positive + true_negative) / total if total else 0.0
    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0.0
    )
    return {
        "feature": feature,
        "operator": operator,
        "threshold": _round_or_none(threshold),
        "positive_wave": positive_wave,
        "accuracy": _round_or_none(accuracy),
        "precision": _round_or_none(precision),
        "recall": _round_or_none(recall),
        "confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
    }


def _best_single_feature_rules(
    wave_one_rows: list[dict[str, Any]], wave_two_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    combined = [{**row, "wave_label": "wave_one"} for row in wave_one_rows] + [
        {**row, "wave_label": "wave_two"} for row in wave_two_rows
    ]
    per_feature_best: dict[str, dict[str, Any]] = {}
    perfect_rules: list[dict[str, Any]] = []
    for feature in FEATURES:
        unique_values = sorted(
            {float(row[feature]) for row in combined if isinstance(row.get(feature), int | float)}
        )
        candidate_thresholds: list[float] = []
        for left, right in zip(unique_values, unique_values[1:], strict=False):
            candidate_thresholds.append((left + right) / 2.0)
        if unique_values:
            candidate_thresholds.extend([unique_values[0], unique_values[-1]])

        best_rule: dict[str, Any] | None = None
        for positive_wave in ("wave_one", "wave_two"):
            for operator in (">=", "<="):
                for threshold in candidate_thresholds:
                    rule = _evaluate_rule(
                        combined,
                        feature=feature,
                        threshold=threshold,
                        operator=operator,
                        positive_wave=positive_wave,
                    )
                    if best_rule is None or (
                        rule["accuracy"],
                        rule["precision"],
                        rule["recall"],
                        -float(rule["threshold"]),
                    ) > (
                        best_rule["accuracy"],
                        best_rule["precision"],
                        best_rule["recall"],
                        -float(best_rule["threshold"]),
                    ):
                        best_rule = rule
                    if rule["accuracy"] == 1.0:
                        perfect_rules.append(rule)
        if best_rule is None:
            raise NormalizedPhaseAgeTransportError(
                f"No threshold rules generated for feature {feature!r}"
            )
        per_feature_best[feature] = best_rule

    return {
        "best_rule_per_feature": [per_feature_best[feature] for feature in FEATURES],
        "perfect_rules": sorted(
            perfect_rules,
            key=lambda item: (
                str(item["feature"]),
                str(item["positive_wave"]),
                str(item["operator"]),
                float(item["threshold"]),
            ),
        ),
    }


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


def _wave_side_counts(values: list[float], rule: dict[str, Any]) -> dict[str, Any]:
    threshold = float(rule["threshold"])
    operator = str(rule["operator"])
    positive_wave = str(rule["positive_wave"])
    predicted_positive = [
        value >= threshold if operator == ">=" else value <= threshold for value in values
    ]
    positive_count = sum(predicted_positive)
    negative_count = len(values) - positive_count
    if positive_wave == "wave_one":
        wave_one_side_count = positive_count
        wave_two_side_count = negative_count
    else:
        wave_two_side_count = positive_count
        wave_one_side_count = negative_count
    return {
        "wave_one_side_count": wave_one_side_count,
        "wave_two_side_count": wave_two_side_count,
        "boundary_count": sum(value == threshold for value in values),
        "threshold": _round_or_none(threshold),
        "operator": operator,
        "positive_wave": positive_wave,
    }


def _feature_transport_for_holdout(
    values: list[float],
    *,
    feature: str,
    reference_summary: dict[str, Any],
    rule: dict[str, Any],
) -> dict[str, Any]:
    summary = _numeric_summary(values)
    wave_one_range = _coerce_dict(
        reference_summary.get("wave_one"), field_name=f"{feature}.wave_one"
    )
    wave_two_range = _coerce_dict(
        reference_summary.get("wave_two"), field_name=f"{feature}.wave_two"
    )
    combined_range = {
        "min": min(float(wave_one_range["min"]), float(wave_two_range["min"])),
        "max": max(float(wave_one_range["max"]), float(wave_two_range["max"])),
    }
    overlap_wave_one = _feature_overlap(summary, wave_one_range)
    overlap_wave_two = _feature_overlap(summary, wave_two_range)
    overlap_combined = _feature_overlap(summary, combined_range)
    if (
        overlap_wave_one["overlaps_reference_range"]
        and not overlap_wave_two["overlaps_reference_range"]
    ):
        verdict = "maps_to_wave_one_envelope_only"
    elif (
        overlap_wave_two["overlaps_reference_range"]
        and not overlap_wave_one["overlaps_reference_range"]
    ):
        verdict = "maps_to_wave_two_envelope_only"
    elif (
        overlap_wave_one["overlaps_reference_range"]
        and overlap_wave_two["overlaps_reference_range"]
    ):
        verdict = "spans_both_wave_envelopes"
    elif overlap_combined["position"] == "below_reference_range":
        verdict = "outside_combined_reference_lower"
    elif overlap_combined["position"] == "above_reference_range":
        verdict = "outside_combined_reference_higher"
    else:
        verdict = "falls_into_reference_gap_only"
    return {
        "holdout_distribution": summary,
        "values": [_round_or_none(value) for value in sorted(values)],
        "reference_wave_one_range_overlap": overlap_wave_one,
        "reference_wave_two_range_overlap": overlap_wave_two,
        "reference_combined_range_overlap": overlap_combined,
        "threshold_side_counts": _wave_side_counts(values, rule),
        "verdict": verdict,
    }


def _visible_shell_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "zone_counts": _label_counts([str(row.get("zone")) for row in rows]),
        "selected_policy_counts": _label_counts(
            [
                str(row.get("selected_policy")) if row.get("selected_policy") is not None else None
                for row in rows
            ]
        ),
        "switch_reason_counts": _label_counts(
            [
                str(row.get("switch_reason")) if row.get("switch_reason") is not None else None
                for row in rows
            ]
        ),
        "phase_label_counts": _label_counts(
            [
                str(row.get("phase_label")) if row.get("phase_label") is not None else None
                for row in rows
            ]
        ),
    }


def _window_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(int(row["window_index"]), []).append(row)
    summaries: list[dict[str, Any]] = []
    for window_index, window_rows in sorted(grouped.items()):
        values = [float(row["bars_since_regime_change"]) for row in window_rows]
        summaries.append(
            {
                "window_index": window_index,
                "start": str(window_rows[0]["window_start"]),
                "end": str(window_rows[0]["window_end"]),
                "row_count": len(window_rows),
                "bars_since_regime_change": _numeric_summary(values),
            }
        )
    return summaries


def _holdout_subject_payload(
    subject_id: str,
    rows: list[dict[str, Any]],
    *,
    source_kind: str,
    reference_numeric_comparison: dict[str, Any],
    best_rules_by_feature: dict[str, dict[str, Any]],
    support_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "subject_id": subject_id,
        "source_kind": source_kind,
        "row_count": len(rows),
        "visible_shell": _visible_shell_summary(rows),
        "windows": _window_summary(rows),
        "support_context": support_context,
        "candidate_transport": {
            feature: _feature_transport_for_holdout(
                _numeric_values(rows, feature),
                feature=feature,
                reference_summary=_coerce_dict(
                    reference_numeric_comparison.get(feature),
                    field_name=f"reference_numeric_comparison.{feature}",
                ),
                rule=_coerce_dict(
                    best_rules_by_feature.get(feature),
                    field_name=f"best_rules_by_feature.{feature}",
                ),
            )
            for feature in FEATURES
        },
    }


def _transport_summary(
    *,
    rule_search: dict[str, Any],
    holdout_subjects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    best_rules = _coerce_list(
        rule_search.get("best_rule_per_feature"), field_name="rule_search.best_rule_per_feature"
    )
    perfect_features = [
        str(rule["feature"])
        for rule in best_rules
        if _coerce_float(rule.get("accuracy"), field_name="rule.accuracy") == 1.0
    ]
    perfect_scale_free = [
        feature
        for feature in ("subject_progress_pct", "subject_rank_pct")
        if feature in perfect_features
    ]
    window_relative_failures = [
        str(rule["feature"])
        for rule in best_rules
        if str(rule["feature"]).startswith("window_")
        and _coerce_float(rule.get("accuracy"), field_name="rule.accuracy") < 1.0
    ]
    exact_holdouts = {
        key: value
        for key, value in holdout_subjects.items()
        if key != "2017_03_continuation_family"
    }
    exact_single_side_counts: dict[str, int] = {}
    full_family_crosses_both: list[str] = []
    for feature in FEATURES:
        exact_single_side_counts[feature] = sum(
            value["candidate_transport"][feature]["verdict"]
            in {"maps_to_wave_one_envelope_only", "maps_to_wave_two_envelope_only"}
            for value in exact_holdouts.values()
        )
        if (
            holdout_subjects["2017_03_continuation_family"]["candidate_transport"][feature][
                "verdict"
            ]
            == "spans_both_wave_envelopes"
        ):
            full_family_crosses_both.append(feature)

    scale_free_exact_rescues = [
        feature
        for feature in ("subject_progress_pct", "subject_rank_pct")
        if exact_single_side_counts.get(feature) == len(exact_holdouts)
    ]
    if perfect_scale_free and scale_free_exact_rescues:
        status = TRANSPORT_STATUS_PARTIAL
        inference = (
            "Scale-free subject-relative phase-age candidates preserve the original 2023-12 "
            "wave split and recover coherent single-side mappings on all exact holdouts, while "
            "the full 2017 family still spans both sides because it contains multiple waves."
        )
    else:
        status = TRANSPORT_STATUS_FAIL
        inference = (
            "No tested subject-relative normalized candidate both preserved the local 2023-12 split "
            "and produced useful exact-holdout mappings."
        )

    return {
        "status": status,
        "perfect_reference_features": perfect_features,
        "perfect_scale_free_reference_features": perfect_scale_free,
        "window_relative_reference_failures": window_relative_failures,
        "exact_holdout_single_side_mapping_counts": exact_single_side_counts,
        "scale_free_exact_holdout_rescues": scale_free_exact_rescues,
        "full_family_spans_both_for_features": full_family_crosses_both,
        "inference": inference,
        "next_hypothesis": (
            "Subject-relative normalized phase-age looks more transportable than raw absolute age or "
            "window-reset progress, so the next honest test is to carry the same subject-relative "
            "candidates onto the continuation-release hysteresis holdout bench."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-clean-continuation-normalized-phase-age-transport-2026-05-25",
        "base_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "taxonomy_artifact": str(TAXONOMY_PASS_RELATIVE),
            "wave_discriminator_artifact": str(WAVE_DISCRIMINATOR_RELATIVE),
            "prior_holdout_artifact": str(PRIOR_HOLDOUT_RELATIVE),
            "annual_2017_action_diff_surface": str(ACTION_DIFF_2017_RELATIVE),
            "local_window_reference_2017": str(LOCAL_WINDOW_2017_RELATIVE),
            "chronology_reference_2017": str(CHRONOLOGY_REFERENCE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_normalized_phase_age_transport_check() -> dict[str, Any]:
    prior_holdout_status = _load_prior_holdout_status()
    reference_combined_rows, _ = _load_taxonomy_subject_rows("continuation_2023_combined")
    harmful_displacement_rows, harmful_displacement_summary = _load_taxonomy_subject_rows(
        "harmful_2024_displacement"
    )
    reference_augmented = _augment_rows(
        reference_combined_rows, subject_id="continuation_2023_combined"
    )
    reference_wave_one_rows, reference_wave_two_rows = _reference_wave_rows(reference_augmented)
    reference_numeric_comparison = {
        feature: _describe_numeric_feature(
            reference_wave_one_rows,
            reference_wave_two_rows,
            feature=feature,
        )
        for feature in FEATURES
    }
    rule_search = _best_single_feature_rules(reference_wave_one_rows, reference_wave_two_rows)
    best_rules_by_feature = {
        str(rule["feature"]): _coerce_dict(rule, field_name="best_rule")
        for rule in _coerce_list(
            rule_search.get("best_rule_per_feature"),
            field_name="rule_search.best_rule_per_feature",
        )
    }

    harmful_displacement_augmented = _augment_rows(
        harmful_displacement_rows, subject_id="harmful_2024_displacement"
    )
    march_2017_rows = _load_2017_continuation_rows()
    march_2017_augmented = _augment_rows(march_2017_rows, subject_id="2017_03_continuation_family")
    named_windows = _extract_named_2017_windows(march_2017_rows)
    named_window_augmented = _extract_named_2017_augmented_windows(
        march_2017_augmented,
        named_windows,
    )

    holdout_subjects = {
        "harmful_2024_displacement": _holdout_subject_payload(
            "harmful_2024_displacement",
            harmful_displacement_augmented,
            source_kind="taxonomy_clean_continuation_exact_holdout",
            reference_numeric_comparison=reference_numeric_comparison,
            best_rules_by_feature=best_rules_by_feature,
            support_context={
                "dominant_state_label": harmful_displacement_summary.get("dominant_state_label"),
                "classification_reason": harmful_displacement_summary.get("classification_reason"),
            },
        ),
        "2017_03_continuation_family": _holdout_subject_payload(
            "2017_03_continuation_family",
            march_2017_augmented,
            source_kind="annual_enabled_vs_absent_continuation_family_holdout",
            reference_numeric_comparison=reference_numeric_comparison,
            best_rules_by_feature=best_rules_by_feature,
            support_context={
                "local_window_reference": str(LOCAL_WINDOW_2017_RELATIVE),
                "chronology_reference": str(CHRONOLOGY_REFERENCE_RELATIVE),
            },
        ),
    }
    named_window_support = _load_named_2017_window_specs()
    source_labels = {
        "2017_03_early_anchor": "named_2017_03_early_anchor_exact_holdout",
        "2017_03_late_revisit": "named_2017_03_late_revisit_exact_holdout",
        "2017_03_month_end_revisit": "named_2017_03_month_end_revisit_exact_holdout",
    }
    for subject_id, rows in named_window_augmented.items():
        holdout_subjects[subject_id] = _holdout_subject_payload(
            subject_id,
            rows,
            source_kind=source_labels[subject_id],
            reference_numeric_comparison=reference_numeric_comparison,
            best_rules_by_feature=best_rules_by_feature,
            support_context=named_window_support[subject_id],
        )

    return {
        "audit_version": "ri-policy-router-clean-continuation-normalized-phase-age-transport-2026-05-25",
        "base_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "state_lock_required": EXPECTED_STATE_LABEL,
            "reference_subject": "continuation_2023_combined",
            "wave_labels_derived_from": "cohort_label on the fixed taxonomy rows",
            "candidate_feature_families": {
                family_name: list(features) for family_name, features in FEATURE_FAMILIES.items()
            },
            "local_packaging_rule": {
                "max_adjacency_hours": 24,
                "statement": (
                    "Adjacent continuation timestamps separated by <=24h are packaged into the same "
                    "descriptive local window before window-relative candidate features are computed."
                ),
            },
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "taxonomy_artifact": str(TAXONOMY_PASS_RELATIVE),
            "wave_discriminator_artifact": str(WAVE_DISCRIMINATOR_RELATIVE),
            "prior_holdout_artifact": str(PRIOR_HOLDOUT_RELATIVE),
            "prior_holdout_status": prior_holdout_status,
            "annual_2017_action_diff_surface": str(ACTION_DIFF_2017_RELATIVE),
            "local_window_reference_2017": str(LOCAL_WINDOW_2017_RELATIVE),
            "chronology_reference_2017": str(CHRONOLOGY_REFERENCE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "reference_subjects": {
            "continuation_2023_combined": {
                "row_count": len(reference_augmented),
                "wave_one_row_count": len(reference_wave_one_rows),
                "wave_two_row_count": len(reference_wave_two_rows),
                "windows": _window_summary(reference_augmented),
            }
        },
        "reference_candidate_comparison": reference_numeric_comparison,
        "reference_rule_search": rule_search,
        "holdout_subjects": holdout_subjects,
        "transport_summary": _transport_summary(
            rule_search=rule_search,
            holdout_subjects=holdout_subjects,
        ),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_normalized_phase_age_transport_check()
    except NormalizedPhaseAgeTransportError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("transport_summary", {}).get("status", result.get("status")),
        "perfect_scale_free_reference_features": result.get("transport_summary", {}).get(
            "perfect_scale_free_reference_features"
        ),
        "scale_free_exact_holdout_rescues": result.get("transport_summary", {}).get(
            "scale_free_exact_holdout_rescues"
        ),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
