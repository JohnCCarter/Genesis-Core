# Repo Cleanup Fas B6 Execution Report (2026-02-17)

## Syfte

Genomföra nästa destruktiva mikrotranche i Fas B genom att ta bort TEST_ONLY-kandidaten `src/core/strategy/validation.py` och dess test `tests/test_validation_min.py` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_B6_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: carry-forward-krock remedierad; kontraktet är pre-code godkänt för execution inom Scope IN.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch src/core/strategy/validation.py tests/test_validation_min.py` -> tracked.
- `git grep -n -E "core\.strategy\.validation|strategy/validation\.py|test_validation_min\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md` -> scope-relevanta refs.
- Kända governance/historik-referenser (allowlisted):
  - `docs/ops/*`
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Planned change set (strict)

1. Delete: `src/core/strategy/validation.py`
2. Delete: `tests/test_validation_min.py`
3. Update: `src/genesis_core.egg-info/SOURCES.txt`
4. Update: `docs/architecture/ARCHITECTURE_VISUAL.md`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                                                             |
| ------------------------ | ------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files ...` PASS före och efter.                                                                                                                                                 |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` PASS före och efter.                                                                                                                                 |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` PASS före och efter.                                                                                                                                   |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` PASS före och efter.                                                                                        |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` PASS före och efter.                                                                                                                                     |
| scope + reference checks | `PASS` | `PASS` | BEFORE: tracked proof + scoped refs; AFTER: scoped sökningar utan träff i `src/scripts/mcp_server/config/tests/SOURCES/ARCHITECTURE_VISUAL` och inga nya out-of-scope paths utöver carry-forward. |

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: NO BEHAVIOR CHANGE verifierad; scope hölls till B6 Scope IN + dokumenterad B5 carry-forward.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- B6 implementation: `införd`.
