# Candidate28 Gate Transcript (2026-03-10)

## Execution context

- Branch: `feature/docs-archive-review-2026-03-09`
- Mode: `RESEARCH`

## Pre-gates

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `python -m pytest -q tests/test_feature_cache.py` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Post-gates

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `python -m pytest -q tests/test_feature_cache.py` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Result

All required Candidate28 gates passed pre and post deletion.

## Session verification evidence

- Verification timestamp: `2026-03-10 11:01:08+01:00`
- Execution context: `feature/docs-archive-review-2026-03-09`, local terminal session in this workspace
- Command outcomes (pre): all exit codes `0`
- Command outcomes (post): all exit codes `0`

Detailed command outputs were captured in-session for each gate run and matched the PASS entries above.

## Exit-code table

| Gate command | Pre exit code | Post exit code |
|---|---:|---:|
| `python -m pre_commit run --all-files` | 0 | 0 |
| `python -m pytest -q tests/test_backtest_determinism_smoke.py` | 0 | 0 |
| `python -m pytest -q tests/test_feature_cache.py` | 0 | 0 |
| `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` | 0 | 0 |
| `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | 0 | 0 |
| `python scripts/run/run_backtest.py --help` | 0 | 0 |

## Final revalidation after audit-note closure

- Full gate chain rerun after post-audit notes: PASS
- Outcome remained unchanged: all required gates PASS
