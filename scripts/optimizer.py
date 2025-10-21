"""CLI-verktyg för optimizer (Phase-7a)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results" / "hparam_search"


def summarize_run(run_id: str) -> dict[str, Any]:
    run_dir = (RESULTS_DIR / run_id).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory saknas: {run_dir}")

    meta_path = run_dir / "run_meta.json"
    meta: dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Ogiltig JSON i {meta_path}") from exc

    trials: list[dict[str, Any]] = []
    for path in sorted(run_dir.glob("trial_*.json")):
        try:
            t = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(t, dict):
            t["trial_file"] = path.name
            trials.append(t)

    total = len(trials)
    skipped = sum(1 for t in trials if t.get("skipped"))
    failed = sum(1 for t in trials if t.get("error"))
    completed = total - skipped
    best_score = None
    best_trial = None
    for t in trials:
        score_block = t.get("score") or {}
        hard_failures = score_block.get("hard_failures") or []
        constraints_ok = (t.get("constraints") or {}).get("ok", False)
        if hard_failures or not constraints_ok:
            continue
        try:
            score_value = float(score_block.get("score"))
        except (TypeError, ValueError):
            continue
        if best_score is None or score_value > best_score:
            best_score = score_value
            best_trial = t

    return {
        "meta": meta,
        "run_dir": str(run_dir),
        "counts": {
            "total": total,
            "skipped": skipped,
            "failed": failed,
            "completed": completed,
        },
        "best_trial": best_trial,
        "trials": trials,
    }


def _print_summary(data: dict[str, Any]) -> None:
    meta = data.get("meta") or {}
    counts = data.get("counts") or {}
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
        f"skipped={counts.get('skipped', 0)} failed={counts.get('failed', 0)}"
    )
    best = data.get("best_trial")
    if best:
        print("Best trial:")
        print(f"  id: {best.get('trial_id')}")
        print(f"  file: {best.get('trial_file')}")
        score = best.get("score") or {}
        metrics = score.get("metrics") or {}
        print(f"  score: {score.get('score')}")
        if metrics:
            print(f"  num_trades: {metrics.get('num_trades')}")
            print(f"  sharpe_ratio: {metrics.get('sharpe_ratio')}")
            print(f"  total_return: {metrics.get('total_return')}%")
            print(f"  profit_factor: {metrics.get('profit_factor')}")
    else:
        print("Ingen giltig trial utan constraint-fel hittades.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optimizer CLI")
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Sammanfatta run")
    summarize_parser.add_argument("run_id", type=str, help="Run-id (katalognamn)")

    args = parser.parse_args(argv)
    if args.command == "summarize":
        data = summarize_run(args.run_id)
        _print_summary(data)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
