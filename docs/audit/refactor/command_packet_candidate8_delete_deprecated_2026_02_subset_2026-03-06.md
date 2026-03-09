# Command Packet — Candidate 8 Delete `archive/deprecated_2026-02` subset (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — deleting archived scripts can break hidden path contracts if references are missed
- **Required Path:** `Full`
- **Objective:** Execute a safe, traceable deletion of 5 files under `scripts/archive/deprecated_2026-02/` with evidence and required gates.
- **Candidate:** `delete_archive_deprecated_2026_02_subset`
- **Base SHA:** `4206f28843442ef2d549767a58e0d4b236359a11`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/archive/deprecated_2026-02/diagnose_optuna_issues.py`
  - `scripts/archive/deprecated_2026-02/diagnose_zero_trades.py`
  - `scripts/archive/deprecated_2026-02/freeze_data.py`
  - `scripts/archive/deprecated_2026-02/sweep_optuna_holdout_top_trials.py`
  - `scripts/archive/deprecated_2026-02/sync_precompute_and_train.py`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_path_refcheck_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_exact_path_refcheck_2026-03-06.json`
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_github_skills_refcheck_2026-03-06.json`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt` (EOF normalization by required pre-commit hook)
  - `docs/audit/refactor/command_packet_candidate8_delete_deprecated_2026_02_subset_2026-03-06.md`
  - `docs/audit/refactor/deprecated_2026_02_subset_delete_signoff_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `.github/workflows/**`
  - all non-target paths under `scripts/**`
- **Expected changed files:** `12` (5 deletes + 7 docs/evidence files)
- **Max files touched:** `13`
- **Hard lock:** one-candidate-per-PR (`delete_archive_deprecated_2026_02_subset`) with explicit no-active-reference evidence.

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

- Exact delete manifest: `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_manifest_2026-03-06.txt`
- Strict folder path refcheck outside docs/archive surfaces:
  - `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_path_refcheck_2026-03-06.txt`
- Exact per-file path refcheck across active surfaces (`src`, `scripts`, `tests`, `config`, `mcp_server`, `.github/workflows`):
  - `target_count = 5`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - Source: `docs/audit/refactor/evidence/candidate8_deprecated_2026_02_exact_path_refcheck_2026-03-06.json`

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
