from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
PHASE_AGE_TRIAD_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_phase_age_transport_2026-05-25.json"
)
TRIAD_SYNTHESIS_NOTE_RELATIVE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_intra_band_sign_candidates_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_intra_band_sign_candidates_fail_closed"
SIGN_STATUS_CANDIDATES = "frozen_triad_intra_band_structure_yields_sign_candidates"

CANDIDATE_FAMILIES = {
    "cluster_shape": (
        "cluster_row_count",
        "release_retention_ratio",
    ),
    "decisive_timing": (
        "decisive_index_within_cluster",
        "decisive_rank_pct",
        "decisive_hours_from_cluster_start",
    ),
    "decisive_support": (
        "decisive_action_edge",
        "decisive_confidence_gate",
        "decisive_clarity_score",
    ),
    "path_divergence": (
        "cluster_policy_diff_rows",
        "cluster_switch_diff_rows",
        "cluster_size_diff_rows",
    ),
}
FEATURES = tuple(feature for family in CANDIDATE_FAMILIES.values() for feature in family)


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


class IntraBandSignCandidatesError(RuntimeError):
    pass


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntraBandSignCandidatesError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise IntraBandSignCandidatesError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise IntraBandSignCandidatesError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise IntraBandSignCandidatesError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise IntraBandSignCandidatesError(
            f"Expected bool for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _parse_timestamp(raw: Any, *, field_name: str) -> datetime:
    timestamp = _coerce_str(raw, field_name=field_name)
    normalized = timestamp.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise IntraBandSignCandidatesError(
            f"Invalid timestamp for {field_name}: {timestamp!r}"
        ) from exc


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
        raise IntraBandSignCandidatesError("Expected at least one numeric value to summarize")
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "mean": _round_or_none(fmean(values)),
        "max": _round_or_none(max(values)),
    }


def _sign_label(total_return_diff: float) -> str:
    if total_return_diff > 0:
        return "positive"
    if total_return_diff < 0:
        return "negative"
    return "flat"


def _normalize_cluster_rows(payload: list[Any], *, subject_id: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, raw_row in enumerate(payload):
        row = _coerce_dict(raw_row, field_name=f"{subject_id}.row_diffs[{index}]")
        if not _coerce_bool(
            row.get("continuation_release_involved"),
            field_name=f"{subject_id}.continuation_release_involved",
        ):
            continue

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
                "row_index": index,
                "timestamp": _parse_timestamp(
                    row.get("timestamp"), field_name=f"{subject_id}.timestamp"
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
                "baseline_selected_policy": _coerce_str(
                    baseline_router_state.get("selected_policy"),
                    field_name=f"{subject_id}.baseline_selected_policy",
                ),
                "release_zero_selected_policy": _coerce_str(
                    release_zero_router_state.get("selected_policy"),
                    field_name=f"{subject_id}.release_zero_selected_policy",
                ),
                "baseline_switch_reason": _coerce_str(
                    baseline_router_debug.get("switch_reason"),
                    field_name=f"{subject_id}.baseline_switch_reason",
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
            }
        )

    if not normalized:
        raise IntraBandSignCandidatesError(
            f"No continuation-release cluster rows materialized for {subject_id}"
        )
    return sorted(normalized, key=lambda row: row["timestamp"])


def _first_decisive_cluster_row(cluster_rows: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    for index, row in enumerate(cluster_rows):
        if (
            bool(row["selected_policy_changed"])
            or bool(row["switch_reason_changed"])
            or bool(row["size_changed"])
        ):
            return index, row
    raise IntraBandSignCandidatesError(
        "Could not recover a decisive cluster row inside the continuation-release zone"
    )


def _subject_payload(artifacts: ExactSubjectArtifacts) -> dict[str, Any]:
    summary_payload = _coerce_dict(
        _load_json(artifacts.summary_relative), field_name=artifacts.subject_id
    )
    comparison = _coerce_dict(
        summary_payload.get("comparison"), field_name=f"{artifacts.subject_id}.comparison"
    )
    row_diff_payload = _coerce_list(
        _load_json(artifacts.row_diff_relative), field_name=f"{artifacts.subject_id}.row_diffs"
    )
    cluster_rows = _normalize_cluster_rows(row_diff_payload, subject_id=artifacts.subject_id)
    decisive_index, decisive_row = _first_decisive_cluster_row(cluster_rows)

    baseline_release_count = int(
        _coerce_float(
            comparison.get("baseline_continuation_release_row_count"),
            field_name=f"{artifacts.subject_id}.baseline_continuation_release_row_count",
        )
    )
    release_zero_release_count = int(
        _coerce_float(
            comparison.get("release_zero_continuation_release_row_count"),
            field_name=f"{artifacts.subject_id}.release_zero_continuation_release_row_count",
        )
    )
    if baseline_release_count <= 0:
        raise IntraBandSignCandidatesError(
            f"Baseline continuation-release count is not positive for {artifacts.subject_id}"
        )

    cluster_start = cluster_rows[0]["timestamp"]
    decisive_timestamp = decisive_row["timestamp"]
    total_return_diff = _coerce_float(
        comparison.get("total_return_diff"), field_name=f"{artifacts.subject_id}.total_return_diff"
    )
    action_edges = [float(row["action_edge"]) for row in cluster_rows]
    confidence_gates = [float(row["confidence_gate"]) for row in cluster_rows]
    clarity_scores = [float(row["clarity_score"]) for row in cluster_rows]

    subject_features = {
        "cluster_row_count": float(len(cluster_rows)),
        "release_retention_ratio": release_zero_release_count / baseline_release_count,
        "decisive_index_within_cluster": float(decisive_index),
        "decisive_rank_pct": (
            0.0 if len(cluster_rows) == 1 else decisive_index / (len(cluster_rows) - 1)
        ),
        "decisive_hours_from_cluster_start": (decisive_timestamp - cluster_start).total_seconds()
        / 3600.0,
        "decisive_action_edge": float(decisive_row["action_edge"]),
        "decisive_confidence_gate": float(decisive_row["confidence_gate"]),
        "decisive_clarity_score": float(decisive_row["clarity_score"]),
        "cluster_policy_diff_rows": float(
            sum(
                row["baseline_selected_policy"] != row["release_zero_selected_policy"]
                for row in cluster_rows
            )
        ),
        "cluster_switch_diff_rows": float(
            sum(
                row["baseline_switch_reason"] != row["release_zero_switch_reason"]
                for row in cluster_rows
            )
        ),
        "cluster_size_diff_rows": float(sum(bool(row["size_changed"]) for row in cluster_rows)),
    }

    return {
        "subject_id": artifacts.subject_id,
        "top_line_sign": _sign_label(total_return_diff),
        "total_return_diff": _round_or_none(total_return_diff),
        "final_capital_diff": _round_or_none(
            _coerce_float(
                comparison.get("final_capital_diff"),
                field_name=f"{artifacts.subject_id}.final_capital_diff",
            )
        ),
        "cluster_context": {
            "first_timestamp": cluster_start.isoformat(),
            "last_timestamp": cluster_rows[-1]["timestamp"].isoformat(),
            "decisive_timestamp": decisive_timestamp.isoformat(),
            "baseline_continuation_release_row_count": baseline_release_count,
            "release_zero_continuation_release_row_count": release_zero_release_count,
            "cluster_action_edge": _numeric_summary(action_edges),
            "cluster_confidence_gate": _numeric_summary(confidence_gates),
            "cluster_clarity_score": _numeric_summary(clarity_scores),
        },
        "subject_features": {
            feature: _round_or_none(value) for feature, value in subject_features.items()
        },
    }


def _evaluate_rule(
    subjects: list[dict[str, Any]],
    *,
    feature: str,
    threshold: float,
    operator: str,
    positive_label: str,
) -> dict[str, Any]:
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    for subject in subjects:
        value = float(subject["subject_features"][feature])
        is_positive = str(subject["top_line_sign"]) == positive_label
        predicted_positive = value >= threshold if operator == ">=" else value <= threshold
        if predicted_positive and is_positive:
            true_positive += 1
        elif predicted_positive and not is_positive:
            false_positive += 1
        elif not predicted_positive and is_positive:
            false_negative += 1
        else:
            true_negative += 1

    total = len(subjects)
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
        "positive_label": positive_label,
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


def _rule_sort_key(rule: dict[str, Any]) -> tuple[float, float, float, int, int, float]:
    return (
        float(rule["accuracy"]),
        float(rule["precision"]),
        float(rule["recall"]),
        1 if str(rule["positive_label"]) == "negative" else 0,
        1 if str(rule["operator"]) == "<=" else 0,
        -float(rule["threshold"]),
    )


def _candidate_thresholds(values: list[float]) -> list[float]:
    unique_values = sorted(set(values))
    thresholds: list[float] = []
    for left, right in zip(unique_values, unique_values[1:], strict=False):
        thresholds.append((left + right) / 2.0)
    if unique_values:
        thresholds.extend([unique_values[0], unique_values[-1]])
    return thresholds


def _best_rules(subjects: list[dict[str, Any]]) -> dict[str, Any]:
    best_rules: dict[str, dict[str, Any]] = {}
    perfect_rules: list[dict[str, Any]] = []
    for feature in FEATURES:
        values = [float(subject["subject_features"][feature]) for subject in subjects]
        thresholds = _candidate_thresholds(values)
        best_rule: dict[str, Any] | None = None
        for positive_label in ("negative", "positive"):
            for operator in ("<=", ">="):
                for threshold in thresholds:
                    rule = _evaluate_rule(
                        subjects,
                        feature=feature,
                        threshold=threshold,
                        operator=operator,
                        positive_label=positive_label,
                    )
                    if best_rule is None or _rule_sort_key(rule) > _rule_sort_key(best_rule):
                        best_rule = rule
                    if float(rule["accuracy"]) == 1.0:
                        perfect_rules.append(rule)
        if best_rule is None:
            raise IntraBandSignCandidatesError(f"No threshold rules generated for {feature!r}")
        best_rules[feature] = best_rule

    return {
        "best_rule_per_feature": [best_rules[feature] for feature in FEATURES],
        "perfect_rules": sorted(
            perfect_rules,
            key=lambda rule: (
                str(rule["feature"]),
                str(rule["positive_label"]),
                str(rule["operator"]),
                float(rule["threshold"]),
            ),
        ),
    }


def _feature_family(feature: str) -> str:
    for family, features in CANDIDATE_FAMILIES.items():
        if feature in features:
            return family
    raise IntraBandSignCandidatesError(f"Feature family missing for {feature!r}")


def _candidate_comparison(subjects: list[dict[str, Any]]) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for feature in FEATURES:
        negative_values = [
            float(subject["subject_features"][feature])
            for subject in subjects
            if subject["top_line_sign"] == "negative"
        ]
        positive_values = [
            float(subject["subject_features"][feature])
            for subject in subjects
            if subject["top_line_sign"] == "positive"
        ]
        if not negative_values or not positive_values:
            raise IntraBandSignCandidatesError(
                f"Feature {feature!r} missing positive or negative values on the frozen triad"
            )
        comparison[feature] = {
            "family": _feature_family(feature),
            "negative_subjects": {
                "count": len(negative_values),
                "values": [_round_or_none(value) for value in negative_values],
                "min": _round_or_none(min(negative_values)),
                "mean": _round_or_none(fmean(negative_values)),
                "max": _round_or_none(max(negative_values)),
            },
            "positive_subjects": {
                "count": len(positive_values),
                "values": [_round_or_none(value) for value in positive_values],
                "min": _round_or_none(min(positive_values)),
                "mean": _round_or_none(fmean(positive_values)),
                "max": _round_or_none(max(positive_values)),
            },
        }
    return comparison


def _sign_summary(subjects: list[dict[str, Any]], rule_search: dict[str, Any]) -> dict[str, Any]:
    best_rules = _coerce_list(
        rule_search.get("best_rule_per_feature"), field_name="rule_search.best_rule_per_feature"
    )
    perfect_negative_separators = [
        str(rule["feature"])
        for rule in best_rules
        if float(rule["accuracy"]) == 1.0 and str(rule["positive_label"]) == "negative"
    ]
    non_perfect_features = [
        str(rule["feature"]) for rule in best_rules if float(rule["accuracy"]) < 1.0
    ]
    perfect_families = sorted({_feature_family(feature) for feature in perfect_negative_separators})

    if perfect_negative_separators:
        status = SIGN_STATUS_CANDIDATES
        inference = (
            "Inside the same early continuation-release phase band, several cluster-local features "
            "perfectly separate the lone negative exact subject from the two positive exact subjects on the "
            "frozen triad. The strongest triad-local signals are lower release retention, earlier decisive "
            "timing within the cluster, weaker decisive support, and heavier policy/size divergence."
        )
    else:
        status = "frozen_triad_intra_band_sign_candidates_not_materialized"
        inference = "No tested cluster-local feature separated the frozen exact-subject triad by top-line sign."

    return {
        "status": status,
        "perfect_negative_separators": perfect_negative_separators,
        "perfect_negative_separator_families": perfect_families,
        "non_perfect_features": non_perfect_features,
        "inference": inference,
        "next_hypothesis": (
            "Because this bench still contains only one negative subject, the next honest test is not to claim "
            "a portable sign law but to widen the exact-subject bench or find another opposite-sign seam-active "
            "subject before trusting any of these intra-band features beyond the frozen triad."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-intra-band-sign-candidates-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "phase_age_transport_artifact": str(PHASE_AGE_TRIAD_RELATIVE),
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


def run_intra_band_sign_candidates() -> dict[str, Any]:
    subjects = [_subject_payload(artifacts) for artifacts in SUBJECT_ARTIFACTS]
    rule_search = _best_rules(subjects)
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-intra-band-sign-candidates-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": "frozen continuation_release_hysteresis exact-subject triad already shown to share one early phase-age band",
            "candidate_scope": {
                family_name: list(features) for family_name, features in CANDIDATE_FAMILIES.items()
            },
            "question": (
                "Within the already-shared early phase band, do any cluster-local subject features separate the "
                "lone negative exact subject from the two positive exact subjects on the frozen triad?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "phase_age_transport_artifact": str(PHASE_AGE_TRIAD_RELATIVE),
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
        "subject_summaries": {subject["subject_id"]: subject for subject in subjects},
        "candidate_comparison": _candidate_comparison(subjects),
        "rule_search": rule_search,
        "sign_summary": _sign_summary(subjects, rule_search),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_intra_band_sign_candidates()
    except IntraBandSignCandidatesError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("sign_summary", {}).get("status", result.get("status")),
        "perfect_negative_separators": result.get("sign_summary", {}).get(
            "perfect_negative_separators"
        ),
        "non_perfect_features": result.get("sign_summary", {}).get("non_perfect_features"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
