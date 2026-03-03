from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CompareFailure(str):
    INPUT_MISSING = "INPUT_MISSING"
    INPUT_INVALID_JSON = "INPUT_INVALID_JSON"
    INPUT_INVALID_SHAPE = "INPUT_INVALID_SHAPE"
    METRIC_MISSING = "METRIC_MISSING"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True)
class CompareResult:
    status: str  # PASS|FAIL
    failure: str | None
    failures: list[str]
    baseline_metrics: dict[str, float | None]
    candidate_metrics: dict[str, float | None]
    deltas: dict[str, float | None]


@dataclass(frozen=True)
class RIOffParityResult:
    """Result for P1 OFF-mode parity attestation.

    Contract:
    - PASS only when action/reason/size mismatches are all zero
    - and no decision rows are added/missing between baseline/candidate.
    """

    parity_verdict: str  # PASS|FAIL
    action_mismatch_count: int
    reason_mismatch_count: int
    size_mismatch_count: int
    added_row_count: int
    missing_row_count: int


@dataclass(frozen=True)
class _NormalizedDecisionRow:
    row_key: str
    action: str
    reason: str
    size: float | None
    canonical_raw: str


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Missing input file: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


def _dig(obj: object, dotted_path: str) -> object:
    cur = obj
    for part in dotted_path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _as_float(val: object) -> float | None:
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, int | float):
        f = float(val)
        if math.isfinite(f):
            return f
        return None
    try:
        f = float(str(val))
    except (ValueError, TypeError):
        return None
    return f if math.isfinite(f) else None


def _extract_metrics(payload: object) -> dict[str, float | None]:
    """Extract a small, stable metric set from a backtest JSON payload.

    We intentionally keep this flexible: Genesis-Core artifacts have evolved over time.
    """

    candidates: dict[str, list[str]] = {
        "score": ["score", "summary.score", "metrics.score"],
        "total_return": [
            "total_return",
            "summary.total_return",
            "metrics.total_return",
            "metrics.total_return_pct",
        ],
        "profit_factor": ["profit_factor", "summary.profit_factor", "metrics.profit_factor"],
        "max_drawdown": [
            "max_drawdown",
            "summary.max_drawdown",
            "metrics.max_drawdown",
            "metrics.max_drawdown_pct",
        ],
        "total_trades": [
            "total_trades",
            "summary.total_trades",
            "metrics.total_trades",
            "metrics.total_trades_count",
        ],
    }

    out: dict[str, float | None] = {}
    for name, paths in candidates.items():
        val: float | None = None
        for p in paths:
            v = _dig(payload, p)
            val = _as_float(v)
            if val is not None:
                break
        out[name] = val
    return out


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _extract_decision_action(row: dict[str, Any]) -> str:
    raw = row.get("action")
    if raw is None:
        raw = row.get("side")
    return str(raw or "").strip().upper()


def _extract_decision_reason(row: dict[str, Any]) -> str:
    if "reason" in row:
        raw = row.get("reason")
    elif "reasons" in row:
        raw = row.get("reasons")
    else:
        raw = row.get("entry_reasons")

    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    return _canonical_json(raw)


def _extract_decision_row_key(row: dict[str, Any]) -> str:
    stable_fields = (
        "row_id",
        "bar_index",
        "timestamp",
        "entry_time",
        "position_id",
        "symbol",
        "timeframe",
    )

    parts: list[str] = []
    for field in stable_fields:
        value = row.get(field)
        if value is not None and value != "":
            parts.append(f"{field}={value}")
    if parts:
        return "|".join(parts)

    fallback_payload = {
        k: v
        for k, v in sorted(row.items(), key=lambda kv: kv[0])
        if k not in {"action", "side", "reason", "reasons", "entry_reasons", "size"}
    }
    if fallback_payload:
        return "payload:" + _canonical_json(fallback_payload)

    action = _extract_decision_action(row)
    reason = _extract_decision_reason(row)
    size = _as_float(row.get("size"))
    return "value:" + _canonical_json({"action": action, "reason": reason, "size": size})


def _normalize_decision_rows(rows: list[dict[str, Any]]) -> list[_NormalizedDecisionRow]:
    out: list[_NormalizedDecisionRow] = []
    for row in rows:
        canonical_raw = _canonical_json(row)
        out.append(
            _NormalizedDecisionRow(
                row_key=_extract_decision_row_key(row),
                action=_extract_decision_action(row),
                reason=_extract_decision_reason(row),
                size=_as_float(row.get("size")),
                canonical_raw=canonical_raw,
            )
        )
    return out


def _normalized_row_sort_key(row: _NormalizedDecisionRow) -> tuple[str, str, str, str]:
    size_key = "" if row.size is None else f"{row.size:.17g}"
    return (row.action, row.reason, size_key, row.canonical_raw)


def compare_ri_p1_off_parity_rows(
    *,
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    size_tolerance: float = 1e-12,
) -> RIOffParityResult:
    """Compare decision rows for locked RI P1 OFF-mode parity contract.

    Matching strategy:
    - Rows are grouped by deterministic row key.
    - Within each key group, rows are sorted canonically to avoid order-only noise.
    """

    if size_tolerance < 0:
        raise ValueError("size_tolerance must be >= 0")

    baseline_norm = _normalize_decision_rows(baseline_rows)
    candidate_norm = _normalize_decision_rows(candidate_rows)

    baseline_map: dict[str, list[_NormalizedDecisionRow]] = defaultdict(list)
    candidate_map: dict[str, list[_NormalizedDecisionRow]] = defaultdict(list)
    for row in baseline_norm:
        baseline_map[row.row_key].append(row)
    for row in candidate_norm:
        candidate_map[row.row_key].append(row)

    action_mismatch_count = 0
    reason_mismatch_count = 0
    size_mismatch_count = 0
    added_row_count = 0
    missing_row_count = 0

    for key in sorted(set(baseline_map) | set(candidate_map)):
        b_rows = sorted(baseline_map.get(key, []), key=_normalized_row_sort_key)
        c_rows = sorted(candidate_map.get(key, []), key=_normalized_row_sort_key)

        max_len = max(len(b_rows), len(c_rows))
        for idx in range(max_len):
            if idx >= len(b_rows):
                added_row_count += 1
                continue
            if idx >= len(c_rows):
                missing_row_count += 1
                continue

            b_row = b_rows[idx]
            c_row = c_rows[idx]

            if b_row.action != c_row.action:
                action_mismatch_count += 1
            if b_row.reason != c_row.reason:
                reason_mismatch_count += 1

            if b_row.size is None or c_row.size is None:
                size_mismatch_count += 1
            elif abs(c_row.size - b_row.size) > size_tolerance:
                size_mismatch_count += 1

    parity_pass = (
        action_mismatch_count == 0
        and reason_mismatch_count == 0
        and size_mismatch_count == 0
        and added_row_count == 0
        and missing_row_count == 0
    )

    return RIOffParityResult(
        parity_verdict="PASS" if parity_pass else "FAIL",
        action_mismatch_count=action_mismatch_count,
        reason_mismatch_count=reason_mismatch_count,
        size_mismatch_count=size_mismatch_count,
        added_row_count=added_row_count,
        missing_row_count=missing_row_count,
    )


def build_ri_p1_off_parity_artifact(
    *,
    run_id: str,
    git_sha: str,
    symbols: list[str],
    timeframes: list[str],
    start_utc: str,
    end_utc: str,
    baseline_artifact_ref: str,
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    mode: str = "OFF",
    window_spec_id: str = "ri_p1_off_parity_v1",
    size_tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Build machine-readable P1 OFF parity evidence artifact payload."""

    if mode != "OFF":
        raise ValueError("P1 parity artifact mode must be OFF")
    if not run_id.strip():
        raise ValueError("run_id must be non-empty")
    if not git_sha.strip():
        raise ValueError("git_sha must be non-empty")
    if not baseline_artifact_ref.strip():
        raise ValueError("baseline_artifact_ref must be non-empty")

    parity = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        size_tolerance=size_tolerance,
    )

    return {
        "window_spec_id": window_spec_id,
        "run_id": run_id,
        "git_sha": git_sha,
        "mode": mode,
        "symbols": list(symbols),
        "timeframes": list(timeframes),
        "start_utc": start_utc,
        "end_utc": end_utc,
        "baseline_artifact_ref": baseline_artifact_ref,
        "parity_verdict": parity.parity_verdict,
        "action_mismatch_count": parity.action_mismatch_count,
        "reason_mismatch_count": parity.reason_mismatch_count,
        "size_mismatch_count": parity.size_mismatch_count,
        "size_tolerance": f"{size_tolerance:.0e}",
        "added_row_count": parity.added_row_count,
        "missing_row_count": parity.missing_row_count,
    }


def compare_backtest_payloads(
    *,
    baseline: object,
    candidate: object,
    mode: str = "strict",
) -> CompareResult:
    """Compare two backtest payloads.

    Modes:
      - strict: require non-regression on core metrics when present
      - report: never fails for regressions; still fails for invalid inputs
    """

    if not isinstance(baseline, dict) or not isinstance(candidate, dict):
        return CompareResult(
            status="FAIL",
            failure=CompareFailure.INPUT_INVALID_SHAPE,
            failures=["baseline and candidate must be JSON objects"],
            baseline_metrics={},
            candidate_metrics={},
            deltas={},
        )

    b = _extract_metrics(baseline)
    c = _extract_metrics(candidate)

    deltas: dict[str, float | None] = {}
    for k in sorted(set(b) | set(c)):
        bv = b.get(k)
        cv = c.get(k)
        if bv is None or cv is None:
            deltas[k] = None
        else:
            deltas[k] = cv - bv

    failures: list[str] = []

    missing = [k for k, v in b.items() if v is None] + [k for k, v in c.items() if v is None]
    if missing:
        failures.append("missing_metrics=" + ",".join(sorted(set(missing))))

    if mode not in {"strict", "report"}:
        failures.append(f"unknown mode: {mode!r}")

    if failures and any(f.startswith("unknown mode") for f in failures):
        return CompareResult(
            status="FAIL",
            failure=CompareFailure.INPUT_INVALID_SHAPE,
            failures=failures,
            baseline_metrics=b,
            candidate_metrics=c,
            deltas=deltas,
        )

    if mode == "strict":
        # Only enforce regressions for metrics that exist in both payloads.
        def _regress(name: str, ok: bool, *, reason: str) -> None:
            if not ok:
                failures.append(f"regression:{name}:{reason}")

        if b.get("profit_factor") is not None and c.get("profit_factor") is not None:
            _regress("profit_factor", c["profit_factor"] >= b["profit_factor"], reason="lower")

        if b.get("score") is not None and c.get("score") is not None:
            _regress("score", c["score"] >= b["score"], reason="lower")

        if b.get("total_return") is not None and c.get("total_return") is not None:
            _regress("total_return", c["total_return"] >= b["total_return"], reason="lower")

        if b.get("max_drawdown") is not None and c.get("max_drawdown") is not None:
            _regress("max_drawdown", c["max_drawdown"] <= b["max_drawdown"], reason="higher")

        if b.get("total_trades") is not None and c.get("total_trades") is not None:
            _regress("total_trades", c["total_trades"] >= b["total_trades"], reason="lower")

    if failures and any(f.startswith("regression:") for f in failures):
        return CompareResult(
            status="FAIL",
            failure=CompareFailure.REGRESSION,
            failures=failures,
            baseline_metrics=b,
            candidate_metrics=c,
            deltas=deltas,
        )

    # Missing metrics are reported but do not fail in strict mode unless we also had regressions.
    return CompareResult(
        status="PASS",
        failure=None,
        failures=failures,
        baseline_metrics=b,
        candidate_metrics=c,
        deltas=deltas,
    )


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("baseline", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--mode", default="strict", choices=["strict", "report"])
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON result")
    args = p.parse_args(argv)

    try:
        baseline = _load_json(args.baseline)
        candidate = _load_json(args.candidate)
    except FileNotFoundError as e:
        out = {"status": "FAIL", "failure": CompareFailure.INPUT_MISSING, "message": str(e)}
        print(json.dumps(out, sort_keys=True))
        return 2
    except ValueError as e:
        out = {"status": "FAIL", "failure": CompareFailure.INPUT_INVALID_JSON, "message": str(e)}
        print(json.dumps(out, sort_keys=True))
        return 2

    result = compare_backtest_payloads(baseline=baseline, candidate=candidate, mode=args.mode)

    payload = {
        "status": result.status,
        "failure": result.failure,
        "failures": result.failures,
        "baseline_metrics": result.baseline_metrics,
        "candidate_metrics": result.candidate_metrics,
        "deltas": result.deltas,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"[COMPARE] {result.status}")
        if result.failure:
            print(f"[COMPARE] failure={result.failure}")
        if result.failures:
            for f in result.failures:
                print(f"- {f}")
        for k in sorted(result.deltas):
            print(
                f"{k}: {result.baseline_metrics.get(k)} -> {result.candidate_metrics.get(k)} (Δ={result.deltas[k]})"
            )

    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
