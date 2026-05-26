# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
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


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(inner) for key, inner in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(inner) for inner in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, Path):
        return str(value)
    return value


def _parse_timestamp(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _normalize_timestamp_text(raw: Any) -> str:
    if raw is None:
        raise ValueError("timestamp is required")
    if hasattr(raw, "isoformat"):
        return _parse_timestamp(str(raw.isoformat())).isoformat()
    return _parse_timestamp(str(raw)).isoformat()


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


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority
from scripts.run.run_backtest import GenesisPipeline, _deep_merge

os.environ["GENESIS_RANDOM_SEED"] = "42"
os.environ["GENESIS_FAST_WINDOW"] = "1"
os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
os.environ["GENESIS_PRECOMPUTE_CACHE_WRITE"] = "0"
os.environ["GENESIS_MODE_EXPLICIT"] = "1"
os.environ["GENESIS_FAST_HASH"] = "0"
os.environ["GENESIS_SCORE_VERSION"] = "v2"

SYMBOL = "tBTCUSD"
TIMEFRAME = "3h"
DATA_SOURCE_POLICY = "curated_only"
DECISION_ARTIFACT_RELATIVE = Path(
    "results/evaluation/feature_attribution_post_phase14_ri_decision_surface_fixed_three_cohort_2026-05-26.json"
)
CARRIER_PATH = (
    ROOT_DIR
    / "tmp"
    / "policy_router_evidence"
    / "tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = (
    "feature_attribution_post_phase14_ri_trade_exit_join_fixed_three_cohort_2026-05-26.json"
)
STATUS_OK = "feature_attribution_ri_trade_exit_join_fixed_three_cohort_generated"
STATUS_FAIL_CLOSED = "feature_attribution_ri_trade_exit_join_fixed_three_cohort_fail_closed"
EXPECTED_DECISION_STATUS = "feature_attribution_ri_decision_surface_fixed_three_cohort_generated"
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")


class TradeJoinError(RuntimeError):
    """Raised when the bounded trade/exit join slice cannot complete safely."""


@dataclass(frozen=True)
class CohortSurface:
    cohort_label: str
    display_name: str
    source_key: str
    run_start_date: str
    run_end_date: str
    exact_timestamps: tuple[str, ...]
    decision_rows: tuple[dict[str, Any], ...]
    expected_config_fingerprint: str
    expected_warmup_bars: int


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Join the fixed-three-cohort RI decision surface to bounded trade and exit outcomes "
            "while freezing observed vs derived join semantics."
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
        help="Repo-relative decision-surface artifact used as the canonical Slice 2 input.",
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


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TradeJoinError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise TradeJoinError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TradeJoinError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


def _load_decision_artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise TradeJoinError(f"Decision artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TradeJoinError("Decision artifact is not a JSON object")
    if payload.get("status") != EXPECTED_DECISION_STATUS:
        raise TradeJoinError(f"Unexpected decision artifact status: {payload.get('status')!r}")
    return payload


def _extract_cohort_surfaces(payload: dict[str, Any]) -> dict[str, CohortSurface]:
    decision_rows = _coerce_list(payload.get("decision_rows"), field_name="decision_rows")
    cohorts_payload = _coerce_dict(payload.get("cohorts"), field_name="cohorts")

    rows_by_cohort: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for raw_row in decision_rows:
        row = _coerce_dict(raw_row, field_name="decision_row")
        cohort_label = _coerce_str(row.get("cohort_label"), field_name="decision_row.cohort_label")
        rows_by_cohort[cohort_label].append(row)

    extracted: dict[str, CohortSurface] = {}
    for cohort_label, cohort_payload_raw in cohorts_payload.items():
        cohort_payload = _coerce_dict(cohort_payload_raw, field_name=f"cohorts.{cohort_label}")
        display_name = _coerce_str(
            cohort_payload.get("display_name"), field_name=f"cohorts.{cohort_label}.display_name"
        )
        source_key = _coerce_str(
            cohort_payload.get("source_key"), field_name=f"cohorts.{cohort_label}.source_key"
        )
        window = _coerce_dict(
            cohort_payload.get("window"), field_name=f"cohorts.{cohort_label}.window"
        )
        run_context = _coerce_dict(
            cohort_payload.get("run_context"), field_name=f"cohorts.{cohort_label}.run_context"
        )
        execution_mode = _coerce_dict(
            run_context.get("execution_mode"), field_name=f"cohorts.{cohort_label}.execution_mode"
        )
        exact_timestamps = tuple(
            _normalize_timestamp_text(
                _coerce_str(
                    timestamp,
                    field_name=f"cohorts.{cohort_label}.window.exact_timestamp",
                )
            )
            for timestamp in _coerce_list(
                window.get("exact_timestamps"),
                field_name=f"cohorts.{cohort_label}.window.exact_timestamps",
            )
        )
        cohort_rows = tuple(
            sorted(
                rows_by_cohort.get(cohort_label, []),
                key=lambda row: _normalize_timestamp_text(row.get("timestamp")),
            )
        )
        if not cohort_rows:
            raise TradeJoinError(f"Decision artifact has no rows for cohort {cohort_label!r}")

        extracted[cohort_label] = CohortSurface(
            cohort_label=cohort_label,
            display_name=display_name,
            source_key=source_key,
            run_start_date=_coerce_str(
                window.get("start_date"), field_name=f"cohorts.{cohort_label}.window.start_date"
            ),
            run_end_date=_coerce_str(
                window.get("end_date"), field_name=f"cohorts.{cohort_label}.window.end_date"
            ),
            exact_timestamps=exact_timestamps,
            decision_rows=cohort_rows,
            expected_config_fingerprint=_coerce_str(
                run_context.get("effective_config_fingerprint"),
                field_name=f"cohorts.{cohort_label}.run_context.effective_config_fingerprint",
            ),
            expected_warmup_bars=int(payload.get("decision_rows", [{}])[0].get("warmup_bars", 120)),
        )
        if str(execution_mode.get("env_precompute_features")) != "1":
            raise TradeJoinError(
                f"Decision artifact execution mode drifted for cohort {cohort_label}: "
                "env_precompute_features != 1"
            )
    return extracted


def _load_base_and_carrier_cfg() -> tuple[dict[str, Any], dict[str, Any], ConfigAuthority]:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    carrier_cfg = override_payload.get("cfg") or override_payload.get("parameters")
    if not isinstance(carrier_cfg, dict):
        raise TradeJoinError("Evidence carrier missing cfg/parameters object")
    return base_cfg, carrier_cfg, authority


def _validate_execution_mode(execution_mode: dict[str, Any], *, cohort_label: str) -> None:
    if not execution_mode.get("fast_window"):
        raise TradeJoinError(f"Execution mode drift for {cohort_label}: fast_window false")
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise TradeJoinError(
            f"Execution mode drift for {cohort_label}: env_precompute_features != 1"
        )
    if not execution_mode.get("precompute_enabled"):
        raise TradeJoinError(f"Execution mode drift for {cohort_label}: precompute_enabled false")
    if str(execution_mode.get("mode_explicit")) != "1":
        raise TradeJoinError(f"Execution mode drift for {cohort_label}: mode_explicit != 1")


def _normalize_trade_row(trade: dict[str, Any]) -> dict[str, Any]:
    position_id = str(trade.get("position_id") or "").strip()
    entry_time = _normalize_timestamp_text(trade.get("entry_time"))
    if not position_id:
        position_id = f"{trade.get('symbol', 'unknown')}_{entry_time}"
    normalized = {
        "symbol": str(trade.get("symbol") or ""),
        "side": str(trade.get("side") or ""),
        "size": float(trade.get("size") or 0.0),
        "entry_price": float(trade.get("entry_price") or 0.0),
        "entry_time": entry_time,
        "entry_regime": trade.get("entry_regime"),
        "exit_price": float(trade.get("exit_price") or 0.0),
        "exit_time": _normalize_timestamp_text(trade.get("exit_time")),
        "pnl": float(trade.get("pnl") or 0.0),
        "pnl_pct": float(trade.get("pnl_pct") or 0.0),
        "commission": float(trade.get("commission") or 0.0),
        "exit_reason": str(trade.get("exit_reason") or ""),
        "is_partial": bool(trade.get("is_partial")),
        "remaining_size": float(trade.get("remaining_size") or 0.0),
        "position_id": position_id,
        "entry_reasons": list(trade.get("entry_reasons") or []),
        "entry_fib_debug": _json_safe(trade.get("entry_fib_debug")),
        "exit_fib_debug": _json_safe(trade.get("exit_fib_debug")),
    }
    return normalized


def _position_key_from_trade(trade: dict[str, Any]) -> str:
    return str(trade.get("position_id") or f"{trade.get('symbol')}_{trade.get('entry_time')}")


def _classify_exit_family(exit_reason: str) -> str:
    reason = str(exit_reason or "").strip().upper()
    if re.match(r"^TP\d+_", reason) or re.match(r"^TP\d+\s+HIT\b", reason):
        return "take_profit"
    if reason == "EMERGENCY_TP":
        return "take_profit"
    if reason == "EMERGENCY_SL":
        return "stop_loss"
    if reason in {"TRAIL_STOP", "FALLBACK_TRAIL"}:
        return "trailing_stop"
    if reason == "REGIME_CHANGE":
        return "regime_exit"
    if reason == "CONF_DROP":
        return "confidence_exit"
    if reason == "OPPOSITE_SIGNAL":
        return "manual_or_other"
    return "unknown_unclassified"


def _cohort_position_summaries(
    *,
    trades: list[dict[str, Any]],
    decision_rows_by_timestamp: dict[str, list[dict[str, Any]]],
    entry_events_by_position: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[_position_key_from_trade(trade)].append(trade)

    summaries: list[dict[str, Any]] = []
    for position_key in sorted(grouped):
        events = sorted(
            grouped[position_key], key=lambda trade: (trade["exit_time"], trade["remaining_size"])
        )
        first_event = events[0]
        matched_decisions = decision_rows_by_timestamp.get(first_event["entry_time"], [])
        decision_reason_match = any(
            list(row.get("reasons") or []) == list(first_event.get("entry_reasons") or [])
            for row in matched_decisions
        )
        exit_reason_counts = Counter(trade["exit_reason"] for trade in events)
        exit_family_counts = Counter(
            _classify_exit_family(trade["exit_reason"]) for trade in events
        )
        summaries.append(
            {
                "position_key": position_key,
                "entry_time": first_event["entry_time"],
                "entry_regime": first_event.get("entry_regime"),
                "entry_reasons": list(first_event.get("entry_reasons") or []),
                "matched_decision_identity_keys": [
                    str(row.get("decision_identity_key") or "") for row in matched_decisions
                ],
                "matched_decision_count": len(matched_decisions),
                "decision_reason_exact_match": decision_reason_match,
                "observed_entry_open_event": position_key in entry_events_by_position,
                "trade_event_count": len(events),
                "partial_trade_event_count": sum(1 for trade in events if trade["is_partial"]),
                "full_trade_event_count": sum(1 for trade in events if not trade["is_partial"]),
                "gross_trade_pnl": round(sum(trade["pnl"] for trade in events), 12),
                "total_exit_commission": round(sum(trade["commission"] for trade in events), 12),
                "exit_reason_counts": dict(sorted(exit_reason_counts.items())),
                "exit_family_counts": dict(sorted(exit_family_counts.items())),
                "final_exit_reason": events[-1]["exit_reason"],
                "final_exit_family": _classify_exit_family(events[-1]["exit_reason"]),
                "trade_events": events,
            }
        )
    return summaries


def _run_cohort_join(
    cohort: CohortSurface,
    *,
    base_sha: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise TradeJoinError(
            f"Carrier does not expose enabled research_policy_router for {cohort.cohort_label}"
        )

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()
    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        start_date=cohort.run_start_date,
        end_date=cohort.run_end_date,
        warmup_bars=cohort.expected_warmup_bars,
        data_source_policy=DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise TradeJoinError(f"BacktestEngine.load_data() failed for cohort {cohort.cohort_label}")

    entry_events: list[dict[str, Any]] = []

    def post_execution_hook(symbol: str, bar_index: int, action: str, executed: bool):
        if not executed:
            return
        position = engine.position_tracker.position
        if position is None:
            return
        entry_time = _normalize_timestamp_text(position.entry_time)
        entry_events.append(
            {
                "symbol": symbol,
                "timeframe": TIMEFRAME,
                "bar_index": int(bar_index),
                "action": str(action),
                "executed": bool(executed),
                "entry_time": entry_time,
                "entry_price": float(position.entry_price),
                "entry_size": float(position.current_size),
                "entry_regime": position.entry_regime,
                "entry_reasons": list(position.entry_reasons or []),
                "position_key": f"{position.symbol}_{position.entry_time.isoformat()}",
            }
        )

    engine.post_execution_hook = post_execution_hook
    results = engine.run(policy={"symbol": SYMBOL, "timeframe": TIMEFRAME}, configs=validated_cfg)
    if "error" in results:
        raise TradeJoinError(
            f"Backtest run failed for cohort {cohort.cohort_label}: {results['error']}"
        )

    backtest_info = _coerce_dict(results.get("backtest_info") or {}, field_name="backtest_info")
    execution_mode = _coerce_dict(
        backtest_info.get("execution_mode") or {},
        field_name=f"{cohort.cohort_label}.execution_mode",
    )
    _validate_execution_mode(execution_mode, cohort_label=cohort.cohort_label)
    effective_config_fingerprint = str(backtest_info.get("effective_config_fingerprint") or "")
    if effective_config_fingerprint != cohort.expected_config_fingerprint:
        raise TradeJoinError(
            f"Effective config fingerprint drift for cohort {cohort.cohort_label}: "
            f"expected={cohort.expected_config_fingerprint}, actual={effective_config_fingerprint}"
        )

    exact_timestamp_set = set(cohort.exact_timestamps)
    exact_entry_events = [
        _json_safe(event)
        for event in entry_events
        if str(event.get("entry_time")) in exact_timestamp_set
    ]
    entry_events_by_timestamp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    entry_events_by_position: dict[str, dict[str, Any]] = {}
    for event in exact_entry_events:
        entry_events_by_timestamp[str(event["entry_time"])].append(event)
        entry_events_by_position[str(event["position_key"])] = event

    normalized_trades = [
        _normalize_trade_row(_coerce_dict(trade, field_name="trade"))
        for trade in _coerce_list(results.get("trades"), field_name="trades")
    ]
    exact_position_keys = set(entry_events_by_position)
    exact_trades = [
        trade
        for trade in normalized_trades
        if _position_key_from_trade(trade) in exact_position_keys
    ]

    decision_rows_by_timestamp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision_row in cohort.decision_rows:
        timestamp_text = _normalize_timestamp_text(decision_row.get("timestamp"))
        decision_rows_by_timestamp[timestamp_text].append(decision_row)

    decision_join_rows: list[dict[str, Any]] = []
    for decision_row in cohort.decision_rows:
        timestamp_text = _normalize_timestamp_text(decision_row.get("timestamp"))
        matching_entry_events = entry_events_by_timestamp.get(timestamp_text, [])
        decision_reasons = list(decision_row.get("reasons") or [])
        exact_reason_match = any(
            list(event.get("entry_reasons") or []) == decision_reasons
            for event in matching_entry_events
        )
        action = str(decision_row.get("action") or "")
        if action == "NONE":
            join_status = "no_action_decision"
        elif matching_entry_events:
            join_status = "observed_open_event_matched"
        else:
            join_status = "non_opening_signal_without_execution_row"
        decision_join_rows.append(
            {
                "decision_identity_key": decision_row.get("decision_identity_key"),
                "timestamp": timestamp_text,
                "action": action,
                "reasons": decision_reasons,
                "matched_open_event_count": len(matching_entry_events),
                "matched_position_keys": [
                    str(event.get("position_key") or "") for event in matching_entry_events
                ],
                "entry_reasons_exact_match": exact_reason_match,
                "join_status": join_status,
            }
        )

    position_summaries = _cohort_position_summaries(
        trades=exact_trades,
        decision_rows_by_timestamp=decision_rows_by_timestamp,
        entry_events_by_position=entry_events_by_position,
    )

    exit_reason_counts = Counter(trade["exit_reason"] for trade in exact_trades)
    exit_family_counts = Counter(
        _classify_exit_family(trade["exit_reason"]) for trade in exact_trades
    )
    observed_open_decisions = sum(
        1 for row in decision_join_rows if row["join_status"] == "observed_open_event_matched"
    )
    unresolved_non_none_decisions = sum(
        1
        for row in decision_join_rows
        if row["join_status"] == "non_opening_signal_without_execution_row"
    )

    return {
        "cohort_label": cohort.cohort_label,
        "display_name": cohort.display_name,
        "source_key": cohort.source_key,
        "window": {
            "run_start_date": cohort.run_start_date,
            "run_end_date": cohort.run_end_date,
            "exact_timestamp_count": len(cohort.exact_timestamps),
            "exact_timestamps": list(cohort.exact_timestamps),
        },
        "run_context": {
            "execution_mode": _json_safe(execution_mode),
            "effective_config_fingerprint": effective_config_fingerprint,
            "bars_total": _json_safe(backtest_info.get("bars_total")),
            "bars_processed": _json_safe(backtest_info.get("bars_processed")),
            "data_source_policy": DATA_SOURCE_POLICY,
            "exit_config_context": _json_safe(validated_cfg.get("exit") or {}),
            "htf_exit_config_context": _json_safe(validated_cfg.get("htf_exit_config") or {}),
        },
        "observed_vs_derived_contract": {
            "observed_surfaces": [
                "decision_row.timestamp",
                "decision_row.action",
                "decision_row.reasons",
                "entry_open_event.entry_time",
                "entry_open_event.entry_reasons",
                "trade.position_id",
                "trade.entry_time",
                "trade.exit_time",
                "trade.exit_reason",
                "trade.is_partial",
                "trade.remaining_size",
            ],
            "derived_steps": [
                "decision_row.timestamp == entry_open_event.entry_time for open-event matching",
                "decision_row.reasons == entry_open_event.entry_reasons for bounded join strengthening",
                "entry_open_event.position_key == trade.position_id for position grouping",
                "exit_family derived from trade.exit_reason",
            ],
            "not_directly_observed_in_current_outputs": [
                "decision_row.position_id",
                "decision_row.execution_status for non-opening signals",
                "canonical decision_to_trade join without helper-side execution capture",
            ],
        },
        "summary": {
            "exact_decision_row_count": len(cohort.decision_rows),
            "non_none_decision_row_count": sum(
                1 for row in cohort.decision_rows if str(row.get("action") or "") != "NONE"
            ),
            "observed_open_event_count": len(exact_entry_events),
            "observed_open_decision_count": observed_open_decisions,
            "unresolved_non_none_decision_count": unresolved_non_none_decisions,
            "position_count": len(position_summaries),
            "trade_event_count": len(exact_trades),
            "partial_trade_event_count": sum(1 for trade in exact_trades if trade["is_partial"]),
            "full_trade_event_count": sum(1 for trade in exact_trades if not trade["is_partial"]),
            "exit_reason_counts": dict(sorted(exit_reason_counts.items())),
            "exit_family_counts": dict(sorted(exit_family_counts.items())),
        },
        "decision_join_rows": decision_join_rows,
        "entry_open_events": exact_entry_events,
        "position_summaries": position_summaries,
    }


def _build_fail_closed_result(
    *, base_sha: str, reason: str, decision_artifact_relative: str
) -> dict[str, Any]:
    return {
        "audit_version": "feature-attribution-post-phase14-ri-trade-exit-join-fixed-three-cohort-2026-05-26",
        "base_sha": base_sha,
        "actual_head_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "decision_artifact": decision_artifact_relative,
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
        },
    }


def run_trade_exit_join(*, base_sha: str, decision_artifact_relative: Path) -> dict[str, Any]:
    try:
        decision_payload = _load_decision_artifact(ROOT_DIR / decision_artifact_relative)
        cohort_surfaces = _extract_cohort_surfaces(decision_payload)
        base_cfg, carrier_cfg, authority = _load_base_and_carrier_cfg()
        cohort_payloads = {
            cohort_label: _run_cohort_join(
                cohort,
                base_sha=base_sha,
                base_cfg=base_cfg,
                carrier_cfg=carrier_cfg,
                authority=authority,
            )
            for cohort_label, cohort in cohort_surfaces.items()
        }
    except TradeJoinError as exc:
        return _build_fail_closed_result(
            base_sha=base_sha,
            reason=str(exc),
            decision_artifact_relative=str(decision_artifact_relative),
        )

    total_exit_reason_counts = Counter()
    total_exit_family_counts = Counter()
    total_trade_event_count = 0
    total_position_count = 0
    total_observed_open_event_count = 0
    total_unresolved_non_none_decisions = 0
    for cohort_label in sorted(cohort_payloads):
        summary = cohort_payloads[cohort_label]["summary"]
        total_exit_reason_counts.update(summary.get("exit_reason_counts") or {})
        total_exit_family_counts.update(summary.get("exit_family_counts") or {})
        total_trade_event_count += int(summary.get("trade_event_count") or 0)
        total_position_count += int(summary.get("position_count") or 0)
        total_observed_open_event_count += int(summary.get("observed_open_event_count") or 0)
        total_unresolved_non_none_decisions += int(
            summary.get("unresolved_non_none_decision_count") or 0
        )

    return {
        "audit_version": "feature-attribution-post-phase14-ri-trade-exit-join-fixed-three-cohort-2026-05-26",
        "base_sha": base_sha,
        "actual_head_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "source_surface": "Slice 2 fixed-three-cohort decision artifact plus bounded same-stack cohort reruns",
            "schema_target": "trade_row join contract and exit taxonomy over the fixed cohort surface",
            "observed_execution_support": "helper-side open-event capture via post_execution_hook only",
            "still_not_a_canonical_runtime_execution_row": True,
        },
        "inputs": {
            "decision_artifact": str(decision_artifact_relative),
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "data_source_policy": DATA_SOURCE_POLICY,
            "env": {
                "GENESIS_RANDOM_SEED": os.environ.get("GENESIS_RANDOM_SEED"),
                "GENESIS_FAST_WINDOW": os.environ.get("GENESIS_FAST_WINDOW"),
                "GENESIS_PRECOMPUTE_FEATURES": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
                "GENESIS_PRECOMPUTE_CACHE_WRITE": os.environ.get("GENESIS_PRECOMPUTE_CACHE_WRITE"),
                "GENESIS_MODE_EXPLICIT": os.environ.get("GENESIS_MODE_EXPLICIT"),
                "GENESIS_FAST_HASH": os.environ.get("GENESIS_FAST_HASH"),
                "GENESIS_SCORE_VERSION": os.environ.get("GENESIS_SCORE_VERSION"),
            },
        },
        "global_summary": {
            "cohort_count": len(cohort_payloads),
            "total_position_count": total_position_count,
            "total_trade_event_count": total_trade_event_count,
            "total_observed_open_event_count": total_observed_open_event_count,
            "total_unresolved_non_none_decisions": total_unresolved_non_none_decisions,
            "exit_reason_counts": dict(sorted(total_exit_reason_counts.items())),
            "exit_family_counts": dict(sorted(total_exit_family_counts.items())),
        },
        "exit_taxonomy_contract": {
            "observed_source_field": "trade.exit_reason",
            "derived_target_field": "exit_family",
            "mapping": {
                "TP*": "take_profit",
                "EMERGENCY_TP": "take_profit",
                "EMERGENCY_SL": "stop_loss",
                "TRAIL_STOP": "trailing_stop",
                "FALLBACK_TRAIL": "trailing_stop",
                "REGIME_CHANGE": "regime_exit",
                "CONF_DROP": "confidence_exit",
                "OPPOSITE_SIGNAL": "manual_or_other",
                "*unknown*": "unknown_unclassified",
            },
        },
        "cohorts": cohort_payloads,
    }


def main() -> int:
    args = _parse_args()
    decision_artifact_relative = Path(args.decision_artifact_relative)
    output_root = ROOT_DIR / Path(args.output_root_relative)
    output_json = output_root / args.summary_filename
    result = run_trade_exit_join(
        base_sha=args.base_sha,
        decision_artifact_relative=decision_artifact_relative,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_artifact": str(output_json),
                "status": result["status"],
                "total_position_count": result.get("global_summary", {}).get(
                    "total_position_count"
                ),
                "total_trade_event_count": result.get("global_summary", {}).get(
                    "total_trade_event_count"
                ),
                "failure_reason": result.get("failure_reason"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
