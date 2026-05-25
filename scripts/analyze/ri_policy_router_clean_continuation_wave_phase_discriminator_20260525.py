from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json"
STATUS_OK = "clean_continuation_wave_phase_discriminator_generated"
STATUS_FAIL_CLOSED = "clean_continuation_wave_phase_discriminator_fail_closed"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
EXPECTED_STATE_LABEL = "clean_continuation"
NUMERIC_FEATURES = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
)
CATEGORICAL_FEATURES = (
    "zone",
    "selected_policy",
    "switch_reason",
    "previous_policy",
    "phase_label",
)
OUTCOME_FEATURES = (
    "fwd_16_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_4_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)


class WaveDiscriminatorError(RuntimeError):
    """Raised when the source artifact is missing or structurally invalid."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a read-only decision-time discriminator pass over the fixed clean-continuation "
            "wave one vs wave two subjects."
        )
    )
    parser.add_argument(
        "--base-sha",
        required=True,
        help="Exact repository HEAD SHA for provenance in the emitted artifact.",
    )
    parser.add_argument(
        "--source-artifact-relative",
        default=str(SOURCE_ARTIFACT_RELATIVE),
        help="Repo-relative source taxonomy artifact used for the wave split pass.",
    )
    parser.add_argument(
        "--output-root-relative",
        default=str(OUTPUT_ROOT_RELATIVE),
        help="Repo-relative output directory for the emitted JSON summary.",
    )
    parser.add_argument(
        "--summary-filename",
        default=OUTPUT_FILENAME,
        help="Filename to use for the emitted JSON summary.",
    )
    return parser.parse_args()


def _load_source_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise WaveDiscriminatorError(f"Source artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise WaveDiscriminatorError("Source artifact is not a JSON object")
    if payload.get("status") != "fixed_subject_state_taxonomy_generated":
        raise WaveDiscriminatorError(
            f"Unexpected source artifact status: {payload.get('status')!r}"
        )
    subjects = payload.get("subjects")
    if not isinstance(subjects, dict):
        raise WaveDiscriminatorError("Source artifact missing subjects payload")
    return payload


def _extract_wave_rows(
    payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    subjects = payload["subjects"]
    wave_one = subjects.get("continuation_2023_wave_one")
    wave_two = subjects.get("continuation_2023_wave_two")
    if not isinstance(wave_one, dict) or not isinstance(wave_two, dict):
        raise WaveDiscriminatorError("Source artifact missing wave subject summaries")
    if wave_one.get("dominant_state_label") != EXPECTED_STATE_LABEL:
        raise WaveDiscriminatorError(
            "Wave one is not locked as clean_continuation in the source taxonomy artifact"
        )
    if wave_two.get("dominant_state_label") != EXPECTED_STATE_LABEL:
        raise WaveDiscriminatorError(
            "Wave two is not locked as clean_continuation in the source taxonomy artifact"
        )
    rows_one = wave_one.get("rows")
    rows_two = wave_two.get("rows")
    if not isinstance(rows_one, list) or not isinstance(rows_two, list):
        raise WaveDiscriminatorError("Source artifact wave rows are malformed")
    return rows_one, rows_two


def _numeric_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if isinstance(row.get(key), int | float)]


def _categorical_counts(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get(key))
        counts[label] = counts.get(label, 0) + 1
    return [{"label": key_, "count": counts[key_]} for key_ in sorted(counts)]


def _describe_numeric_feature(
    wave_one_rows: list[dict[str, Any]],
    wave_two_rows: list[dict[str, Any]],
    *,
    feature: str,
) -> dict[str, Any]:
    wave_one_values = _numeric_values(wave_one_rows, feature)
    wave_two_values = _numeric_values(wave_two_rows, feature)
    if not wave_one_values or not wave_two_values:
        raise WaveDiscriminatorError(f"Numeric feature {feature!r} missing on one of the waves")

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
            "lower_exclusive": round(left_max, 6),
            "upper_exclusive": round(right_min, 6),
        }

    return {
        "wave_one": {
            "count": len(wave_one_values),
            "mean": round(fmean(wave_one_values), 6),
            "min": round(wave_one_min, 6),
            "max": round(wave_one_max, 6),
        },
        "wave_two": {
            "count": len(wave_two_values),
            "mean": round(fmean(wave_two_values), 6),
            "min": round(wave_two_min, 6),
            "max": round(wave_two_max, 6),
        },
        "mean_gap_wave_two_minus_wave_one": round(
            fmean(wave_two_values) - fmean(wave_one_values),
            6,
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
        "threshold": round(threshold, 6),
        "positive_wave": positive_wave,
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "confusion": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
    }


def _best_single_feature_rules(
    wave_one_rows: list[dict[str, Any]],
    wave_two_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    combined = [{**row, "wave_label": "wave_one"} for row in wave_one_rows] + [
        {**row, "wave_label": "wave_two"} for row in wave_two_rows
    ]

    per_feature_best: dict[str, dict[str, Any]] = {}
    perfect_rules: list[dict[str, Any]] = []
    for feature in NUMERIC_FEATURES:
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
                        -rule["threshold"],
                    ) > (
                        best_rule["accuracy"],
                        best_rule["precision"],
                        best_rule["recall"],
                        -best_rule["threshold"],
                    ):
                        best_rule = rule
                    if rule["accuracy"] == 1.0:
                        perfect_rules.append(rule)
        if best_rule is None:
            raise WaveDiscriminatorError(f"No threshold rules generated for feature {feature!r}")
        per_feature_best[feature] = best_rule

    ordered_best_rules = [per_feature_best[feature] for feature in sorted(per_feature_best)]
    perfect_rules = sorted(
        perfect_rules,
        key=lambda item: (
            item["feature"],
            item["positive_wave"],
            item["operator"],
            item["threshold"],
        ),
    )
    return {
        "best_rule_per_feature": ordered_best_rules,
        "perfect_rules": perfect_rules,
    }


def _categorical_comparison(
    wave_one_rows: list[dict[str, Any]],
    wave_two_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for feature in CATEGORICAL_FEATURES:
        wave_one_counts = _categorical_counts(wave_one_rows, feature)
        wave_two_counts = _categorical_counts(wave_two_rows, feature)
        wave_one_labels = {item["label"] for item in wave_one_counts}
        wave_two_labels = {item["label"] for item in wave_two_counts}
        result[feature] = {
            "wave_one": wave_one_counts,
            "wave_two": wave_two_counts,
            "same_label_set": wave_one_labels == wave_two_labels,
            "same_distribution": wave_one_counts == wave_two_counts,
        }
    return result


def _outcome_context(
    wave_one_rows: list[dict[str, Any]],
    wave_two_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for feature in OUTCOME_FEATURES:
        wave_one_values = _numeric_values(wave_one_rows, feature)
        wave_two_values = _numeric_values(wave_two_rows, feature)
        if not wave_one_values or not wave_two_values:
            continue
        out[feature] = {
            "wave_one": {
                "count": len(wave_one_values),
                "mean": round(fmean(wave_one_values), 6),
                "gt_zero_share": round(
                    sum(value > 0.0 for value in wave_one_values) / len(wave_one_values),
                    6,
                ),
            },
            "wave_two": {
                "count": len(wave_two_values),
                "mean": round(fmean(wave_two_values), 6),
                "gt_zero_share": round(
                    sum(value > 0.0 for value in wave_two_values) / len(wave_two_values),
                    6,
                ),
            },
            "mean_gap_wave_two_minus_wave_one": round(
                fmean(wave_two_values) - fmean(wave_one_values),
                6,
            ),
        }
    return out


def _build_fail_closed_result(
    base_sha: str, reason: str, source_artifact_relative: str
) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-clean-continuation-wave-phase-discriminator-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "source_artifact": source_artifact_relative,
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_wave_phase_discriminator(base_sha: str, source_artifact_relative: Path) -> dict[str, Any]:
    try:
        payload = _load_source_artifact(ROOT_DIR / source_artifact_relative)
        wave_one_rows, wave_two_rows = _extract_wave_rows(payload)
        numeric_comparison = {
            feature: _describe_numeric_feature(
                wave_one_rows,
                wave_two_rows,
                feature=feature,
            )
            for feature in NUMERIC_FEATURES
        }
        rule_search = _best_single_feature_rules(wave_one_rows, wave_two_rows)
        categorical_comparison = _categorical_comparison(wave_one_rows, wave_two_rows)
        outcome_context = _outcome_context(wave_one_rows, wave_two_rows)
    except WaveDiscriminatorError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            source_artifact_relative=str(source_artifact_relative),
        )

    return {
        "audit_version": "ri-policy-router-clean-continuation-wave-phase-discriminator-2026-05-25",
        "base_sha": base_sha,
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "state_lock_required": EXPECTED_STATE_LABEL,
            "decision_time_features_only_for_rule_search": list(NUMERIC_FEATURES)
            + list(CATEGORICAL_FEATURES),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "source_artifact": str(source_artifact_relative),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "subjects": {
            "wave_one": {
                "row_count": len(wave_one_rows),
                "timestamps": [str(row["timestamp"]) for row in wave_one_rows],
                "dominant_state_label": EXPECTED_STATE_LABEL,
            },
            "wave_two": {
                "row_count": len(wave_two_rows),
                "timestamps": [str(row["timestamp"]) for row in wave_two_rows],
                "dominant_state_label": EXPECTED_STATE_LABEL,
            },
        },
        "decision_time_comparison": {
            "numeric_features": numeric_comparison,
            "categorical_features": categorical_comparison,
        },
        "single_feature_rule_search": rule_search,
        "observational_outcome_context": outcome_context,
    }


def main() -> int:
    args = _parse_args()
    source_artifact_relative = Path(args.source_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_wave_phase_discriminator(
        base_sha=args.base_sha,
        source_artifact_relative=source_artifact_relative,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "perfect_rules": result.get("single_feature_rule_search", {}).get("perfect_rules"),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
