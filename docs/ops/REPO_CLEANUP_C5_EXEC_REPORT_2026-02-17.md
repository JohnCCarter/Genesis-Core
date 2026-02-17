# Repo Cleanup Fas C5 Execution Report (2026-02-17)

## Syfte

Genomföra en låg-risk Fas C-tranche genom att flytta tre deprecated analysis scripts (`analyze_feature_importance.py`, `analyze_feature_synergy.py`, `analyze_permutation_importance.py`) till `scripts/archive/analysis/` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: initial `BLOCKED` remederades (split legacy/archive checks + skarpare allowlist); recheck gav `SAFE TO EXECUTE NOW: yes`.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch scripts/analyze_feature_importance.py scripts/analyze_feature_synergy.py scripts/analyze_permutation_importance.py` -> `PASS` (tracked proof verifierad).
- Scoped referensscan före execution -> `PASS` med kända träffar i `docs/audits/**`, docs-referenser i Scope IN och kandidatscriptens self-usage-rader.
- `git status --porcelain` BEFORE -> carry-forward out-of-scope:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
  - `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C5_EXEC_REPORT_2026-02-17.md`
- Kandidatlista (deprecated scripts):
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Executed change set (strict)

1. Move: `scripts/analyze_feature_importance.py` -> `scripts/archive/analysis/analyze_feature_importance.py`
2. Move: `scripts/analyze_feature_synergy.py` -> `scripts/archive/analysis/analyze_feature_synergy.py`
3. Move: `scripts/analyze_permutation_importance.py` -> `scripts/archive/analysis/analyze_permutation_importance.py`
4. Update path refs:
   - `docs/features/INDICATORS_REFERENCE.md`
   - `docs/validation/VALIDATION_CHECKLIST.md`
5. Preserve pre-move import-bootstrap semantics:

- `scripts/archive/analysis/analyze_permutation_importance.py` (`Path(__file__).resolve().parents[3] / "src"`)

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------ | ------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | BEFORE: `pre-commit run --files docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C5_EXEC_REPORT_2026-02-17.md` passerade. AFTER: `pre-commit run --files scripts/archive/analysis/analyze_feature_importance.py scripts/archive/analysis/analyze_feature_synergy.py scripts/archive/analysis/analyze_permutation_importance.py docs/features/INDICATORS_REFERENCE.md docs/validation/VALIDATION_CHECKLIST.md docs/ops/REPO_CLEANUP_C5_EXEC_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C5_EXEC_REPORT_2026-02-17.md` passerade. |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`).                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| scope + reference checks | `PASS` | `PASS` | AFTER: scoped legacy-path check (src/scripts/mcp*server/config/tests/docs/features/docs/validation) tom; archive-path check visar uppdaterade refs i `docs/features/INDICATORS_REFERENCE.md` och `docs/validation/VALIDATION_CHECKLIST.md`; move-verifiering `new*\_=True`, `old\_\_=False`.                                                                                                                                                                                                                                                               |

## Stop condition

- Om scoped referenskontroll efter execution visar träffar utanför allowlist ska tranche C5 markeras `BLOCKED` och ingen commit/push får ske förrän kontrakt/allowlist uppdaterats och Opus har re-godkänt.

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: post-audit verifierade scope-disciplin, no-behavior-change och gröna AFTER-gates; carry-forward-filer ska fortsatt exkluderas från commit.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C5 implementation: `införd` i arbetskopia.
