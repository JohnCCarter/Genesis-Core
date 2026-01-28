#!/usr/bin/env python3
"""Kör en snabb grid för att testa LTF-gating mot HTF-inställningar."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    candidate = str(path)
    if candidate not in sys.path:
        sys.path.insert(0, candidate)


def _default_run_id() -> str:
    now = datetime.now(UTC)
    return now.strftime("run_%Y%m%d_%H%M%S_ltfgrid")


def main() -> int:
    from core.optimizer.runner import run_optimizer
    from scripts.optimizer import summarize_run

    parser = argparse.ArgumentParser(
        description="Snabb grid för att analysera LTF-confidence vs HTF-gate"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/optimizer/tBTCUSD_1h_ltf_confidence_grid.yaml"),
        help="Sökväg till grid-konfigurationen",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Valfritt run-id; genereras annars automatiskt",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Hur många topp-trials som ska sammanfattas",
    )

    args = parser.parse_args()
    run_id = args.run_id or _default_run_id()

    if not args.config.exists():
        raise FileNotFoundError(f"Konfigfil saknas: {args.config}")

    print(f"[GRID] Startar run_id={run_id} med config={args.config}")
    run_optimizer(args.config, run_id=run_id)

    print("\n[GRID] Sammanfattning")
    summary = summarize_run(run_id)
    counts = summary.get("counts", {})
    print(
        "Trials: total={total} completed={completed} skipped={skipped} failed={failed}".format(
            total=counts.get("total", 0),
            completed=counts.get("completed", 0),
            skipped=counts.get("skipped", 0),
            failed=counts.get("failed", 0),
        )
    )

    valid_trials = summary.get("valid_trials", [])
    if not valid_trials:
        print("Inga giltiga trials hittades (constraints eller hårda fel).")
        return 0

    top_n = max(1, min(int(args.top), len(valid_trials)))
    print(f"Top {top_n} trials (score desc):")
    for idx, entry in enumerate(valid_trials[:top_n], start=1):
        metrics = entry.get("metrics") or {}
        print(
            "  {idx}. {tid} score={score:.4f} trades={trades} profit_factor={pf:.2f}".format(
                idx=idx,
                tid=entry.get("trial_id"),
                score=entry.get("score", 0.0),
                trades=metrics.get("num_trades"),
                pf=metrics.get("profit_factor", 0.0),
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
