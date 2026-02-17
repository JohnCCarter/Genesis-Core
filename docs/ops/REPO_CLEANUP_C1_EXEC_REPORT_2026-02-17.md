# Repo Cleanup Fas C1 Execution Report (2026-02-17)

## Syfte

Genomföra en första låg-risk Fas C-tranche genom att flytta tre deprecated scripts (`smoke_test.py`, `smoke_test_eth.py`, `submit_test.py`) till `scripts/archive/test_prototypes/` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C1_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: kontrakt/referenskrav godkända efter remediation; SAFE TO EXECUTE NOW: yes.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch scripts/smoke_test.py scripts/smoke_test_eth.py scripts/submit_test.py` -> `PASS` (tracked proof verifierad).
- Referensbevis före execution (`grep_search` + scoped grep): endast träff i `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md` inom repo-scope.
- `git status --porcelain` BEFORE -> dirty baseline är endast docs:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_CONTRACT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_C1_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C1_EXEC_REPORT_2026-02-17.md`
- Kandidatlista (deprecated scripts):
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Planned change set (strict)

1. Move: `scripts/smoke_test.py` -> `scripts/archive/test_prototypes/smoke_test.py`
2. Move: `scripts/smoke_test_eth.py` -> `scripts/archive/test_prototypes/smoke_test_eth.py`
3. Move: `scripts/submit_test.py` -> `scripts/archive/test_prototypes/submit_test.py`

## Gate results

| Gate                     | BEFORE    | AFTER     | Notes |
| ------------------------ | --------- | --------- | ----- |
| pre-commit/lint          | `PASS`    | `PASS`    | `pre-commit run --files docs/ops/REPO_CLEANUP_C1_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C1_EXEC_REPORT_2026-02-17.md` passerade före och efter execution. |
| smoke test               | `PASS`    | `PASS`    | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`) före och efter. |
| determinism replay       | `PASS`    | `PASS`    | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`) före och efter. |
| feature-cache invariance | `PASS`    | `PASS`    | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`) före och efter. |
| pipeline invariant       | `PASS`    | `PASS`    | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`) före och efter. |
| scope + reference checks | `PASS`    | `PASS`    | AFTER: `scripts/smoke_test.py`, `scripts/smoke_test_eth.py`, `scripts/submit_test.py` saknas i `scripts/`; scoped referenser kvar endast i allowlistad historik/governance (`docs/audits/**`, `docs/ops/**`). |

## Stop condition

- Om scoped referenskontroll efter execution visar träffar utanför allowlist ska tranche C1 markeras `BLOCKED` och ingen commit/push får ske förrän kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: scope/no-behavior-change verifierad; SAFE TO COMMIT: yes.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C1 implementation: `införd`.
