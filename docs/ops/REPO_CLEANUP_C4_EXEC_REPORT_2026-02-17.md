# Repo Cleanup Fas C4 Execution Report (2026-02-17)

## Syfte

Genomföra en låg-risk Fas C-tranche genom att flytta tre deprecated scripts (`train_regression_model.py`, `filter_model_features.py`, `run_timeframe_sweep.py`) till `scripts/archive/experiments/` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C4_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: initial `BLOCKED` remederades med explicit allowlist för destinationernas self-usage; recheck gav `SAFE TO EXECUTE NOW: yes`.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch scripts/train_regression_model.py scripts/filter_model_features.py scripts/run_timeframe_sweep.py` -> `PASS` (tracked proof verifierad).
- Scoped referensscan före execution -> `PASS` med kända träffar i `docs/audits/**` samt kandidatscriptens self-usage-rader.
- `git status --porcelain` BEFORE -> dirty baseline är endast docs:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_CONTRACT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_C4_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C4_EXEC_REPORT_2026-02-17.md`
- Kandidatlista (deprecated scripts):
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Planned change set (strict)

1. Move: `scripts/train_regression_model.py` -> `scripts/archive/experiments/train_regression_model.py`
2. Move: `scripts/filter_model_features.py` -> `scripts/archive/experiments/filter_model_features.py`
3. Move: `scripts/run_timeframe_sweep.py` -> `scripts/archive/experiments/run_timeframe_sweep.py`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                                                                                                                                                                     |
| ------------------------ | ------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files scripts/archive/experiments/train_regression_model.py scripts/archive/experiments/filter_model_features.py scripts/archive/experiments/run_timeframe_sweep.py docs/ops/REPO_CLEANUP_C4_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C4_EXEC_REPORT_2026-02-17.md` passerade. |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`).                                                                                                                                                                                                                                              |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`).                                                                                                                                                                                                                                              |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`).                                                                                                                                                                                                |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`).                                                                                                                                                                                                                                                |
| scope + reference checks | `PASS` | `PASS` | Efter execution: destination paths finns, source paths saknas i working tree (`new_*=True`, `old_*=False`); scoped grep visar endast `docs/ops/*` + destinationernas self-usage.                                                                                                                          |

## Stop condition

- Om scoped referenskontroll efter execution visar träffar utanför allowlist ska tranche C4 markeras `BLOCKED` och ingen commit/push får ske förrän kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: post-audit verifierade move-only scope, gröna AFTER-gates och inga out-of-scope drift.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C4 implementation: `införd` i arbetskopia.
