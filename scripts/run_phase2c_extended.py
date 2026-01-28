#!/usr/bin/env python3
"""Kör Phase2c Extended - 12 månader, 50 trials."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    candidate = str(path)
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

if __name__ == "__main__":
    from core.optimizer.runner import run_optimizer

    config_path = ROOT / "config" / "optimizer" / "tBTCUSD_1h_optuna_phase2c_extended.yaml"
    print("=" * 80)
    print("Phase2c Extended Optimization")
    print("=" * 80)
    print(f"Config: {config_path.name}")
    print("Tidsperiod: 12 månader (2024-04-01 → 2025-03-31)")
    print("Trials: 50")
    print("Concurrent: 4")
    print("Estimerad tid: ~6-8 timmar")
    print()
    print("Sökrymd highlights:")
    print("  - zones.low: 0.18-0.26 (breddad från 0.20-0.24)")
    print("  - entry_conf: 0.28-0.34 (snävare fokus)")
    print("  - exit_conf: 0.30-0.40 (bredare)")
    print("  - max_hold: 12-20 bars (bredare)")
    print("  - min_edge: 0.004-0.012 (fokuserad)")
    print("=" * 80)
    print()

    run_optimizer(config_path)
