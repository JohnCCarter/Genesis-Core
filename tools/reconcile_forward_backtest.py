"""Forward-vs-backtest reconciliation harness (Phase 3).

Aligns forward (paper-trading) decision rows against backtest decision rows by
a deterministic key (timestamp + symbol + timeframe) and classifies each pair so
we can answer the only question that matters for an unproven edge: *does the live
path do what the backtest said it would?*

This is deliberately measurement-honest:
  - It does not invent fills or prices.
  - It reports divergence rather than smoothing it.
  - A high FORWARD_ONLY / ACTION_DRIFT count is a red flag that backtest results
    do not transfer to live-paper, which is exactly the Phase 1-4 thesis
    (EDGE_MAP=UNRESOLVED) made checkable.

Row schema (either JSON array or NDJSON), per decision:
  {
    "timestamp": <int ms | iso str>,   # bar close time, required for alignment
    "symbol":    "tBTCUSD",            # optional but recommended
    "timeframe": "1h",                 # optional but recommended
    "action":    "LONG"|"SHORT"|"NONE",
    "size":      0.005,                 # optional (BTC)
    "price":     98000.0                # optional (fill/decision price) -> slippage
  }
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Per-pair classification labels.
MATCH = "MATCH"
ACTION_DRIFT = "ACTION_DRIFT"
SIZE_DRIFT = "SIZE_DRIFT"
PRICE_SLIPPAGE = "PRICE_SLIPPAGE"
FORWARD_ONLY = "FORWARD_ONLY"
BACKTEST_ONLY = "BACKTEST_ONLY"


@dataclass(frozen=True)
class _Row:
    key: str
    action: str
    size: float | None
    price: float | None


@dataclass(frozen=True)
class PairOutcome:
    key: str
    label: str
    backtest_action: str | None
    forward_action: str | None
    size_delta: float | None
    slippage_bps: float | None


@dataclass(frozen=True)
class ReconcileResult:
    total_keys: int
    counts: dict[str, int]
    fidelity_ratio: float  # MATCH / total_keys (1.0 == perfect transfer)
    mean_abs_slippage_bps: float | None
    outcomes: list[PairOutcome] = field(default_factory=list)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    """Load decision rows from a JSON-array file or an NDJSON file."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Missing input file: {path}") from e

    try:
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Row file must be a JSON array of objects: {path}")
        if any(not isinstance(row, dict) for row in payload):
            raise ValueError(f"Row file contains non-object entries: {path}")
        return payload
    except json.JSONDecodeError:
        pass

    rows: list[dict[str, Any]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        raw = line.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid NDJSON in {path} at line {idx}: {e}") from e
        if not isinstance(row, dict):
            raise ValueError(f"NDJSON row must be an object in {path} at line {idx}")
        rows.append(row)

    if rows:
        return rows
    raise ValueError(f"Could not parse row file as JSON array or NDJSON: {path}")


def _as_float(val: object) -> float | None:
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, int | float):
        f = float(val)
        return f if math.isfinite(f) else None
    try:
        f = float(str(val))
    except (ValueError, TypeError):
        return None
    return f if math.isfinite(f) else None


def _action(row: dict[str, Any]) -> str:
    raw = row.get("action")
    if raw is None:
        raw = row.get("side")
    return str(raw or "NONE").strip().upper() or "NONE"


def _key(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for field_name in ("timestamp", "entry_time", "bar_index"):
        value = row.get(field_name)
        if value is not None and value != "":
            parts.append(f"ts={value}")
            break
    for field_name in ("symbol", "timeframe"):
        value = row.get(field_name)
        if value is not None and value != "":
            parts.append(f"{field_name}={value}")
    if not parts:
        raise ValueError(f"Row lacks an alignable key (need timestamp): {row!r}")
    return "|".join(parts)


def _normalize(rows: list[dict[str, Any]]) -> list[_Row]:
    return [
        _Row(key=_key(r), action=_action(r), size=_as_float(r.get("size")), price=_as_float(r.get("price")))
        for r in rows
    ]


def reconcile(
    *,
    backtest_rows: list[dict[str, Any]],
    forward_rows: list[dict[str, Any]],
    size_tolerance: float = 1e-9,
    slippage_tolerance_bps: float = 5.0,
) -> ReconcileResult:
    """Align forward rows to backtest rows by key and classify each pair.

    Precedence per matched key: ACTION_DRIFT > SIZE_DRIFT > PRICE_SLIPPAGE > MATCH.
    Unmatched keys are FORWARD_ONLY or BACKTEST_ONLY.
    """
    if size_tolerance < 0 or slippage_tolerance_bps < 0:
        raise ValueError("tolerances must be >= 0")

    bt = {r.key: r for r in _normalize(backtest_rows)}
    fw = {r.key: r for r in _normalize(forward_rows)}

    counts: dict[str, int] = defaultdict(int)
    outcomes: list[PairOutcome] = []
    slippages: list[float] = []

    for key in sorted(set(bt) | set(fw)):
        b = bt.get(key)
        f = fw.get(key)

        if b is None:
            counts[FORWARD_ONLY] += 1
            outcomes.append(PairOutcome(key, FORWARD_ONLY, None, f.action, None, None))
            continue
        if f is None:
            counts[BACKTEST_ONLY] += 1
            outcomes.append(PairOutcome(key, BACKTEST_ONLY, b.action, None, None, None))
            continue

        size_delta = None
        if b.size is not None and f.size is not None:
            size_delta = f.size - b.size

        slippage_bps = None
        if b.price is not None and f.price is not None and b.price != 0:
            slippage_bps = (f.price - b.price) / b.price * 10_000.0
            slippages.append(abs(slippage_bps))

        if b.action != f.action:
            label = ACTION_DRIFT
        elif size_delta is not None and abs(size_delta) > size_tolerance:
            label = SIZE_DRIFT
        elif slippage_bps is not None and abs(slippage_bps) > slippage_tolerance_bps:
            label = PRICE_SLIPPAGE
        else:
            label = MATCH

        counts[label] += 1
        outcomes.append(PairOutcome(key, label, b.action, f.action, size_delta, slippage_bps))

    total = len(set(bt) | set(fw))
    fidelity = (counts.get(MATCH, 0) / total) if total else 1.0
    mean_slip = (sum(slippages) / len(slippages)) if slippages else None

    return ReconcileResult(
        total_keys=total,
        counts={k: counts[k] for k in sorted(counts)},
        fidelity_ratio=fidelity,
        mean_abs_slippage_bps=mean_slip,
        outcomes=outcomes,
    )


def build_artifact(result: ReconcileResult, *, run_id: str, max_detail: int = 200) -> dict[str, Any]:
    """Build a machine-readable reconciliation artifact payload."""
    return {
        "run_id": run_id,
        "total_keys": result.total_keys,
        "counts": result.counts,
        "fidelity_ratio": round(result.fidelity_ratio, 6),
        "mean_abs_slippage_bps": (
            round(result.mean_abs_slippage_bps, 4) if result.mean_abs_slippage_bps is not None else None
        ),
        "divergences": [
            {
                "key": o.key,
                "label": o.label,
                "backtest_action": o.backtest_action,
                "forward_action": o.forward_action,
                "size_delta": o.size_delta,
                "slippage_bps": (round(o.slippage_bps, 4) if o.slippage_bps is not None else None),
            }
            for o in result.outcomes
            if o.label != MATCH
        ][:max_detail],
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Reconcile forward (paper) vs backtest decision rows")
    p.add_argument("backtest", type=Path, help="Backtest decision rows (JSON array or NDJSON)")
    p.add_argument("forward", type=Path, help="Forward/paper decision rows (JSON array or NDJSON)")
    p.add_argument("--run-id", default="adhoc")
    p.add_argument("--size-tolerance", type=float, default=1e-9)
    p.add_argument("--slippage-tolerance-bps", type=float, default=5.0)
    p.add_argument("--artifact-out", type=Path, default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        backtest_rows = _load_rows(args.backtest)
        forward_rows = _load_rows(args.forward)
        result = reconcile(
            backtest_rows=backtest_rows,
            forward_rows=forward_rows,
            size_tolerance=args.size_tolerance,
            slippage_tolerance_bps=args.slippage_tolerance_bps,
        )
    except FileNotFoundError as e:
        print(json.dumps({"status": "FAIL", "failure": "INPUT_MISSING", "message": str(e)}))
        return 2
    except ValueError as e:
        print(json.dumps({"status": "FAIL", "failure": "INPUT_INVALID", "message": str(e)}))
        return 2

    artifact = build_artifact(result, run_id=args.run_id)

    if args.artifact_out is not None:
        args.artifact_out.parent.mkdir(parents=True, exist_ok=True)
        args.artifact_out.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    if args.json:
        print(json.dumps(artifact, indent=2, sort_keys=True))
    else:
        print(f"[RECONCILE] fidelity={result.fidelity_ratio:.3f} over {result.total_keys} keys")
        for label in sorted(result.counts):
            print(f"  {label}: {result.counts[label]}")
        if result.mean_abs_slippage_bps is not None:
            print(f"  mean_abs_slippage_bps: {result.mean_abs_slippage_bps:.2f}")
        if args.artifact_out is not None:
            print(f"[RECONCILE] artifact={args.artifact_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
