# ruff: noqa: E402

from __future__ import annotations

import json
import sys
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
    ri_policy_router_continuation_release_hysteresis_local_packet_20260526 as local_packet,
)

NEGATIVE_CANDIDATE = local_packet.SubjectDefinition(
    subject_id="2024-01",
    role="negative_like_candidate",
    shortlist_key="negative_like_candidates",
    shortlist_rank=2,
)
POSITIVE_CONTROL = local_packet.SubjectDefinition(
    subject_id="2023-05",
    role="positive_control",
    shortlist_key="positive_control_candidates",
    shortlist_rank=0,
)
SUBJECT_DEFINITIONS = (NEGATIVE_CANDIDATE, POSITIVE_CONTROL)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json"
STATUS_OK = "continuation_release_hysteresis_local_packet_candidate_2024_01_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_packet_candidate_2024_01_fail_closed"


class Candidate202401LocalPacketError(RuntimeError):
    pass


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-packet-candidate-2024-01-2026-05-26"
        ),
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "monthly_inventory_windows": str(local_packet.MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(
                local_packet.INTRA_BAND_SIGN_CANDIDATES_RELATIVE
            ),
            "widening_candidate_inventory_artifact": str(
                local_packet.WIDENING_CANDIDATE_INVENTORY_RELATIVE
            ),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "comparison": {
                "negative_like_candidate": NEGATIVE_CANDIDATE.subject_id,
                "positive_control": POSITIVE_CONTROL.subject_id,
            },
        },
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = local_packet._coerce_dict(
        subject_payloads.get(NEGATIVE_CANDIDATE.subject_id),
        field_name=f"subject_payloads.{NEGATIVE_CANDIDATE.subject_id}",
    )
    control = local_packet._coerce_dict(
        subject_payloads.get(POSITIVE_CONTROL.subject_id),
        field_name=f"subject_payloads.{POSITIVE_CONTROL.subject_id}",
    )
    candidate_rules = local_packet._coerce_dict(
        candidate.get("negative_rule_evaluation"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.negative_rule_evaluation",
    )
    control_rules = local_packet._coerce_dict(
        control.get("negative_rule_evaluation"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.negative_rule_evaluation",
    )
    candidate_hits = int(
        local_packet._coerce_float(
            candidate_rules.get("hit_count"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.hit_count",
        )
    )
    control_hits = int(
        local_packet._coerce_float(
            control_rules.get("hit_count"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.hit_count",
        )
    )
    candidate_retention = local_packet._coerce_float(
        local_packet._coerce_dict(
            candidate.get("subject_features"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.subject_features",
        ).get("release_retention_ratio"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.release_retention_ratio",
    )
    control_retention = local_packet._coerce_float(
        local_packet._coerce_dict(
            control.get("subject_features"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.subject_features",
        ).get("release_retention_ratio"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.release_retention_ratio",
    )
    candidate_span_delta = local_packet._coerce_float(
        local_packet._coerce_dict(
            candidate.get("cluster_groups"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.cluster_groups",
        ).get("baseline_minus_release_zero_span_hours"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.span_delta",
    )
    control_span_delta = local_packet._coerce_float(
        local_packet._coerce_dict(
            control.get("cluster_groups"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.cluster_groups",
        ).get("baseline_minus_release_zero_span_hours"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.span_delta",
    )

    if candidate_hits > control_hits:
        status = local_packet.PACKET_STATUS_CANDIDATE_STRONGER
        inference = (
            "The next negative-like widening candidate (`2024-01`) preserves more of the frozen triad's negative "
            "local asymmetry than the established positive control (`2023-05`) when both are rerun on the same "
            "carrier. That keeps `2024-01` alive as the next serious local-window target after `2020-06`."
        )
    elif candidate_hits == control_hits:
        status = local_packet.PACKET_STATUS_TIED
        inference = (
            "The `2024-01` candidate and the `2023-05` control hit the same number of frozen negative-rule "
            "separators, so widening beyond the retired `2020-06` candidate does not yet sharpen the next target "
            "by local structure alone."
        )
    else:
        status = local_packet.PACKET_STATUS_CONTROL_STRONGER
        inference = (
            "The established positive control (`2023-05`) preserves more frozen negative-rule separators than the "
            "supposed next negative-like candidate (`2024-01`), so this widening step does not sustain the current "
            "negative-like ordering."
        )

    return {
        "status": status,
        "candidate_subject_id": NEGATIVE_CANDIDATE.subject_id,
        "control_subject_id": POSITIVE_CONTROL.subject_id,
        "candidate_negative_rule_hit_count": candidate_hits,
        "control_negative_rule_hit_count": control_hits,
        "candidate_release_retention_ratio": local_packet._round_or_none(candidate_retention),
        "control_release_retention_ratio": local_packet._round_or_none(control_retention),
        "candidate_span_compression_hours": local_packet._round_or_none(candidate_span_delta),
        "control_span_compression_hours": local_packet._round_or_none(control_span_delta),
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a strictly local envelope around the `2024-01` "
            "candidate cluster and the already-characterized `2023-05` control cluster to test whether this next "
            "widening target also collapses before execution or carries a different local decay pattern."
        ),
    }


def run_candidate_2024_01_local_packet() -> dict[str, Any]:
    monthly_inventory = local_packet._load_monthly_inventory_windows()
    shortlist = local_packet._load_shortlist()
    negative_feature_order, negative_rules_by_feature = local_packet._load_negative_rules()
    base_cfg, carrier_cfg, authority = local_packet._load_base_and_carrier_cfg()

    subject_payloads = {
        definition.subject_id: local_packet._subject_payload(
            definition,
            monthly_inventory=monthly_inventory,
            shortlist=shortlist,
            negative_feature_order=negative_feature_order,
            negative_rules_by_feature=negative_rules_by_feature,
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in SUBJECT_DEFINITIONS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-packet-candidate-2024-01-2026-05-26"
        ),
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "widening shortlist rerun as two exact full-month subjects on the same carrier, with the next "
                "negative-like candidate (`2024-01`) measured against the already characterized positive control "
                "(`2023-05`) on the frozen local negative rules"
            ),
            "question": (
                "When the next widening candidate (`2024-01`) is rerun against the established control (`2023-05`) on "
                "the same carrier, does the new candidate preserve more of the frozen negative local asymmetry than "
                "the control?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "monthly_inventory_windows": str(local_packet.MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(
                local_packet.INTRA_BAND_SIGN_CANDIDATES_RELATIVE
            ),
            "widening_candidate_inventory_artifact": str(
                local_packet.WIDENING_CANDIDATE_INVENTORY_RELATIVE
            ),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "variant_setting": {
                    "field": "multi_timeframe.research_policy_router.continuation_release_hysteresis",
                    "baseline": "implicit shared hysteresis",
                    "release_zero": 0,
                },
                "negative_like_candidate": NEGATIVE_CANDIDATE.subject_id,
                "positive_control": POSITIVE_CONTROL.subject_id,
            },
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_candidate_2024_01_local_packet()
    except local_packet.LocalPacketError as exc:
        result = _build_fail_closed_result(str(exc))
    except Candidate202401LocalPacketError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = local_packet._coerce_optional_dict(result.get("packet_summary")) or {}
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "candidate_negative_rule_hit_count": packet_summary.get(
            "candidate_negative_rule_hit_count"
        ),
        "control_negative_rule_hit_count": packet_summary.get("control_negative_rule_hit_count"),
        "candidate_subject_id": packet_summary.get("candidate_subject_id"),
        "control_subject_id": packet_summary.get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
