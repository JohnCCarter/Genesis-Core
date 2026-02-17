# Repo Cleanup Fas C3 Execution Report (2026-02-17)

## Syfte

Genomföra en låg-risk Fas C-tranche genom att flytta tre deprecated scripts (`train_meta_model.py`, `probe_min_order_sizes.py`, `probe_min_order_sizes_live.py`) till `scripts/archive/experiments/` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C3_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: kontrakt/evidence godkänt; SAFE TO EXECUTE NOW: yes.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch scripts/train_meta_model.py scripts/probe_min_order_sizes.py scripts/probe_min_order_sizes_live.py` -> `PASS` (tracked proof verifierad).
- Scoped referensscan före execution -> `PASS` (träffar endast allowlistad historik/governance under `docs/audits/**`).
- `git status --porcelain` BEFORE -> dirty baseline är endast docs:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_CONTRACT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_C3_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C3_EXEC_REPORT_2026-02-17.md`
- Kandidatlista (deprecated scripts):
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Planned change set (strict)

1. Move: `scripts/train_meta_model.py` -> `scripts/archive/experiments/train_meta_model.py`
2. Move: `scripts/probe_min_order_sizes.py` -> `scripts/archive/experiments/probe_min_order_sizes.py`
3. Move: `scripts/probe_min_order_sizes_live.py` -> `scripts/archive/experiments/probe_min_order_sizes_live.py`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                                                                                                     |
| ------------------------ | ------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files docs/ops/REPO_CLEANUP_C3_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C3_EXEC_REPORT_2026-02-17.md` passerade före och efter execution.                                                                      |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`) före och efter.                                                                                                                                                               |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`) före och efter.                                                                                                                                                               |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`) före och efter.                                                                                                                 |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`) före och efter.                                                                                                                                                                 |
| scope + reference checks | `PASS` | `PASS` | AFTER: `scripts/train_meta_model.py`, `scripts/probe_min_order_sizes.py`, `scripts/probe_min_order_sizes_live.py` saknas i `scripts/`; scoped referenser kvar endast i allowlistad historik/governance (`docs/audits/**`, `docs/ops/**`). |

## Stop condition

- Om scoped referenskontroll efter execution visar träffar utanför allowlist ska tranche C3 markeras `BLOCKED` och ingen commit/push får ske förrän kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: scope/no-behavior-change verifierad; SAFE TO COMMIT: yes.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C3 implementation: `införd`.
