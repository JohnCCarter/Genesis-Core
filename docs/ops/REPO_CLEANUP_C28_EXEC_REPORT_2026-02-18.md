# Repo Cleanup Fas C28 Execution Report (2026-02-18)

## Syfte

Införa 14-dagars deprecation window med wrapper-bakåtkompatibilitet och usage-loggning, utan raderingar.

## Contract

- `docs/ops/REPO_CLEANUP_C28_EXEC_CONTRACT_2026-02-18.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED` (efter kontraktsremediation)

## Planned change set

- Uppdatera policy/checklista i `scripts/README.md`
- Uppdatera wrapper-template i `scripts/deprecate_move.py`
- Skapa 76 saknade wrappers för archive-flyttar inom senaste 14 dagar
- Inga deletions, inga CI/workflow-ändringar

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                 |
| ------------------------ | ------ | ------ | ------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --all-files`                                                          |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py`                                          |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py`                                            |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py`                                              |
| scope guard              | `PASS` | `PASS` | endast Scope IN-filer                                                                 |
| wrapper usage-logg       | `N/A`  | `PASS` | Manuell verifiering: success path + simulerat loggfel utan exit-code-drift            |

## Post-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED`
- Audit: `C28 post-code audit APPROVED: scope-disciplin verifierad, no-behavior-change bibehållen, och usage-loggning fail-open enligt kontrakt.`

## Status

- C28 execution: `införd`.
