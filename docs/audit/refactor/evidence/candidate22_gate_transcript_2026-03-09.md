# Candidate22 Gate Transcript (2026-03-09)

## Pre-gates

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` -> PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Post-gates

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` -> PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Result

All required Candidate22 gates passed pre and post deletion.

## Final gate rerun (after remediation)

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` -> PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Final gate rerun (after scope-evidence sync)

- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` -> PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS
