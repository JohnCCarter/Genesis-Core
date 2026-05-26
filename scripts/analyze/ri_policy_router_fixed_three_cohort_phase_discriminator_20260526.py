from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_ARTIFACT_RELATIVE = Path(
    "results/evaluation/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_fixed_three_cohort_phase_discriminator_2026-05-26.json"
STATUS_OK = "fixed_three_cohort_phase_discriminator_generated"
STATUS_FAIL_CLOSED = "fixed_three_cohort_phase_discriminator_fail_closed"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
SOURCE_EXPECTED_STATUS = "fixed_window_phase_contrast_generated"
NUMERIC_FEATURES = (
    "bars_since_regime_change",
    "action_edge",
    "confidence_gate",
    "clarity_score",
)
CATEGORICAL_FEATURES = (
    "phase_label",
    "phase_family",
    "selected_policy",
    "switch_reason",
    "previous_policy",
    "action_pair",
    "zone",
)
OUTCOME_FEATURES = (
    "fwd_16_close_return_pct",
    "fwd_8_close_return_pct",
    "fwd_4_close_return_pct",
    "mfe_16_pct",
    "mae_16_pct",
)
COHORT_SPECS = {
    "less_hostile_clean_continuation": {
        "source_key": "continuation_2023_wave_one",
        "display_name": "2023-12 wave 1",
    },
    "weak_clean_continuation": {
        "source_key": "continuation_2023_wave_two",
        "display_name": "2023-12 wave 2",
    },
    "blocked_dominant_mixed_pocket": {
        "source_key": "harmful_2024_regression_target",
        "display_name": "2024 harmful target",
    },
}


class ThreeCohortDiscriminatorError(RuntimeError):
    """Raised when the source artifact is missing or structurally invalid."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a read-only three-cohort decision-time discriminator pass over fixed 2023-12 "
            "wave one, 2023-12 wave two, and the fixed 2024 harmful target pocket."
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
        help="Repo-relative phase-contrast artifact used as the three-cohort source.",
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
        raise ThreeCohortDiscriminatorError(f"Source artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ThreeCohortDiscriminatorError("Source artifact is not a JSON object")
    if payload.get("status") != SOURCE_EXPECTED_STATUS:
        raise ThreeCohortDiscriminatorError(
            f"Unexpected source artifact status: {payload.get('status')!r}"
        )
    cohorts = payload.get("cohorts")
    if not isinstance(cohorts, dict):
        raise ThreeCohortDiscriminatorError("Source artifact missing cohorts payload")
    return payload


def _extract_cohort_rows(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    cohorts_payload = payload["cohorts"]
    extracted: dict[str, list[dict[str, Any]]] = {}
    for cohort_label, spec in COHORT_SPECS.items():
        cohort = cohorts_payload.get(spec["source_key"])
        if not isinstance(cohort, dict):
            raise ThreeCohortDiscriminatorError(
                f"Source artifact missing cohort {spec['source_key']!r}"
            )
        rows = cohort.get("rows")
        if not isinstance(rows, list):
            raise ThreeCohortDiscriminatorError(
                f"Source artifact cohort {spec['source_key']!r} missing row payload"
            )
        extracted[cohort_label] = rows
    return extracted


def _numeric_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if isinstance(row.get(key), int | float)]


def _categorical_counts(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get(key))
        counts[label] = counts.get(label, 0) + 1
    return [{"label": key_, "count": counts[key_]} for key_ in sorted(counts)]


def _feature_summary_by_cohort(
    cohort_rows: dict[str, list[dict[str, Any]]],
    *,
    feature: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {"cohorts": {}}
    ordered_means: list[tuple[str, float]] = []
    for cohort_label, rows in cohort_rows.items():
        values = _numeric_values(rows, feature)
        if not values:
            raise ThreeCohortDiscriminatorError(
                f"Numeric feature {feature!r} missing on cohort {cohort_label!r}"
            )
        mean_value = fmean(values)
        ordered_means.append((cohort_label, mean_value))
        result["cohorts"][cohort_label] = {
            "display_name": COHORT_SPECS[cohort_label]["display_name"],
            "count": len(values),
            "mean": round(mean_value, 6),
            "min": round(min(values), 6),
            "max": round(max(values), 6),
        }
    result["ordered_by_mean_low_to_high"] = [
        {
            "cohort": cohort_label,
            "display_name": COHORT_SPECS[cohort_label]["display_name"],
            "mean": round(mean_value, 6),
        }
        for cohort_label, mean_value in sorted(ordered_means, key=lambda item: item[1])
    ]
    return result


def _categorical_comparison(cohort_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for feature in CATEGORICAL_FEATURES:
        feature_payload: dict[str, Any] = {"cohorts": {}}
        label_sets: dict[str, set[str]] = {}
        for cohort_label, rows in cohort_rows.items():
            counts = _categorical_counts(rows, feature)
            labels = {item["label"] for item in counts}
            label_sets[cohort_label] = labels
            feature_payload["cohorts"][cohort_label] = {
                "display_name": COHORT_SPECS[cohort_label]["display_name"],
                "counts": counts,
            }
        feature_payload["all_label_sets_equal"] = (
            len({frozenset(labels) for labels in label_sets.values()}) == 1
        )
        result[feature] = feature_payload
    return result


def _evaluate_one_vs_rest_rule(
    rows: list[dict[str, Any]],
    *,
    feature: str,
    threshold: float,
    operator: str,
    positive_cohort: str,
) -> dict[str, Any]:
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    for row in rows:
        value = float(row[feature])
        is_positive = row["cohort_label"] == positive_cohort
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
        "positive_cohort": positive_cohort,
        "positive_display_name": COHORT_SPECS[positive_cohort]["display_name"],
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


def _best_one_vs_rest_rules(cohort_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    combined = [
        {**row, "cohort_label": cohort_label}
        for cohort_label, rows in cohort_rows.items()
        for row in rows
    ]
    best_rules: list[dict[str, Any]] = []
    perfect_rules: list[dict[str, Any]] = []
    for feature in NUMERIC_FEATURES:
        unique_values = sorted(
            {float(row[feature]) for row in combined if isinstance(row.get(feature), int | float)}
        )
        candidate_thresholds = [
            (left + right) / 2.0
            for left, right in zip(unique_values, unique_values[1:], strict=False)
        ]
        if unique_values:
            candidate_thresholds.extend([unique_values[0], unique_values[-1]])
        for positive_cohort in COHORT_SPECS:
            best_rule: dict[str, Any] | None = None
            for operator in (">=", "<="):
                for threshold in candidate_thresholds:
                    rule = _evaluate_one_vs_rest_rule(
                        combined,
                        feature=feature,
                        threshold=threshold,
                        operator=operator,
                        positive_cohort=positive_cohort,
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
                raise ThreeCohortDiscriminatorError(
                    f"No one-vs-rest threshold rule generated for {feature!r}/{positive_cohort!r}"
                )
            best_rules.append(best_rule)
    best_rules = sorted(
        best_rules,
        key=lambda item: (
            item["feature"],
            item["positive_cohort"],
            item["operator"],
            item["threshold"],
        ),
    )
    perfect_rules = sorted(
        perfect_rules,
        key=lambda item: (
            item["feature"],
            item["positive_cohort"],
            item["operator"],
            item["threshold"],
        ),
    )
    return {
        "best_rule_per_feature_and_cohort": best_rules,
        "perfect_rules": perfect_rules,
    }


def _evaluate_ordered_split(
    rows: list[dict[str, Any]],
    *,
    feature: str,
    lower_threshold: float,
    upper_threshold: float,
    cohort_order: tuple[str, str, str],
) -> dict[str, Any]:
    confusion = {actual: dict.fromkeys(COHORT_SPECS, 0) for actual in COHORT_SPECS}
    correct = 0
    for row in rows:
        value = float(row[feature])
        if value <= lower_threshold:
            predicted = cohort_order[0]
        elif value <= upper_threshold:
            predicted = cohort_order[1]
        else:
            predicted = cohort_order[2]
        actual = row["cohort_label"]
        confusion[actual][predicted] += 1
        if actual == predicted:
            correct += 1
    total = len(rows)
    accuracy = correct / total if total else 0.0
    return {
        "feature": feature,
        "cohort_order": list(cohort_order),
        "cohort_order_display": [COHORT_SPECS[label]["display_name"] for label in cohort_order],
        "lower_threshold": round(lower_threshold, 6),
        "upper_threshold": round(upper_threshold, 6),
        "accuracy": round(accuracy, 6),
        "confusion": confusion,
    }


def _best_ordered_feature_splits(cohort_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    combined = [
        {**row, "cohort_label": cohort_label}
        for cohort_label, rows in cohort_rows.items()
        for row in rows
    ]
    best_splits: list[dict[str, Any]] = []
    perfect_splits: list[dict[str, Any]] = []
    for feature in NUMERIC_FEATURES:
        unique_values = sorted(
            {float(row[feature]) for row in combined if isinstance(row.get(feature), int | float)}
        )
        thresholds = [
            (left + right) / 2.0
            for left, right in zip(unique_values, unique_values[1:], strict=False)
        ]
        if len(thresholds) < 2:
            raise ThreeCohortDiscriminatorError(
                f"Insufficient thresholds for ordered split search on feature {feature!r}"
            )
        best_split: dict[str, Any] | None = None
        for lower_threshold, upper_threshold in combinations(thresholds, 2):
            for cohort_order in permutations(COHORT_SPECS.keys(), 3):
                split = _evaluate_ordered_split(
                    combined,
                    feature=feature,
                    lower_threshold=lower_threshold,
                    upper_threshold=upper_threshold,
                    cohort_order=cohort_order,
                )
                if best_split is None or (
                    split["accuracy"],
                    -split["lower_threshold"],
                    -split["upper_threshold"],
                ) > (
                    best_split["accuracy"],
                    -best_split["lower_threshold"],
                    -best_split["upper_threshold"],
                ):
                    best_split = split
                if split["accuracy"] == 1.0:
                    perfect_splits.append(split)
        if best_split is None:
            raise ThreeCohortDiscriminatorError(
                f"No ordered split generated for feature {feature!r}"
            )
        best_splits.append(best_split)
    best_splits = sorted(best_splits, key=lambda item: item["feature"])
    perfect_splits = sorted(
        perfect_splits,
        key=lambda item: (
            item["feature"],
            tuple(item["cohort_order"]),
            item["lower_threshold"],
            item["upper_threshold"],
        ),
    )
    return {
        "best_split_per_feature": best_splits,
        "perfect_splits": perfect_splits,
    }


def _outcome_context(cohort_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for feature in OUTCOME_FEATURES:
        feature_payload: dict[str, Any] = {"cohorts": {}}
        any_values = False
        for cohort_label, rows in cohort_rows.items():
            values = _numeric_values(rows, feature)
            if not values:
                continue
            any_values = True
            feature_payload["cohorts"][cohort_label] = {
                "display_name": COHORT_SPECS[cohort_label]["display_name"],
                "count": len(values),
                "mean": round(fmean(values), 6),
                "gt_zero_share": round(
                    sum(value > 0.0 for value in values) / len(values),
                    6,
                ),
            }
        if any_values:
            result[feature] = feature_payload
    return result


def _build_fail_closed_result(
    base_sha: str, reason: str, source_artifact_relative: str
) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-fixed-three-cohort-phase-discriminator-2026-05-26",
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


def run_three_cohort_discriminator(
    *,
    base_sha: str,
    source_artifact_relative: Path,
) -> dict[str, Any]:
    try:
        payload = _load_source_artifact(ROOT_DIR / source_artifact_relative)
        cohort_rows = _extract_cohort_rows(payload)
        numeric_comparison = {
            feature: _feature_summary_by_cohort(cohort_rows, feature=feature)
            for feature in NUMERIC_FEATURES
        }
        one_vs_rest_rules = _best_one_vs_rest_rules(cohort_rows)
        ordered_splits = _best_ordered_feature_splits(cohort_rows)
        categorical_comparison = _categorical_comparison(cohort_rows)
        outcome_context = _outcome_context(cohort_rows)
    except ThreeCohortDiscriminatorError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            source_artifact_relative=str(source_artifact_relative),
        )

    return {
        "audit_version": "ri-policy-router-fixed-three-cohort-phase-discriminator-2026-05-26",
        "base_sha": base_sha,
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "source_surface": "fixed local subjects only",
            "decision_time_numeric_features_only_for_rule_search": list(NUMERIC_FEATURES),
            "categorical_features_descriptive_only": list(CATEGORICAL_FEATURES),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "source_artifact": str(source_artifact_relative),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "subjects": {
            cohort_label: {
                "display_name": COHORT_SPECS[cohort_label]["display_name"],
                "row_count": len(rows),
                "timestamps": [str(row["timestamp"]) for row in rows],
            }
            for cohort_label, rows in cohort_rows.items()
        },
        "decision_time_comparison": {
            "numeric_features": numeric_comparison,
            "categorical_features": categorical_comparison,
        },
        "one_vs_rest_rule_search": one_vs_rest_rules,
        "single_feature_ordered_split_search": ordered_splits,
        "observational_outcome_context": outcome_context,
    }


def main() -> int:
    args = _parse_args()
    source_artifact_relative = Path(args.source_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_three_cohort_discriminator(
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
                "perfect_ordered_splits": result.get("single_feature_ordered_split_search", {}).get(
                    "perfect_splits"
                ),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
