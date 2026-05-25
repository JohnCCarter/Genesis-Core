from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
REFERENCE_PHASE_AGE_RELATIVE = Path(
    "results/evaluation/ri_policy_router_clean_continuation_normalized_phase_age_transport_2026-05-25.json"
)
TRIAD_SYNTHESIS_NOTE_RELATIVE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_phase_age_transport_2026-05-25.json"
)
STATUS_OK = "continuation_release_hysteresis_phase_age_transport_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_phase_age_transport_fail_closed"
TRANSPORT_STATUS_EARLY_ONLY = (
    "subject_relative_phase_age_marks_early_hysteresis_release_without_sign_separation"
)
FEATURES = ("subject_progress_pct", "subject_rank_pct")


@dataclass(frozen=True)
class ExactSubjectArtifacts:
    subject_id: str
    summary_relative: Path
    row_diff_relative: Path


SUBJECT_ARTIFACTS = (
    ExactSubjectArtifacts(
        subject_id="2021-08",
        summary_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/"
            "continuation_release_hysteresis_topline_subject_summary.json"
        ),
        row_diff_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/"
            "continuation_release_hysteresis_topline_subject_row_diffs.json"
        ),
    ),
    ExactSubjectArtifacts(
        subject_id="2025-10",
        summary_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/"
            "continuation_release_hysteresis_topline_subject_2025_10_summary.json"
        ),
        row_diff_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/"
            "continuation_release_hysteresis_topline_subject_2025_10_row_diffs.json"
        ),
    ),
    ExactSubjectArtifacts(
        subject_id="2018-03",
        summary_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/"
            "continuation_release_hysteresis_topline_subject_2018_03_summary.json"
        ),
        row_diff_relative=Path(
            "results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/"
            "continuation_release_hysteresis_topline_subject_2018_03_row_diffs.json"
        ),
    ),
)


class HysteresisPhaseAgeTransportError(RuntimeError):
    pass


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HysteresisPhaseAgeTransportError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise HysteresisPhaseAgeTransportError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise HysteresisPhaseAgeTransportError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise HysteresisPhaseAgeTransportError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise HysteresisPhaseAgeTransportError(
            f"Expected bool for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


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
        raise HysteresisPhaseAgeTransportError("Expected at least one numeric value to summarize")
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "mean": _round_or_none(fmean(values)),
        "max": _round_or_none(max(values)),
    }


def _feature_verdict(
    *, subject_min: float, subject_max: float, wave_one_max: float, wave_two_min: float
) -> str:
    if subject_max <= wave_one_max:
        return "maps_to_wave_one_envelope_only"
    if subject_min >= wave_two_min:
        return "maps_to_wave_two_envelope_only"
    if subject_min <= wave_one_max and subject_max >= wave_two_min:
        return "spans_both_wave_envelopes"
    if subject_min > wave_one_max and subject_max < wave_two_min:
        return "falls_between_reference_waves_only"
    return "overlaps_boundary_without_single_side_mapping"


def _reference_feature_bounds() -> dict[str, dict[str, Any]]:
    payload = _coerce_dict(_load_json(REFERENCE_PHASE_AGE_RELATIVE), field_name="reference_payload")
    comparison = _coerce_dict(
        payload.get("reference_candidate_comparison"),
        field_name="reference_payload.reference_candidate_comparison",
    )
    bounds: dict[str, dict[str, Any]] = {}
    for feature in FEATURES:
        feature_payload = _coerce_dict(comparison.get(feature), field_name=f"reference.{feature}")
        wave_one = _coerce_dict(
            feature_payload.get("wave_one"), field_name=f"reference.{feature}.wave_one"
        )
        wave_two = _coerce_dict(
            feature_payload.get("wave_two"), field_name=f"reference.{feature}.wave_two"
        )
        bounds[feature] = {
            "wave_one": {
                "min": _coerce_float(
                    wave_one.get("min"), field_name=f"reference.{feature}.wave_one.min"
                ),
                "max": _coerce_float(
                    wave_one.get("max"), field_name=f"reference.{feature}.wave_one.max"
                ),
            },
            "wave_two": {
                "min": _coerce_float(
                    wave_two.get("min"), field_name=f"reference.{feature}.wave_two.min"
                ),
                "max": _coerce_float(
                    wave_two.get("max"), field_name=f"reference.{feature}.wave_two.max"
                ),
            },
        }
    return bounds


def _normalize_row_diff_surface(payload: list[Any], *, subject_id: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, raw_row in enumerate(payload):
        row = _coerce_dict(raw_row, field_name=f"{subject_id}.row_diffs[{index}]")
        baseline = _coerce_dict(row.get("baseline"), field_name=f"{subject_id}.baseline")
        release_zero = _coerce_dict(
            row.get("release_zero"), field_name=f"{subject_id}.release_zero"
        )
        baseline_router_debug = _coerce_dict(
            baseline.get("router_debug"), field_name=f"{subject_id}.baseline.router_debug"
        )
        release_zero_router_debug = _coerce_dict(
            release_zero.get("router_debug"),
            field_name=f"{subject_id}.release_zero.router_debug",
        )
        baseline_router_state = _coerce_dict(
            baseline.get("router_state"), field_name=f"{subject_id}.baseline.router_state"
        )
        release_zero_router_state = _coerce_dict(
            release_zero.get("router_state"),
            field_name=f"{subject_id}.release_zero.router_state",
        )
        normalized.append(
            {
                "subject_id": subject_id,
                "row_index": index,
                "timestamp": _coerce_str(
                    row.get("timestamp"), field_name=f"{subject_id}.timestamp"
                ),
                "bars_since_regime_change": _coerce_float(
                    baseline_router_debug.get("bars_since_regime_change"),
                    field_name=f"{subject_id}.bars_since_regime_change",
                ),
                "continuation_release_involved": _coerce_bool(
                    row.get("continuation_release_involved"),
                    field_name=f"{subject_id}.continuation_release_involved",
                ),
                "selected_policy_changed": _coerce_bool(
                    row.get("selected_policy_changed"),
                    field_name=f"{subject_id}.selected_policy_changed",
                ),
                "switch_reason_changed": _coerce_bool(
                    row.get("switch_reason_changed"),
                    field_name=f"{subject_id}.switch_reason_changed",
                ),
                "size_changed": _coerce_bool(
                    row.get("size_changed"), field_name=f"{subject_id}.size_changed"
                ),
                "behavior_changed": _coerce_bool(
                    row.get("behavior_changed"), field_name=f"{subject_id}.behavior_changed"
                ),
                "baseline_selected_policy": _coerce_str(
                    baseline_router_state.get("selected_policy"),
                    field_name=f"{subject_id}.baseline_selected_policy",
                ),
                "baseline_switch_reason": _coerce_str(
                    baseline_router_debug.get("switch_reason"),
                    field_name=f"{subject_id}.baseline_switch_reason",
                ),
                "release_zero_selected_policy": _coerce_str(
                    release_zero_router_state.get("selected_policy"),
                    field_name=f"{subject_id}.release_zero_selected_policy",
                ),
                "release_zero_switch_reason": _coerce_str(
                    release_zero_router_debug.get("switch_reason"),
                    field_name=f"{subject_id}.release_zero_switch_reason",
                ),
                "action_edge": _coerce_float(
                    baseline_router_debug.get("action_edge"),
                    field_name=f"{subject_id}.action_edge",
                ),
                "confidence_gate": _coerce_float(
                    baseline_router_debug.get("confidence_gate"),
                    field_name=f"{subject_id}.confidence_gate",
                ),
                "clarity_score": _coerce_float(
                    baseline_router_debug.get("clarity_score"),
                    field_name=f"{subject_id}.clarity_score",
                ),
                "zone": _coerce_str(
                    baseline_router_debug.get("zone"), field_name=f"{subject_id}.zone"
                ),
            }
        )

    if not normalized:
        raise HysteresisPhaseAgeTransportError(f"No row diffs materialized for {subject_id}")
    return _augment_subject_relative(normalized)


def _augment_subject_relative(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: (str(row["timestamp"]), int(row["row_index"])))
    subject_min = min(float(row["bars_since_regime_change"]) for row in ordered)
    subject_max = max(float(row["bars_since_regime_change"]) for row in ordered)
    subject_span = subject_max - subject_min
    subject_count = len(ordered)
    augmented: list[dict[str, Any]] = []
    for position, row in enumerate(ordered):
        subject_offset = float(row["bars_since_regime_change"]) - subject_min
        augmented.append(
            {
                **row,
                "subject_offset_from_floor": _round_or_none(subject_offset),
                "subject_progress_pct": _round_or_none(
                    0.0 if subject_span == 0.0 else subject_offset / subject_span
                ),
                "subject_rank_pct": _round_or_none(
                    0.0 if subject_count == 1 else position / (subject_count - 1)
                ),
            }
        )
    return augmented


def _first_decisive_cluster_row(cluster_rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in cluster_rows:
        if (
            bool(row["selected_policy_changed"])
            or bool(row["switch_reason_changed"])
            or bool(row["size_changed"])
        ):
            return row
    raise HysteresisPhaseAgeTransportError(
        "Could not recover a first decisive local split inside the continuation-release cluster"
    )


def _feature_payload(
    rows: list[dict[str, Any]],
    *,
    feature: str,
    reference_bounds: dict[str, Any],
) -> dict[str, Any]:
    values = [float(row[feature]) for row in rows]
    summary = _numeric_summary(values)
    wave_one_max = float(reference_bounds["wave_one"]["max"])
    wave_two_min = float(reference_bounds["wave_two"]["min"])
    verdict = _feature_verdict(
        subject_min=float(summary["min"]),
        subject_max=float(summary["max"]),
        wave_one_max=wave_one_max,
        wave_two_min=wave_two_min,
    )
    return {
        "distribution": summary,
        "values": [_round_or_none(value) for value in values],
        "reference_wave_one": {
            "min": _round_or_none(float(reference_bounds["wave_one"]["min"])),
            "max": _round_or_none(wave_one_max),
        },
        "reference_wave_two": {
            "min": _round_or_none(wave_two_min),
            "max": _round_or_none(float(reference_bounds["wave_two"]["max"])),
        },
        "verdict": verdict,
    }


def _subject_payload(
    artifacts: ExactSubjectArtifacts,
    *,
    reference_bounds: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    summary_payload = _coerce_dict(
        _load_json(artifacts.summary_relative), field_name=artifacts.subject_id
    )
    comparison = _coerce_dict(
        summary_payload.get("comparison"), field_name=f"{artifacts.subject_id}.comparison"
    )
    row_diff_payload = _coerce_list(
        _load_json(artifacts.row_diff_relative), field_name=f"{artifacts.subject_id}.row_diffs"
    )
    subject_rows = _normalize_row_diff_surface(row_diff_payload, subject_id=artifacts.subject_id)
    cluster_rows = [row for row in subject_rows if bool(row["continuation_release_involved"])]
    if not cluster_rows:
        raise HysteresisPhaseAgeTransportError(
            f"No continuation-release cluster rows recovered for {artifacts.subject_id}"
        )
    decisive_row = _first_decisive_cluster_row(cluster_rows)
    total_return_diff = _coerce_float(
        comparison.get("total_return_diff"), field_name=f"{artifacts.subject_id}.total_return_diff"
    )
    if total_return_diff > 0:
        top_line_sign = "positive"
    elif total_return_diff < 0:
        top_line_sign = "negative"
    else:
        top_line_sign = "flat"

    cluster_transport = {
        feature: _feature_payload(
            cluster_rows, feature=feature, reference_bounds=reference_bounds[feature]
        )
        for feature in FEATURES
    }
    decisive_transport = {
        feature: _feature_payload(
            [decisive_row],
            feature=feature,
            reference_bounds=reference_bounds[feature],
        )
        for feature in FEATURES
    }
    bars_values = [float(row["bars_since_regime_change"]) for row in subject_rows]
    cluster_bars_values = [float(row["bars_since_regime_change"]) for row in cluster_rows]

    return {
        "subject_id": artifacts.subject_id,
        "top_line_sign": top_line_sign,
        "total_return_diff": _round_or_none(total_return_diff),
        "final_capital_diff": _round_or_none(
            _coerce_float(
                comparison.get("final_capital_diff"),
                field_name=f"{artifacts.subject_id}.final_capital_diff",
            )
        ),
        "full_subject_surface": {
            "row_count": len(subject_rows),
            "bars_since_regime_change": _numeric_summary(bars_values),
            "first_timestamp": str(subject_rows[0]["timestamp"]),
            "last_timestamp": str(subject_rows[-1]["timestamp"]),
        },
        "continuation_release_cluster": {
            "row_count": len(cluster_rows),
            "first_timestamp": str(cluster_rows[0]["timestamp"]),
            "last_timestamp": str(cluster_rows[-1]["timestamp"]),
            "bars_since_regime_change_values": [
                _round_or_none(value) for value in sorted(set(cluster_bars_values))
            ],
            "transport": cluster_transport,
        },
        "first_decisive_local_split": {
            "timestamp": str(decisive_row["timestamp"]),
            "bars_since_regime_change": _round_or_none(
                float(decisive_row["bars_since_regime_change"])
            ),
            "baseline_selected_policy": str(decisive_row["baseline_selected_policy"]),
            "baseline_switch_reason": str(decisive_row["baseline_switch_reason"]),
            "release_zero_selected_policy": str(decisive_row["release_zero_selected_policy"]),
            "release_zero_switch_reason": str(decisive_row["release_zero_switch_reason"]),
            "transport": decisive_transport,
        },
    }


def _transport_summary(
    subject_payloads: list[dict[str, Any]],
) -> dict[str, Any]:
    cluster_wave_one_counts = {
        feature: sum(
            subject["continuation_release_cluster"]["transport"][feature]["verdict"]
            == "maps_to_wave_one_envelope_only"
            for subject in subject_payloads
        )
        for feature in FEATURES
    }
    decisive_wave_one_counts = {
        feature: sum(
            subject["first_decisive_local_split"]["transport"][feature]["verdict"]
            == "maps_to_wave_one_envelope_only"
            for subject in subject_payloads
        )
        for feature in FEATURES
    }
    positive_subjects = [
        str(subject["subject_id"])
        for subject in subject_payloads
        if subject["top_line_sign"] == "positive"
    ]
    negative_subjects = [
        str(subject["subject_id"])
        for subject in subject_payloads
        if subject["top_line_sign"] == "negative"
    ]
    mixed_signs = bool(positive_subjects and negative_subjects)
    all_cluster_wave_one = all(
        cluster_wave_one_counts[feature] == len(subject_payloads) for feature in FEATURES
    )
    all_decisive_wave_one = all(
        decisive_wave_one_counts[feature] == len(subject_payloads) for feature in FEATURES
    )
    if all_cluster_wave_one and all_decisive_wave_one and mixed_signs:
        status = TRANSPORT_STATUS_EARLY_ONLY
        inference = (
            "On the frozen continuation_release_hysteresis exact-subject triad, clean-continuation "
            "subject-relative phase-age transports as an early-phase marker: every continuation-release "
            "cluster and every first decisive local split stays inside the same wave_one-like envelope, "
            "but that shared early-phase band does not separate positive from negative top-line sign."
        )
    else:
        status = "continuation_release_hysteresis_phase_age_transport_not_resolved"
        inference = "The tested hysteresis triad did not collapse into one stable subject-relative phase-age read."
    return {
        "status": status,
        "cluster_wave_one_only_counts": cluster_wave_one_counts,
        "decisive_wave_one_only_counts": decisive_wave_one_counts,
        "positive_subject_ids": positive_subjects,
        "negative_subject_ids": negative_subjects,
        "mixed_signs_inside_same_phase_band": mixed_signs,
        "inference": inference,
        "next_hypothesis": (
            "If sign separation still matters on this seam, the next honest test is intra-band structure "
            "inside the early continuation-release zone (for example cluster length, decisive split timing "
            "within the cluster, or local edge/clarity path), not broader subject-relative phase-age alone."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-phase-age-transport-2026-05-25",
        "base_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "reference_phase_age_artifact": str(REFERENCE_PHASE_AGE_RELATIVE),
            "triad_synthesis_note": str(TRIAD_SYNTHESIS_NOTE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "exact_subjects": [
                {
                    "subject_id": artifacts.subject_id,
                    "summary_artifact": str(artifacts.summary_relative),
                    "row_diff_artifact": str(artifacts.row_diff_relative),
                }
                for artifacts in SUBJECT_ARTIFACTS
            ],
        },
    }


def run_hysteresis_phase_age_transport() -> dict[str, Any]:
    reference_bounds = _reference_feature_bounds()
    subject_payloads = [
        _subject_payload(artifacts, reference_bounds=reference_bounds)
        for artifacts in SUBJECT_ARTIFACTS
    ]
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-phase-age-transport-2026-05-25",
        "base_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": "clean_continuation normalized phase-age wave envelopes from 2023-12",
            "holdout_surface": "frozen continuation_release_hysteresis exact-subject triad",
            "subject_definition": (
                "Each exact subject is read from its tracked row-diff surface, and subject-relative phase-age "
                "is computed across the full exact-subject row-diff timeline before the continuation-release "
                "cluster and first decisive local split are projected onto the clean-continuation envelopes."
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "reference_phase_age_artifact": str(REFERENCE_PHASE_AGE_RELATIVE),
            "triad_synthesis_note": str(TRIAD_SYNTHESIS_NOTE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "exact_subjects": [
                {
                    "subject_id": artifacts.subject_id,
                    "summary_artifact": str(artifacts.summary_relative),
                    "row_diff_artifact": str(artifacts.row_diff_relative),
                }
                for artifacts in SUBJECT_ARTIFACTS
            ],
        },
        "reference_wave_envelopes": reference_bounds,
        "holdout_subjects": {subject["subject_id"]: subject for subject in subject_payloads},
        "transport_summary": _transport_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_hysteresis_phase_age_transport()
    except HysteresisPhaseAgeTransportError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("transport_summary", {}).get("status", result.get("status")),
        "cluster_wave_one_only_counts": result.get("transport_summary", {}).get(
            "cluster_wave_one_only_counts"
        ),
        "decisive_wave_one_only_counts": result.get("transport_summary", {}).get(
            "decisive_wave_one_only_counts"
        ),
        "mixed_signs_inside_same_phase_band": result.get("transport_summary", {}).get(
            "mixed_signs_inside_same_phase_band"
        ),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
