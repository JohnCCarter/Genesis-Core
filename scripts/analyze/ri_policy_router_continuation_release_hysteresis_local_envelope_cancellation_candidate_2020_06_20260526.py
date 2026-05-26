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
    ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_20260526 as envelope_base,
)
from scripts.analyze import (
    ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_20260526 as packet_2020_06,
)

NEGATIVE_CANDIDATE = packet_2020_06.NEGATIVE_CANDIDATE
POSITIVE_CONTROL = packet_2020_06.POSITIVE_CONTROL
SUBJECT_DEFINITIONS = (NEGATIVE_CANDIDATE, POSITIVE_CONTROL)
LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_2026-05-26.json"
STATUS_OK = (
    "continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_generated"
)
STATUS_FAIL_CLOSED = (
    "continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_fail_closed"
)


class Candidate202006LocalEnvelopeError(RuntimeError):
    pass


def _load_local_packet_specs() -> dict[str, envelope_base.EnvelopeSubjectSpec]:
    payload = envelope_base.local_packet._coerce_dict(
        json.loads((ROOT_DIR / LOCAL_PACKET_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_2020_06_local_envelope.local_packet",
    )
    subject_payloads = envelope_base.local_packet._coerce_dict(
        payload.get("subject_payloads"),
        field_name="candidate_2020_06_local_envelope.subject_payloads",
    )

    specs: dict[str, envelope_base.EnvelopeSubjectSpec] = {}
    for definition in SUBJECT_DEFINITIONS:
        subject_payload = envelope_base.local_packet._coerce_dict(
            subject_payloads.get(definition.subject_id),
            field_name=f"candidate_2020_06_local_envelope.subject_payloads.{definition.subject_id}",
        )
        month_window = envelope_base.local_packet._coerce_dict(
            subject_payload.get("month_window"),
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.month_window",
        )
        cluster_groups = envelope_base.local_packet._coerce_dict(
            subject_payload.get("cluster_groups"),
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.cluster_groups",
        )
        union_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("union_diff_surface"),
            field_name=(
                f"candidate_2020_06_local_envelope.{definition.subject_id}.union_diff_surface"
            ),
        )
        baseline_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("baseline"),
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.baseline_groups",
        )
        release_zero_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("release_zero"),
            field_name=(
                f"candidate_2020_06_local_envelope.{definition.subject_id}.release_zero_groups"
            ),
        )
        if len(union_groups) != 1 or len(baseline_groups) != 1 or len(release_zero_groups) != 1:
            raise Candidate202006LocalEnvelopeError(
                f"Expected exactly one envelope group per mode for {definition.subject_id}"
            )

        envelope_group = envelope_base.local_packet._coerce_dict(
            union_groups[0],
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.union_group",
        )
        baseline_group = envelope_base.local_packet._coerce_dict(
            baseline_groups[0],
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.baseline_group",
        )
        release_zero_group = envelope_base.local_packet._coerce_dict(
            release_zero_groups[0],
            field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.release_zero_group",
        )

        specs[definition.subject_id] = envelope_base.EnvelopeSubjectSpec(
            subject_id=definition.subject_id,
            role=envelope_base.local_packet._coerce_str(
                subject_payload.get("role"),
                field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.role",
            ),
            month_start=envelope_base.local_packet._coerce_str(
                month_window.get("start"),
                field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.month_start",
            ),
            month_end=envelope_base.local_packet._coerce_str(
                month_window.get("end"),
                field_name=f"candidate_2020_06_local_envelope.{definition.subject_id}.month_end",
            ),
            inventory_total_return_diff=envelope_base.local_packet._coerce_float(
                month_window.get("inventory_total_return_diff"),
                field_name=(
                    f"candidate_2020_06_local_envelope.{definition.subject_id}.inventory_total_return_diff"
                ),
            ),
            inventory_final_capital_diff=envelope_base.local_packet._coerce_float(
                month_window.get("inventory_final_capital_diff"),
                field_name=(
                    f"candidate_2020_06_local_envelope.{definition.subject_id}.inventory_final_capital_diff"
                ),
            ),
            envelope_start=envelope_base.local_packet._coerce_str(
                envelope_group.get("start"),
                field_name=(
                    f"candidate_2020_06_local_envelope.{definition.subject_id}.envelope_start"
                ),
            ),
            envelope_end=envelope_base.local_packet._coerce_str(
                envelope_group.get("end"),
                field_name=(
                    f"candidate_2020_06_local_envelope.{definition.subject_id}.envelope_end"
                ),
            ),
            envelope_row_count=int(
                envelope_base.local_packet._coerce_float(
                    envelope_group.get("row_count"),
                    field_name=(
                        f"candidate_2020_06_local_envelope.{definition.subject_id}.envelope_row_count"
                    ),
                )
            ),
            baseline_timestamps=tuple(
                envelope_base.local_packet._coerce_str(
                    timestamp,
                    field_name=(
                        f"candidate_2020_06_local_envelope.{definition.subject_id}.baseline_timestamp"
                    ),
                )
                for timestamp in envelope_base.local_packet._coerce_list(
                    baseline_group.get("timestamps"),
                    field_name=(
                        f"candidate_2020_06_local_envelope.{definition.subject_id}.baseline_timestamps"
                    ),
                )
            ),
            release_zero_timestamps=tuple(
                envelope_base.local_packet._coerce_str(
                    timestamp,
                    field_name=(
                        f"candidate_2020_06_local_envelope.{definition.subject_id}.release_zero_timestamp"
                    ),
                )
                for timestamp in envelope_base.local_packet._coerce_list(
                    release_zero_group.get("timestamps"),
                    field_name=(
                        f"candidate_2020_06_local_envelope.{definition.subject_id}.release_zero_timestamps"
                    ),
                )
            ),
        )
    return specs


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = envelope_base.local_packet._coerce_dict(
        subject_payloads.get(NEGATIVE_CANDIDATE.subject_id),
        field_name=f"candidate_2020_06_local_envelope.subject_payloads.{NEGATIVE_CANDIDATE.subject_id}",
    )
    control = envelope_base.local_packet._coerce_dict(
        subject_payloads.get(POSITIVE_CONTROL.subject_id),
        field_name=f"candidate_2020_06_local_envelope.subject_payloads.{POSITIVE_CONTROL.subject_id}",
    )
    candidate_path = envelope_base.local_packet._coerce_dict(
        candidate.get("path_summary"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.path_summary",
    )
    control_path = envelope_base.local_packet._coerce_dict(
        control.get("path_summary"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.path_summary",
    )

    candidate_peak = abs(
        envelope_base.local_packet._coerce_float(
            candidate_path.get("peak_absolute_total_equity_diff"),
            field_name=f"{NEGATIVE_CANDIDATE.subject_id}.peak_absolute_total_equity_diff",
        )
    )
    control_peak = abs(
        envelope_base.local_packet._coerce_float(
            control_path.get("peak_absolute_total_equity_diff"),
            field_name=f"{POSITIVE_CONTROL.subject_id}.peak_absolute_total_equity_diff",
        )
    )
    candidate_month_end = envelope_base.local_packet._coerce_float(
        candidate_path.get("month_end_total_equity_diff"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.month_end_total_equity_diff",
    )
    control_month_end = envelope_base.local_packet._coerce_float(
        control_path.get("month_end_total_equity_diff"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.month_end_total_equity_diff",
    )
    candidate_envelope_end = envelope_base.local_packet._coerce_float(
        candidate_path.get("envelope_end_total_equity_diff"),
        field_name=f"{NEGATIVE_CANDIDATE.subject_id}.envelope_end_total_equity_diff",
    )
    control_envelope_end = envelope_base.local_packet._coerce_float(
        control_path.get("envelope_end_total_equity_diff"),
        field_name=f"{POSITIVE_CONTROL.subject_id}.envelope_end_total_equity_diff",
    )

    if candidate_peak > control_peak + envelope_base.DIFF_TOLERANCE:
        status = envelope_base.PACKET_STATUS_CANDIDATE_STRONGER
        inference = (
            "`2020-06` opens a larger local equity gap than `2023-05` on the same release_zero-minus-baseline "
            "economic path while both months still close back to flat by month end. That would support the local "
            "outcome-cancellation hypothesis more strongly for the new widening candidate than for the control."
        )
    elif control_peak > candidate_peak + envelope_base.DIFF_TOLERANCE:
        status = envelope_base.PACKET_STATUS_CONTROL_STRONGER
        inference = (
            "`2023-05` opens a larger local equity gap than `2020-06`, so the new widening candidate does not "
            "dominate the control on the bounded local economic path."
        )
    else:
        status = envelope_base.PACKET_STATUS_TIED
        inference = (
            "`2020-06` and `2023-05` remain economically invariant on the bounded local envelope path: the "
            "release_zero-minus-baseline total-equity series stays flat, so the observed local packet asymmetry does "
            "not materialize as a local economic gap on this surface."
        )

    return {
        "status": status,
        "candidate_subject_id": NEGATIVE_CANDIDATE.subject_id,
        "control_subject_id": POSITIVE_CONTROL.subject_id,
        "candidate_peak_absolute_total_equity_diff": envelope_base._round_or_none(candidate_peak),
        "control_peak_absolute_total_equity_diff": envelope_base._round_or_none(control_peak),
        "candidate_envelope_end_total_equity_diff": envelope_base._round_or_none(
            candidate_envelope_end
        ),
        "control_envelope_end_total_equity_diff": envelope_base._round_or_none(
            control_envelope_end
        ),
        "candidate_month_end_total_equity_diff": envelope_base._round_or_none(candidate_month_end),
        "control_month_end_total_equity_diff": envelope_base._round_or_none(control_month_end),
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a local action-or-position equivalence check inside "
            "the `2020-06` envelope to determine whether the retained policy/size differences are economically inert "
            "because they preserve the same executed trade path."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-candidate-2020-06-2026-05-26"
        ),
        "base_sha": envelope_base.local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "carrier_path": str(envelope_base.local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(
                envelope_base.local_packet.WORKING_CONTRACT_REFERENCE
            ),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "economic_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
        },
    }


def run_candidate_2020_06_local_envelope_cancellation() -> dict[str, Any]:
    envelope_specs = _load_local_packet_specs()
    base_cfg, carrier_cfg, authority = envelope_base.local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: envelope_base._subject_payload(
            envelope_specs[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in SUBJECT_DEFINITIONS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-candidate-2020-06-2026-05-26"
        ),
        "base_sha": envelope_base.local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed `2020-06` local packet, rerun on the same carrier "
                "and measured only on the release_zero-minus-baseline equity path"
            ),
            "question": (
                "Does the `2020-06` candidate open a larger local equity gap than the `2023-05` control inside the "
                "same continuation-release envelope, and is that local gap later canceled back to flat by month end?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "carrier_path": str(envelope_base.local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(
                envelope_base.local_packet.WORKING_CONTRACT_REFERENCE
            ),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "economic_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
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
        result = run_candidate_2020_06_local_envelope_cancellation()
    except envelope_base.LocalEnvelopeError as exc:
        result = _build_fail_closed_result(str(exc))
    except Candidate202006LocalEnvelopeError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    packet_summary = (
        envelope_base.local_packet._coerce_optional_dict(result.get("packet_summary")) or {}
    )
    summary = {
        "summary_artifact": str(output_json),
        "status": packet_summary.get("status", result.get("status")),
        "candidate_peak_absolute_total_equity_diff": packet_summary.get(
            "candidate_peak_absolute_total_equity_diff"
        ),
        "control_peak_absolute_total_equity_diff": packet_summary.get(
            "control_peak_absolute_total_equity_diff"
        ),
        "candidate_subject_id": packet_summary.get("candidate_subject_id"),
        "control_subject_id": packet_summary.get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
