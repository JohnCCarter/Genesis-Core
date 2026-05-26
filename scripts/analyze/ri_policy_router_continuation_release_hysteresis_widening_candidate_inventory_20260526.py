from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
MONTHLY_INVENTORY_WINDOWS_RELATIVE = Path(
    "results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/"
    "continuation_release_hysteresis_monthly_inventory_windows.json"
)
INTRA_BAND_SIGN_CANDIDATES_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json"
)
TRIAD_SYNTHESIS_NOTE_RELATIVE = Path(
    "docs/analysis/regime_intelligence/policy_router/"
    "ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_widening_candidate_inventory_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_widening_candidate_inventory_fail_closed"
RANKING_STATUS = "seam_active_non_divergent_months_ranked_for_widening"

PROXY_FEATURES = (
    "behavioral_row_diff_count",
    "selected_policy_diff_count",
    "switch_reason_diff_count",
    "size_diff_count",
    "baseline_continuation_release_row_count",
    "release_zero_continuation_release_row_count",
    "release_retention_ratio",
)
NEGATIVE_SHORTLIST_LIMIT = 4
POSITIVE_SHORTLIST_LIMIT = 3
EXPECTED_TRIAD = {
    "2018-03": "negative",
    "2021-08": "positive",
    "2025-10": "positive",
}


@dataclass(frozen=True)
class MonthlyWindow:
    label: str
    top_line_sign: str
    topline_changed: bool
    subject_features: dict[str, float]


class WideningCandidateInventoryError(RuntimeError):
    pass


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WideningCandidateInventoryError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise WideningCandidateInventoryError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise WideningCandidateInventoryError(
            f"Expected non-empty string for {field_name}, got {value!r}"
        )
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise WideningCandidateInventoryError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise WideningCandidateInventoryError(
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


def _sign_label(total_return_diff: float) -> str:
    if total_return_diff > 0:
        return "positive"
    if total_return_diff < 0:
        return "negative"
    return "flat"


def _normalize_windows(payload: list[Any]) -> list[MonthlyWindow]:
    normalized: list[MonthlyWindow] = []
    for index, raw_window in enumerate(payload):
        window = _coerce_dict(raw_window, field_name=f"monthly_inventory[{index}]")
        baseline_release_rows = int(
            _coerce_float(
                window.get("baseline_continuation_release_row_count"),
                field_name=f"monthly_inventory[{index}].baseline_continuation_release_row_count",
            )
        )
        release_zero_release_rows = int(
            _coerce_float(
                window.get("release_zero_continuation_release_row_count"),
                field_name=f"monthly_inventory[{index}].release_zero_continuation_release_row_count",
            )
        )
        if baseline_release_rows <= 0 and release_zero_release_rows <= 0:
            continue

        total_return_diff = _coerce_float(
            window.get("total_return_diff"),
            field_name=f"monthly_inventory[{index}].total_return_diff",
        )
        retention_ratio = (
            release_zero_release_rows / baseline_release_rows if baseline_release_rows else 0.0
        )
        normalized.append(
            MonthlyWindow(
                label=_coerce_str(
                    window.get("label"), field_name=f"monthly_inventory[{index}].label"
                ),
                top_line_sign=_sign_label(total_return_diff),
                topline_changed=_coerce_bool(
                    window.get("topline_changed"),
                    field_name=f"monthly_inventory[{index}].topline_changed",
                ),
                subject_features={
                    "behavioral_row_diff_count": _coerce_float(
                        window.get("behavioral_row_diff_count"),
                        field_name=f"monthly_inventory[{index}].behavioral_row_diff_count",
                    ),
                    "selected_policy_diff_count": _coerce_float(
                        window.get("selected_policy_diff_count"),
                        field_name=f"monthly_inventory[{index}].selected_policy_diff_count",
                    ),
                    "switch_reason_diff_count": _coerce_float(
                        window.get("switch_reason_diff_count"),
                        field_name=f"monthly_inventory[{index}].switch_reason_diff_count",
                    ),
                    "size_diff_count": _coerce_float(
                        window.get("size_diff_count"),
                        field_name=f"monthly_inventory[{index}].size_diff_count",
                    ),
                    "baseline_continuation_release_row_count": float(baseline_release_rows),
                    "release_zero_continuation_release_row_count": float(release_zero_release_rows),
                    "release_retention_ratio": retention_ratio,
                },
            )
        )

    if not normalized:
        raise WideningCandidateInventoryError("No seam-active monthly windows recovered")
    return normalized


def _feature_extrema(windows: list[MonthlyWindow]) -> dict[str, dict[str, float]]:
    extrema: dict[str, dict[str, float]] = {}
    for feature in PROXY_FEATURES:
        values = [float(window.subject_features[feature]) for window in windows]
        extrema[feature] = {
            "min": min(values),
            "max": max(values),
        }
    return extrema


def _normalized_feature(
    window: MonthlyWindow, *, feature: str, extrema: dict[str, dict[str, float]]
) -> float:
    min_value = float(extrema[feature]["min"])
    max_value = float(extrema[feature]["max"])
    raw_value = float(window.subject_features[feature])
    if max_value == min_value:
        return 0.0
    return (raw_value - min_value) / (max_value - min_value)


def _normalized_vector(
    window: MonthlyWindow, *, extrema: dict[str, dict[str, float]]
) -> dict[str, float]:
    return {
        feature: _normalized_feature(window, feature=feature, extrema=extrema)
        for feature in PROXY_FEATURES
    }


def _distance(left: dict[str, float], right: dict[str, float]) -> float:
    return math.sqrt(sum((left[feature] - right[feature]) ** 2 for feature in PROXY_FEATURES))


def _triad_windows(windows: list[MonthlyWindow]) -> dict[str, MonthlyWindow]:
    triad = {window.label: window for window in windows if window.topline_changed}
    if set(triad) != set(EXPECTED_TRIAD):
        raise WideningCandidateInventoryError(
            f"Frozen triad drifted: expected {sorted(EXPECTED_TRIAD)}, got {sorted(triad)}"
        )
    for label, sign in EXPECTED_TRIAD.items():
        if triad[label].top_line_sign != sign:
            raise WideningCandidateInventoryError(
                f"Frozen triad sign drifted for {label}: expected {sign}, got {triad[label].top_line_sign}"
            )
    return triad


def _proxy_limitations() -> list[str]:
    return [
        "monthly inventory exposes whole-window count/retention proxies, not the decisive-timing or decisive-support fields used in the intra-band triad slice",
        "selected_policy_diff_count, switch_reason_diff_count, and size_diff_count are inventory-level counts, not exact continuation-release cluster-only counts",
        "this slice ranks widening candidates for a fresh packet; it does not create new exact-subject verdicts or claim hidden local top-line divergence already exists",
    ]


def _candidate_payload(
    window: MonthlyWindow,
    *,
    negative_signature: dict[str, float],
    positive_centroid: dict[str, float],
    extrema: dict[str, dict[str, float]],
) -> dict[str, Any]:
    normalized = _normalized_vector(window, extrema=extrema)
    negative_distance = _distance(normalized, negative_signature)
    positive_distance = _distance(normalized, positive_centroid)
    closer_to_negative = negative_distance < positive_distance
    return {
        "label": window.label,
        "orientation": "negative_like" if closer_to_negative else "positive_like_or_neutral",
        "negative_signature_distance": _round_or_none(negative_distance),
        "positive_signature_distance": _round_or_none(positive_distance),
        "orientation_margin": _round_or_none(positive_distance - negative_distance),
        "subject_features": {
            feature: _round_or_none(window.subject_features[feature]) for feature in PROXY_FEATURES
        },
    }


def _candidate_rankings(windows: list[MonthlyWindow]) -> dict[str, Any]:
    triad = _triad_windows(windows)
    extrema = _feature_extrema(windows)
    negative_anchor = triad["2018-03"]
    positive_windows = [triad["2021-08"], triad["2025-10"]]
    negative_signature = _normalized_vector(negative_anchor, extrema=extrema)
    positive_vectors = [_normalized_vector(window, extrema=extrema) for window in positive_windows]
    positive_centroid = {
        feature: fmean(vector[feature] for vector in positive_vectors) for feature in PROXY_FEATURES
    }

    candidate_payloads = [
        _candidate_payload(
            window,
            negative_signature=negative_signature,
            positive_centroid=positive_centroid,
            extrema=extrema,
        )
        for window in windows
        if not window.topline_changed
    ]

    negative_like = sorted(
        [payload for payload in candidate_payloads if payload["orientation"] == "negative_like"],
        key=lambda payload: (
            float(payload["negative_signature_distance"]),
            -float(payload["subject_features"]["behavioral_row_diff_count"]),
            str(payload["label"]),
        ),
    )
    positive_like = sorted(
        [
            payload
            for payload in candidate_payloads
            if payload["orientation"] == "positive_like_or_neutral"
        ],
        key=lambda payload: (
            float(payload["positive_signature_distance"]),
            -float(payload["subject_features"]["behavioral_row_diff_count"]),
            str(payload["label"]),
        ),
    )

    return {
        "triad_reference": {
            label: {
                "top_line_sign": triad[label].top_line_sign,
                "subject_features": {
                    feature: _round_or_none(triad[label].subject_features[feature])
                    for feature in PROXY_FEATURES
                },
            }
            for label in sorted(triad)
        },
        "extrema": {
            feature: {
                "min": _round_or_none(extrema[feature]["min"]),
                "max": _round_or_none(extrema[feature]["max"]),
            }
            for feature in PROXY_FEATURES
        },
        "negative_signature_anchor": {
            "label": negative_anchor.label,
            "normalized_features": {
                feature: _round_or_none(negative_signature[feature]) for feature in PROXY_FEATURES
            },
        },
        "positive_signature_centroid": {
            "labels": [window.label for window in positive_windows],
            "normalized_features": {
                feature: _round_or_none(positive_centroid[feature]) for feature in PROXY_FEATURES
            },
        },
        "all_non_divergent_candidates": candidate_payloads,
        "negative_like_ranked": negative_like,
        "positive_like_or_neutral_ranked": positive_like,
        "next_packet_shortlist": {
            "negative_like_candidates": negative_like[:NEGATIVE_SHORTLIST_LIMIT],
            "positive_control_candidates": positive_like[:POSITIVE_SHORTLIST_LIMIT],
        },
    }


def _sign_candidate_context() -> dict[str, Any]:
    payload = _coerce_dict(
        _load_json(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
        field_name="intra_band_sign_candidates_artifact",
    )
    sign_summary = _coerce_dict(payload.get("sign_summary"), field_name="sign_summary")
    return {
        "status": _coerce_str(sign_summary.get("status"), field_name="sign_summary.status"),
        "perfect_negative_separators": _coerce_list(
            sign_summary.get("perfect_negative_separators"),
            field_name="sign_summary.perfect_negative_separators",
        ),
        "non_perfect_features": _coerce_list(
            sign_summary.get("non_perfect_features"),
            field_name="sign_summary.non_perfect_features",
        ),
    }


def _ranking_summary(rankings: dict[str, Any]) -> dict[str, Any]:
    negative_like = _coerce_list(
        rankings.get("negative_like_ranked"), field_name="rankings.negative_like_ranked"
    )
    positive_like = _coerce_list(
        rankings.get("positive_like_or_neutral_ranked"),
        field_name="rankings.positive_like_or_neutral_ranked",
    )
    shortlist = _coerce_dict(
        rankings.get("next_packet_shortlist"), field_name="rankings.next_packet_shortlist"
    )
    negative_shortlist = _coerce_list(
        shortlist.get("negative_like_candidates"),
        field_name="rankings.next_packet_shortlist.negative_like_candidates",
    )
    positive_shortlist = _coerce_list(
        shortlist.get("positive_control_candidates"),
        field_name="rankings.next_packet_shortlist.positive_control_candidates",
    )

    return {
        "status": RANKING_STATUS,
        "negative_like_candidate_count": len(negative_like),
        "positive_like_or_neutral_candidate_count": len(positive_like),
        "top_negative_like_labels": [str(candidate["label"]) for candidate in negative_shortlist],
        "top_positive_control_labels": [
            str(candidate["label"]) for candidate in positive_shortlist
        ],
        "inference": (
            "The frozen monthly inventory remains exhausted as an exact top-line-divergent subject bench, but "
            "it still contains seam-active non-divergent months that look materially closer to the negative "
            "triad signature than to the positive centroid on the monthly count/retention proxies. Those months "
            "are the smallest current widening targets for a fresh packet."
        ),
        "next_hypothesis": (
            "If this chain continues, the next honest widening packet should localize around the top "
            "negative-like near-miss months and pair them with positive-like controls, rather than reopening the "
            "full monthly bench without a narrowing target."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-widening-candidate-inventory-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "monthly_inventory_windows": str(MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
            "triad_synthesis_note": str(TRIAD_SYNTHESIS_NOTE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_widening_candidate_inventory() -> dict[str, Any]:
    windows_payload = _coerce_list(
        _load_json(MONTHLY_INVENTORY_WINDOWS_RELATIVE), field_name="monthly_inventory_windows"
    )
    normalized_windows = _normalize_windows(windows_payload)
    rankings = _candidate_rankings(normalized_windows)
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-widening-candidate-inventory-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": "frozen continuation_release_hysteresis monthly inventory plus the triad-local intra-band sign candidate slice",
            "question": (
                "Which seam-active monthly windows with zero monthly top-line divergence are the best current widening "
                "candidates for a fresh packet, when ranked by monthly inventory proxies for the triad-local negative "
                "vs positive signatures?"
            ),
            "proxy_features": list(PROXY_FEATURES),
            "proxy_limitations": _proxy_limitations(),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "monthly_inventory_windows": str(MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
            "triad_synthesis_note": str(TRIAD_SYNTHESIS_NOTE_RELATIVE),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
        "sign_candidate_context": _sign_candidate_context(),
        "rankings": rankings,
        "ranking_summary": _ranking_summary(rankings),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_widening_candidate_inventory()
    except WideningCandidateInventoryError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("ranking_summary", {}).get("status", result.get("status")),
        "top_negative_like_labels": result.get("ranking_summary", {}).get(
            "top_negative_like_labels"
        ),
        "top_positive_control_labels": result.get("ranking_summary", {}).get(
            "top_positive_control_labels"
        ),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
