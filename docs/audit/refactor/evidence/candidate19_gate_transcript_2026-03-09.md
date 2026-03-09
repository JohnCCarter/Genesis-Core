# Candidate19 Gate Transcript (2026-03-09)

## Pre-execution gates

- `python -m pre_commit run --all-files` → PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` → PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` → PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → PASS
- `python scripts/run/run_backtest.py --help` → PASS

## Skill invocation evidence (governance SPEC, non-substitutive)

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` → STOP (`skill has no executable steps`)
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` → STOP (`skill has no executable steps`)

Skill invocations are recorded as governance SPEC evidence only and are **not** treated as substitutes for required test/determinism/invariance gates.

## Post-execution gates

- `python -m pre_commit run --all-files` → PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` → PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` → PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → PASS (0 tests collected, no failures)
- `python scripts/run/run_backtest.py --help` → PASS

## Post-execution invariant proof (targeted rerun)

- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` → PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → PASS

## Final gate rerun (after remediation)

- `python -m pre_commit run --all-files` → PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` → PASS (3 passed)
- `python -m pytest -q tests/test_feature_cache.py` → PASS (5 passed)
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` → PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → PASS
- `python scripts/run/run_backtest.py --help` → PASS
