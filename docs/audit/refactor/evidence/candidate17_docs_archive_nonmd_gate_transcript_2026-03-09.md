# Candidate 17 D2 Gate Transcript (2026-03-09)

## Scope
- Operation: rename-only move of 4 non-md files under `docs/archive/**`.
- Constraint: NO BEHAVIOR CHANGE, no content edits.

## Pre-gates (PASS)
- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `python -m pytest -q tests/test_feature_cache.py` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Execution
- Performed 4x `git mv` according to manifest `docs_archive_nonmd_proposed_manifest_2026-03-09.tsv`.
- No content edits applied to moved `.py`/`.ipynb` files.

## Post-gates (PASS)
- `python -m pre_commit run --all-files` -> PASS
- `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `python -m pytest -q tests/test_feature_cache.py` -> PASS
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS
- `python scripts/run/run_backtest.py --help` -> PASS

## Post-check evidence
- reference scan status: PASS_NO_ACTIVE_REFS
- hash parity status: PASS_HASH_PARITY
- details: `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_postcheck_2026-03-09.txt`

## Result
- D2 execution completed under packet constraints with gate parity maintained.
