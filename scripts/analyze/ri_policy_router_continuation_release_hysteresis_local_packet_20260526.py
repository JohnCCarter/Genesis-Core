# ruff: noqa: E402

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean
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


ROOT_DIR = _find_repo_root(Path(__file__).resolve())
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority
from core.strategy.ri_policy_router import RESEARCH_POLICY_ROUTER_DEBUG_KEY
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
WARMUP = 120
DATA_SOURCE_POLICY = "curated_only"
MAX_ADJACENCY_HOURS = 24.0
MONTHLY_INVENTORY_WINDOWS_RELATIVE = Path(
    "results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/"
    "continuation_release_hysteresis_monthly_inventory_windows.json"
)
INTRA_BAND_SIGN_CANDIDATES_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json"
)
WIDENING_CANDIDATE_INVENTORY_RELATIVE = Path(
    "results/evaluation/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json"
)
WORKING_CONTRACT_REFERENCE = Path("GENESIS_WORKING_CONTRACT.md")
CARRIER_PATH = (
    ROOT_DIR
    / "tmp"
    / "policy_router_evidence"
    / "tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json"
)
OUTPUT_ROOT_RELATIVE = Path("results/evaluation")
OUTPUT_FILENAME = "ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json"
STATUS_OK = "continuation_release_hysteresis_local_packet_generated"
STATUS_FAIL_CLOSED = "continuation_release_hysteresis_local_packet_fail_closed"
PACKET_STATUS_CANDIDATE_STRONGER = (
    "negative_like_candidate_preserves_more_triad_local_asymmetry_than_control"
)
PACKET_STATUS_TIED = "candidate_and_control_preserve_same_triad_local_asymmetry_count"
PACKET_STATUS_CONTROL_STRONGER = (
    "positive_control_preserves_more_triad_local_asymmetry_than_candidate"
)
RETURN_DIFF_TOLERANCE = 1e-12
CAPITAL_DIFF_TOLERANCE = 1e-9


@dataclass(frozen=True)
class SubjectDefinition:
    subject_id: str
    role: str
    shortlist_key: str
    shortlist_rank: int


SUBJECT_DEFINITIONS = (
    SubjectDefinition(
        subject_id="2021-04",
        role="negative_like_candidate",
        shortlist_key="negative_like_candidates",
        shortlist_rank=0,
    ),
    SubjectDefinition(
        subject_id="2023-05",
        role="positive_control",
        shortlist_key="positive_control_candidates",
        shortlist_rank=0,
    ),
)


class LocalPacketError(RuntimeError):
    pass


def _load_json(relative_path: Path) -> Any:
    return json.loads((ROOT_DIR / relative_path).read_text(encoding="utf-8"))


def _coerce_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LocalPacketError(
            f"Expected object for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise LocalPacketError(
            f"Expected list for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LocalPacketError(f"Expected non-empty string for {field_name}, got {value!r}")
    return value


def _coerce_float(value: Any, *, field_name: str) -> float:
    if not isinstance(value, int | float):
        raise LocalPacketError(
            f"Expected number for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return float(value)


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise LocalPacketError(
            f"Expected bool for {field_name}, got {type(value).__name__}: {value!r}"
        )
    return value


def _coerce_optional_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _coerce_optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _coerce_optional_float(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _parse_timestamp(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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


def _numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        raise LocalPacketError("Expected at least one numeric value to summarize")
    return {
        "count": len(values),
        "min": _round_or_none(min(values)),
        "mean": _round_or_none(fmean(values)),
        "max": _round_or_none(max(values)),
    }


def _load_base_and_carrier_cfg() -> tuple[dict[str, Any], dict[str, Any], ConfigAuthority]:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    carrier_cfg = override_payload.get("cfg") or override_payload.get("parameters")
    if not isinstance(carrier_cfg, dict):
        raise LocalPacketError("Evidence carrier missing cfg/parameters object")
    return base_cfg, carrier_cfg, authority


def _run_case(
    mode: str,
    *,
    start_date: str,
    end_date: str,
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    override_cfg = deepcopy(carrier_cfg)
    mtf = override_cfg.setdefault("multi_timeframe", {})
    router_cfg = mtf.setdefault("research_policy_router", {})
    if not isinstance(router_cfg, dict) or not bool(router_cfg.get("enabled", False)):
        raise LocalPacketError(f"Carrier does not expose enabled research_policy_router for {mode}")

    if mode == "baseline":
        router_cfg.pop("continuation_release_hysteresis", None)
    elif mode == "release_zero":
        router_cfg["continuation_release_hysteresis"] = 0
    else:
        raise LocalPacketError(f"Unsupported mode {mode!r}")

    validated_cfg = authority.validate(_deep_merge(base_cfg, override_cfg)).model_dump()

    pipeline = GenesisPipeline()
    pipeline.setup_environment(seed=42)
    engine = pipeline.create_engine(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        start_date=start_date,
        end_date=end_date,
        warmup_bars=WARMUP,
        data_source_policy=DATA_SOURCE_POLICY,
    )
    if not engine.load_data():
        raise LocalPacketError(f"BacktestEngine.load_data() failed for {mode}")

    rows: dict[str, dict[str, Any]] = {}
    continuation_release_rows: dict[str, dict[str, Any]] = {}

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
        row = {
            "action": result.get("action"),
            "reasons": decision.get("reasons"),
            "size": decision.get("size"),
            "router_state": state_out.get("research_policy_router_state"),
            "router_debug": state_out.get(RESEARCH_POLICY_ROUTER_DEBUG_KEY),
        }
        rows[timestamp_text] = _json_safe(row)
        debug = row.get("router_debug") or {}
        if debug.get("switch_control_mode") == "continuation_release":
            continuation_release_rows[timestamp_text] = _json_safe(row)
        return result, meta

    engine.evaluation_hook = capture
    results = engine.run(policy={"symbol": SYMBOL, "timeframe": TIMEFRAME}, configs=validated_cfg)
    if "error" in results:
        raise LocalPacketError(f"Backtest run failed for {mode}: {results['error']}")

    backtest_info = results.get("backtest_info") or {}
    execution_mode = backtest_info.get("execution_mode") or {}
    if not execution_mode.get("fast_window"):
        raise LocalPacketError(f"Execution mode drift for {mode}: fast_window false")
    if str(execution_mode.get("env_precompute_features")) != "1":
        raise LocalPacketError(f"Execution mode drift for {mode}: env_precompute_features != 1")
    if not execution_mode.get("precompute_enabled"):
        raise LocalPacketError(f"Execution mode drift for {mode}: precompute_enabled false")
    if str(execution_mode.get("mode_explicit")) != "1":
        raise LocalPacketError(f"Execution mode drift for {mode}: mode_explicit != 1")

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
        "rows": rows,
        "continuation_release_rows": continuation_release_rows,
    }


def _behavior_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    normalized = deepcopy(row)
    debug = normalized.get("router_debug") or {}
    router_params = debug.get("router_params")
    if (
        isinstance(router_params, dict)
        and debug.get("switch_control_mode") != "continuation_release"
    ):
        router_params.pop("continuation_release_hysteresis", None)
    return normalized


def _group_adjacent_timestamps(timestamps: list[str]) -> list[list[str]]:
    if not timestamps:
        return []
    ordered = sorted(timestamps)
    groups: list[list[str]] = [[ordered[0]]]
    for current in ordered[1:]:
        if (
            _parse_timestamp(current) - _parse_timestamp(groups[-1][-1])
        ).total_seconds() / 3600.0 <= MAX_ADJACENCY_HOURS:
            groups[-1].append(current)
        else:
            groups.append([current])
    return groups


def _serialize_timestamp_group(timestamps: list[str]) -> dict[str, Any]:
    start = _parse_timestamp(timestamps[0])
    end = _parse_timestamp(timestamps[-1])
    return {
        "row_count": len(timestamps),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "span_hours": _round_or_none((end - start).total_seconds() / 3600.0),
        "timestamps": timestamps,
    }


def _serialize_cluster_diff_row(raw_row: dict[str, Any]) -> dict[str, Any]:
    baseline = _coerce_optional_dict(raw_row.get("baseline"))
    release_zero = _coerce_optional_dict(raw_row.get("release_zero"))
    baseline_debug = _coerce_optional_dict(baseline.get("router_debug"))
    release_zero_debug = _coerce_optional_dict(release_zero.get("router_debug"))
    return {
        "timestamp": _coerce_str(raw_row.get("timestamp"), field_name="cluster_row.timestamp"),
        "selected_policy_changed": _coerce_bool(
            raw_row.get("selected_policy_changed"),
            field_name="cluster_row.selected_policy_changed",
        ),
        "switch_reason_changed": _coerce_bool(
            raw_row.get("switch_reason_changed"),
            field_name="cluster_row.switch_reason_changed",
        ),
        "size_changed": _coerce_bool(
            raw_row.get("size_changed"), field_name="cluster_row.size_changed"
        ),
        "behavior_changed": _coerce_bool(
            raw_row.get("behavior_changed"), field_name="cluster_row.behavior_changed"
        ),
        "baseline_selected_policy": _coerce_optional_str(baseline_debug.get("selected_policy")),
        "release_zero_selected_policy": _coerce_optional_str(
            release_zero_debug.get("selected_policy")
        ),
        "baseline_switch_reason": _coerce_optional_str(baseline_debug.get("switch_reason")),
        "release_zero_switch_reason": _coerce_optional_str(release_zero_debug.get("switch_reason")),
        "baseline_action_edge": _coerce_optional_float(baseline_debug.get("action_edge")),
        "baseline_confidence_gate": _coerce_optional_float(baseline_debug.get("confidence_gate")),
        "baseline_clarity_score": _coerce_optional_float(baseline_debug.get("clarity_score")),
        "baseline_bars_since_regime_change": _coerce_optional_float(
            baseline_debug.get("bars_since_regime_change")
        ),
        "baseline_zone": _coerce_optional_str(baseline_debug.get("zone")),
        "baseline_switch_control_mode": _coerce_optional_str(
            baseline_debug.get("switch_control_mode")
        ),
        "release_zero_switch_control_mode": _coerce_optional_str(
            release_zero_debug.get("switch_control_mode")
        ),
    }


def _first_decisive_cluster_row(cluster_rows: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    for index, row in enumerate(cluster_rows):
        if (
            bool(row["selected_policy_changed"])
            or bool(row["switch_reason_changed"])
            or bool(row["size_changed"])
        ):
            return index, row
    raise LocalPacketError(
        "Could not recover a decisive row inside the continuation-release cluster"
    )


def _apply_rule(*, value: float, operator: str, threshold: float) -> bool:
    if operator == "<=":
        return value <= threshold
    if operator == ">=":
        return value >= threshold
    raise LocalPacketError(f"Unsupported operator {operator!r}")


def _load_monthly_inventory_windows() -> dict[str, dict[str, Any]]:
    payload = _coerce_list(
        _load_json(MONTHLY_INVENTORY_WINDOWS_RELATIVE),
        field_name="monthly_inventory_windows",
    )
    output: dict[str, dict[str, Any]] = {}
    for index, raw_window in enumerate(payload):
        window = _coerce_dict(raw_window, field_name=f"monthly_inventory_windows[{index}]")
        label = _coerce_str(
            window.get("label"), field_name=f"monthly_inventory_windows[{index}].label"
        )
        output[label] = window
    return output


def _load_shortlist() -> dict[str, list[str]]:
    payload = _coerce_dict(
        _load_json(WIDENING_CANDIDATE_INVENTORY_RELATIVE),
        field_name="widening_candidate_inventory",
    )
    rankings = _coerce_dict(payload.get("rankings"), field_name="rankings")
    shortlist = _coerce_dict(
        rankings.get("next_packet_shortlist"), field_name="next_packet_shortlist"
    )
    negative_candidates = [
        _coerce_str(
            _coerce_dict(candidate, field_name="negative_shortlist_entry").get("label"),
            field_name="negative_shortlist_entry.label",
        )
        for candidate in _coerce_list(
            shortlist.get("negative_like_candidates"),
            field_name="next_packet_shortlist.negative_like_candidates",
        )
    ]
    positive_controls = [
        _coerce_str(
            _coerce_dict(candidate, field_name="positive_shortlist_entry").get("label"),
            field_name="positive_shortlist_entry.label",
        )
        for candidate in _coerce_list(
            shortlist.get("positive_control_candidates"),
            field_name="next_packet_shortlist.positive_control_candidates",
        )
    ]
    return {
        "negative_like_candidates": negative_candidates,
        "positive_control_candidates": positive_controls,
    }


def _load_negative_rules() -> tuple[list[str], dict[str, dict[str, Any]]]:
    payload = _coerce_dict(
        _load_json(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
        field_name="intra_band_sign_candidates",
    )
    sign_summary = _coerce_dict(payload.get("sign_summary"), field_name="sign_summary")
    perfect_negative_separators = [
        _coerce_str(feature, field_name="perfect_negative_separator")
        for feature in _coerce_list(
            sign_summary.get("perfect_negative_separators"),
            field_name="sign_summary.perfect_negative_separators",
        )
    ]
    rule_search = _coerce_dict(payload.get("rule_search"), field_name="rule_search")
    best_rules_payload = _coerce_list(
        rule_search.get("best_rule_per_feature"),
        field_name="rule_search.best_rule_per_feature",
    )
    rules_by_feature: dict[str, dict[str, Any]] = {}
    for raw_rule in best_rules_payload:
        rule = _coerce_dict(raw_rule, field_name="best_rule_per_feature_entry")
        feature = _coerce_str(rule.get("feature"), field_name="best_rule.feature")
        if feature not in perfect_negative_separators:
            continue
        positive_label = _coerce_str(
            rule.get("positive_label"), field_name="best_rule.positive_label"
        )
        accuracy = _coerce_float(rule.get("accuracy"), field_name="best_rule.accuracy")
        if positive_label != "negative" or not math.isclose(accuracy, 1.0):
            raise LocalPacketError(
                f"Feature {feature} no longer carries a perfect negative best rule: {rule}"
            )
        rules_by_feature[feature] = {
            "feature": feature,
            "operator": _coerce_str(rule.get("operator"), field_name="best_rule.operator"),
            "threshold": _coerce_float(rule.get("threshold"), field_name="best_rule.threshold"),
        }
    missing = [
        feature for feature in perfect_negative_separators if feature not in rules_by_feature
    ]
    if missing:
        raise LocalPacketError(f"Missing perfect negative rules for features: {missing}")
    return perfect_negative_separators, rules_by_feature


def _subject_window(
    definition: SubjectDefinition, monthly_inventory: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    try:
        return monthly_inventory[definition.subject_id]
    except KeyError as exc:
        raise LocalPacketError(
            f"Monthly inventory missing subject {definition.subject_id}"
        ) from exc


def _validate_shortlist_position(
    definition: SubjectDefinition, shortlist: dict[str, list[str]]
) -> None:
    labels = shortlist[definition.shortlist_key]
    if definition.shortlist_rank >= len(labels):
        raise LocalPacketError(
            f"Shortlist {definition.shortlist_key} shorter than expected for {definition.subject_id}"
        )
    if labels[definition.shortlist_rank] != definition.subject_id:
        raise LocalPacketError(
            f"Shortlist drifted for {definition.subject_id}: expected rank {definition.shortlist_rank}, got {labels}"
        )


def _evaluate_negative_rules(
    subject_features: dict[str, float],
    *,
    feature_order: list[str],
    rules_by_feature: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    evaluations: list[dict[str, Any]] = []
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for feature in feature_order:
        rule = rules_by_feature[feature]
        value = float(subject_features[feature])
        threshold = float(rule["threshold"])
        operator = str(rule["operator"])
        matched = _apply_rule(value=value, operator=operator, threshold=threshold)
        if matched:
            satisfied.append(feature)
        else:
            unsatisfied.append(feature)
        evaluations.append(
            {
                "feature": feature,
                "operator": operator,
                "threshold": _round_or_none(threshold),
                "subject_value": _round_or_none(value),
                "matched_negative_rule": matched,
            }
        )

    hit_count = len(satisfied)
    total = len(feature_order)
    return {
        "hit_count": hit_count,
        "total": total,
        "hit_share": _round_or_none(hit_count / total if total else 0.0),
        "satisfied_features": satisfied,
        "unsatisfied_features": unsatisfied,
        "evaluations": evaluations,
    }


def _subject_payload(
    definition: SubjectDefinition,
    *,
    monthly_inventory: dict[str, dict[str, Any]],
    shortlist: dict[str, list[str]],
    negative_feature_order: list[str],
    negative_rules_by_feature: dict[str, dict[str, Any]],
    base_cfg: dict[str, Any],
    carrier_cfg: dict[str, Any],
    authority: ConfigAuthority,
) -> dict[str, Any]:
    _validate_shortlist_position(definition, shortlist)
    inventory_window = _subject_window(definition, monthly_inventory)
    inventory_topline_changed = _coerce_bool(
        inventory_window.get("topline_changed"),
        field_name=f"{definition.subject_id}.topline_changed",
    )
    if inventory_topline_changed:
        raise LocalPacketError(
            f"Subject {definition.subject_id} is no longer a non-divergent near-miss month"
        )

    start_date = _coerce_str(
        inventory_window.get("window_start"), field_name=f"{definition.subject_id}.window_start"
    )
    end_date = _coerce_str(
        inventory_window.get("window_end"), field_name=f"{definition.subject_id}.window_end"
    )
    expected_baseline_timestamps = tuple(
        _coerce_str(
            ts, field_name=f"{definition.subject_id}.baseline_continuation_release_timestamp"
        )
        for ts in _coerce_list(
            inventory_window.get("baseline_continuation_release_timestamps"),
            field_name=f"{definition.subject_id}.baseline_continuation_release_timestamps",
        )
    )
    expected_release_zero_timestamps = tuple(
        _coerce_str(
            ts, field_name=f"{definition.subject_id}.release_zero_continuation_release_timestamp"
        )
        for ts in _coerce_list(
            inventory_window.get("release_zero_continuation_release_timestamps"),
            field_name=f"{definition.subject_id}.release_zero_continuation_release_timestamps",
        )
    )

    baseline = _run_case(
        "baseline",
        start_date=start_date,
        end_date=end_date,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )
    release_zero = _run_case(
        "release_zero",
        start_date=start_date,
        end_date=end_date,
        base_cfg=base_cfg,
        carrier_cfg=carrier_cfg,
        authority=authority,
    )

    baseline_rows = _coerce_dict(
        baseline.pop("rows"), field_name=f"{definition.subject_id}.baseline.rows"
    )
    release_zero_rows = _coerce_dict(
        release_zero.pop("rows"), field_name=f"{definition.subject_id}.release_zero.rows"
    )
    baseline_release_rows = _coerce_dict(
        baseline.pop("continuation_release_rows"),
        field_name=f"{definition.subject_id}.baseline.continuation_release_rows",
    )
    release_zero_release_rows = _coerce_dict(
        release_zero.pop("continuation_release_rows"),
        field_name=f"{definition.subject_id}.release_zero.continuation_release_rows",
    )

    observed_baseline_timestamps = tuple(sorted(baseline_release_rows))
    observed_release_zero_timestamps = tuple(sorted(release_zero_release_rows))
    if observed_baseline_timestamps != expected_baseline_timestamps:
        raise LocalPacketError(
            f"Baseline continuation-release timestamps drifted for {definition.subject_id}: "
            f"expected={expected_baseline_timestamps}, actual={observed_baseline_timestamps}"
        )
    if observed_release_zero_timestamps != expected_release_zero_timestamps:
        raise LocalPacketError(
            f"Release-zero continuation-release timestamps drifted for {definition.subject_id}: "
            f"expected={expected_release_zero_timestamps}, actual={observed_release_zero_timestamps}"
        )

    diffs: list[dict[str, Any]] = []
    for timestamp in sorted(set(baseline_rows) | set(release_zero_rows)):
        baseline_row = baseline_rows.get(timestamp)
        release_zero_row = release_zero_rows.get(timestamp)
        if baseline_row == release_zero_row:
            continue

        baseline_debug = _coerce_optional_dict((baseline_row or {}).get("router_debug"))
        release_zero_debug = _coerce_optional_dict((release_zero_row or {}).get("router_debug"))
        continuation_release_involved = (
            baseline_debug.get("switch_control_mode") == "continuation_release"
            or release_zero_debug.get("switch_control_mode") == "continuation_release"
        )
        action_changed = (baseline_row or {}).get("action") != (release_zero_row or {}).get(
            "action"
        )
        size_changed = (baseline_row or {}).get("size") != (release_zero_row or {}).get("size")
        selected_policy_changed = baseline_debug.get("selected_policy") != release_zero_debug.get(
            "selected_policy"
        )
        switch_reason_changed = baseline_debug.get("switch_reason") != release_zero_debug.get(
            "switch_reason"
        )
        behavior_changed = _behavior_row(baseline_row) != _behavior_row(release_zero_row)
        diffs.append(
            {
                "timestamp": timestamp,
                "action_changed": action_changed,
                "size_changed": size_changed,
                "selected_policy_changed": selected_policy_changed,
                "switch_reason_changed": switch_reason_changed,
                "behavior_changed": behavior_changed,
                "continuation_release_involved": continuation_release_involved,
                "baseline": baseline_row,
                "release_zero": release_zero_row,
            }
        )

    cluster_rows = [
        _serialize_cluster_diff_row(raw_row)
        for raw_row in diffs
        if _coerce_bool(
            _coerce_dict(raw_row, field_name="diff_row").get("continuation_release_involved"),
            field_name="diff_row.continuation_release_involved",
        )
    ]
    cluster_rows = sorted(cluster_rows, key=lambda row: str(row["timestamp"]))
    if not cluster_rows:
        raise LocalPacketError(
            f"No continuation-release cluster rows materialized for {definition.subject_id}"
        )

    decisive_index, decisive_row = _first_decisive_cluster_row(cluster_rows)
    cluster_timestamps = [str(row["timestamp"]) for row in cluster_rows]
    baseline_groups = [
        _serialize_timestamp_group(group)
        for group in _group_adjacent_timestamps(list(observed_baseline_timestamps))
    ]
    release_zero_groups = [
        _serialize_timestamp_group(group)
        for group in _group_adjacent_timestamps(list(observed_release_zero_timestamps))
    ]
    union_groups = [
        _serialize_timestamp_group(group)
        for group in _group_adjacent_timestamps(cluster_timestamps)
    ]

    cluster_start = _parse_timestamp(cluster_timestamps[0])
    decisive_timestamp = _parse_timestamp(str(decisive_row["timestamp"]))
    baseline_summary = _coerce_dict(
        baseline.get("summary"), field_name=f"{definition.subject_id}.baseline.summary"
    )
    release_zero_summary = _coerce_dict(
        release_zero.get("summary"), field_name=f"{definition.subject_id}.release_zero.summary"
    )
    total_return_diff = _coerce_float(
        release_zero_summary.get("total_return"),
        field_name=f"{definition.subject_id}.release_zero.total_return",
    ) - _coerce_float(
        baseline_summary.get("total_return"),
        field_name=f"{definition.subject_id}.baseline.total_return",
    )
    final_capital_diff = _coerce_float(
        release_zero_summary.get("final_capital"),
        field_name=f"{definition.subject_id}.release_zero.final_capital",
    ) - _coerce_float(
        baseline_summary.get("final_capital"),
        field_name=f"{definition.subject_id}.baseline.final_capital",
    )
    inventory_total_return_diff = _coerce_float(
        inventory_window.get("total_return_diff"),
        field_name=f"{definition.subject_id}.inventory.total_return_diff",
    )
    inventory_final_capital_diff = _coerce_float(
        inventory_window.get("final_capital_diff"),
        field_name=f"{definition.subject_id}.inventory.final_capital_diff",
    )
    if not math.isclose(
        total_return_diff, inventory_total_return_diff, abs_tol=RETURN_DIFF_TOLERANCE
    ):
        raise LocalPacketError(
            f"Monthly total return diff drifted for {definition.subject_id}: "
            f"expected={inventory_total_return_diff}, actual={total_return_diff}"
        )
    if not math.isclose(
        final_capital_diff, inventory_final_capital_diff, abs_tol=CAPITAL_DIFF_TOLERANCE
    ):
        raise LocalPacketError(
            f"Monthly final capital diff drifted for {definition.subject_id}: "
            f"expected={inventory_final_capital_diff}, actual={final_capital_diff}"
        )

    action_edges = [
        _coerce_float(
            row["baseline_action_edge"], field_name=f"{definition.subject_id}.baseline_action_edge"
        )
        for row in cluster_rows
    ]
    confidence_gates = [
        _coerce_float(
            row["baseline_confidence_gate"],
            field_name=f"{definition.subject_id}.baseline_confidence_gate",
        )
        for row in cluster_rows
    ]
    clarity_scores = [
        _coerce_float(
            row["baseline_clarity_score"],
            field_name=f"{definition.subject_id}.baseline_clarity_score",
        )
        for row in cluster_rows
    ]

    baseline_group = baseline_groups[0]
    release_zero_group = release_zero_groups[0]
    subject_features = {
        "cluster_row_count": float(len(cluster_rows)),
        "release_retention_ratio": len(observed_release_zero_timestamps)
        / len(observed_baseline_timestamps),
        "decisive_index_within_cluster": float(decisive_index),
        "decisive_rank_pct": (
            0.0 if len(cluster_rows) == 1 else decisive_index / (len(cluster_rows) - 1)
        ),
        "decisive_hours_from_cluster_start": (decisive_timestamp - cluster_start).total_seconds()
        / 3600.0,
        "decisive_action_edge": _coerce_float(
            decisive_row["baseline_action_edge"],
            field_name=f"{definition.subject_id}.decisive_action_edge",
        ),
        "decisive_confidence_gate": _coerce_float(
            decisive_row["baseline_confidence_gate"],
            field_name=f"{definition.subject_id}.decisive_confidence_gate",
        ),
        "decisive_clarity_score": _coerce_float(
            decisive_row["baseline_clarity_score"],
            field_name=f"{definition.subject_id}.decisive_clarity_score",
        ),
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
    negative_rule_evaluation = _evaluate_negative_rules(
        subject_features,
        feature_order=negative_feature_order,
        rules_by_feature=negative_rules_by_feature,
    )

    return {
        "subject_id": definition.subject_id,
        "role": definition.role,
        "month_window": {
            "start": start_date,
            "end": end_date,
            "inventory_topline_changed": inventory_topline_changed,
            "inventory_total_return_diff": _round_or_none(inventory_total_return_diff),
            "inventory_final_capital_diff": _round_or_none(inventory_final_capital_diff),
        },
        "monthly_reproduction": {
            "top_line_sign": _sign_label(total_return_diff),
            "rerun_total_return_diff": _round_or_none(total_return_diff),
            "rerun_final_capital_diff": _round_or_none(final_capital_diff),
            "matches_inventory_total_return_diff": True,
            "matches_inventory_final_capital_diff": True,
        },
        "cluster_groups": {
            "baseline": baseline_groups,
            "release_zero": release_zero_groups,
            "union_diff_surface": union_groups,
            "baseline_minus_release_zero_span_hours": _round_or_none(
                _coerce_float(
                    baseline_group["span_hours"],
                    field_name=f"{definition.subject_id}.baseline_group.span_hours",
                )
                - _coerce_float(
                    release_zero_group["span_hours"],
                    field_name=f"{definition.subject_id}.release_zero_group.span_hours",
                )
            ),
        },
        "cluster_context": {
            "cluster_action_edge": _numeric_summary(action_edges),
            "cluster_confidence_gate": _numeric_summary(confidence_gates),
            "cluster_clarity_score": _numeric_summary(clarity_scores),
            "first_decisive_timestamp": decisive_timestamp.isoformat(),
        },
        "subject_features": {
            feature: _round_or_none(value) for feature, value in subject_features.items()
        },
        "negative_rule_evaluation": negative_rule_evaluation,
        "cluster_rows": cluster_rows,
    }


def _packet_summary(subject_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = _coerce_dict(subject_payloads.get("2021-04"), field_name="subject_payloads.2021-04")
    control = _coerce_dict(subject_payloads.get("2023-05"), field_name="subject_payloads.2023-05")
    candidate_rules = _coerce_dict(
        candidate.get("negative_rule_evaluation"), field_name="candidate.negative_rule_evaluation"
    )
    control_rules = _coerce_dict(
        control.get("negative_rule_evaluation"), field_name="control.negative_rule_evaluation"
    )
    candidate_hits = int(
        _coerce_float(candidate_rules.get("hit_count"), field_name="candidate.hit_count")
    )
    control_hits = int(
        _coerce_float(control_rules.get("hit_count"), field_name="control.hit_count")
    )
    candidate_retention = _coerce_float(
        _coerce_dict(
            candidate.get("subject_features"), field_name="candidate.subject_features"
        ).get("release_retention_ratio"),
        field_name="candidate.release_retention_ratio",
    )
    control_retention = _coerce_float(
        _coerce_dict(control.get("subject_features"), field_name="control.subject_features").get(
            "release_retention_ratio"
        ),
        field_name="control.release_retention_ratio",
    )
    candidate_span_delta = _coerce_float(
        _coerce_dict(candidate.get("cluster_groups"), field_name="candidate.cluster_groups").get(
            "baseline_minus_release_zero_span_hours"
        ),
        field_name="candidate.span_delta",
    )
    control_span_delta = _coerce_float(
        _coerce_dict(control.get("cluster_groups"), field_name="control.cluster_groups").get(
            "baseline_minus_release_zero_span_hours"
        ),
        field_name="control.span_delta",
    )

    if candidate_hits > control_hits:
        status = PACKET_STATUS_CANDIDATE_STRONGER
        inference = (
            "The first negative-like widening candidate (`2021-04`) preserves more of the frozen triad's "
            "negative local asymmetry than the first positive control (`2023-05`) when both are rerun on the "
            "same carrier. This keeps `2021-04` as the least arbitrary next local-window target."
        )
    elif candidate_hits == control_hits:
        status = PACKET_STATUS_TIED
        inference = (
            "The candidate and control hit the same number of frozen negative-rule separators, so the widening "
            "shortlist does not yet sharpen the next local-window target by decisive local structure alone."
        )
    else:
        status = PACKET_STATUS_CONTROL_STRONGER
        inference = (
            "The positive control preserves more frozen negative-rule separators than the supposed negative-like "
            "candidate, so the current shortlist ordering should not be trusted without re-framing."
        )

    return {
        "status": status,
        "candidate_subject_id": "2021-04",
        "control_subject_id": "2023-05",
        "candidate_negative_rule_hit_count": candidate_hits,
        "control_negative_rule_hit_count": control_hits,
        "candidate_release_retention_ratio": _round_or_none(candidate_retention),
        "control_release_retention_ratio": _round_or_none(control_retention),
        "candidate_span_compression_hours": _round_or_none(candidate_span_delta),
        "control_span_compression_hours": _round_or_none(control_span_delta),
        "inference": inference,
        "next_hypothesis": (
            "If this chain continues, the next honest slice is a strictly local envelope around the `2021-04` "
            "candidate cluster and the `2023-05` control cluster to test whether offsetting local outcome paths are "
            "what keep the full-month ledger flat."
        ),
    }


def _build_fail_closed_result(reason: str) -> dict[str, Any]:
    return {
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-packet-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_FAIL_CLOSED,
        "observational_only": True,
        "non_authoritative": True,
        "failure_reason": reason,
        "inputs": {
            "monthly_inventory_windows": str(MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
            "widening_candidate_inventory_artifact": str(WIDENING_CANDIDATE_INVENTORY_RELATIVE),
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
        },
    }


def run_local_packet() -> dict[str, Any]:
    monthly_inventory = _load_monthly_inventory_windows()
    shortlist = _load_shortlist()
    negative_feature_order, negative_rules_by_feature = _load_negative_rules()
    base_cfg, carrier_cfg, authority = _load_base_and_carrier_cfg()

    subject_payloads = {
        definition.subject_id: _subject_payload(
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
        "audit_version": "ri-policy-router-continuation-release-hysteresis-local-packet-2026-05-26",
        "base_sha": _git_head_sha(),
        "status": STATUS_OK,
        "observational_only": True,
        "non_authoritative": True,
        "classification_boundary": {
            "reference_surface": (
                "widening shortlist rerun as two exact full-month subjects on the same carrier, with local "
                "continuation-release clusters measured against the frozen triad's negative local rules"
            ),
            "question": (
                "When the first negative-like widening candidate (`2021-04`) and first positive control "
                "(`2023-05`) are rerun on the same carrier, does the candidate preserve more of the frozen negative "
                "triad's local asymmetry than the control?"
            ),
            "outcome_metrics_observational_only": True,
        },
        "inputs": {
            "monthly_inventory_windows": str(MONTHLY_INVENTORY_WINDOWS_RELATIVE),
            "intra_band_sign_candidates_artifact": str(INTRA_BAND_SIGN_CANDIDATES_RELATIVE),
            "widening_candidate_inventory_artifact": str(WIDENING_CANDIDATE_INVENTORY_RELATIVE),
            "carrier_path": str(CARRIER_PATH.relative_to(ROOT_DIR)),
            "working_contract_reference": str(WORKING_CONTRACT_REFERENCE),
            "subjects": [definition.subject_id for definition in SUBJECT_DEFINITIONS],
            "comparison": {
                "baseline": "enabled carrier as-is (implicit shared hysteresis)",
                "release_zero": "same enabled carrier with continuation_release_hysteresis=0",
                "variant_setting": {
                    "field": "multi_timeframe.research_policy_router.continuation_release_hysteresis",
                    "baseline": "implicit shared hysteresis",
                    "release_zero": 0,
                },
            },
        },
        "subject_payloads": subject_payloads,
        "packet_summary": _packet_summary(subject_payloads),
    }


def main() -> int:
    output_root = ROOT_DIR / OUTPUT_ROOT_RELATIVE
    output_json = output_root / OUTPUT_FILENAME
    try:
        result = run_local_packet()
    except LocalPacketError as exc:
        result = _build_fail_closed_result(str(exc))

    output_root.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "summary_artifact": str(output_json),
        "status": result.get("packet_summary", {}).get("status", result.get("status")),
        "candidate_negative_rule_hit_count": result.get("packet_summary", {}).get(
            "candidate_negative_rule_hit_count"
        ),
        "control_negative_rule_hit_count": result.get("packet_summary", {}).get(
            "control_negative_rule_hit_count"
        ),
        "candidate_subject_id": result.get("packet_summary", {}).get("candidate_subject_id"),
        "control_subject_id": result.get("packet_summary", {}).get("control_subject_id"),
        "failure_reason": result.get("failure_reason"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
