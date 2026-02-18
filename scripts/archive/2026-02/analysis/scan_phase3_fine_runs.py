#!/usr/bin/env python3
"""Scan Phase3-Fine run directories and report best-trial artifacts.

Why this exists
--------------
We sometimes need to quickly answer:
- Which *run_* directories correspond to Phase 3 Fine studies?
- Does the best-trial *results* JSON include top-level ``merged_config`` (required for drift-check)?

The script is intentionally lightweight and read-only.

Usage
-----
  python scripts/scan_phase3_fine_runs.py
  python scripts/scan_phase3_fine_runs.py --limit 200
  python scripts/scan_phase3_fine_runs.py --full-parse

Notes
-----
- Default mode avoids parsing large result JSON files. Instead it checks for the
  string '"merged_config"' within the first N bytes of the file.
- ``--full-parse`` is slower but authoritative.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Row:
    run_id: str
    study_name: str
    trials: int | None
    best_trial_id: str | None
    best_score: float | None
    best_profit_factor: float | None
    best_total_return: float | None
    best_num_trades: int | None
    results_relpath: str | None
    results_file_mb: float | None
    merged_config_present: bool | None


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _maybe_float(v: object) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _maybe_int(v: object) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def _detect_merged_config(results_file: Path, *, full_parse: bool, head_bytes: int) -> bool | None:
    if not results_file.exists():
        return None

    if full_parse:
        try:
            payload = _read_json(results_file)
        except Exception:
            return None
        return "merged_config" in payload

    try:
        with results_file.open("rb") as f:
            head = f.read(head_bytes)
    except Exception:
        return None

    return b'"merged_config"' in head


def _is_phase3_fine(study_name: str) -> bool:
    s = (study_name or "").lower()
    return ("phase3" in s) and ("fine" in s)


def _scan_run_dir(run_dir: Path, *, full_parse: bool, head_bytes: int) -> Row | None:
    meta_path = run_dir / "run_meta.json"
    best_path = run_dir / "best_trial.json"
    if not meta_path.exists() or not best_path.exists():
        return None

    try:
        meta = _read_json(meta_path)
        best = _read_json(best_path)
    except Exception:
        return None

    optuna = meta.get("optuna") or {}
    study_name = str(optuna.get("study_name") or "")
    if not _is_phase3_fine(study_name):
        return None

    trials = _maybe_int(optuna.get("n_trials"))

    best_trial_id = best.get("trial_id")
    results_relpath = best.get("results_path")

    score = None
    pf = None
    total_return = None
    num_trades = None

    score_obj = best.get("score")
    if isinstance(score_obj, dict):
        score = _maybe_float(score_obj.get("score"))
        metrics = score_obj.get("metrics") or {}
        pf = _maybe_float(metrics.get("profit_factor"))
        total_return = _maybe_float(metrics.get("total_return"))
        num_trades = _maybe_int(metrics.get("num_trades"))

    results_file_mb = None
    merged_present = None
    if results_relpath:
        results_file = run_dir / str(results_relpath)
        if results_file.exists():
            results_file_mb = round(results_file.stat().st_size / (1024 * 1024), 2)
        merged_present = _detect_merged_config(
            results_file,
            full_parse=full_parse,
            head_bytes=head_bytes,
        )

    return Row(
        run_id=run_dir.name,
        study_name=study_name,
        trials=trials,
        best_trial_id=best_trial_id,
        best_score=score,
        best_profit_factor=pf,
        best_total_return=total_return,
        best_num_trades=num_trades,
        results_relpath=results_relpath,
        results_file_mb=results_file_mb,
        merged_config_present=merged_present,
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--base-dir",
        type=Path,
        default=Path("results/hparam_search"),
        help="Base directory containing run_*/",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max number of run_* dirs to scan (newest first)",
    )
    p.add_argument(
        "--full-parse",
        action="store_true",
        help="Parse full result JSON to detect merged_config (slower)",
    )
    p.add_argument(
        "--head-bytes",
        type=int,
        default=300_000,
        help="Bytes to read in non-full-parse mode",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    base_dir: Path = args.base_dir
    if not base_dir.exists():
        print(f"[ERROR] base-dir not found: {base_dir}")
        return 2

    run_dirs = sorted(
        [p for p in base_dir.glob("run_*") if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )[: args.limit]

    rows: list[Row] = []
    for d in run_dirs:
        r = _scan_run_dir(d, full_parse=args.full_parse, head_bytes=args.head_bytes)
        if r is not None:
            rows.append(r)

    print(f"phase3_fine runs found: {len(rows)}")
    for r in rows:
        print(
            "  ".join(
                [
                    r.run_id,
                    f"trials={r.trials}",
                    f"best={r.best_trial_id}",
                    f"score={r.best_score}",
                    f"pf={r.best_profit_factor}",
                    f"ret={r.best_total_return}",
                    f"trades={r.best_num_trades}",
                    f"fileMB={r.results_file_mb}",
                    f"merged_config={r.merged_config_present}",
                ]
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
