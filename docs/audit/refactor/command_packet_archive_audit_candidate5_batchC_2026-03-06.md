# Command Packet — Archive Audit Candidate 5 Batch C (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — archive removals can break path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Apply one atomic no-behavior-change batch candidate (32 wrapper-only archive files).
- **Candidate:** `deprecated_wrapper_batch_C` (32 files)
- **Base SHA:** `25b702594b276874dbf14cb5a15600829bbff5bb`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/archive/deprecated_2026-02/evaluate_all_models.py`
  - `scripts/archive/deprecated_2026-02/extract_ev_distribution.py`
  - `scripts/archive/deprecated_2026-02/extract_optuna_blocks_top_trials.py`
  - `scripts/archive/deprecated_2026-02/filter_model_features.py`
  - `scripts/archive/deprecated_2026-02/identify_config_difference.py`
  - `scripts/archive/deprecated_2026-02/monitor_feature_drift.py`
  - `scripts/archive/deprecated_2026-02/monitor_optuna_study.py`
  - `scripts/archive/deprecated_2026-02/phase2_metrics.py`
  - `scripts/archive/deprecated_2026-02/precompute_features_v18.py`
  - `scripts/archive/deprecated_2026-02/profile_pipeline.py`
  - `scripts/archive/deprecated_2026-02/reliability.py`
  - `scripts/archive/deprecated_2026-02/repo_inventory_report.py`
  - `scripts/archive/deprecated_2026-02/reproduce_mismatch.py`
  - `scripts/archive/deprecated_2026-02/reproduce_trial_from_merged_config.py`
  - `scripts/archive/deprecated_2026-02/reproduce_trial_subprocess.py`
  - `scripts/archive/deprecated_2026-02/resample_1h_to_3h.py`
  - `scripts/archive/deprecated_2026-02/resample_1h_to_6h.py`
  - `scripts/archive/deprecated_2026-02/run_ltf_confidence_grid.py`
  - `scripts/archive/deprecated_2026-02/run_optimizer_smoke.py`
  - `scripts/archive/deprecated_2026-02/run_phase2c_extended.py`
  - `scripts/archive/deprecated_2026-02/run_phase2d_corrected.py`
  - `scripts/archive/deprecated_2026-02/run_phase3_fine.py`
  - `scripts/archive/deprecated_2026-02/run_timeframe_sweep.py`
  - `scripts/archive/deprecated_2026-02/sanity_check_evgate_percentiles.py`
  - `scripts/archive/deprecated_2026-02/show_best_results.py`
  - `scripts/archive/deprecated_2026-02/show_feature_loading_modes.py`
  - `scripts/archive/deprecated_2026-02/show_loaded_model.py`
  - `scripts/archive/deprecated_2026-02/show_v4_features_loading.py`
  - `scripts/archive/deprecated_2026-02/simple_htf_integration_check.py`
  - `scripts/archive/deprecated_2026-02/summarize_hparam_results.py`
  - `scripts/archive/deprecated_2026-02/trace_champion_loading.py`
  - `scripts/archive/deprecated_2026-02/tune_confidence_threshold.py`
  - `docs/audit/refactor/command_packet_archive_audit_candidate5_batchC_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `scripts/paper_trading_runner.py`
  - `scripts/mcp_session_preflight.py`
  - freeze-sensitive/runtime authority paths
- **Expected changed files:**
  - Same 32 wrapper files as Scope IN
  - `docs/audit/refactor/command_packet_archive_audit_candidate5_batchC_2026-03-06.md`
- **Max files touched:** `33`
- **Hard lock:** one-candidate-per-PR (`deprecated_wrapper_batch_C`) with explicit no-active-reference evidence before action.

### Gates required

- `pre-commit run --all-files`
- `ruff check .`
- `pytest -q`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- determinism replay selector: `pytest -q tests/test_backtest_determinism_smoke.py`
- feature cache invariance selector: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
- pipeline invariant/hash selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Default parity constraints (mandatory)

- No default behavior change.
- No env/config interpretation changes.
- No API contract changes.

### Evidence for candidate safety

- All 32 files are wrapper-only (deprecated print + deprecated usage log + `runpy` handoff attempt) in deprecated archive surface.
- Exact deletion set is frozen in `docs/audit/refactor/evidence/candidate5_manifest_2026-03-06.txt`.
- Active reference check excludes `scripts/archive/**` and `docs/archive/**` and is captured in `docs/audit/refactor/evidence/candidate5_refcheck_2026-03-06.txt` (`all_files_no_active_refs: True`).
- Target scripts for these wrappers exist under `scripts/archive/analysis/**`.

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, status `STOP` reason `no_steps`, logged in `logs/skill_runs.jsonl`).

### Stop Conditions

- Scope drift outside hard lock files.
- Any active reference evidence outside archive/docs-archive.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**

### Gate evidence artifacts

- Manifest: `docs/audit/refactor/evidence/candidate5_manifest_2026-03-06.txt`
- Active ref-check: `docs/audit/refactor/evidence/candidate5_refcheck_2026-03-06.txt`
- Pre-commit: `docs/audit/refactor/evidence/candidate5_precommit_2026-03-06.txt`
- Ruff: `docs/audit/refactor/evidence/candidate5_ruff_2026-03-06.txt`
- Smoke selector: `docs/audit/refactor/evidence/candidate5_smoke_2026-03-06.txt`
- Determinism selector: `docs/audit/refactor/evidence/candidate5_determinism_2026-03-06.txt`
- Feature cache selectors: `docs/audit/refactor/evidence/candidate5_cache_2026-03-06.txt`
- Pipeline selector: `docs/audit/refactor/evidence/candidate5_pipeline_2026-03-06.txt`
- Full pytest: `docs/audit/refactor/evidence/candidate5_pytest_full_2026-03-06.txt`
