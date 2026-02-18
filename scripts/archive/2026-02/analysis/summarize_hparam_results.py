#!/usr/bin/env python3
"""
Summera resultat i en hparam-search katalog.

Usage:
    python -m scripts.summarize_hparam_results --run-dir results/hparam_search/run_YYYYMMDD_HHMMSS
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TrialSummary:
    trial_id: str
    score: float
    params: dict[str, Any]
    metrics: dict[str, Any]
    constraints_ok: bool


def _load_trial(path: Path) -> TrialSummary:
    payload = json.loads(path.read_text(encoding="utf-8"))
    score_block = payload.get("score") or {}
    metrics = score_block.get("metrics") or {}
    return TrialSummary(
        trial_id=str(payload.get("trial_id") or path.stem),
        score=float(score_block.get("score") or 0.0),
        params=payload.get("parameters") or {},
        metrics=metrics,
        constraints_ok=bool((payload.get("constraints") or {}).get("ok", True)),
    )


def summarize(run_dir: Path, top_k: int = 5) -> None:
    trial_paths = sorted(
        path for path in run_dir.glob("trial_*.json") if "_config" not in path.stem
    )
    if not trial_paths:
        raise FileNotFoundError(f"Inga trial_*.json hittades i {run_dir}")

    trials = [_load_trial(path) for path in trial_paths]
    trials.sort(key=lambda t: t.score, reverse=True)

    print(f"=== {run_dir} ===")
    print(f"Totalt {len(trials)} trials")
    print()
    for idx, trial in enumerate(trials[:top_k], start=1):
        metrics = trial.metrics
        print(
            f"#{idx} {trial.trial_id}  score={trial.score:.3f}  "
            f"trades={metrics.get('num_trades')}  PF={metrics.get('profit_factor')}"
        )
        print(f"    constraints_ok={trial.constraints_ok}")
        print(f"    entry_conf={trial.params.get('thresholds', {}).get('entry_conf_overall')}")
        print(
            f"    regime_bal={trial.params.get('thresholds', {}).get('regime_proba', {}).get('balanced')}"
        )
        print(f"    risk_map={trial.params.get('risk', {}).get('risk_map')}")
        print(
            f"    exit_conf={trial.params.get('exit', {}).get('exit_conf_threshold')}  "
            f"max_hold={trial.params.get('exit', {}).get('max_hold_bars')}"
        )
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir", type=Path, required=True, help="Sökväg till hparam-run katalog"
    )
    parser.add_argument("--top-k", type=int, default=5, help="Antal toppresultat att visa")
    args = parser.parse_args()
    summarize(args.run_dir, top_k=args.top_k)


if __name__ == "__main__":
    main()
