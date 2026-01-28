"""Analyze Optuna run artifacts for skipped trials and trade-level identity.

Why this exists:
- Optuna degeneracy can look like "params do nothing".
- There are two distinct failure modes:
  1) Trials are explicitly skipped (e.g. duplicate_within_run / duplicate_guard_precheck).
  2) Trials run, but params are effectively inert (e.g. missing HTF inputs) -> identical trades.

This script reads `results/hparam_search/<run_id>/trial_*.json` and corresponding
`results/backtests/<results_path>` JSON files to:
- summarize skip reasons
- compute a stable trade fingerprint and group identical outcomes
- surface HTF activation/availability signals from backtest_info

Usage (PowerShell):
  python scripts/analyze_optuna_run_identity.py --run-id run_20260108_htf_exits_50t

Exit code:
  0 always (diagnostic tool).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HYPER_DIR = PROJECT_ROOT / "results" / "hparam_search"
BACKTEST_DIR = PROJECT_ROOT / "results" / "backtests"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _trade_fingerprint(trades: list[dict[str, Any]]) -> str:
    """Compute a stable fingerprint for a trade list.

    We intentionally focus on *structural identity* (timings/reasons/side) rather than
    exact float equality. If two runs produce the same trades at the same bars, they
    should hash the same even if tiny float rounding differs.
    """

    normalized: list[list[Any]] = []
    for t in trades or []:
        normalized.append(
            [
                str(t.get("side")),
                str(t.get("entry_time")),
                str(t.get("exit_time")),
                str(t.get("exit_reason")),
                bool(t.get("is_partial")),
                _safe_float(t.get("size")),
                _safe_float(t.get("remaining_size")),
            ]
        )

    # Sort deterministically by entry/exit time then side.
    normalized.sort(key=lambda row: (row[1], row[2], row[0], row[3]))

    payload = json.dumps(normalized, separators=(",", ":"), sort_keys=False, default=str)
    return _sha256_text(payload)


def _exit_reason_counts(trades: list[dict[str, Any]]) -> dict[str, int]:
    c = Counter()
    for t in trades or []:
        c[str(t.get("exit_reason"))] += 1
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


@dataclass(frozen=True)
class TrialRow:
    trial_id: str
    skipped: bool
    reason: str | None
    results_path: str | None
    fingerprint: str | None
    num_trades: int | None
    exit_reason_counts: dict[str, int] | None
    htf: dict[str, Any] | None


def _resolve_run_dir(run_id: str | None, run_dir: str | None) -> Path:
    if run_dir:
        p = Path(run_dir)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p
    if not run_id:
        raise SystemExit("Provide --run-id or --run-dir")
    return HYPER_DIR / run_id


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--limit", type=int, default=0, help="limit number of trials printed")
    args = ap.parse_args()

    run_path = _resolve_run_dir(args.run_id, args.run_dir)
    if not run_path.exists():
        raise SystemExit(f"Run dir not found: {run_path}")

    # Only include actual trial payloads (trial_###.json), not trial_###_config.json.
    trial_files: list[Path] = []
    for p in sorted(run_path.glob("trial_*.json")):
        stem = p.stem
        if not stem.startswith("trial_"):
            continue
        # Accept exactly: trial_001.json (3 digits) and reject: trial_001_config.json
        suffix = stem.removeprefix("trial_")
        if suffix.isdigit() and len(suffix) == 3:
            trial_files.append(p)
    if not trial_files:
        raise SystemExit(f"No trial_*.json found in: {run_path}")

    rows: list[TrialRow] = []
    skip_reasons = Counter()

    for tf in trial_files:
        payload = _read_json(tf)
        # Use filename as canonical trial id (payload may contain ints like 0/1/2).
        trial_id = tf.stem
        skipped = bool(payload.get("skipped", False))
        reason = payload.get("reason")
        results_path = payload.get("results_path")

        if skipped:
            skip_reasons[str(reason)] += 1

        fp = None
        num_trades = None
        exit_counts = None
        htf_block = None

        if results_path:
            rp = Path(str(results_path))
            if not rp.is_absolute():
                bt_path_candidates = [BACKTEST_DIR / rp, run_path / rp]
            else:
                bt_path_candidates = [rp]

            bt_path = next((p for p in bt_path_candidates if p.exists()), None)
            if bt_path is not None:
                bt = _read_json(bt_path)
                trades = bt.get("trades") or []
                if isinstance(trades, list):
                    num_trades = len(trades)
                    fp = _trade_fingerprint(trades)
                    exit_counts = _exit_reason_counts(trades)
                backtest_info = bt.get("backtest_info") or {}
                htf_block = backtest_info.get("htf") if isinstance(backtest_info, dict) else None

        rows.append(
            TrialRow(
                trial_id=trial_id,
                skipped=skipped,
                reason=str(reason) if reason is not None else None,
                results_path=str(results_path) if results_path is not None else None,
                fingerprint=fp,
                num_trades=num_trades,
                exit_reason_counts=exit_counts,
                htf=htf_block,
            )
        )

    # Group identical outcomes
    groups: dict[str, list[TrialRow]] = defaultdict(list)
    for r in rows:
        if r.fingerprint:
            groups[r.fingerprint].append(r)

    identical_groups = [g for g in groups.values() if len(g) >= 2]
    identical_groups.sort(key=lambda g: (-len(g), g[0].trial_id))

    print(f"Run: {run_path}")
    print(f"Trials: {len(rows)}")

    if skip_reasons:
        print("\nSkipped trials by reason:")
        for k, v in skip_reasons.most_common():
            print(f"  - {k}: {v}")
    else:
        print("\nSkipped trials by reason: none")

    print("\nTrade-identity groups (fingerprint-based):")
    if not identical_groups:
        print("  none")
    else:
        limit = args.limit if args.limit and args.limit > 0 else None
        for idx, group in enumerate(identical_groups, start=1):
            if limit is not None and idx > limit:
                print(f"  ... (truncated; {len(identical_groups)} groups total)")
                break

            example = group[0]
            htf = example.htf or {}
            htf_summary = {
                "env_htf_exits": htf.get("env_htf_exits"),
                "use_new_exit_engine": htf.get("use_new_exit_engine"),
                "htf_candles_loaded": htf.get("htf_candles_loaded"),
                "htf_context_seen": htf.get("htf_context_seen"),
            }

            trial_ids = ", ".join(r.trial_id for r in group)
            print(f"\n  Group {idx}: {len(group)} trials")
            print(f"    trial_ids: {trial_ids}")
            print(f"    num_trades: {example.num_trades}")
            print(f"    exit_reason_counts: {example.exit_reason_counts}")
            print(f"    htf: {htf_summary}")
            # Show backtest file names to make it easy to open artifacts
            bt_files = [r.results_path for r in group if r.results_path]
            if bt_files:
                print(f"    backtests: {', '.join(bt_files)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
