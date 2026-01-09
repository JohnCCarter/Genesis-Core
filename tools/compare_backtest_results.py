from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path


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
    if isinstance(val, (int, float)):
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
