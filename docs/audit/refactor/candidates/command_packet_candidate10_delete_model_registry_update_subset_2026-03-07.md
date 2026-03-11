# Command Packet — Candidate 10 Delete `archive/model_registry_update` subset (2026-03-07)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — deleting archived scripts can break hidden path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Execute a safe, traceable deletion of 14 files under `scripts/archive/model_registry_update/` with evidence and required gates.
- **Candidate:** `delete_archive_model_registry_update_subset`
- **Base SHA:** `71789f38841548c5d9d2a0484c13975b916c456e`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/archive/model_registry_update/analyze_full_registry.py`
  - `scripts/archive/model_registry_update/analyze_tbtcusd_models.py`
  - `scripts/archive/model_registry_update/cleanup_old_models.py`
  - `scripts/archive/model_registry_update/cleanup_tbtcusd_metrics.py`
  - `scripts/archive/model_registry_update/cleanup_tbtcusd_models.py`
  - `scripts/archive/model_registry_update/complete_model_registry_update.py`
  - `scripts/archive/model_registry_update/create_advanced_models.py`
  - `scripts/archive/model_registry_update/execute_model_registry_update.py`
  - `scripts/archive/model_registry_update/fix_timeframe_4h.py`
  - `scripts/archive/model_registry_update/model_update_plan.json`
  - `scripts/archive/model_registry_update/tbtcusd_cleanup_plan.json`
  - `scripts/archive/model_registry_update/update_model_registry_plan.py`
  - `scripts/archive/model_registry_update/update_registry_mapping.py`
  - `scripts/archive/model_registry_update/verify_model_registry.py`
  - `docs/audit/refactor/evidence/candidate10_model_registry_update_manifest_2026-03-07.txt`
  - `docs/audit/refactor/evidence/candidate10_model_registry_update_path_refcheck_2026-03-07.txt`
  - `docs/audit/refactor/evidence/candidate10_model_registry_update_exact_path_refcheck_2026-03-07.json`
  - `docs/audit/refactor/evidence/candidate10_final_rerun_transcript_2026-03-07.txt` (post-delete artifact)
  - `docs/audit/refactor/command_packet_candidate10_delete_model_registry_update_subset_2026-03-07.md`
  - `docs/audit/refactor/model_registry_update_subset_delete_signoff_2026-03-07.md` (post-delete artifact)
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt` (EOF normalization by required pre-commit hook, if touched)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `.github/workflows/**`
  - all non-target paths under `scripts/**`
- **Expected changed files:** `20` (14 deletes + 6 docs/evidence files)
- **Max files touched:** `21`
- **Hard lock:** one-candidate-per-PR (`delete_archive_model_registry_update_subset`) with explicit no-active-reference evidence.

### Gates required

- `pre-commit run --all-files`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- determinism selector: `pytest -q tests/test_backtest_determinism_smoke.py`
- feature cache selectors: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
- pipeline invariant selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Default parity constraints (mandatory)

- No default behavior change.
- No env/config interpretation changes.
- No API contract changes.

### Evidence for candidate safety

- Exact delete manifest: `docs/audit/refactor/evidence/candidate10_model_registry_update_manifest_2026-03-07.txt`
- Strict folder path refcheck outside docs/archive and scripts/archive surfaces:
  - `docs/audit/refactor/evidence/candidate10_model_registry_update_path_refcheck_2026-03-07.txt`
- Exact per-file path refcheck across active surfaces (`src`, `scripts`, `tests`, `config`, `mcp_server`, `.github/workflows`, `.github/skills`):
  - `target_count = 14`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - Source: `docs/audit/refactor/evidence/candidate10_model_registry_update_exact_path_refcheck_2026-03-07.json`

### Skill Usage (evidence)

- `repo_clean_refactor` run_id `d7c98a85d7ba` (manifest `dev`, Triggered=`OK`, Verified/Result=`STOP` reason `no_steps`).
- `python_engineering` run_id `d8859a61e5cf` (manifest `dev`, Triggered=`OK`, Verified/Result=`STOP` reason `no_steps`).
- Note: These are governance-evidence invocations and **not** substitutes for required test gates.

### Stop Conditions

- Scope drift outside Scope IN.
- Any active reference to target paths outside docs/archive surfaces.
- Any behavior change without explicit exception.
- Any required gate failure.

### Output required

- **Implementation Report**
- **PR evidence template**
