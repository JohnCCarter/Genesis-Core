# Repo Cleanup Fas C27 Execution Report (2026-02-18)

## Syfte

Accelerera scriptstädning med en 10-filers delete-only tranche av legacy wrappers med låg risk.

## Contract

- `docs/ops/REPO_CLEANUP_C27_EXEC_CONTRACT_2026-02-18.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED`
- Minimal remediation: ingen ytterligare pre-code remediation.

## Evidence anchors

- `reports/script_activity_latest.md` (rader 107-117): kandidater markerade `STALE`, score `0`, refs `0`.
- Scoped grep före execution:
  - inga träffar i `src/**`, `tests/**`, `mcp_server/**`, `config/**`
  - träffar i `scripts/*.py` endast self-wrapper-referenser (förväntat före delete)
- Archive-targets verifierade för samtliga 10 kandidater under `scripts/archive/2026-02/analysis/`.
- Extra kontroll: ingen archive-self-reference för `scripts/list_top_trials.py`.

## Retention exception

- Normpolicy: 2-4 veckors wrapper-retention (`scripts/README.md`).
- C27 genomförs tidigare än retentionfönstret.
- Undantag: explicit user-authorized (2026-02-18) för denna tranche.

## Planned change set

1. Delete `scripts/create_trial_1940_config.py`
2. Delete `scripts/diag_trades.py`
3. Delete `scripts/evaluate_all_models.py`
4. Delete `scripts/freeze_data.py`
5. Delete `scripts/get_trial_params.py`
6. Delete `scripts/identify_config_difference.py`
7. Delete `scripts/inspect_dates.py`
8. Delete `scripts/inspect_trial_4.py`
9. Delete `scripts/join_holdout_blocks.py`
10. Delete `scripts/list_top_trials.py`

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                 |
| ------------------------ | ------ | ------ | ------------------------------------------------------------------------------------- |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --all-files`                                                          |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py`                                          |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py`                                            |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py`                                              |
| scope + negative grep    | `PASS` | `PASS` | root-only scripts grep + `src/tests/mcp_server/config`                                |

## Post-code review (Opus 4.6)

- Status: `införd`
- Beslut: `APPROVED`
- Audit: `Opus 4.6 post-code diff-audit C27: APPROVED — scope-disciplin verifierad (endast 10 delete-only wrappers + 2 kontrakts/docsfiler), inga beteendedrifter utanför scope, required AFTER-gates PASS.`

## Status

- C27 execution: `införd`.
