# ruff: noqa: E402

from __future__ import annotations

import json
import math
import os
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
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
from scripts.run.run_backtest import GenesisPipeline, _deep_merge

os.environ["GENESIS_RANDOM_SEED"] = "42"
os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
os.environ["GENESIS_PRECOMPUTE_CACHE_WRITE"] = "0"
os.environ["GENESIS_MODE_EXPLICIT"] = "1"
os.environ["GENESIS_FAST_HASH"] = "0"
os.environ["GENESIS_SCORE_VERSION"] = "v2"

LOCAL_PACKET_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_2026-05-26.json"
)
STATUS_OK = "continuation_release_hysteresis_local_envelope_cancellation_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_envelope_cancellation_fail_closed"
PACKET_STATUS_CANDIDATE_STRONGER = (
    "candidate_exposes_larger_local_equity_gap_than_control_before_month_end_cancellation"
)
PACKET_STATUS_TIED = "candidate_and_control_remain_economically_invariant_on_local_envelope_path"
PACKET_STATUS_CONTROL_STRONGER = (
    "control_exposes_larger_local_equity_gap_than_candidate_before_month_end_cancellation"
)
DIFF_TOLERANCE = 1e-9


@dataclass(frozen=True)
class EnvelopeSubjectSpec:
    subject_id: str
    role: str
    month_start: str
    month_end: str
    inventory_total_return_diff: float
    inventory_final_capital_diff: float
    envelope_start: str
    envelope_end: str
    envelope_row_count: int
    baseline_timestamps: tuple[str, ...]
    release_zero_timestamps: tuple[str, ...]


class LocalEnvelopeError(RuntimeError):
    pass


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(inner) for key, inner in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(inner) for inner in value]
    if isinstance(value, datetime):
        normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
        return normalized.astimezone(UTC).isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, Path):
        return str(value)
    return value


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _load_local_packet_specs() -> dict[str, EnvelopeSubjectSpec]:
    payload = local_packet._coerce_dict(
        json.loads((ROOT_DIR / LOCAL_PACKET_RELATIVE).read_text(encoding="utf-8")),
        field_name="local_envelope.local_packet",
    )
    subject_payloads = local_packet._coerce_dict(
        payload.get("subject_payloads"),
        field_name="local_envelope.subject_payloads",
    )

    specs: dict[str, EnvelopeSubjectSpec] = {}
    for definition in local_packet.SUBJECT_DEFINITIONS:
        subject_payload = local_packet._coerce_dict(
            subject_payloads.get(definition.subject_id),
            field_name=f"local_envelope.subject_payloads.{definition.subject_id}",
        )
        month_window = local_packet._coerce_dict(
            subject_payload.get("month_window"),
            field_name=f"local_envelope.{definition.subject_id}.month_window",
        )
        cluster_groups = local_packet._coerce_dict(
            subject_payload.get("cluster_groups"),
            field_name=f"local_envelope.{definition.subject_id}.cluster_groups",
        )
        union_groups = local_packet._coerce_list(
            cluster_groups.get("union_diff_surface"),
            field_name=f"local_envelope.{definition.subject_id}.union_diff_surface",
        )
        baseline_groups = local_packet._coerce_list(
            cluster_groups.get("baseline"),
            field_name=f"local_envelope.{definition.subject_id}.baseline_groups",
        )
        release_zero_groups = local_packet._coerce_list(
            cluster_groups.get("release_zero"),
            field_name=f"local_envelope.{definition.subject_id}.release_zero_groups",
        )
        if len(union_groups) != 1 or len(baseline_groups) != 1 or len(release_zero_groups) != 1:
            raise LocalEnvelopeError(
                f"Expected exactly one envelope group per mode for {definition.subject_id}"
            )

        envelope = local_packet._coerce_dict(
            union_groups[0],
            field_name=f"local_envelope.{definition.subject_id}.union_group",
        )
        baseline_group = local_packet._coerce_dict(
            baseline_groups[0],
            field_name=f"local_envelope.{definition.subject_id}.baseline_group",
        )
        release_zero_group = local_packet._coerce_dict(
            release_zero_groups[0],
            field_name=f"local_envelope.{definition.subject_id}.release_zero_group",
        )

        specs[definition.subject_id] = EnvelopeSubjectSpec(
            subject_id=definition.subject_id,
            role=local_packet._coerce_str(
                subject_payload.get("role"),
                field_name=f"local_envelope.{definition.subject_id}.role",
            ),
            month_start=local_packet._coerce_str(
                month_window.get("start"),
                field_name=f"local_envelope.{definition.subject_id}.month_start",
            ),
            month_end=local_packet._coerce_str(
                month_window.get("end"),
                field_name=f"local_envelope.{definition.subject_id}.month_end",
            ),
            inventory_total_return_diff=local_packet._coerce_float(
                month_window.get("inventory_total_return_diff"),
                field_name=f"local_envelope.{definition.subject_id}.inventory_total_return_diff",
            ),
            inventory_final_capital_diff=local_packet._coerce_float(
                month_window.get("inventory_final_capital_diff"),
                field_name=f"local_envelope.{definition.subject_id}.inventory_final_capital_diff",
            ),
            envelope_start=local_packet._coerce_str(
                envelope.get("start"),
                field_name=f"local_envelope.{definition.subject_id}.envelope_start",
            ),
            envelope_end=local_packet._coerce_str(
                envelope.get("end"),
                field_name=f"local_envelope.{definition.subject_id}.envelope_end",
            ),
            envelope_row_count=int(
                local_packet._coerce_float(
                    envelope.get("row_count"),
                    field_name=f"local_envelope.{definition.subject_id}.envelope_row_count",
                )
            ),
            baseline_timestamps=tuple(
                local_packet._coerce_str(
                    timestamp,
                    field_name=f"local_envelope.{definition.subject_id}.baseline_timestamp",
                )
                for timestamp in local_packet._coerce_list(
                    baseline_group.get("timestamps"),
                    field_name=f"local_envelope.{definition.subject_id}.baseline_timestamps",
                )
            ),
            release_zero_timestamps=tuple(
                local_packet._coerce_str(
                    timestamp,
                    field_name=f"local_envelope.{definition.subject_id}.release_zero_timestamp",
                )
                for timestamp in local_packet._coerce_list(
                    release_zero_group.get("timestamps"),
                    field_name=f"local_envelope.{definition.subject_id}.release_zero_timestamps",
                )
            ),
        )
    return specs


def _run_case_with_economics(
    mode: str,
    *,
    start_date: str,
    end_date: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise LocalEnvelopeError(
            f"Carrier does not expose enabled research_policy_router for {mode}"
        )

    if mode == "baseline":
        router_cfg.pop("continuation_release_hysteresis", None)
    elif mode == "release_zero":
        router_cfg["continuation_release_hysteresis"] = 0
    else:
        raise LocalEnvelopeError(f"Unsupported mode {mode!r}")

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=local_packet.SYMBOL,
        timeframe=local_packet.TIMEFRAME,
        start_date=start_date,
        end_date=end_date,
        warmup_bars=local_packet.WARMUP,
        data_source_policy=local_packet.DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise LocalEnvelopeError(f"BacktestEngine.load_data() failed for {mode}")

    continuation_release_timestamps: list[str] = []

    def capture(result: dict[str, Any], meta: dict[str, Any] | None, candles: dict[str, Any]):
        timestamps = candles.get("timestamp") or []
        if not timestamps:
            return result, meta
        timestamp = timestamps[-1]
        timestamp_text = str(
            timestamp.isoformat() if hasattr(timestamp, "isoformat") else timestamp
        )
        decision = (meta or {}).get("decision") or {}
        state_out = decision.get("state_out") or {}
        debug = state_out.get(local_packet.RESEARCH_POLICY_ROUTER_DEBUG_KEY) or {}
        if debug.get("switch_control_mode") == "continuation_release":
            continuation_release_timestamps.append(timestamp_text)
        return result, meta

    engine.evaluation_hook = capture
    results = engine.run(
        policy={"symbol": local_packet.SYMBOL, "timeframe": local_packet.TIMEFRAME},
        configs=validated_cfg,
    )
    if "error" in results:
        raise LocalEnvelopeError(f"Backtest run failed for {mode}: {results['error']}")

    backtest_info = results.get("backtest_info") or {}
    execution_mode = backtest_info.get("execution_mode") or {}
    if not execution_mode.get("fast_window"):
        raise LocalEnvelopeError(f"Execution mode drift for {mode}: fast_window false")
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise LocalEnvelopeError(f"Execution mode drift for {mode}: env_precompute_features != 1")
    if not execution_mode.get("precompute_enabled"):
        raise LocalEnvelopeError(f"Execution mode drift for {mode}: precompute_enabled false")
    if str(execution_mode.get("mode_explicit")) != "1":
        raise LocalEnvelopeError(f"Execution mode drift for {mode}: mode_explicit != 1")

    return {
        "summary": _json_safe(results.get("summary")),
        "position_summary": _json_safe(results.get("position_summary")),
        "metrics": _json_safe(results.get("metrics")),
        "execution_mode": _json_safe(execution_mode),
        "bars_total": _json_safe(backtest_info.get("bars_total")),
        "bars_processed": _json_safe(backtest_info.get("bars_processed")),
        "effective_config_fingerprint": _json_safe(
            backtest_info.get("effective_config_fingerprint")
        ),
        "trades": _json_safe(results.get("trades")),
        "equity_curve": _json_safe(results.get("equity_curve")),
        "continuation_release_timestamps": tuple(sorted(continuation_release_timestamps)),
    }


def _coerce_equity_curve(raw_rows: Any, *, field_name: str) -> list[dict[str, Any]]:
    rows = local_packet._coerce_list(raw_rows, field_name=field_name)
    normalized: list[dict[str, Any]] = []
    for index, raw_row in enumerate(rows):
        row = local_packet._coerce_dict(raw_row, field_name=f"{field_name}[{index}]")
        normalized.append(
            {
                "timestamp": local_packet._coerce_str(
                    row.get("timestamp"), field_name=f"{field_name}[{index}].timestamp"
                ),
                "capital": local_packet._coerce_float(
                    row.get("capital"), field_name=f"{field_name}[{index}].capital"
                ),
                "unrealized_pnl": local_packet._coerce_float(
                    row.get("unrealized_pnl"),
                    field_name=f"{field_name}[{index}].unrealized_pnl",
                ),
                "total_equity": local_packet._coerce_float(
                    row.get("total_equity"),
                    field_name=f"{field_name}[{index}].total_equity",
                ),
            }
        )
    return normalized


def _coerce_trade_rows(raw_rows: Any, *, field_name: str) -> list[dict[str, Any]]:
    rows = local_packet._coerce_list(raw_rows, field_name=field_name)
    normalized: list[dict[str, Any]] = []
    for index, raw_row in enumerate(rows):
        row = local_packet._coerce_dict(raw_row, field_name=f"{field_name}[{index}]")
        normalized.append(
            {
                "entry_time": local_packet._coerce_str(
                    row.get("entry_time"), field_name=f"{field_name}[{index}].entry_time"
                ),
                "exit_time": local_packet._coerce_str(
                    row.get("exit_time"), field_name=f"{field_name}[{index}].exit_time"
                ),
                "side": local_packet._coerce_str(
                    row.get("side"), field_name=f"{field_name}[{index}].side"
                ),
                "size": local_packet._coerce_float(
                    row.get("size"), field_name=f"{field_name}[{index}].size"
                ),
                "pnl": local_packet._coerce_float(
                    row.get("pnl"), field_name=f"{field_name}[{index}].pnl"
                ),
                "commission": local_packet._coerce_float(
                    row.get("commission"), field_name=f"{field_name}[{index}].commission"
                ),
                "exit_reason": local_packet._coerce_str(
                    row.get("exit_reason"), field_name=f"{field_name}[{index}].exit_reason"
                ),
                "is_partial": local_packet._coerce_bool(
                    row.get("is_partial"), field_name=f"{field_name}[{index}].is_partial"
                ),
                "position_id": str(row.get("position_id") or ""),
            }
        )
    return normalized


def _trade_signature(trade: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(trade["entry_time"]),
        str(trade["exit_time"]),
        str(trade["side"]),
        round(float(trade["size"]), 12),
        round(float(trade["pnl"]), 12),
        round(float(trade["commission"]), 12),
        str(trade["exit_reason"]),
        bool(trade["is_partial"]),
        str(trade["position_id"]),
    )


def _trade_overlaps_envelope(trade: dict[str, Any], spec: EnvelopeSubjectSpec) -> bool:
    return local_packet._parse_timestamp(str(trade["entry_time"])) <= local_packet._parse_timestamp(
        spec.envelope_end
    ) and local_packet._parse_timestamp(str(trade["exit_time"])) >= local_packet._parse_timestamp(
        spec.envelope_start
    )


def _trade_exits_inside_envelope(trade: dict[str, Any], spec: EnvelopeSubjectSpec) -> bool:
    exit_time = local_packet._parse_timestamp(str(trade["exit_time"]))
    return (
        local_packet._parse_timestamp(spec.envelope_start)
        <= exit_time
        <= local_packet._parse_timestamp(spec.envelope_end)
    )


def _trade_path_summary(
    baseline_trades_raw: Any,
    release_zero_trades_raw: Any,
    *,
    spec: EnvelopeSubjectSpec,
    field_name: str,
) -> dict[str, Any]:
    baseline_trades = _coerce_trade_rows(
        baseline_trades_raw,
        field_name=f"{field_name}.baseline_trades",
    )
    release_zero_trades = _coerce_trade_rows(
        release_zero_trades_raw,
        field_name=f"{field_name}.release_zero_trades",
    )

    baseline_overlap = [trade for trade in baseline_trades if _trade_overlaps_envelope(trade, spec)]
    release_zero_overlap = [
        trade for trade in release_zero_trades if _trade_overlaps_envelope(trade, spec)
    ]
    baseline_exit_in_envelope = [
        trade for trade in baseline_trades if _trade_exits_inside_envelope(trade, spec)
    ]
    release_zero_exit_in_envelope = [
        trade for trade in release_zero_trades if _trade_exits_inside_envelope(trade, spec)
    ]

    return {
        "baseline_trade_event_count": len(baseline_trades),
        "release_zero_trade_event_count": len(release_zero_trades),
        "baseline_overlap_trade_event_count": len(baseline_overlap),
        "release_zero_overlap_trade_event_count": len(release_zero_overlap),
        "baseline_exit_event_count_inside_envelope": len(baseline_exit_in_envelope),
        "release_zero_exit_event_count_inside_envelope": len(release_zero_exit_in_envelope),
        "full_month_trade_signature_match": {_trade_signature(trade) for trade in baseline_trades}
        == {_trade_signature(trade) for trade in release_zero_trades},
        "overlap_trade_signature_match": {_trade_signature(trade) for trade in baseline_overlap}
        == {_trade_signature(trade) for trade in release_zero_overlap},
    }


def _build_equity_diff_series(
    baseline_curve: Any,
    release_zero_curve: Any,
    *,
    field_name: str,
) -> list[dict[str, Any]]:
    baseline_rows = _coerce_equity_curve(
        baseline_curve,
        field_name=f"{field_name}.baseline_curve",
    )
    release_zero_rows = _coerce_equity_curve(
        release_zero_curve,
        field_name=f"{field_name}.release_zero_curve",
    )
    if len(baseline_rows) != len(release_zero_rows):
        raise LocalEnvelopeError(
            f"Equity curve length drift for {field_name}: {len(baseline_rows)} vs {len(release_zero_rows)}"
        )

    diff_rows: list[dict[str, Any]] = []
    for index, (baseline_row, release_zero_row) in enumerate(
        zip(baseline_rows, release_zero_rows, strict=True)
    ):
        baseline_timestamp = str(baseline_row["timestamp"])
        release_zero_timestamp = str(release_zero_row["timestamp"])
        if baseline_timestamp != release_zero_timestamp:
            raise LocalEnvelopeError(
                f"Equity curve timestamp drift for {field_name} at index {index}: "
                f"{baseline_timestamp} vs {release_zero_timestamp}"
            )

        capital_diff = float(release_zero_row["capital"]) - float(baseline_row["capital"])
        unrealized_diff = float(release_zero_row["unrealized_pnl"]) - float(
            baseline_row["unrealized_pnl"]
        )
        total_equity_diff = float(release_zero_row["total_equity"]) - float(
            baseline_row["total_equity"]
        )
        diff_rows.append(
            {
                "timestamp": baseline_timestamp,
                "capital_diff": capital_diff,
                "unrealized_pnl_diff": unrealized_diff,
                "total_equity_diff": total_equity_diff,
                "baseline_total_equity": float(baseline_row["total_equity"]),
                "release_zero_total_equity": float(release_zero_row["total_equity"]),
            }
        )
    return diff_rows


def _snapshot_from_diff_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": str(row["timestamp"]),
        "capital_diff": _round_or_none(float(row["capital_diff"])),
        "unrealized_pnl_diff": _round_or_none(float(row["unrealized_pnl_diff"])),
        "total_equity_diff": _round_or_none(float(row["total_equity_diff"])),
        "baseline_total_equity": _round_or_none(float(row["baseline_total_equity"])),
        "release_zero_total_equity": _round_or_none(float(row["release_zero_total_equity"])),
    }


def _diff_direction(value: float) -> str:
    if value > DIFF_TOLERANCE:
        return "release_zero_ahead"
    if value < -DIFF_TOLERANCE:
        return "baseline_ahead"
    return "flat"


def _cancellation_share(start_value: float, end_value: float) -> float | None:
    if math.isclose(start_value, 0.0, abs_tol=DIFF_TOLERANCE):
        return None
    return abs(end_value - start_value) / abs(start_value)


def _find_row_by_timestamp(diff_rows: list[dict[str, Any]], timestamp: str) -> dict[str, Any]:
    for row in diff_rows:
        if str(row["timestamp"]) == timestamp:
            return row
    raise LocalEnvelopeError(f"Could not recover diff row for timestamp {timestamp}")


def _last_row_before(diff_rows: list[dict[str, Any]], timestamp: str) -> dict[str, Any]:
    target = local_packet._parse_timestamp(timestamp)
    prior_rows = [
        row for row in diff_rows if local_packet._parse_timestamp(str(row["timestamp"])) < target
    ]
    if prior_rows:
        return prior_rows[-1]
    return _find_row_by_timestamp(diff_rows, timestamp)


def _first_row_matching_month_end_diff(
    diff_rows: list[dict[str, Any]],
    *,
    month_end_diff: float,
    start_index: int,
) -> dict[str, Any] | None:
    for row in diff_rows[start_index:]:
        if math.isclose(float(row["total_equity_diff"]), month_end_diff, abs_tol=DIFF_TOLERANCE):
            return row
    return None


def _subject_payload(
    spec: EnvelopeSubjectSpec,
    *,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: Any,
) -> dict[str, Any]:
    baseline = _run_case_with_economics(
        "baseline",
        start_date=spec.month_start,
        end_date=spec.month_end,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = _run_case_with_economics(
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
        raise LocalEnvelopeError(
            f"Baseline continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.baseline_timestamps}, actual={observed_baseline_timestamps}"
        )
    if observed_release_zero_timestamps != spec.release_zero_timestamps:
        raise LocalEnvelopeError(
            f"Release-zero continuation-release timestamps drifted for {spec.subject_id}: "
            f"expected={spec.release_zero_timestamps}, actual={observed_release_zero_timestamps}"
        )

    baseline_summary = local_packet._coerce_dict(
        baseline.get("summary"), field_name=f"{spec.subject_id}.baseline.summary"
    )
    release_zero_summary = local_packet._coerce_dict(
        release_zero.get("summary"), field_name=f"{spec.subject_id}.release_zero.summary"
    )
    total_return_diff = local_packet._coerce_float(
        release_zero_summary.get("total_return"),
        field_name=f"{spec.subject_id}.release_zero.total_return",
    ) - local_packet._coerce_float(
        baseline_summary.get("total_return"),
        field_name=f"{spec.subject_id}.baseline.total_return",
    )
    final_capital_diff = local_packet._coerce_float(
        release_zero_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.release_zero.final_capital",
    ) - local_packet._coerce_float(
        baseline_summary.get("final_capital"),
        field_name=f"{spec.subject_id}.baseline.final_capital",
    )
    if not math.isclose(total_return_diff, spec.inventory_total_return_diff, abs_tol=1e-12):
        raise LocalEnvelopeError(
            f"Monthly total return diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_total_return_diff}, actual={total_return_diff}"
        )
    if not math.isclose(final_capital_diff, spec.inventory_final_capital_diff, abs_tol=1e-9):
        raise LocalEnvelopeError(
            f"Monthly final capital diff drifted for {spec.subject_id}: "
            f"expected={spec.inventory_final_capital_diff}, actual={final_capital_diff}"
        )

    diff_rows = _build_equity_diff_series(
        baseline.get("equity_curve"),
        release_zero.get("equity_curve"),
        field_name=f"{spec.subject_id}.equity_diff_series",
    )
    envelope_rows = [
        row
        for row in diff_rows
        if spec.envelope_start <= str(row["timestamp"]) <= spec.envelope_end
    ]
    if len(envelope_rows) != spec.envelope_row_count:
        raise LocalEnvelopeError(
            f"Envelope row-count drift for {spec.subject_id}: expected={spec.envelope_row_count}, actual={len(envelope_rows)}"
        )

    pre_anchor_row = _last_row_before(diff_rows, spec.envelope_start)
    envelope_start_row = _find_row_by_timestamp(diff_rows, spec.envelope_start)
    envelope_end_row = _find_row_by_timestamp(diff_rows, spec.envelope_end)
    month_end_row = diff_rows[-1]
    peak_positive_row = max(envelope_rows, key=lambda row: float(row["total_equity_diff"]))
    peak_negative_row = min(envelope_rows, key=lambda row: float(row["total_equity_diff"]))
    peak_abs_row = max(envelope_rows, key=lambda row: abs(float(row["total_equity_diff"])))
    full_month_peak_abs_row = max(diff_rows, key=lambda row: abs(float(row["total_equity_diff"])))

    month_end_total_equity_diff = float(month_end_row["total_equity_diff"])
    if not math.isclose(month_end_total_equity_diff, final_capital_diff, abs_tol=1e-9):
        raise LocalEnvelopeError(
            f"Month-end equity diff drifted from final capital diff for {spec.subject_id}: "
            f"equity={month_end_total_equity_diff}, final_capital={final_capital_diff}"
        )

    peak_abs_index = next(
        index
        for index, row in enumerate(diff_rows)
        if str(row["timestamp"]) == str(peak_abs_row["timestamp"])
    )
    first_month_end_diff_return = _first_row_matching_month_end_diff(
        diff_rows,
        month_end_diff=month_end_total_equity_diff,
        start_index=peak_abs_index + 1,
    )

    peak_abs_value = float(peak_abs_row["total_equity_diff"])
    envelope_end_value = float(envelope_end_row["total_equity_diff"])
    initial_capital = local_packet._coerce_float(
        baseline_summary.get("initial_capital"),
        field_name=f"{spec.subject_id}.baseline.initial_capital",
    )
    trade_path_summary = _trade_path_summary(
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
            "inventory_total_return_diff": _round_or_none(spec.inventory_total_return_diff),
            "inventory_final_capital_diff": _round_or_none(spec.inventory_final_capital_diff),
        },
        "envelope_window": {
            "start": spec.envelope_start,
            "end": spec.envelope_end,
            "row_count": spec.envelope_row_count,
            "span_hours": _round_or_none(
                (
                    local_packet._parse_timestamp(spec.envelope_end)
                    - local_packet._parse_timestamp(spec.envelope_start)
                ).total_seconds()
                / 3600.0
            ),
        },
        "continuation_release_timestamp_validation": {
            "baseline_matches_local_packet": True,
            "release_zero_matches_local_packet": True,
        },
        "monthly_reproduction": {
            "top_line_sign": local_packet._sign_label(total_return_diff),
            "rerun_total_return_diff": _round_or_none(total_return_diff),
            "rerun_final_capital_diff": _round_or_none(final_capital_diff),
            "matches_local_packet_total_return_diff": True,
            "matches_local_packet_final_capital_diff": True,
        },
        "equity_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
        "keypoints": {
            "pre_envelope_anchor": _snapshot_from_diff_row(pre_anchor_row),
            "envelope_start": _snapshot_from_diff_row(envelope_start_row),
            "envelope_end": _snapshot_from_diff_row(envelope_end_row),
            "month_end": _snapshot_from_diff_row(month_end_row),
            "first_return_to_month_end_diff_after_peak": (
                _snapshot_from_diff_row(first_month_end_diff_return)
                if first_month_end_diff_return is not None
                else None
            ),
        },
        "envelope_extrema": {
            "peak_release_zero_advantage": _snapshot_from_diff_row(peak_positive_row),
            "peak_baseline_advantage": _snapshot_from_diff_row(peak_negative_row),
            "peak_absolute_gap": _snapshot_from_diff_row(peak_abs_row),
            "full_month_peak_absolute_gap": _snapshot_from_diff_row(full_month_peak_abs_row),
            "envelope_captures_full_month_peak_absolute_gap": (
                str(full_month_peak_abs_row["timestamp"]) == str(peak_abs_row["timestamp"])
            ),
        },
        "path_summary": {
            "initial_capital": _round_or_none(initial_capital),
            "pre_envelope_anchor_total_equity_diff": _round_or_none(
                float(pre_anchor_row["total_equity_diff"])
            ),
            "envelope_end_total_equity_diff": _round_or_none(envelope_end_value),
            "month_end_total_equity_diff": _round_or_none(month_end_total_equity_diff),
            "peak_absolute_total_equity_diff": _round_or_none(peak_abs_value),
            "peak_absolute_pct_of_initial_capital": _round_or_none(
                0.0
                if math.isclose(initial_capital, 0.0, abs_tol=DIFF_TOLERANCE)
                else peak_abs_value / initial_capital
            ),
            "peak_absolute_direction": _diff_direction(peak_abs_value),
            "pre_anchor_to_peak_change": _round_or_none(
                peak_abs_value - float(pre_anchor_row["total_equity_diff"])
            ),
            "pre_anchor_to_envelope_end_change": _round_or_none(
                envelope_end_value - float(pre_anchor_row["total_equity_diff"])
            ),
            "peak_to_month_end_cancellation_amount": _round_or_none(
                month_end_total_equity_diff - peak_abs_value
            ),
            "peak_to_month_end_cancellation_share": _round_or_none(
                _cancellation_share(peak_abs_value, month_end_total_equity_diff)
            ),
            "envelope_end_to_month_end_cancellation_amount": _round_or_none(
                month_end_total_equity_diff - envelope_end_value
            ),
            "envelope_end_to_month_end_cancellation_share": _round_or_none(
                _cancellation_share(envelope_end_value, month_end_total_equity_diff)
            ),
        },
        "trade_path_summary": trade_path_summary,
        "envelope_diff_series": [_snapshot_from_diff_row(row) for row in envelope_rows],
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = local_packet._coerce_dict(
        subject_payloads.get("2021-04"), field_name="local_envelope.subject_payloads.2021-04"
    )
    control = local_packet._coerce_dict(
        subject_payloads.get("2023-05"), field_name="local_envelope.subject_payloads.2023-05"
    )
    candidate_path = local_packet._coerce_dict(
        candidate.get("path_summary"), field_name="candidate.path_summary"
    )
    control_path = local_packet._coerce_dict(
        control.get("path_summary"), field_name="control.path_summary"
    )

    candidate_peak = abs(
        local_packet._coerce_float(
            candidate_path.get("peak_absolute_total_equity_diff"),
            field_name="candidate.peak_absolute_total_equity_diff",
        )
    )
    control_peak = abs(
        local_packet._coerce_float(
            control_path.get("peak_absolute_total_equity_diff"),
            field_name="control.peak_absolute_total_equity_diff",
        )
    )
    candidate_month_end = local_packet._coerce_float(
        candidate_path.get("month_end_total_equity_diff"),
        field_name="candidate.month_end_total_equity_diff",
    )
    control_month_end = local_packet._coerce_float(
        control_path.get("month_end_total_equity_diff"),
        field_name="control.month_end_total_equity_diff",
    )
    candidate_envelope_end = local_packet._coerce_float(
        candidate_path.get("envelope_end_total_equity_diff"),
        field_name="candidate.envelope_end_total_equity_diff",
    )
    control_envelope_end = local_packet._coerce_float(
        control_path.get("envelope_end_total_equity_diff"),
        field_name="control.envelope_end_total_equity_diff",
    )

    if candidate_peak > control_peak + DIFF_TOLERANCE:
        status = PACKET_STATUS_CANDIDATE_STRONGER
        inference = (
            "`2021-04` opens a larger local equity gap than `2023-05` on the same release_zero-minus-baseline "
            "economic path while both months still close back to flat at month end. This supports the "
            "outcome-cancellation hypothesis around the candidate envelope more than around the control."
        )
    elif control_peak > candidate_peak + DIFF_TOLERANCE:
        status = PACKET_STATUS_CONTROL_STRONGER
        inference = (
            "`2023-05` opens a larger local equity gap than `2021-04`, so the current negative-like candidate "
            "does not dominate the control on the bounded local economic path."
        )
    else:
        status = PACKET_STATUS_TIED
        inference = (
            "`2021-04` and `2023-05` remain economically invariant on the bounded local envelope path: the "
            "release_zero-minus-baseline total-equity series stays flat, so the observed policy-router asymmetry "
            "does not materialize as a local economic gap on this surface."
        )

    return {
        "status": status,
        "candidate_subject_id": "2021-04",
        "control_subject_id": "2023-05",
        "candidate_peak_absolute_total_equity_diff": _round_or_none(candidate_peak),
        "control_peak_absolute_total_equity_diff": _round_or_none(control_peak),
        "candidate_envelope_end_total_equity_diff": _round_or_none(candidate_envelope_end),
        "control_envelope_end_total_equity_diff": _round_or_none(control_envelope_end),
        "candidate_month_end_total_equity_diff": _round_or_none(candidate_month_end),
        "control_month_end_total_equity_diff": _round_or_none(control_month_end),
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a local action-or-position equivalence check inside "
            "the `2021-04` envelope to determine whether the retained policy/size differences are economically inert "
            "because they preserve the same executed trade path."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in local_packet.SUBJECT_DEFINITIONS],
            "economic_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
        },
    }


def run_local_envelope_cancellation() -> dict[str, Any]:
    envelope_specs = _load_local_packet_specs()
    base_cfg, carrier_cfg, authority = local_packet._load_base_and_carrier_cfg()
    subject_payloads = {
        definition.subject_id: _subject_payload(
            envelope_specs[definition.subject_id],
            base_cfg=base_cfg,
            carrier_cfg=carrier_cfg,
            authority=authority,
        )
        for definition in local_packet.SUBJECT_DEFINITIONS
    }
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-envelope-cancellation-2026-05-26",
        "base_sha": local_packet._git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "exact local envelopes imported from the landed local packet, rerun on the same carrier and "
                "measured only on the release_zero-minus-baseline equity path"
            ),
            "question": (
                "Does the `2021-04` candidate open a larger local equity gap than the `2023-05` control inside the "
                "same continuation-release envelope, and is that local gap later canceled back to flat by month end?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "local_packet_artifact": str(LOCAL_PACKET_RELATIVE),
            "carrier_path": str(local_packet.CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(local_packet.WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in local_packet.SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "economic_diff_basis": "release_zero_total_equity_minus_baseline_total_equity",
            },
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_local_envelope_cancellation()
    except LocalEnvelopeError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("packet_summary", {}).get("status", result.get("status")),
        "candidate_peak_absolute_total_equity_diff": result.get("packet_summary", {}).get(
            "candidate_peak_absolute_total_equity_diff"
        ),
        "control_peak_absolute_total_equity_diff": result.get("packet_summary", {}).get(
            "control_peak_absolute_total_equity_diff"
        ),
        "candidate_subject_id": result.get("packet_summary", {}).get("candidate_subject_id"),
        "control_subject_id": result.get("packet_summary", {}).get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
