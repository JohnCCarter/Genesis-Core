# Repo Cleanup Fas C7 Evidence Report (2026-02-17)

## Syfte

Införa ett evidensdrivet och reproducerbart underlag för att klassificera scripts som `ACTIVE`, `REVIEW` eller `STALE` innan framtida cleanup-trancher.

## Contract

- `docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md`

## Pre-code review (Opus 4.6)

- Status: `införd`
- Kommentar: `APPROVED` (SAFE TO EXECUTE NOW: `yes`) efter remediation av scope-check + script-lint-gate.

## Evidence anchors (pre-execution)

- `git status --porcelain` BEFORE:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md` (carry-forward)
  - `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md` (carry-forward)
  - `docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md`
  - `docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md`

## Planned change set (strict)

1. Add: `scripts/classify_script_activity.py`
2. Update: `docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md` (gate/evidence status)

## Gate results

| Gate                     | BEFORE | AFTER  | Notes                                                                                                                                                              |
| ------------------------ | ------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| pre-commit/lint          | `PASS` | `PASS` | `pre-commit run --files docs/ops/REPO_CLEANUP_C7_EVIDENCE_CONTRACT_2026-02-17.md docs/ops/REPO_CLEANUP_C7_EVIDENCE_REPORT_2026-02-17.md` passerade före och efter. |
| smoke test               | `PASS` | `PASS` | `tests/test_import_smoke_backtest_optuna.py` (`.` `[100%]`).                                                                                                       |
| determinism replay       | `PASS` | `PASS` | `tests/test_backtest_determinism_smoke.py` (`...` `[100%]`).                                                                                                       |
| feature-cache invariance | `PASS` | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` (`......` `[100%]`).                                                         |
| pipeline invariant       | `PASS` | `PASS` | `tests/test_pipeline_fast_hash_guard.py` (`...` `[100%]`).                                                                                                         |
| script smoke checks      | `PASS` | `PASS` | `python scripts/classify_script_activity.py --help` (exit=0) samt sample-körning gav `ACTIVE=15, REVIEW=51, STALE=62` och skrev `tmp/c7_script_activity_sample.*`. |
| script lint/sanity       | `PASS` | `PASS` | `python -m ruff check scripts/classify_script_activity.py` passerade efter import-fix (`collections.abc.Iterable`).                                                |
| scope checks             | `PASS` | `PASS` | `git status --porcelain` visar endast Scope IN + kända carry-forward paths; `git diff --cached --name-only` är tom (ingen out-of-scope staging).                   |

## Stop condition

- Om någon required gate failar: markera `BLOCKED`, stoppa commit/push och kör minimal remediation + Opus re-review.

## Post-code review (Opus 4.6)

- Status: `införd`
- Kommentar: `APPROVED` (SAFE TO COMMIT NOW: `yes`) efter diff-audit av scope/gates/no-behavior-change.

## Status

- Execution plan-underlag: `införd` i arbetskopia.
- C7 implementation: `införd` i arbetskopia.
