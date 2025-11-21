#!/usr/bin/env python3
"""Test abort-heuristic med restriktiva trösklar."""
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

    config_path = ROOT / "config" / "optimizer" / "test_abort_heuristic.yaml"
    print(f"[TEST] Kör abort-heuristik test: {config_path}")
    print("[TEST] Förväntat resultat: alla trials ska abortas pga höga trösklar")
    print("-" * 80)

    run_optimizer(config_path)
