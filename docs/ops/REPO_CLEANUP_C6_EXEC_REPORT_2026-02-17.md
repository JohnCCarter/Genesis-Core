# Repo Cleanup Fas C6 Execution Report (2026-02-17)

## Syfte

Genomföra en turbo-tranche i Fas C genom att flytta sex deprecated validation/analysis scripts till `scripts/archive/analysis/` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C6_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Kommentar: `APPROVED` (SAFE TO EXECUTE NOW: `yes`) efter BEFORE-gates.

## Evidence anchors (pre-execution)

- Tracked proof -> `PASS`:
  - `git ls-files --error-unmatch scripts/benchmark_optimizations.py scripts/calculate_ic_metrics.py scripts/calculate_partial_ic.py scripts/fdr_correction.py scripts/feature_ic_v18.py scripts/monitor_feature_drift.py`
- Scoped referensscan -> `PASS`:
  - `git grep -n -E "scripts/benchmark_optimizations\.py|scripts/calculate_ic_metrics\.py|scripts/calculate_partial_ic\.py|scripts/fdr_correction\.py|scripts/feature_ic_v18\.py|scripts/monitor_feature_drift\.py" -- src scripts mcp_server config tests docs/validation`
- Script help-check BEFORE -> `PASS`:
  - `tmp/c6_help_results_validation6.txt` visar `exit=0` för alla sex scripts.
- `git status --porcelain` BEFORE -> carry-forward out-of-scope:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
  - `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C6_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C6_EXEC_REPORT_2026-02-17.md`

## Planned change set (strict)

1. Move: `scripts/benchmark_optimizations.py` -> `scripts/archive/analysis/benchmark_optimizations.py`
2. Move: `scripts/calculate_ic_metrics.py` -> `scripts/archive/analysis/calculate_ic_metrics.py`
3. Move: `scripts/calculate_partial_ic.py` -> `scripts/archive/analysis/calculate_partial_ic.py`
4. Move: `scripts/fdr_correction.py` -> `scripts/archive/analysis/fdr_correction.py`
5. Move: `scripts/feature_ic_v18.py` -> `scripts/archive/analysis/feature_ic_v18.py`
6. Move: `scripts/monitor_feature_drift.py` -> `scripts/archive/analysis/monitor_feature_drift.py`
7. Update path refs:
   - `docs/validation/VALIDATION_CHECKLIST.md`
   - `docs/validation/ADVANCED_VALIDATION_PRODUCTION.md`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                      |
| ------------------------ | ------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files docs/ops/REPO_CLEANUP_C6_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C6_EXEC_REPORT_2026-02-17.md` passerade före och efter. |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`).                                                                                               |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`).                                                                                               |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`).                                                 |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`).                                                                                                 |
| script help checks       | `PASS` | `PASS` | BEFORE: `tmp/c6_help_results_validation6.txt`; AFTER: `tmp/c6_help_results_after.txt` (samtliga sex scripts `exit=0`).                                     |
| scope + reference checks | `PASS` | `PASS` | AFTER: legacy negative check tom (exit code 1 utan träffar) och archive positive check visar uppdaterade refs i `docs/validation/**`.                      |

## Stop condition

- Om någon required gate failar, eller om legacy-check inte är tom, eller om archive-check saknar scopeade refs: markera `BLOCKED`, stoppa commit/push och kör minimal remediation + Opus re-review.

## Post-code review (Opus 4.6)

- Status: `införd`
- Kommentar: `APPROVED` (SAFE TO COMMIT NOW: `yes`) efter diff-audit av scope, gates och referenschecks.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C6 implementation: `införd` i arbetskopia.
