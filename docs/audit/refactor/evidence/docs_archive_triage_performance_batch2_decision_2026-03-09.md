# Triage Decision — Candidate22 performance/optimization batch2 (2026-03-09)

## Decision

Selected an 8-file batch from `UNCERTAIN` for governed deletion with no behavior change.

## Selection rationale

- Same deprecated archive zone as prior candidates for consistent governance handling.
- Files are dated performance/optimization snapshots and superseded status artifacts.
- Exact filename/path refcheck found no external references outside `docs/archive/**` and `docs/audit/**` for the 8 in-scope files.
- Throughput increase vs Candidate21 (8 files instead of 2) while keeping risk low.

## Exclusion note

`docs/archive/deprecated_2026-02-24/docs/performance/OPTUNA_OPTIMIZATIONS.md` remains **UNCERTAIN** and is not included in Candidate22 due to an external reference hit in `docs/optuna/OPTUNA_OPTIMIZATION_ANALYSIS.md`.

## Candidate22 in-scope files

1. `docs/archive/deprecated_2026-02-24/docs/performance/IMPROVEMENTS_2025_11_21.md`
2. `docs/archive/deprecated_2026-02-24/docs/performance/OPTIMIZATION_20251126.md`
3. `docs/archive/deprecated_2026-02-24/docs/performance/OPTIMIZATION_STATUS_20251126.md`
4. `docs/archive/deprecated_2026-02-24/docs/performance/OPTUNA_IMPROVEMENTS_SUMMARY.md`
5. `docs/archive/deprecated_2026-02-24/docs/performance/performance_analysis.md`
6. `docs/archive/deprecated_2026-02-24/docs/performance/performance_optimization_summary.md`
7. `docs/archive/deprecated_2026-02-24/docs/performance/PERFORMANCE_OPTIMIZATION_SUMMARY_.md`
8. `docs/archive/deprecated_2026-02-24/docs/optimization/run_20251208_140048_summary.md`
