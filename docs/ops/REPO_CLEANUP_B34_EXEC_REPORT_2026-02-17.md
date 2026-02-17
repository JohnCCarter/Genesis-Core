# Repo Cleanup Fas B3+B4 Execution Report (2026-02-17)

## Syfte

Genomföra nästa destruktiva mikrotranche i Fas B genom att ta bort test-only modulerna B3/B4 (`ema_cross` + `fvg`) med strikt scope och utan beteendeförändring.

## Contract

- `docs/ops/REPO_CLEANUP_B34_EXEC_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: kontraktet godkänt av Opus med caution att köra BEFORE-gates före deletion och hålla kirurgisk docs-ändring i scope.

## Evidence anchors (pre-execution)

- `git ls-files --error-unmatch src/core/strategy/ema_cross.py tests/test_strategy_ema_cross.py src/core/indicators/fvg.py tests/test_fvg.py` -> tracked.
- `git grep -n -E "core\.strategy\.ema_cross|strategy/ema_cross\.py|core\.indicators\.fvg|indicators/fvg\.py|test_strategy_ema_cross\.py|test_fvg\.py" -- ...` -> kända refs i scope-relevanta paths.
- Legitimitetsbeslut:
  - `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`

Tillåtna kvarvarande referenser (governance/historik):

- `docs/ops/*`
- `docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`

## Planned change set (strict)

1. Delete: `src/core/strategy/ema_cross.py`
2. Delete: `tests/test_strategy_ema_cross.py`
3. Delete: `src/core/indicators/fvg.py`
4. Delete: `tests/test_fvg.py`
5. Update: `src/genesis_core.egg-info/SOURCES.txt`
6. Update: `docs/architecture/ARCHITECTURE_VISUAL.md`
7. Update: `docs/features/GENESIS-CORE_FEATURES.md`
8. Update: `docs/archive/GENESIS-CORE_FEATURES_phase1-4.md`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                      |
| ------------------------ | ------ | ------ | ---------------------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files ...` passerade för scoped filer.                                                   |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`).                                               |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`).                                               |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`). |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`).                                                 |
| scope + reference checks | `PASS` | `PASS` | `git status` BEFORE/AFTER + `git diff` verifierat; scope-narrow `git grep` gav exit=1 efter execution.     |

## Post-code review (Opus 4.6)

- Status: `APPROVED`
- Kommentar: post-audit godkände B3+B4-scope, gateutfall och referensrensning; ingen kontraktsdrift kvar.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- B3+B4 implementation: `införd` i arbetskopia (post-audit + AFTER-gates gröna).
