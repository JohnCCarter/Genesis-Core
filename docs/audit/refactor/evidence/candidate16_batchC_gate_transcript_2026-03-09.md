# Candidate16 Batch C — Gate Transcript (2026-03-09)

## Execution summary

- Branch: `feature/archive-mixed-assets-curation`
- Batch executed: **C (tmp-config snapshots)**
- Operation type: `git mv` only (rename/move)
- Batch C moved files: **8**

## Pre-gates (before Batch C move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Move execution

- Source of truth: `docs/audit/refactor/evidence/candidate16_exact_old_new_manifest_2026-03-09.tsv`
- Applied rows with `batch=C`: **8**
- Result verification: `BATCH_C_STAGED_RENAMES=8`

## Post-gates (after Batch C move)

1. `python -m pre_commit run --all-files` → **PASS**
2. `python -m pytest -q tests/test_backtest_determinism_smoke.py` → **PASS**
3. `python -m pytest -q tests/test_feature_cache.py` → **PASS**
4. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` → **PASS**
5. `python scripts/run/run_backtest.py --help` → **PASS**

## Safety checks

- Temporary configs were moved to quarantine path:
  - `archive/quarantine/tmp_configs/2025-11-03/*.json`
- `archive` python content modifications (`M archive/**/*.py`): **0**

## Representative staged lines

- `archive/2025-11-03/tmp_configs/tmp_aggressive_candidate.json -> archive/quarantine/tmp_configs/2025-11-03/tmp_aggressive_candidate.json`
- `archive/2025-11-03/tmp_configs/tmp_threshold_relax.json -> archive/quarantine/tmp_configs/2025-11-03/tmp_threshold_relax.json`
