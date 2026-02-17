# Repo Cleanup Fas B7 Execution Report (2026-02-17)

## Syfte

Genomföra nästa destruktiva mikrotranche i Fas B genom att ta bort TEST_ONLY-kandidaten `src/core/backtest/walk_forward.py` och dess test `tests/test_walk_forward.py` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_B7_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: kontrakt/referens-allowlist är godkänd efter remediation; execution kan fortsätta inom Scope IN.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch src/core/backtest/walk_forward.py tests/test_walk_forward.py` -> tracked (`TRACK_EXIT=0`).
- `git grep -n -E "core\.backtest\.walk_forward|src\.core\.backtest\.walk_forward|backtest/walk_forward\.py|test_walk_forward\.py" -- src scripts mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md` -> scope-relevanta refs.
- Kända governance/historik-referenser (allowlisted):
  - `docs/ops/*`
  - `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
  - `docs/daily_summaries/daily_summary_2026-01-23.md`

## Planned change set (strict)

1. Delete: `src/core/backtest/walk_forward.py`
2. Delete: `tests/test_walk_forward.py`
3. Update: `src/genesis_core.egg-info/SOURCES.txt`
4. Update: `docs/architecture/ARCHITECTURE_VISUAL.md`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                                      |
| ------------------------ | ------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files ...` PASS före och efter.                                                                                                                          |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` PASS före och efter.                                                                                                          |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` PASS före och efter.                                                                                                            |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` PASS före och efter.                                                                 |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` PASS före och efter.                                                                                                              |
| scope + reference checks | `PASS` | `PASS` | BEFORE: tracked proof (`TRACK_EXIT=0`) + scoped refs; AFTER: inga träffar i `src/scripts/mcp_server/config/tests/SOURCES/ARCHITECTURE_VISUAL` och inga out-of-scope paths. |

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: NO BEHAVIOR CHANGE verifierad; scope hölls till kontraktets Scope IN med allowlistade residual-referenser.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- B7 implementation: `införd`.
