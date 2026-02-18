# Repo Cleanup Fas C25 Execution Report (2026-02-18)

## Syfte

Stänga scriptfasen med en minimal delete-only tranche av tre legacy wrappers med noll interna refs.

## Contract

- `docs/ops/REPO_CLEANUP_C25_EXEC_CONTRACT_2026-02-18.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED`
- Minimal remediation från Opus: logga retention-undantag explicit och kör full AFTER-gate-stack + negative grep.

## Evidence anchors

- `reports/script_activity_latest.md`:
  - `scripts/calculate_score_260.py` -> `STALE`, score `0`, refs `0`
  - `scripts/calculate_score_realistic.py` -> `STALE`, score `0`, refs `0`
  - `scripts/check_robustness_top_trials.py` -> `STALE`, score `0`, refs `0`
- Scoped grep före execution: endast self-wrapper-referenser.
- Archive-targets verifierade:
  - `scripts/archive/2026-02/analysis/calculate_score_260.py`
  - `scripts/archive/2026-02/analysis/calculate_score_realistic.py`
  - `scripts/archive/2026-02/analysis/check_robustness_top_trials.py`

## Retention exception

- Normpolicy: 2-4 veckors wrapper-retention (`scripts/README.md`).
- C25 genomförs tidigare än retentionfönstret.
- Undantag: explicit user-authorized (2026-02-18) för att avsluta scriptfasen nu.

## Planned change set

1. Delete `scripts/calculate_score_260.py`
2. Delete `scripts/calculate_score_realistic.py`
3. Delete `scripts/check_robustness_top_trials.py`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                          |
| ------------------------ | ------ | ------ | ---------------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --all-files`                                                                   |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py`                                                   |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py`                                                     |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py`          |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py`                                                       |
| scope + negative grep    | `PASS` | `PASS` | staged scope exakt 5 filer; negative grep utan träffar i `src/tests/mcp_server/config/scripts` |

## Post-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED`
- Minimal remediation: ingen

## Status

- C25 execution: `införd`.
