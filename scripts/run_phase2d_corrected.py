#!/usr/bin/env python3
"""
Phase2d Corrected Optimization Launcher
Korrigerade ATR-zoner baserat på tmp-filernas framgångsrika parametrar
"""

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from core.optimizer.runner import run_optimizer  # noqa: E402

if __name__ == "__main__":
    config_path = repo_root / "config" / "optimizer" / "tBTCUSD_1h_optuna_phase2d_corrected.yaml"

    print("=" * 80)
    print("Phase2d Corrected Optimization")
    print("=" * 80)
    print("Config: tBTCUSD_1h_optuna_phase2d_corrected.yaml")
    print("Tidsperiod: 12 månader (2024-04-01 → 2025-03-31)")
    print("Trials: 50")
    print("Concurrent: 4")
    print("Estimerad tid: ~13-15 minuter")
    print()
    print("KORRIGERINGAR från Phase2c (v6 - Lowered Thresholds):")
    print("  - zones.low: 0.22-0.30 (var 0.18-0.26) → +4pp")
    print("  - zones.mid: 0.28-0.38 (var 0.24-0.30) → +4-8pp")
    print("  - zones.high: 0.34-0.44 (var 0.28-0.34) → +6-10pp")
    print("  - entry_conf: 0.24-0.34 (var 0.28-0.34) → -4pp (wider)")
    print("  - min_edge: 0.004-0.012 (var 0.004-0.012) → same baseline")
    print("  - Constraints: PF 1.1, DD 0.25 (var 0.9, 0.35) → strängare")
    print()
    print("Förväntat resultat: Fler trades än v5, men högre kvalitet än v2")
    print("=" * 80)
    print()

    run_optimizer(config_path)
