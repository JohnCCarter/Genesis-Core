# Repo Cleanup Fas B5 Execution Report (2026-02-17)

## Syfte

Genomföra nästa destruktiva mikrotranche i Fas B genom att ta bort ARCHIVE_ONLY-kandidaten `src/core/indicators/macd.py` med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_B5_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: kontrakt/gates bedömdes tillräckligt strikta; execution får fortsätta inom Scope IN.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch src/core/indicators/macd.py` -> tracked.
- `git grep -n -E "core\.indicators\.macd|indicators/macd\.py" -- src mcp_server config tests src/genesis_core.egg-info/SOURCES.txt docs/architecture/ARCHITECTURE_VISUAL.md` -> scope-relevanta refs.
- Känd archive-only referens (allowlisted):
  - `scripts/archive/debug/legacy_data/comprehensive_feature_analysis.py`

## Planned change set (strict)

1. Delete: `src/core/indicators/macd.py`
2. Update: `src/genesis_core.egg-info/SOURCES.txt`
3. Update: `docs/architecture/ARCHITECTURE_VISUAL.md`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                          |
| ------------------------ | ------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files ...` PASS före och efter.                                                                                                              |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` PASS före och efter.                                                                                              |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` PASS före och efter.                                                                                                |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` PASS före och efter.                                                     |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` PASS före och efter.                                                                                                  |
| scope + reference checks | `PASS` | `PASS` | BEFORE: tracked proof + scoped refs; AFTER: `git diff` endast Scope IN och scoped grep utan träff i `src/mcp_server/config/tests/SOURCES/ARCHITECTURE_VISUAL`. |

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: NO BEHAVIOR CHANGE verifierad; scope hölls till kontraktets Scope IN och gate stack bedömdes adekvat.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- B5 implementation: `införd`.
