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
    ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526 as packet_2024_01,
)

NEGATIVE_CANDIDATE = packet_2024_01.NEGATIVE_CANDIDATE
POSITIVE_CONTROL = packet_2024_01.POSITIVE_CONTROL
SUBJECT_DEFINITIONS = (NEGATIVE_CANDIDATE, POSITIVE_CONTROL)
LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_2026-05-26.json"
STATUS_OK = (
    "continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_generated"
)
STATUS_FAIL_CLOSED = (
    "continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_fail_closed"
)


class Candidate202401LocalEnvelopeError(RuntimeError):
    pass


def _load_local_packet_specs() -> dict[str, envelope_base.EnvelopeSubjectSpec]:
    payload = envelope_base.local_packet._coerce_dict(
        json.loads((ROOT_DIR / LOCAL_PACKET_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_2024_01_local_envelope.local_packet",
    )
    subject_payloads = envelope_base.local_packet._coerce_dict(
        payload.get("subject_payloads"),
        field_name="candidate_2024_01_local_envelope.subject_payloads",
    )

    specs: dict[str, envelope_base.EnvelopeSubjectSpec] = {}
    for definition in SUBJECT_DEFINITIONS:
        subject_payload = envelope_base.local_packet._coerce_dict(
            subject_payloads.get(definition.subject_id),
            field_name=f"candidate_2024_01_local_envelope.subject_payloads.{definition.subject_id}",
        )
        month_window = envelope_base.local_packet._coerce_dict(
            subject_payload.get("month_window"),
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.month_window",
        )
        cluster_groups = envelope_base.local_packet._coerce_dict(
            subject_payload.get("cluster_groups"),
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.cluster_groups",
        )
        union_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("union_diff_surface"),
            field_name=(
                f"candidate_2024_01_local_envelope.{definition.subject_id}.union_diff_surface"
            ),
        )
        baseline_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("baseline"),
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.baseline_groups",
        )
        release_zero_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("release_zero"),
            field_name=(
                f"candidate_2024_01_local_envelope.{definition.subject_id}.release_zero_groups"
            ),
        )
        if len(union_groups) != 1 or len(baseline_groups) != 1 or len(release_zero_groups) != 1:
            raise Candidate202401LocalEnvelopeError(
                f"Expected exactly one envelope group per mode for {definition.subject_id}"
            )

        envelope_group = envelope_base.local_packet._coerce_dict(
            union_groups[0],
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.union_group",
        )
        baseline_group = envelope_base.local_packet._coerce_dict(
            baseline_groups[0],
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.baseline_group",
        )
        release_zero_group = envelope_base.local_packet._coerce_dict(
            release_zero_groups[0],
            field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.release_zero_group",
        )

        specs[definition.subject_id] = envelope_base.EnvelopeSubjectSpec(
            subject_id=definition.subject_id,
            role=envelope_base.local_packet._coerce_str(
                subject_payload.get("role"),
                field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.role",
            ),
            month_start=envelope_base.local_packet._coerce_str(
                month_window.get("start"),
                field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.month_start",
            ),
            month_end=envelope_base.local_packet._coerce_str(
                month_window.get("end"),
                field_name=f"candidate_2024_01_local_envelope.{definition.subject_id}.month_end",
            ),
            inventory_total_return_diff=envelope_base.local_packet._coerce_float(
                month_window.get("inventory_total_return_diff"),
                field_name=(
                    f"candidate_2024_01_local_envelope.{definition.subject_id}.inventory_total_return_diff"
                ),
            ),
            inventory_final_capital_diff=envelope_base.local_packet._coerce_float(
                month_window.get("inventory_final_capital_diff"),
                field_name=(
                    f"candidate_2024_01_local_envelope.{definition.subject_id}.inventory_final_capital_diff"
                ),
            ),
            envelope_start=envelope_base.local_packet._coerce_str(
                envelope_group.get("start"),
                field_name=(
                    f"candidate_2024_01_local_envelope.{definition.subject_id}.envelope_start"
                ),
            ),
            envelope_end=envelope_base.local_packet._coerce_str(
                envelope_group.get("end"),
                field_name=(
                    f"candidate_2024_01_local_envelope.{definition.subject_id}.envelope_end"
                ),
            ),
            envelope_row_count=int(
                envelope_base.local_packet._coerce_float(
                    envelope_group.get("row_count"),
                    field_name=(
                        f"candidate_2024_01_local_envelope.{definition.subject_id}.envelope_row_count"
                    ),
                )
            ),
            baseline_timestamps=tuple(
                envelope_base.local_packet._coerce_str(
                    timestamp,
                    field_name=(
                        f"candidate_2024_01_local_envelope.{definition.subject_id}.baseline_timestamp"
                    ),
                )
                for timestamp in envelope_base.local_packet._coerce_list(
                    baseline_group.get("timestamps"),
                    field_name=(
                        f"candidate_2024_01_local_envelope.{definition.subject_id}.baseline_timestamps"
                    ),
                )
            ),
            release_zero_timestamps=tuple(
                envelope_base.local_packet._coerce_str(
                    timestamp,
                    field_name=(
                        f"candidate_2024_01_local_envelope.{definition.subject_id}.release_zero_timestamp"
                    ),
                )
                for timestamp in envelope_base.local_packet._coerce_list(
                    release_zero_group.get("timestamps"),
                    field_name=(
                        f"candidate_2024_01_local_envelope.{definition.subject_id}.release_zero_timestamps"
                    ),
                )
            ),
        )
    return specs


def _load_exact_envelope_timestamps() -> dict[str, tuple[str, ...]]:
    payload = envelope_base.local_packet._coerce_dict(
        json.loads((ROOT_DIR / LOCAL_PACKET_RELATIVE).read_text(encoding="utf-8")),
        field_name="candidate_2024_01_local_envelope.exact_timestamps.local_packet",
    )
    subject_payloads = envelope_base.local_packet._coerce_dict(
        payload.get("subject_payloads"),
        field_name="candidate_2024_01_local_envelope.exact_timestamps.subject_payloads",
    )

    timestamps_by_subject: dict[str, tuple[str, ...]] = {}
    for definition in SUBJECT_DEFINITIONS:
        subject_payload = envelope_base.local_packet._coerce_dict(
            subject_payloads.get(definition.subject_id),
            field_name=(
                f"candidate_2024_01_local_envelope.exact_timestamps.subject_payloads.{definition.subject_id}"
            ),
        )
        cluster_groups = envelope_base.local_packet._coerce_dict(
            subject_payload.get("cluster_groups"),
            field_name=(
                f"candidate_2024_01_local_envelope.exact_timestamps.{definition.subject_id}.cluster_groups"
            ),
        )
        union_groups = envelope_base.local_packet._coerce_list(
            cluster_groups.get("union_diff_surface"),
            field_name=(
                f"candidate_2024_01_local_envelope.exact_timestamps.{definition.subject_id}.union_diff_surface"
            ),
        )
        if len(union_groups) != 1:
            raise Candidate202401LocalEnvelopeError(
                f"Expected exactly one union envelope group for {definition.subject_id}"
            )
        union_group = envelope_base.local_packet._coerce_dict(
            union_groups[0],
            field_name=(
                f"candidate_2024_01_local_envelope.exact_timestamps.{definition.subject_id}.union_group"
            ),
        )
        timestamps_by_subject[definition.subject_id] = tuple(
            envelope_base.local_packet._coerce_str(
                timestamp,
                field_name=(
                    f"candidate_2024_01_local_envelope.exact_timestamps.{definition.subject_id}.timestamp"
                ),
            )
            for timestamp in envelope_base.local_packet._coerce_list(
                union_group.get("timestamps"),
                field_name=(
                    f"candidate_2024_01_local_envelope.exact_timestamps.{definition.subject_id}.timestamps"
                ),
            )
        )
    return timestamps_by_subject


def _subject_payload(
    spec: envelope_base.EnvelopeSubjectSpec,
    *,
    exact_envelope_timestamps: tuple[str, ...],
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    baseline = envelope_base._run_case_with_economics(
        "baseline",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = envelope_base._run_case_with_economics(
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
        raise Candidate202401LocalEnvelopeError(
            f"Baseline continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.baseline_timestamps}, actual={observed_baseline_timestamps}"
        )
    if observed_release_zero_timestamps != spec.release_zero_timestamps:
        raise Candidate202401LocalEnvelopeError(
            f"Release-zero continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.release_zero_timestamps}, actual={observed_release_zero_timestamps}"
        )

    baseline_summary = envelope_base.local_packet._coerce_dict(
        baseline.get("summary"), field_name=f"{spec.subject_id}.baseline.summary"
    )
    release_zero_summary = envelope_base.local_packet._coerce_dict(
        release_zero.get("summary"), field_name=f"{spec.subject_id}.release_zero.summary"
    )
    total_return_diff = envelope_base.local_packet._coerce_float(
        release_zero_summary.get("total_return"),
        field_name=f"{spec.subject_id}.release_zero.total_return",
    ) - envelope_base.local_packet._coerce_float(
        baseline_summary.get("total_return"),
        field_name=f"{spec.subject_id}.baseline.total_return",
    )
    final_capital_diff = envelope_base.local_packet._coerce_float(
        release_zero_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.release_zero.final_capital",
    ) - envelope_base.local_packet._coerce_float(
        baseline_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.baseline.final_capital",
    )
    if not envelope_base.math.isclose(
        total_return_diff, spec.inventory_total_return_diff, abs_tol=1e-12
    ):
        raise Candidate202401LocalEnvelopeError(
            f"Monthly total return diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_total_return_diff}, actual={total_return_diff}"
        )
    if not envelope_base.math.isclose(
        final_capital_diff, spec.inventory_final_capital_diff, abs_tol=1e-9
    ):
        raise Candidate202401LocalEnvelopeError(
            f"Monthly final capital diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_final_capital_diff}, actual={final_capital_diff}"
        )

    diff_rows = envelope_base._build_equity_diff_series(
        baseline.get("equity_curve"),
        release_zero.get("equity_curve"),
        field_name=f"{spec.subject_id}.equity_diff_series",
    )
    exact_timestamps = set(exact_envelope_timestamps)
    envelope_rows = [row for row in diff_rows if str(row["timestamp"]) in exact_timestamps]
    if len(envelope_rows) != len(exact_envelope_timestamps):
        raise Candidate202401LocalEnvelopeError(
            f"Envelope row-count drift for {spec.subject_id}: expected={len(exact_envelope_timestamps)}, actual={len(envelope_rows)}"
        )

    pre_anchor_row = envelope_base._last_row_before(diff_rows, spec.envelope_start)
    envelope_start_row = envelope_base._find_row_by_timestamp(diff_rows, spec.envelope_start)
    envelope_end_row = envelope_base._find_row_by_timestamp(diff_rows, spec.envelope_end)
    month_end_row = diff_rows[-1]
    peak_positive_row = max(envelope_rows, key=lambda row: float(row["total_equity_diff"]))
    peak_negative_row = min(envelope_rows, key=lambda row: float(row["total_equity_diff"]))
    peak_abs_row = max(envelope_rows, key=lambda row: abs(float(row["total_equity_diff"])))
    full_month_peak_abs_row = max(diff_rows, key=lambda row: abs(float(row["total_equity_diff"])))

    month_end_total_equity_diff = float(month_end_row["total_equity_diff"])
    if not envelope_base.math.isclose(
        month_end_total_equity_diff, final_capital_diff, abs_tol=1e-9
    ):
        raise Candidate202401LocalEnvelopeError(
            f"Month-end equity diff drifted from final capital diff for {spec.subject_id}: "
            f"equity={month_end_total_equity_diff}, final_capital={final_capital_diff}"
        )

    peak_abs_index = next(
        index
        for index, row in enumerate(diff_rows)
        if str(row["timestamp"]) == str(peak_abs_row["timestamp"])
    )
    first_month_end_diff_return = envelope_base._first_row_matching_month_end_diff(
        diff_rows,
        month_end_diff=month_end_total_equity_diff,
        start_index=peak_abs_index + 1,
    )

    peak_abs_value = float(peak_abs_row["total_equity_diff"])
    envelope_end_value = float(envelope_end_row["total_equity_diff"])
    initial_capital = envelope_base.local_packet._coerce_float(
        baseline_summary.get("initial_capital"),
        field_name=f"{spec.subject_id}.baseline.initial_capital",
    )
    trade_path_summary = envelope_base._trade_path_summary(
        baseline.get("trades"),
        release_zero.get("trades"),
        spec=spec,
        field_name=f"{spec.subject_id}.trade_path_summary",
    )

    return {
        "subject_id": spec.subject_id,
        "role": spec.role,
        "month_window": {
            "start": spec.month_start,
            "end": spec.month_end,
            "inventory_total_return_diff": envelope_base._round_or_none(
                spec.inventory_total_return_diff
            ),
            "inventory_final_capital_diff": envelope_base._round_or_none(
                spec.inventory_final_capital_diff
            ),
        },
        "envelope_window": {
            "start": spec.envelope_start,
            "end": spec.envelope_end,
            "row_count": len(exact_envelope_timestamps),
            "span_hours": envelope_base._round_or_none(
                (
                    envelope_base.local_packet._parse_timestamp(spec.envelope_end)
                    - envelope_base.local_packet._parse_timestamp(spec.envelope_start)
                ).total_seconds()
                / 3600.0
            ),
            "exact_timestamps": list(exact_envelope_timestamps),
        },
        "continuation_release_timestamp_validation": {
            "baseline_matches_local_packet": True,
            "release_zero_matches_local_packet": True,
        },
        "monthly_reproduction": {
            "top_line_sign": envelope_base.local_packet._sign_label(total_return_diff),
            "rerun_total_return_diff": envelope_base._round_or_none(total_return_diff),
            "rerun_final_capital_diff": envelope_base._round_or_none(final_capital_diff),
            "matches_local_packet_total_return_diff": True,
            "matches_local_packet_final_capital_diff": True,
        },
        "equity_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
        "keypoints": {
            "pre_envelope_anchor": envelope_base._snapshot_from_diff_row(pre_anchor_row),
            "envelope_start": envelope_base._snapshot_from_diff_row(envelope_start_row),
            "envelope_end": envelope_base._snapshot_from_diff_row(envelope_end_row),
            "month_end": envelope_base._snapshot_from_diff_row(month_end_row),
            "first_return_to_month_end_diff_after_peak": (
                envelope_base._snapshot_from_diff_row(first_month_end_diff_return)
                if first_month_end_diff_return is not None
                else None
            ),
        },
        "envelope_extrema": {
            "peak_release_zero_advantage": envelope_base._snapshot_from_diff_row(peak_positive_row),
            "peak_baseline_advantage": envelope_base._snapshot_from_diff_row(peak_negative_row),
            "peak_absolute_gap": envelope_base._snapshot_from_diff_row(peak_abs_row),
            "full_month_peak_absolute_gap": envelope_base._snapshot_from_diff_row(
                full_month_peak_abs_row
            ),
            "envelope_captures_full_month_peak_absolute_gap": (
                str(full_month_peak_abs_row["timestamp"]) == str(peak_abs_row["timestamp"])
            ),
        },
        "path_summary": {
            "initial_capital": envelope_base._round_or_none(initial_capital),
            "pre_envelope_anchor_total_equity_diff": envelope_base._round_or_none(
                float(pre_anchor_row["total_equity_diff"])
            ),
            "envelope_end_total_equity_diff": envelope_base._round_or_none(envelope_end_value),
            "month_end_total_equity_diff": envelope_base._round_or_none(
                month_end_total_equity_diff
            ),
            "peak_absolute_total_equity_diff": envelope_base._round_or_none(peak_abs_value),
            "peak_absolute_pct_of_initial_capital": envelope_base._round_or_none(
                0.0
                if envelope_base.math.isclose(
                    initial_capital, 0.0, abs_tol=envelope_base.DIFF_TOLERANCE
                )
                else peak_abs_value / initial_capital
            ),
            "peak_absolute_direction": envelope_base._diff_direction(peak_abs_value),
            "pre_anchor_to_peak_change": envelope_base._round_or_none(
                peak_abs_value - float(pre_anchor_row["total_equity_diff"])
            ),
            "pre_anchor_to_envelope_end_change": envelope_base._round_or_none(
                envelope_end_value - float(pre_anchor_row["total_equity_diff"])
            ),
            "peak_to_month_end_cancellation_amount": envelope_base._round_or_none(
                month_end_total_equity_diff - peak_abs_value
            ),
            "peak_to_month_end_cancellation_share": envelope_base._round_or_none(
                envelope_base._cancellation_share(peak_abs_value, month_end_total_equity_diff)
            ),
            "envelope_end_to_month_end_cancellation_amount": envelope_base._round_or_none(
                month_end_total_equity_diff - envelope_end_value
            ),
            "envelope_end_to_month_end_cancellation_share": envelope_base._round_or_none(
                envelope_base._cancellation_share(envelope_end_value, month_end_total_equity_diff)
            ),
        },
        "trade_path_summary": trade_path_summary,
        "envelope_diff_series": [
            envelope_base._snapshot_from_diff_row(row) for row in envelope_rows
        ],
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = envelope_base.local_packet._coerce_dict(
        subject_payloads.get(NEGATIVE_CANDIDATE.subject_id),
        field_name=f"candidate_2024_01_local_envelope.subject_payloads.{NEGATIVE_CANDIDATE.subject_id}",
    )
    control = envelope_base.local_packet._coerce_dict(
        subject_payloads.get(POSITIVE_CONTROL.subject_id),
        field_name=f"candidate_2024_01_local_envelope.subject_payloads.{POSITIVE_CONTROL.subject_id}",
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
            "`2024-01` opens a larger local equity gap than `2023-05` on the same release_zero-minus-baseline "
            "economic path while both months still close back to flat by month end. That would support the local "
            "outcome-cancellation hypothesis more strongly for the 2024 widening candidate than for the control."
        )
    elif control_peak > candidate_peak + envelope_base.DIFF_TOLERANCE:
        status = envelope_base.PACKET_STATUS_CONTROL_STRONGER
        inference = (
            "`2023-05` opens a larger local equity gap than `2024-01`, so the 2024 widening candidate does not "
            "dominate the control on the bounded local economic path."
        )
    else:
        status = envelope_base.PACKET_STATUS_TIED
        inference = (
            "`2024-01` and `2023-05` remain economically invariant on the bounded local envelope path: the "
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
            "the `2024-01` envelope to determine whether the retained policy/size differences are economically inert "
            "because they preserve the same executed trade path."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-candidate-2024-01-2026-05-26"
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


def run_candidate_2024_01_local_envelope_cancellation() -> dict[str, Any]:
    envelope_specs = _load_local_packet_specs()
    exact_envelope_timestamps = _load_exact_envelope_timestamps()
    base_cfg, carrier_cfg, authority = envelope_base.local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: _subject_payload(
            envelope_specs[definition.subject_id],
            exact_envelope_timestamps=exact_envelope_timestamps[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in SUBJECT_DEFINITIONS
    }

    return {
        "audit_version": (
            "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-candidate-2024-01-2026-05-26"
        ),
        "base_sha": envelope_base.local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed `2024-01` local packet, rerun on the same carrier "
                "and measured only on the release_zero-minus-baseline equity path"
            ),
            "question": (
                "Does the `2024-01` candidate open a larger local equity gap than the `2023-05` control inside the "
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
        result = run_candidate_2024_01_local_envelope_cancellation()
    except envelope_base.LocalEnvelopeError as exc:
        result = _build_fail_closed_result(str(exc))
    except Candidate202401LocalEnvelopeError as exc:
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
