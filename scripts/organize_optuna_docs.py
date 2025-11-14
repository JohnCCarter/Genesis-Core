#!/usr/bin/env python3
"""Flytta Optuna-relaterade dokument till docs/optuna/ mapp."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OPTUNA_DIR = DOCS_DIR / "optuna"

# Dokument att flytta
FILES_TO_MOVE = [
    "OPTUNA_VS_BACKTEST_CONFIG_DIFFERENCE.md",
    "OPTUNA_FIX_20251113.md",
    "optuna_performance_improvements.md",
    "OPTUNA_BEST_PRACTICES.md",
    "OPTUNA_6MONTH_PROBLEM_REPORT.md",
    "OPTUNA_FIX_SUMMARY.md",
    "BREAKTHROUGH_CONFIG_20251113.md",
    "PARITY_TEST_RESULTS_20251114.md",
    "SCORE_AND_METRICS_ENHANCEMENT_20251114.md",
]

# Skapa optuna-mapp
OPTUNA_DIR.mkdir(exist_ok=True)
print(f"✓ Skapade/kontrollerade {OPTUNA_DIR}")

# Flytta filer
moved = []
not_found = []

for filename in FILES_TO_MOVE:
    source = DOCS_DIR / filename
    dest = OPTUNA_DIR / filename

    if source.exists():
        shutil.move(str(source), str(dest))
        moved.append(filename)
        print(f"✓ Flyttade {filename}")
    else:
        not_found.append(filename)
        print(f"⚠ Hittade inte {filename}")

print(f"\n✓ Flyttade {len(moved)} filer")
if not_found:
    print(f"⚠ {len(not_found)} filer hittades inte: {', '.join(not_found)}")
