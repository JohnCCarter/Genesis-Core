# Repo Cleanup Fas C8 Execution Report (2026-02-17)

## Syfte

Genomföra en minimal, evidensdriven move-only tranche i Fas C genom att flytta tre stale-markerade compare-scripts till `scripts/archive/analysis/` utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C8_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Kommentar: initialt `BLOCKED` (SAFE TO EXECUTE NOW: `no`) pga residual-policy-glapp för legacy self-usage path i `compare_modes.py`; efter remediation + re-review: `APPROVED` (SAFE TO EXECUTE NOW: `yes`).

## Evidence anchors (pre-execution)

- Klassificering:
  - `reports/script_activity_latest.md` -> `compare_htf_exits.py`, `compare_modes.py`, `compare_swing_strategies.py` klassade `STALE` med låg score.
- Deprecated-lista:
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md` listar samma compare-scripts i Fas C.
- `git status --porcelain` BEFORE (carry-forward out-of-scope):
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
  - `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`
  - `reports/script_activity_latest.json`
  - `reports/script_activity_latest.md`
  - `docs/ops/REPO_CLEANUP_C8_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C8_EXEC_REPORT_2026-02-17.md`

## Planned change set (strict)

1. Move: `scripts/compare_htf_exits.py` -> `scripts/archive/analysis/compare_htf_exits.py`
2. Move: `scripts/compare_modes.py` -> `scripts/archive/analysis/compare_modes.py`
3. Move: `scripts/compare_swing_strategies.py` -> `scripts/archive/analysis/compare_swing_strategies.py`
4. Minimal bootstrap patch i flyttade scripts vid behov för bibehållen `src` path-resolution.

## Gate results

| Gate                        | BEFORE | AFTER  | Notes                                                                                                                                                                                                     |
| --------------------------- | ------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint             | `PASS` | `PASS` | `pre-commit run --files docs/ops/REPO_CLEANUP_C8_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C8_EXEC_REPORT_2026-02-17.md` passerade före och efter.                                                |
| smoke test                  | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`) före och efter.                                                                                                                               |
| determinism replay          | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`) före och efter.                                                                                                                               |
| feature-cache invariance    | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`) före och efter.                                                                                 |
| pipeline invariant          | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`) före och efter.                                                                                                                                 |
| script compatibility checks | `PASS` | `PASS` | BEFORE: `python scripts/compare_modes.py --help` PASS + modulimport PASS för tre scripts. AFTER: `python scripts/archive/analysis/compare_modes.py --help` PASS + modulimport PASS för tre archive-paths. |
| scope + reference checks    | `PASS` | `PASS` | AFTER: move-only diff (`D scripts/compare_*` + `?? scripts/archive/analysis/compare_*`) och legacy negative check utan träffar i `src/**`, `scripts/**`, `mcp_server/**`, `config/**`, `tests/**`.        |

## Stop condition

- Om någon required gate failar, eller om legacy-check inte är tom: markera `BLOCKED`, stoppa commit/push och kör minimal remediation + Opus re-review.

## Post-code review (Opus 4.6)

- Status: `införd`
- Kommentar: `APPROVED` (SAFE TO COMMIT NOW: `yes`) efter diff-audit av scope, move-only-semantik, legacy negative check och gate-utfall.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C8 implementation: `införd` i arbetskopia.
