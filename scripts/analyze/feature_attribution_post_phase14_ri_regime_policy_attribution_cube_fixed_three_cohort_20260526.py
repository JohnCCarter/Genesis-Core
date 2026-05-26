from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from probe path")


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
DECISION_ARTIFACT_RELATIVE = Path(
    "results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json"
)
JOIN_ARTIFACT_RELATIVE = Path(
    "results/evaluation/feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "feature_attribution_post_phase14_ri_regime_policy_attribution_cube_fixed_three_cohort_2026-05-26.json"
STATUS_OK = "feature_attribution_ri_regime_policy_attribution_cube_fixed_three_cohort_generated"
STATUS_FAIL_CLOSED = (
    "feature_attribution_ri_regime_policy_attribution_cube_fixed_three_cohort_fail_closed"
)
EXPECTED_DECISION_STATUS = "feature_attribution_ri_decision_surface_fixed_three_cohort_generated"
EXPECTED_JOIN_STATUS = "feature_attribution_ri_trade_exit_join_fixed_three_cohort_generated"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")


class AttributionCubeError(RuntimeError):
    """Raised when the bounded attribution cube cannot be produced safely."""


@dataclass
class BucketAccumulator:
    dimensions: dict[str, str]
    decision_count: int = 0
    actionable_decision_count: int = 0
    no_action_decision_count: int = 0
    observed_open_decision_count: int = 0
    unresolved_non_opening_decision_count: int = 0
    position_count: int = 0
    trade_event_count: int = 0
    partial_trade_event_count: int = 0
    full_trade_event_count: int = 0
    win_position_count: int = 0
    loss_position_count: int = 0
    breakeven_position_count: int = 0
    gross_realized_pnl: float = 0.0
    gross_profit: float = 0.0
    gross_loss_abs: float = 0.0
    total_exit_commission: float = 0.0
    action_counts: Counter[str] = field(default_factory=Counter)
    switch_reason_counts: Counter[str] = field(default_factory=Counter)
    regime_counts: Counter[str] = field(default_factory=Counter)
    selected_policy_counts: Counter[str] = field(default_factory=Counter)
    cohort_counts: Counter[str] = field(default_factory=Counter)
    trade_event_exit_family_counts: Counter[str] = field(default_factory=Counter)
    trade_event_exit_reason_counts: Counter[str] = field(default_factory=Counter)
    final_exit_family_counts: Counter[str] = field(default_factory=Counter)
    final_exit_reason_counts: Counter[str] = field(default_factory=Counter)
    positions_with_take_profit_leg_count: int = 0
    positions_with_stop_loss_leg_count: int = 0
    positions_with_trailing_stop_leg_count: int = 0
    positions_with_regime_exit_leg_count: int = 0
    positions_with_confidence_exit_leg_count: int = 0
    positions_with_manual_or_other_leg_count: int = 0
    positions_with_unknown_exit_leg_count: int = 0
    bars_since_regime_change_values: list[int] = field(default_factory=list)
    clarity_score_values: list[float] = field(default_factory=list)
    confidence_gate_values: list[float] = field(default_factory=list)
    action_edge_values: list[float] = field(default_factory=list)
    size_after_policy_router_values: list[float] = field(default_factory=list)

    def add_decision(self, *, decision_row: dict[str, Any], join_row: dict[str, Any]) -> None:
        action = str(decision_row.get("action") or "")
        router_debug = _coerce_dict(
            decision_row.get("router_debug") or {},
            field_name="decision_row.router_debug",
        )
        regime = _extract_regime(decision_row)
        selected_policy = _extract_selected_policy(decision_row)
        switch_reason = _extract_switch_reason(decision_row)
        cohort_label = _coerce_str(
            decision_row.get("cohort_label"),
            field_name="decision_row.cohort_label",
        )

        self.decision_count += 1
        self.action_counts[action] += 1
        self.regime_counts[regime] += 1
        self.selected_policy_counts[selected_policy] += 1
        self.cohort_counts[cohort_label] += 1
        self.switch_reason_counts[switch_reason] += 1

        if action == "NONE":
            self.no_action_decision_count += 1
        else:
            self.actionable_decision_count += 1

        join_status = str(join_row.get("join_status") or "")
        if join_status == "observed_open_event_matched":
            self.observed_open_decision_count += 1
        elif join_status == "non_opening_signal_without_execution_row":
            self.unresolved_non_opening_decision_count += 1
        elif join_status == "no_action_decision":
            pass
        else:
            raise AttributionCubeError(f"Unexpected join_status: {join_status!r}")

        bars_since_regime_change = router_debug.get("bars_since_regime_change")
        if bars_since_regime_change is not None:
            self.bars_since_regime_change_values.append(int(bars_since_regime_change))

        clarity_score = router_debug.get("clarity_score")
        if clarity_score is not None:
            self.clarity_score_values.append(float(clarity_score))

        confidence_gate = router_debug.get("confidence_gate")
        if confidence_gate is not None:
            self.confidence_gate_values.append(float(confidence_gate))

        action_edge = router_debug.get("action_edge")
        if action_edge is not None:
            self.action_edge_values.append(float(action_edge))

        size_after_policy_router = router_debug.get("size_after_policy_router")
        if size_after_policy_router is not None:
            self.size_after_policy_router_values.append(float(size_after_policy_router))

    def add_position(self, *, position_summary: dict[str, Any]) -> None:
        gross_trade_pnl = float(position_summary.get("gross_trade_pnl") or 0.0)
        trade_event_count = int(position_summary.get("trade_event_count") or 0)
        partial_trade_event_count = int(position_summary.get("partial_trade_event_count") or 0)
        full_trade_event_count = int(position_summary.get("full_trade_event_count") or 0)

        self.position_count += 1
        self.trade_event_count += trade_event_count
        self.partial_trade_event_count += partial_trade_event_count
        self.full_trade_event_count += full_trade_event_count
        self.gross_realized_pnl += gross_trade_pnl
        self.total_exit_commission += float(position_summary.get("total_exit_commission") or 0.0)

        if gross_trade_pnl > 0:
            self.win_position_count += 1
            self.gross_profit += gross_trade_pnl
        elif gross_trade_pnl < 0:
            self.loss_position_count += 1
            self.gross_loss_abs += abs(gross_trade_pnl)
        else:
            self.breakeven_position_count += 1

        exit_family_counts = Counter(
            {
                str(key): int(value)
                for key, value in _coerce_dict(
                    position_summary.get("exit_family_counts") or {},
                    field_name="position_summary.exit_family_counts",
                ).items()
            }
        )
        exit_reason_counts = Counter(
            {
                str(key): int(value)
                for key, value in _coerce_dict(
                    position_summary.get("exit_reason_counts") or {},
                    field_name="position_summary.exit_reason_counts",
                ).items()
            }
        )
        self.trade_event_exit_family_counts.update(exit_family_counts)
        self.trade_event_exit_reason_counts.update(exit_reason_counts)

        final_exit_family = str(position_summary.get("final_exit_family") or "unknown_unclassified")
        final_exit_reason = str(position_summary.get("final_exit_reason") or "")
        self.final_exit_family_counts[final_exit_family] += 1
        self.final_exit_reason_counts[final_exit_reason] += 1

        families_present = {family for family, count in exit_family_counts.items() if count > 0}
        if "take_profit" in families_present:
            self.positions_with_take_profit_leg_count += 1
        if "stop_loss" in families_present:
            self.positions_with_stop_loss_leg_count += 1
        if "trailing_stop" in families_present:
            self.positions_with_trailing_stop_leg_count += 1
        if "regime_exit" in families_present:
            self.positions_with_regime_exit_leg_count += 1
        if "confidence_exit" in families_present:
            self.positions_with_confidence_exit_leg_count += 1
        if "manual_or_other" in families_present:
            self.positions_with_manual_or_other_leg_count += 1
        if "unknown_unclassified" in families_present:
            self.positions_with_unknown_exit_leg_count += 1

    def finalize(self, *, total_gross_loss_abs: float) -> dict[str, Any]:
        profit_factor, profit_factor_mode = _profit_factor(
            gross_profit=self.gross_profit,
            gross_loss_abs=self.gross_loss_abs,
            position_count=self.position_count,
        )
        return {
            "dimensions": dict(sorted(self.dimensions.items())),
            "decision_metrics": {
                "decision_count": self.decision_count,
                "actionable_decision_count": self.actionable_decision_count,
                "no_action_decision_count": self.no_action_decision_count,
                "observed_open_decision_count": self.observed_open_decision_count,
                "unresolved_non_opening_decision_count": self.unresolved_non_opening_decision_count,
                "action_counts": _sorted_counter(self.action_counts),
                "switch_reason_counts": _sorted_counter(self.switch_reason_counts),
                "regime_counts": _sorted_counter(self.regime_counts),
                "selected_policy_counts": _sorted_counter(self.selected_policy_counts),
                "cohort_counts": _sorted_counter(self.cohort_counts),
            },
            "funnel_metrics": {
                "decision_to_observed_open_rate": _safe_rate(
                    self.observed_open_decision_count,
                    self.decision_count,
                ),
                "actionable_to_observed_open_rate": _safe_rate(
                    self.observed_open_decision_count,
                    self.actionable_decision_count,
                ),
                "actionable_to_non_opening_rate": _safe_rate(
                    self.unresolved_non_opening_decision_count,
                    self.actionable_decision_count,
                ),
                "decision_to_realized_position_rate": _safe_rate(
                    self.position_count,
                    self.decision_count,
                ),
                "actionable_to_realized_position_rate": _safe_rate(
                    self.position_count,
                    self.actionable_decision_count,
                ),
                "realized_position_to_trade_event_rate": _safe_rate(
                    self.trade_event_count,
                    self.position_count,
                ),
            },
            "performance_metrics": {
                "position_count": self.position_count,
                "trade_event_count": self.trade_event_count,
                "partial_trade_event_count": self.partial_trade_event_count,
                "full_trade_event_count": self.full_trade_event_count,
                "win_position_count": self.win_position_count,
                "loss_position_count": self.loss_position_count,
                "breakeven_position_count": self.breakeven_position_count,
                "gross_realized_pnl": _round_float(self.gross_realized_pnl),
                "gross_profit": _round_float(self.gross_profit),
                "gross_loss_abs": _round_float(self.gross_loss_abs),
                "expectancy_per_position": _safe_rate(
                    self.gross_realized_pnl,
                    self.position_count,
                ),
                "expectancy_per_actionable_decision": _safe_rate(
                    self.gross_realized_pnl,
                    self.actionable_decision_count,
                ),
                "profit_factor": profit_factor,
                "profit_factor_mode": profit_factor_mode,
                "position_win_rate": _safe_rate(self.win_position_count, self.position_count),
                "position_loss_rate": _safe_rate(self.loss_position_count, self.position_count),
                "realized_drawdown_contribution_share": _safe_rate(
                    self.gross_loss_abs,
                    total_gross_loss_abs,
                ),
                "total_exit_commission": _round_float(self.total_exit_commission),
            },
            "exit_metrics": {
                "trade_event_exit_family_counts": _sorted_counter(
                    self.trade_event_exit_family_counts
                ),
                "trade_event_exit_reason_counts": _sorted_counter(
                    self.trade_event_exit_reason_counts
                ),
                "final_exit_family_counts": _sorted_counter(self.final_exit_family_counts),
                "final_exit_reason_counts": _sorted_counter(self.final_exit_reason_counts),
                "take_profit_trade_event_share": _safe_rate(
                    self.trade_event_exit_family_counts.get("take_profit", 0),
                    self.trade_event_count,
                ),
                "stop_loss_trade_event_share": _safe_rate(
                    self.trade_event_exit_family_counts.get("stop_loss", 0),
                    self.trade_event_count,
                ),
                "trailing_stop_trade_event_share": _safe_rate(
                    self.trade_event_exit_family_counts.get("trailing_stop", 0),
                    self.trade_event_count,
                ),
                "take_profit_final_position_share": _safe_rate(
                    self.final_exit_family_counts.get("take_profit", 0),
                    self.position_count,
                ),
                "stop_loss_final_position_share": _safe_rate(
                    self.final_exit_family_counts.get("stop_loss", 0),
                    self.position_count,
                ),
                "trailing_stop_final_position_share": _safe_rate(
                    self.final_exit_family_counts.get("trailing_stop", 0),
                    self.position_count,
                ),
                "positions_with_take_profit_leg_count": self.positions_with_take_profit_leg_count,
                "positions_with_stop_loss_leg_count": self.positions_with_stop_loss_leg_count,
                "positions_with_trailing_stop_leg_count": self.positions_with_trailing_stop_leg_count,
                "positions_with_regime_exit_leg_count": self.positions_with_regime_exit_leg_count,
                "positions_with_confidence_exit_leg_count": self.positions_with_confidence_exit_leg_count,
                "positions_with_manual_or_other_leg_count": self.positions_with_manual_or_other_leg_count,
                "positions_with_unknown_exit_leg_count": self.positions_with_unknown_exit_leg_count,
            },
            "context_metrics": {
                "bars_since_regime_change": _summarize_numeric(
                    self.bars_since_regime_change_values
                ),
                "clarity_score": _summarize_numeric(self.clarity_score_values),
                "confidence_gate": _summarize_numeric(self.confidence_gate_values),
                "action_edge": _summarize_numeric(self.action_edge_values),
                "size_after_policy_router": _summarize_numeric(
                    self.size_after_policy_router_values
                ),
            },
        }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the first bounded regime-/policy-separated attribution cube over the "
            "fixed three-cohort RI decision and trade-join surfaces."
        )
    )
    parser.add_argument(
        "--base-sha",
        required=True,
        help="Exact repository HEAD SHA for provenance in the emitted artifact.",
    )
    parser.add_argument(
        "--decision-artifact-relative",
        default=str(DECISION_ARTIFACT_RELATIVE),
        help="Repo-relative decision-surface artifact used as canonical Slice 2 input.",
    )
    parser.add_argument(
        "--join-artifact-relative",
        default=str(JOIN_ARTIFACT_RELATIVE),
        help="Repo-relative trade/exit join artifact used as canonical Slice 3 input.",
    )
    parser.add_argument(
        "--output-root-relative",
        default=str(OUTPUT_ROOT_RELATIVE),
        help="Repo-relative output directory for the emitted JSON artifact.",
    )
    parser.add_argument(
        "--summary-filename",
        default=OUTPUT_FILENAME,
        help="Filename to use for the emitted JSON artifact.",
    )
    return parser.parse_args()


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


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AttributionCubeError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise AttributionCubeError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise AttributionCubeError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


def _load_json_object(path: Path, *, field_name: str) -> dict[str, Any]:
    if not path.is_file():
        raise AttributionCubeError(f"Missing required file for {field_name}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AttributionCubeError(f"{field_name} is not a JSON object")
    return payload


def _extract_regime(decision_row: dict[str, Any]) -> str:
    router_debug = _coerce_dict(decision_row.get("router_debug") or {}, field_name="router_debug")
    router_state = _coerce_dict(decision_row.get("router_state") or {}, field_name="router_state")
    return str(router_debug.get("regime") or router_state.get("regime") or "unknown_regime")


def _extract_selected_policy(decision_row: dict[str, Any]) -> str:
    router_debug = _coerce_dict(decision_row.get("router_debug") or {}, field_name="router_debug")
    router_state = _coerce_dict(decision_row.get("router_state") or {}, field_name="router_state")
    return str(
        router_debug.get("selected_policy")
        or router_state.get("selected_policy")
        or "unknown_policy"
    )


def _extract_switch_reason(decision_row: dict[str, Any]) -> str:
    router_debug = _coerce_dict(decision_row.get("router_debug") or {}, field_name="router_debug")
    return str(router_debug.get("switch_reason") or "unknown_switch_reason")


def _safe_rate(numerator: float | int, denominator: float | int) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 12)


def _round_float(value: float) -> float:
    return round(float(value), 12)


def _sorted_counter(counter: Counter[str]) -> dict[str, int]:
    return dict(
        sorted(((str(key), int(value)) for key, value in counter.items()), key=lambda item: item[0])
    )


def _summarize_numeric(values: list[float | int]) -> dict[str, float] | None:
    if not values:
        return None
    numeric = [float(value) for value in values]
    return {
        "count": len(numeric),
        "min": round(min(numeric), 12),
        "max": round(max(numeric), 12),
        "mean": round(sum(numeric) / len(numeric), 12),
    }


def _profit_factor(
    *, gross_profit: float, gross_loss_abs: float, position_count: int
) -> tuple[float | None, str]:
    if position_count == 0:
        return None, "no_realized_positions"
    if gross_loss_abs == 0.0:
        if gross_profit > 0.0:
            return None, "no_losses"
        return None, "no_losses_no_gains"
    return round(gross_profit / gross_loss_abs, 12), "finite"


def _bucket_key(dimensions: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in dimensions.items()))


def _get_bucket(
    buckets: dict[tuple[tuple[str, str], ...], BucketAccumulator],
    dimensions: dict[str, str],
) -> BucketAccumulator:
    key = _bucket_key(dimensions)
    if key not in buckets:
        buckets[key] = BucketAccumulator(dimensions=dict(key))
    return buckets[key]


def _ensure_status(payload: dict[str, Any], *, expected_status: str, field_name: str) -> None:
    status = payload.get("status")
    if status != expected_status:
        raise AttributionCubeError(
            f"Unexpected status for {field_name}: expected {expected_status!r}, got {status!r}"
        )


def _build_join_maps(join_payload: dict[str, Any]) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, str],
]:
    cohorts_payload = _coerce_dict(join_payload.get("cohorts"), field_name="join_payload.cohorts")
    join_rows_by_decision_id: dict[str, dict[str, Any]] = {}
    positions_by_decision_id: dict[str, list[dict[str, Any]]] = {}
    cohort_labels_by_decision_id: dict[str, str] = {}

    for cohort_label, cohort_payload_raw in cohorts_payload.items():
        cohort_payload = _coerce_dict(
            cohort_payload_raw, field_name=f"join_payload.cohorts.{cohort_label}"
        )
        for join_row_raw in _coerce_list(
            cohort_payload.get("decision_join_rows"),
            field_name=f"join_payload.cohorts.{cohort_label}.decision_join_rows",
        ):
            join_row = _coerce_dict(join_row_raw, field_name="decision_join_row")
            decision_identity_key = _coerce_str(
                join_row.get("decision_identity_key"),
                field_name="decision_join_row.decision_identity_key",
            )
            join_rows_by_decision_id[decision_identity_key] = join_row
            cohort_labels_by_decision_id[decision_identity_key] = cohort_label

        for position_summary_raw in _coerce_list(
            cohort_payload.get("position_summaries"),
            field_name=f"join_payload.cohorts.{cohort_label}.position_summaries",
        ):
            position_summary = _coerce_dict(position_summary_raw, field_name="position_summary")
            matched_decision_keys = [
                _coerce_str(key, field_name="position_summary.matched_decision_identity_key")
                for key in _coerce_list(
                    position_summary.get("matched_decision_identity_keys") or [],
                    field_name="position_summary.matched_decision_identity_keys",
                )
            ]
            if len(matched_decision_keys) != 1:
                raise AttributionCubeError(
                    "Each bounded position summary must match exactly one decision_identity_key"
                )
            positions_by_decision_id.setdefault(matched_decision_keys[0], []).append(
                position_summary
            )
    return join_rows_by_decision_id, positions_by_decision_id, cohort_labels_by_decision_id


def _sorted_bucket_list(
    buckets: dict[tuple[tuple[str, str], ...], BucketAccumulator],
    *,
    total_gross_loss_abs: float,
) -> list[dict[str, Any]]:
    return [
        bucket.finalize(total_gross_loss_abs=total_gross_loss_abs)
        for _, bucket in sorted(buckets.items(), key=lambda item: item[0])
    ]


def _build_fail_closed_result(
    *,
    base_sha: str,
    reason: str,
    decision_artifact_relative: str,
    join_artifact_relative: str,
) -> dict[str, Any]:
    return {
        "audit_version": "feature-attribution-post-phase14-ri-regime-policy-attribution-cube-fixed-three-cohort-2026-05-26",
        "base_sha": base_sha,
        "actual_head_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "decision_artifact": decision_artifact_relative,
            "join_artifact": join_artifact_relative,
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_attribution_cube(
    *,
    base_sha: str,
    decision_artifact_relative: Path,
    join_artifact_relative: Path,
) -> dict[str, Any]:
    try:
        decision_payload = _load_json_object(
            ROOT_DIR / decision_artifact_relative,
            field_name="decision_artifact",
        )
        join_payload = _load_json_object(
            ROOT_DIR / join_artifact_relative,
            field_name="join_artifact",
        )
        _ensure_status(
            decision_payload,
            expected_status=EXPECTED_DECISION_STATUS,
            field_name="decision_artifact",
        )
        _ensure_status(
            join_payload,
            expected_status=EXPECTED_JOIN_STATUS,
            field_name="join_artifact",
        )

        decision_rows = [
            _coerce_dict(row, field_name="decision_row")
            for row in _coerce_list(
                decision_payload.get("decision_rows"), field_name="decision_rows"
            )
        ]
        join_rows_by_decision_id, positions_by_decision_id, cohort_labels_by_decision_id = (
            _build_join_maps(join_payload)
        )

        global_bucket = BucketAccumulator(dimensions={"scope": "global"})
        by_cohort: dict[tuple[tuple[str, str], ...], BucketAccumulator] = {}
        by_regime: dict[tuple[tuple[str, str], ...], BucketAccumulator] = {}
        by_policy: dict[tuple[tuple[str, str], ...], BucketAccumulator] = {}
        by_regime_and_policy: dict[tuple[tuple[str, str], ...], BucketAccumulator] = {}
        by_cohort_regime_and_policy: dict[tuple[tuple[str, str], ...], BucketAccumulator] = {}

        unique_regimes: set[str] = set()
        unique_selected_policies: set[str] = set()
        unique_switch_reasons: set[str] = set()

        for decision_row in decision_rows:
            decision_identity_key = _coerce_str(
                decision_row.get("decision_identity_key"),
                field_name="decision_row.decision_identity_key",
            )
            if decision_identity_key not in join_rows_by_decision_id:
                raise AttributionCubeError(
                    f"Missing join row for decision_identity_key {decision_identity_key!r}"
                )
            join_row = join_rows_by_decision_id[decision_identity_key]
            cohort_label = _coerce_str(
                decision_row.get("cohort_label"),
                field_name="decision_row.cohort_label",
            )
            if cohort_labels_by_decision_id.get(decision_identity_key) != cohort_label:
                raise AttributionCubeError(
                    f"Cohort label drift between Slice 2 and Slice 3 for {decision_identity_key!r}"
                )
            regime = _extract_regime(decision_row)
            selected_policy = _extract_selected_policy(decision_row)
            switch_reason = _extract_switch_reason(decision_row)
            unique_regimes.add(regime)
            unique_selected_policies.add(selected_policy)
            unique_switch_reasons.add(switch_reason)

            for bucket in (
                global_bucket,
                _get_bucket(by_cohort, {"cohort_label": cohort_label}),
                _get_bucket(by_regime, {"regime": regime}),
                _get_bucket(by_policy, {"selected_policy": selected_policy}),
                _get_bucket(
                    by_regime_and_policy,
                    {"regime": regime, "selected_policy": selected_policy},
                ),
                _get_bucket(
                    by_cohort_regime_and_policy,
                    {
                        "cohort_label": cohort_label,
                        "regime": regime,
                        "selected_policy": selected_policy,
                    },
                ),
            ):
                bucket.add_decision(decision_row=decision_row, join_row=join_row)

            matched_positions = positions_by_decision_id.get(decision_identity_key, [])
            for position_summary in matched_positions:
                for bucket in (
                    global_bucket,
                    _get_bucket(by_cohort, {"cohort_label": cohort_label}),
                    _get_bucket(by_regime, {"regime": regime}),
                    _get_bucket(by_policy, {"selected_policy": selected_policy}),
                    _get_bucket(
                        by_regime_and_policy,
                        {"regime": regime, "selected_policy": selected_policy},
                    ),
                    _get_bucket(
                        by_cohort_regime_and_policy,
                        {
                            "cohort_label": cohort_label,
                            "regime": regime,
                            "selected_policy": selected_policy,
                        },
                    ),
                ):
                    bucket.add_position(position_summary=position_summary)

        total_gross_loss_abs = global_bucket.gross_loss_abs
        global_summary = global_bucket.finalize(total_gross_loss_abs=total_gross_loss_abs)

        cohort_rollups = _sorted_bucket_list(by_cohort, total_gross_loss_abs=total_gross_loss_abs)
        regime_rollups = _sorted_bucket_list(by_regime, total_gross_loss_abs=total_gross_loss_abs)
        policy_rollups = _sorted_bucket_list(by_policy, total_gross_loss_abs=total_gross_loss_abs)
        regime_policy_rollups = _sorted_bucket_list(
            by_regime_and_policy,
            total_gross_loss_abs=total_gross_loss_abs,
        )
        cohort_regime_policy_rollups = _sorted_bucket_list(
            by_cohort_regime_and_policy,
            total_gross_loss_abs=total_gross_loss_abs,
        )

        realized_positions_by_policy = {
            rollup["dimensions"]["selected_policy"]: rollup["performance_metrics"]["position_count"]
            for rollup in policy_rollups
        }

        return {
            "audit_version": "feature-attribution-post-phase14-ri-regime-policy-attribution-cube-fixed-three-cohort-2026-05-26",
            "base_sha": base_sha,
            "actual_head_sha": _git_head_sha(),
            "status": STATUS_OK,
            "observational_only": True,
            "non_authoritative": True,
            "classification_boundary": {
                "source_surface": "Slice 2 decision rows plus Slice 3 bounded trade/exit join artifact",
                "schema_target": "regime-/policy-separated attribution cube over the fixed three-cohort RI surface",
                "ledger_impact_semantics": "realized trade-row impact proxy only; no canonical ledger_impact_row introduced",
                "still_not_a_canonical_runtime_execution_row": True,
            },
            "inputs": {
                "decision_artifact": str(decision_artifact_relative),
                "join_artifact": str(join_artifact_relative),
                "symbol": decision_payload.get("inputs", {}).get("symbol"),
                "timeframe": decision_payload.get("inputs", {}).get("timeframe"),
                "data_source_policy": decision_payload.get("inputs", {}).get("data_source_policy"),
                "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
                "decision_artifact_status": decision_payload.get("status"),
                "join_artifact_status": join_payload.get("status"),
            },
            "metric_contract": {
                "expectancy_per_position": "gross_realized_pnl / position_count",
                "profit_factor": "gross_profit / gross_loss_abs when gross_loss_abs > 0, else null with explicit mode",
                "realized_drawdown_contribution_share": (
                    "bucket gross_loss_abs / global gross_loss_abs; trade-realized loss proxy only, not a full equity-path drawdown row"
                ),
                "take_profit_share": "take_profit trade-event share over realized trade events",
                "stop_loss_share": "stop_loss trade-event share over realized trade events",
                "trailing_stop_share": "trailing_stop trade-event share over realized trade events",
                "decision_to_ledger_impact_proxy": (
                    "decision -> observed open -> realized position -> realized trade event funnel; ledger impact remains a trade-row proxy in this slice"
                ),
            },
            "surface_characteristics": {
                "unique_regimes_observed": sorted(unique_regimes),
                "unique_selected_policies_observed": sorted(unique_selected_policies),
                "unique_switch_reasons_observed": sorted(unique_switch_reasons),
                "regime_dimension_is_flat_on_fixed_surface": len(unique_regimes) == 1,
                "policy_dimension_is_flat_on_fixed_surface": len(unique_selected_policies) == 1,
                "realized_positions_by_selected_policy": dict(
                    sorted(realized_positions_by_policy.items())
                ),
            },
            "global_summary": global_summary,
            "rollups": {
                "by_cohort": cohort_rollups,
                "by_regime": regime_rollups,
                "by_policy": policy_rollups,
                "by_regime_and_policy": regime_policy_rollups,
                "by_cohort_regime_and_policy": cohort_regime_policy_rollups,
            },
            "preserved_comparator_ready_fields": [
                "decision_identity_key",
                "row_id",
                "timestamp",
                "position_id",
                "entry_time",
                "exit_time",
                "symbol",
                "timeframe",
                "regime",
                "selected_policy",
                "exit_family",
            ],
        }
    except AttributionCubeError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            decision_artifact_relative=str(decision_artifact_relative),
            join_artifact_relative=str(join_artifact_relative),
        )


def main() -> int:
    args = _parse_args()
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_attribution_cube(
        base_sha=args.base_sha,
        decision_artifact_relative=Path(args.decision_artifact_relative),
        join_artifact_relative=Path(args.join_artifact_relative),
    )
    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "unique_regimes": result.get("surface_characteristics", {}).get(
                    "unique_regimes_observed"
                ),
                "unique_selected_policies": result.get("surface_characteristics", {}).get(
                    "unique_selected_policies_observed"
                ),
                "global_position_count": result.get("global_summary", {})
                .get("performance_metrics", {})
                .get("position_count"),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
