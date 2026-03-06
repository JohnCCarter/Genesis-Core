# Shard B Cleanup Lock Note (2026-03-06)

Mode: RESEARCH (branch `feature/cleanup-tests-audit`)

## Scope confirmation

- Scope IN: `tests/**` cleanup only.
- Scope OUT: no runtime/core behavior changes, no test scenario redesign.
- Cleanup policy enforced: no behavior change, evidence-before-delete, fail-closed.

## Compliance reconciliation performed

To keep Shard B strictly as cleanup (not refactor), disallowed test-design hunks were reverted in commit:

- `d43b709d` — `chore(cleanup): revert test-design hunks to cleanup-only scope`

Reverted design-touch patterns:

- parametrized/merged scenario hunk in `tests/test_code_health_regressions.py`
- assertion-form changes in `tests/test_import_smoke_backtest_optuna.py`
- assertion-form change in `tests/test_pipeline_fast_hash_guard.py`

Remaining `def test_...` signature diffs are limited to unused fixture/argument cleanup only.

## Gate evidence

Executed after reconciliation:

- `python -m pre_commit run --all-files` -> PASS
- `python -m ruff check .` -> PASS
- `pytest` -> PASS (`979 passed, 0 failed`)
- RESEARCH-required spot checks:
  - `tests/test_backtest_determinism_smoke.py` -> PASS
  - `tests/test_pipeline_fast_hash_guard.py` -> PASS

## Outcome

Shard B is locked as cleanup-only. Any structural test improvements (scenario merges, parametrization redesign, assertion redesign) are explicitly out of scope and must be moved to a separate follow-up refactor branch.
