"""Audit Optuna objective parity against saved trial payloads.

Why this exists
--------------
We have several early-return paths inside the Optuna objective:
- from_cache reuse
- skipped trials (duplicate/zero_trade_preflight/already_completed)
- pruned/error
- soft-constraints (score minus penalty)
- abort-by-heuristic (post-backtest)

If any path unintentionally returns a different numeric value than the payload implies,
Optuna can optimize a number that cannot be reproduced from the artifacts, which feels
like "inconsistent pipeline".

This script compares:
- Optuna's stored trial.value
vs
- an "expected" value derived from our saved trial_*.json payloads using the same policy.

Usage
-----
python scripts/audit_optuna_objective_parity.py --run-id run_20251226_173828
python scripts/audit_optuna_objective_parity.py --run-dir results/hparam_search/run_20251226_173828

Exit codes
----------
0: No mismatches found
2: Mismatches found
3: Could not load study or artifacts
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Mismatch:
    trial_number: int
    optuna_value: float | None
    expected_value: float | None
    delta: float | None
    payload_path: Path
    reason: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_repo_root() -> Path:
    # scripts/ is at repo root in this project.
    return Path(__file__).resolve().parents[1]


def _resolve_run_dir(repo_root: Path, run_id: str | None, run_dir: str | None) -> Path:
    if run_dir:
        return (repo_root / run_dir).resolve()
    if not run_id:
        raise ValueError("Provide --run-id or --run-dir")
    return (repo_root / "results" / "hparam_search" / run_id).resolve()


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_payload_score(payload: dict[str, Any]) -> float:
    score_block = payload.get("score") or {}
    if isinstance(score_block, dict):
        val = _coerce_float(score_block.get("score"))
        if val is not None:
            return val
    return 0.0


def _expected_objective_value(
    payload: dict[str, Any],
    *,
    constraint_soft_penalty: float = 150.0,
) -> tuple[float | None, str]:
    """Compute the expected Optuna objective return value for a saved payload.

    Returns: (expected_value, label)

    expected_value is None for pruned/error trials.
    """

    if payload.get("from_cache"):
        return _extract_payload_score(payload), "from_cache"

    if payload.get("skipped"):
        reason = str(payload.get("reason") or "")
        if reason == "duplicate_within_run":
            # Objective returns -1e6 unless score_memory has it; we cannot reconstruct score_memory
            # post-hoc deterministically, so we treat this as expected=-1e6.
            return -1e6, "skipped:duplicate_within_run"
        if reason == "zero_trade_preflight":
            return _extract_payload_score(payload), "skipped:zero_trade_preflight"
        return _extract_payload_score(payload), f"skipped:{reason or 'unknown'}"

    if payload.get("error"):
        # Objective raises TrialPruned.
        return None, f"error:{payload.get('error')}"

    constraints = payload.get("constraints") or {}
    score_value = _extract_payload_score(payload)

    if not constraints.get("ok", True):
        reasons = constraints.get("reasons")
        is_abort_heuristic = bool(payload.get("abort_reason")) or (
            isinstance(reasons, list) and "aborted_by_heuristic" in reasons
        )
        if is_abort_heuristic:
            return score_value, "constraints:aborted_by_heuristic"
        return score_value - float(constraint_soft_penalty), "constraints:soft_fail"

    return score_value, "ok"


def _load_optuna_study(storage: str, study_name: str):
    try:
        import optuna
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Optuna is not installed") from exc

    return optuna.load_study(study_name=study_name, storage=storage)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", type=str, default=None)
    parser.add_argument("--run-dir", type=str, default=None)
    parser.add_argument("--eps", type=float, default=1e-9)
    parser.add_argument(
        "--constraint-soft-penalty",
        type=float,
        default=150.0,
        help="Must match GENESIS_CONSTRAINT_SOFT_PENALTY if you override it.",
    )

    args = parser.parse_args()

    repo_root = _find_repo_root()
    run_dir_path = _resolve_run_dir(repo_root, args.run_id, args.run_dir)

    run_meta_path = run_dir_path / "run_meta.json"
    if not run_meta_path.exists():
        print(f"[ERROR] Missing run_meta.json: {run_meta_path}")
        return 3

    run_meta = _load_json(run_meta_path)
    raw_meta = run_meta.get("raw_meta") or {}
    runs = raw_meta.get("runs") or {}
    optuna_cfg = runs.get("optuna") or {}

    storage = optuna_cfg.get("storage")
    study_name = optuna_cfg.get("study_name")

    if not storage or not study_name:
        print("[ERROR] run_meta.json missing raw_meta.runs.optuna.storage/study_name")
        return 3

    try:
        study = _load_optuna_study(storage=str(storage), study_name=str(study_name))
    except Exception as exc:
        print(f"[ERROR] Could not load Optuna study: {exc}")
        return 3

    mismatches: list[Mismatch] = []
    audited = 0
    pruned = 0

    for t in study.trials:
        trial_number = int(t.number)
        # Our local artifacts are 1-indexed: trial_001.json corresponds to optuna trial 0.
        payload_path = run_dir_path / f"trial_{trial_number + 1:03d}.json"
        if not payload_path.exists():
            continue

        payload = _load_json(payload_path)
        expected_value, label = _expected_objective_value(
            payload,
            constraint_soft_penalty=float(args.constraint_soft_penalty),
        )
        optuna_value = _coerce_float(t.value)

        audited += 1

        if expected_value is None:
            pruned += 1
            continue

        if optuna_value is None:
            mismatches.append(
                Mismatch(
                    trial_number=trial_number,
                    optuna_value=optuna_value,
                    expected_value=expected_value,
                    delta=None,
                    payload_path=payload_path,
                    reason=f"optuna_value=None expected={expected_value} ({label})",
                )
            )
            continue

        delta = optuna_value - expected_value
        if not math.isfinite(delta) or abs(delta) > float(args.eps):
            mismatches.append(
                Mismatch(
                    trial_number=trial_number,
                    optuna_value=optuna_value,
                    expected_value=expected_value,
                    delta=delta,
                    payload_path=payload_path,
                    reason=label,
                )
            )

    print(f"[OK] Run dir: {run_dir_path}")
    print(f"[OK] Study: {study.study_name} ({storage})")
    print(f"[OK] Audited trials with payloads: {audited}")
    print(f"[OK] Pruned/error payloads: {pruned}")

    if not mismatches:
        print("[OK] No objective mismatches found")
        return 0

    print(f"[WARN] Objective mismatches: {len(mismatches)}")
    for m in sorted(mismatches, key=lambda x: abs(x.delta or 0.0), reverse=True)[:25]:
        print(
            f"- trial={m.trial_number:4d} optuna={m.optuna_value} expected={m.expected_value} "
            f"delta={m.delta} reason={m.reason} file={m.payload_path.name}"
        )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
