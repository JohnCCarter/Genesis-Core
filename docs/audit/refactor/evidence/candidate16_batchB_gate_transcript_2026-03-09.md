# Candidate16 Batch B — Gate Transcript (2026-03-09)

## Execution summary

- Branch: `feature/archive-mixed-assets-curation`
- Batch executed: **B (executable legacy quarantine)**
- Operation type: `git mv` only (rename/move)
- Batch B moved files: **12**
- Total staged renames after Batch B: **64** (Batch A + Batch B)

## Pre-gates (before Batch B move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Move execution

- Source of truth: `docs/audit/refactor/evidence/candidate16_exact_old_new_manifest_2026-03-09.tsv`
- Applied rows with `batch=B`: **12**
- Result: `BATCH_B_MOVED=12`, `SKIPPED=0`

## Post-gates (after Batch B move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Safety checks

- `archive` python content modifications (`M archive/**/*.py`): **0**
- Batch B changes are rename-only quarantine moves to:
  - `archive/quarantine/executable/2025-11-03/debug_scripts/*.py`
  - `archive/quarantine/executable/2025-11-03/scripts/*.py`
  - `archive/quarantine/executable/model_optimization/*.py`

## Representative staged lines

- `archive/2025-11-03/debug_scripts/debug_decide.py -> archive/quarantine/executable/2025-11-03/debug_scripts/debug_decide.py`
- `archive/2025-11-03/scripts/tmp_reason_counts.py -> archive/quarantine/executable/2025-11-03/scripts/tmp_reason_counts.py`
- `archive/model_optimization/update_1d_config.py -> archive/quarantine/executable/model_optimization/update_1d_config.py`
