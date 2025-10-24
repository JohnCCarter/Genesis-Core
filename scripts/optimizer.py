"""Optimizer CLI helpers (Phase-7)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results" / "hparam_search"


def _coerce_trial_fields(trial: dict[str, Any]) -> dict[str, Any]:
    for key, caster in (("duration_seconds", float), ("attempts", int)):
        value = trial.get(key)
        if value is None:
            continue
        try:
            trial[key] = caster(value)
        except (TypeError, ValueError):
            trial.pop(key, None)
    return trial


def _format_trial_summary(idx: int, entry: dict[str, Any]) -> str:
    metrics = entry.get("metrics") or {}
    parts = [
        f"{idx}. {entry.get('trial_id')}",
        f"score={entry.get('score')}",
        f"sharpe={metrics.get('sharpe_ratio')}",
        f"trades={metrics.get('num_trades')}",
    ]
    duration = entry.get("duration_seconds")
    attempts = entry.get("attempts")
    if duration is not None:
        parts.append(f"duration={duration:.1f}s")
    if attempts is not None:
        parts.append(f"attempts={attempts}")
    return "  " + " ".join(parts)


def summarize_run(run_id: str) -> dict[str, Any]:
    run_dir = (RESULTS_DIR / run_id).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    meta_path = run_dir / "run_meta.json"
    meta: dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {meta_path}") from exc

    trials: list[dict[str, Any]] = []
    for path in sorted(run_dir.glob("trial_*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(raw, dict):
            trial = dict(raw)
            trial["trial_file"] = path.name
            trials.append(_coerce_trial_fields(trial))

    total = len(trials)
    skipped = sum(1 for t in trials if t.get("skipped"))
    failed = sum(1 for t in trials if t.get("error"))
    completed = total - skipped

    valid_trials: list[dict[str, Any]] = []
    for trial in trials:
        score_block = trial.get("score") or {}
        constraints_block = trial.get("constraints") or {}
        hard_failures = list(score_block.get("hard_failures") or [])
        constraints_ok = bool(constraints_block.get("ok"))
        if hard_failures or not constraints_ok:
            continue
        try:
            score_value = float(score_block.get("score"))
        except (TypeError, ValueError):
            continue
        metrics = dict(score_block.get("metrics") or {})
        valid_trials.append(
            {
                "trial_id": trial.get("trial_id"),
                "trial_file": trial.get("trial_file"),
                "results_path": trial.get("results_path"),
                "score": score_value,
                "metrics": metrics,
                "parameters": trial.get("parameters") or {},
                "duration_seconds": trial.get("duration_seconds"),
                "attempts": trial.get("attempts"),
                "raw": trial,
            }
        )

    valid_trials.sort(key=lambda item: item["score"], reverse=True)

    return {
        "meta": meta,
        "run_dir": str(run_dir),
        "counts": {
            "total": total,
            "skipped": skipped,
            "failed": failed,
            "completed": completed,
            "valid": len(valid_trials),
        },
        "best_trial": valid_trials[0] if valid_trials else None,
        "valid_trials": valid_trials,
        "trials": trials,
    }


def _print_summary(data: dict[str, Any], *, top_n: int) -> None:
    meta = data.get("meta") or {}
    counts = data.get("counts") or {}
    valid_trials = data.get("valid_trials") or []
    all_trials = data.get("trials") or []
    total_duration = sum(float(trial.get("duration_seconds") or 0.0) for trial in all_trials)
    completed_trials = [
        trial for trial in all_trials if not trial.get("skipped") and trial.get("duration_seconds")
    ]
    avg_duration = total_duration / len(completed_trials) if completed_trials else 0.0

    print("== Optimizer Summary ==")
    print(f"Run dir: {data.get('run_dir')}")
    if meta:
        print("Meta:")
        for key in ("run_id", "symbol", "timeframe", "snapshot_id", "git_commit"):
            if key in meta:
                print(f"  {key}: {meta[key]}")
    print("Counts:")
    print(
        f"  total={counts.get('total', 0)} completed={counts.get('completed', 0)} "
        f"skipped={counts.get('skipped', 0)} failed={counts.get('failed', 0)} "
        f"valid={counts.get('valid', 0)}"
    )
    if total_duration:
        print(f"  total_duration={total_duration:.1f}s avg_duration={avg_duration:.1f}s")

    if not valid_trials:
        print("No trial satisfied the constraints.")
        return

    best = valid_trials[0]
    print("Best trial:")
    print(f"  id: {best.get('trial_id')}")
    print(f"  file: {best.get('trial_file')}")
    print(f"  score: {best.get('score')}")
    metrics = best.get("metrics") or {}
    if metrics:
        print(f"  num_trades: {metrics.get('num_trades')}")
        print(f"  sharpe_ratio: {metrics.get('sharpe_ratio')}")
        print(f"  total_return: {metrics.get('total_return')}")
        print(f"  profit_factor: {metrics.get('profit_factor')}")

    if top_n > 1:
        print(f"Top {min(top_n, len(valid_trials))} trials (score desc):")
        for idx, entry in enumerate(valid_trials[:top_n], start=1):
            print(_format_trial_summary(idx, entry))
        if top_n < len(valid_trials):
            print(f"  ... {len(valid_trials) - top_n} more")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optimizer CLI")
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Summarise a run")
    summarize_parser.add_argument("run_id", type=str, help="Run id (directory name)")
    summarize_parser.add_argument(
        "--top",
        type=int,
        default=1,
        help="Number of top trials to list (default: 1)",
    )

    args = parser.parse_args(argv)
    if args.command == "summarize":
        data = summarize_run(args.run_id)
        top_n = max(1, int(args.top))
        _print_summary(data, top_n=top_n)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
