#!/usr/bin/env python3
"""Sanity check: verifiera att trial_config == backtest-results merged_config.

Syfte:
- Upptäcka config-drift mellan Optuna/runner-trials och faktiska backtest-resultat.
- Verifiera att subprocess-backtests inte råkar re-merga runtime.json när trial_config redan är "complete".

Exempel:
  python scripts/check_trial_config_equivalence.py --run-dir results/hparam_search/run_20251201_123456 --trial-id trial_001
  python scripts/check_trial_config_equivalence.py --run-dir results/hparam_search/run_20251201_123456 --all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.utils.diffing.config_equivalence import compare_trial_config_to_results  # noqa: E402


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_results_file(run_dir: Path, results_path: str) -> Path:
    """Resolve the results JSON path for a trial.

    Subprocess runs write under results/backtests/.
    Direct-execution runs may write under the run_dir itself.
    """

    p = Path(results_path)
    if p.is_absolute():
        return p

    candidates = [
        ROOT_DIR / "results" / "backtests" / p,
        run_dir / p,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _iter_trial_ids(run_dir: Path) -> list[str]:
    # Only accept trial summary files like trial_001.json; exclude e.g. trial_001_config.json.
    return sorted(p.stem for p in run_dir.glob("trial_[0-9][0-9][0-9].json"))


def _check_one(run_dir: Path, trial_id: str, *, precision: int, max_diffs: int) -> tuple[bool, str]:
    trial_path = run_dir / f"{trial_id}.json"
    if not trial_path.exists():
        return False, f"[ERROR] Saknar trial-fil: {trial_path}"

    trial_payload = _read_json(trial_path)

    # Skip trials that never produced results
    if trial_payload.get("skipped") is True:
        reason = trial_payload.get("reason")
        return True, f"[SKIP] {trial_id} (skipped: {reason})"

    results_path = trial_payload.get("results_path")
    if not results_path:
        return False, f"[ERROR] {trial_id} saknar results_path"

    results_file = _resolve_results_file(run_dir, str(results_path))
    if not results_file.exists():
        return False, f"[ERROR] {trial_id} results saknas: {results_file}"

    config_path = trial_payload.get("config_path") or f"{trial_id}_config.json"
    config_file = run_dir / str(config_path)
    if not config_file.exists():
        return False, f"[ERROR] {trial_id} config saknas: {config_file}"

    trial_config_payload = _read_json(config_file)
    results_payload = _read_json(results_file)

    ok, report = compare_trial_config_to_results(
        trial_config_payload,
        results_payload,
        precision=precision,
        max_diffs=max_diffs,
    )

    if ok:
        return True, f"[OK] {trial_id} ({results_file.name})"

    lines = [
        f"[MISMATCH] {trial_id} ({results_file.name})",
        f"  issues: {report.get('issues')}",
        f"  fp(trial)={report.get('fingerprints', {}).get('trial')}",
        f"  fp(results)={report.get('fingerprints', {}).get('results')}",
    ]
    diffs = report.get("diffs") or []
    if diffs:
        lines.append("  diffs:")
        for d in diffs[:max_diffs]:
            lines.append(
                f"    - {d.get('path')}: trial={d.get('trial')} results={d.get('results')}"
            )
        if report.get("diffs_truncated"):
            lines.append(f"    (truncated to first {max_diffs} diffs)")

    return False, "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="results/hparam_search/run_*/")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--trial-id", type=str, help="e.g. trial_001")
    group.add_argument("--all", action="store_true", help="check all trial_*.json in run-dir")
    parser.add_argument("--precision", type=int, default=6, help="float rounding precision")
    parser.add_argument("--max-diffs", type=int, default=30, help="max diffs to print per mismatch")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    run_dir: Path = args.run_dir

    if not run_dir.exists():
        print(f"[ERROR] run-dir finns inte: {run_dir}")
        return 2

    if args.all or not args.trial_id:
        trial_ids = _iter_trial_ids(run_dir)
        if not trial_ids:
            print(f"[ERROR] Inga trial_*.json hittades i: {run_dir}")
            return 2
    else:
        trial_ids = [args.trial_id]

    any_fail = False
    for trial_id in trial_ids:
        ok, msg = _check_one(run_dir, trial_id, precision=args.precision, max_diffs=args.max_diffs)
        print(msg)
        if not ok:
            any_fail = True

    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
