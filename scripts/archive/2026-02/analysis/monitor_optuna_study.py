#!/usr/bin/env python3
"""Lightweight monitor for an Optuna study.

Purpose:
- Periodically prints and (optionally) appends a one-line status snapshot for a study.
- Safe to run alongside an active optimization (read-only).

Example:
  python scripts/monitor_optuna_study.py \\
    --storage "sqlite:///results/hparam_search/storage/optuna_phase3_fine_v7_long_v2_until_20251222.db" \\
    --study-name "optuna_phase3_fine_v7_long_v2_until_20251222" \\
    --interval 300 \\
    --log-file "logs/optuna_monitor_phase3_fine_v7_long_20251218.log"
"""

from __future__ import annotations

import argparse
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import optuna


def _format_counts(counts: Counter[str]) -> str:
    keys = ["COMPLETE", "PRUNED", "FAIL", "RUNNING", "WAITING"]
    return " ".join(f"{k.lower()}={counts.get(k, 0)}" for k in keys)


def _snapshot(storage: str, study_name: str) -> str:
    ts_local = datetime.now().astimezone().isoformat(timespec="seconds")
    ts_utc = datetime.now(UTC).isoformat(timespec="seconds")

    try:
        study = optuna.load_study(study_name=study_name, storage=storage)
    except KeyError:
        # Study may not exist yet if the optimizer hasn't created it.
        return (
            f"{ts_local} ({ts_utc}Z) waiting_for_study=1 study_name={study_name} "
            f"storage={storage}"
        )
    trials = study.get_trials(deepcopy=False)

    counts: Counter[str] = Counter()
    last_number: int | None = None
    last_state: str | None = None

    for t in trials:
        state_name = getattr(t.state, "name", str(t.state))
        counts[state_name] += 1
        if last_number is None or t.number > last_number:
            last_number = t.number
            last_state = state_name

    try:
        best_value = study.best_value
        best_number = study.best_trial.number
    except Exception:  # noqa: BLE001 - best_value can raise if no COMPLETE trials yet
        best_value = None
        best_number = None

    best_part = "best=None" if best_value is None else f"best={best_value:.6f}"
    best_num_part = "" if best_number is None else f" best_trial={best_number}"

    last_part = "" if last_number is None else f" last_trial={last_number}({last_state})"

    return (
        f"{ts_local} ({ts_utc}Z) trials={len(trials)} {_format_counts(counts)} "
        f"{best_part}{best_num_part}{last_part}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor an Optuna study (read-only).")
    parser.add_argument(
        "--storage", required=True, help="Optuna storage URL (e.g., sqlite:///path.db)"
    )
    parser.add_argument("--study-name", required=True, help="Optuna study name")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between snapshots")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional log file to append")
    parser.add_argument("--once", action="store_true", help="Print a single snapshot and exit")
    args = parser.parse_args()

    if args.interval < 1:
        raise SystemExit("--interval must be >= 1")

    if args.log_file is not None:
        args.log_file.parent.mkdir(parents=True, exist_ok=True)

    while True:
        line = _snapshot(args.storage, args.study_name)
        print(line, flush=True)
        if args.log_file is not None:
            with args.log_file.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

        if args.once:
            return 0

        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
