# Candidate 9 Signoff — Delete `scripts/archive/experiments` subset (2026-03-06)

Mode: RESEARCH (source=branch mapping `feature/*`)
Candidate: `delete_archive_experiments_subset`

## Scope summary

- Deleted exactly 6 files:
  - `scripts/archive/experiments/filter_model_features.py`
  - `scripts/archive/experiments/probe_min_order_sizes_live.py`
  - `scripts/archive/experiments/probe_min_order_sizes.py`
  - `scripts/archive/experiments/run_timeframe_sweep.py`
  - `scripts/archive/experiments/train_meta_model.py`
  - `scripts/archive/experiments/train_regression_model.py`
- Added/updated candidate evidence/contract files:
  - `docs/audit/refactor/command_packet_candidate9_delete_experiments_subset_2026-03-06.md`
  - `docs/audit/refactor/evidence/candidate9_experiments_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate9_experiments_path_refcheck_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate9_experiments_exact_path_refcheck_2026-03-06.json`
  - `docs/audit/refactor/experiments_subset_delete_signoff_2026-03-06.md`
- `candidate7_test_prototypes_path_refcheck_2026-03-06.txt` was not touched in this Candidate 9 run.

## Reference safety evidence

- Manifest size: 6 targets (`candidate9_experiments_manifest_2026-03-06.txt`).
- Exact per-file path refcheck across `src`, `scripts`, `tests`, `config`, `mcp_server`, `.github/workflows`, and `.github/skills`:
  - `target_count = 6`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - source: `candidate9_experiments_exact_path_refcheck_2026-03-06.json`
- Strict path refcheck artifact:
  - `candidate9_experiments_path_refcheck_2026-03-06.txt`
- Manifest parity check:
  - `remaining_files = 0`

## Skill evidence (governance supplement)

- `repo_clean_refactor` run_id `d7c98a85d7ba`: Triggered=`OK`, Verified/Result=`STOP` (`no_steps`).
- `python_engineering` run_id `d8859a61e5cf`: Triggered=`OK`, Verified/Result=`STOP` (`no_steps`).
- These invocations are supplemental evidence and not test gate replacements.

## Gates

### Pre-change gates

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Post-change gates

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Final rerun before push

- `pre-commit run --all-files` -> PASS
- `pytest -q` selector bundle (smoke + determinism + feature cache + pipeline invariant) -> PASS (`11 passed`)
- Raw transcript artifact: `docs/audit/refactor/evidence/candidate9_final_rerun_transcript_2026-03-06.txt`

## No-behavior-change assertion

- No runtime/config/API paths changed.
- No env/config interpretation changes.
- Change is constrained to archive cleanup + governance evidence artifacts.
