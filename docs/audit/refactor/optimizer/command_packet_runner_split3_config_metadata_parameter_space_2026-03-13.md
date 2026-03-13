# Command Packet — runner split-3 config / metadata / parameter-space

## COMMAND PACKET

- **Mode:** `STRICT` — source: user-required HIGH-risk / full gated protocol override
- **Risk:** `HIGH` — why: touches optimizer-core preparation semantics in `src/core/optimizer/*`, including config loading, metadata/provenance writing, parameter expansion, trial fingerprinting, cache-prep, and trial artifact preparation
- **Required Path:** `Full`
- **Objective:** Extract and semantically structure config-, metadata-, parameter-space-, and trial-artifact-preparation responsibilities from `src/core/optimizer/runner.py` into one flat sibling module while preserving `runner.py` as SSOT facade/orchestrator and preserving all default behavior.
- **Candidate:** `runner split-3 config-metadata-parameter-space`
- **Base SHA:** `5549ad69223a2ddde9a2b04f552069475f971342`

### Scope

- **Scope IN:**
  - `src/core/optimizer/runner.py`
  - `src/core/optimizer/runner_config.py`
  - `tests/utils/test_optimizer_runner.py`
  - `tests/utils/test_optuna_resume_signature.py`
  - `tests/utils/test_optimizer_json_cache_env_flag.py`
  - `tests/utils/test_optimizer_duplicate_fixes.py`
  - `docs/audit/refactor/optimizer/context_map_runner_split3_config_metadata_parameter_space_2026-03-13.md`
  - `docs/audit/refactor/optimizer/command_packet_runner_split3_config_metadata_parameter_space_2026-03-13.md`
- **Scope OUT:**
  - Any other file under `src/core/optimizer/` unless required by import repair within Scope IN
  - `_extract_results_path_from_log(...)`
  - `_candidate_from_result(...)`
  - `_extract_num_trades(...)`
  - `_check_abort_heuristic(...)`
  - `_trial_requests_htf_exits(...)`
  - `_run_backtest_direct(...)`
  - `_build_backtest_cmd(...)`
  - trial execution / subprocess / direct backtest flow
  - `_compute_optuna_resume_signature(...)`
  - `_verify_or_set_optuna_study_signature(...)`
  - `_verify_or_set_optuna_study_score_version(...)`
  - `_resolve_score_version_for_optimizer(...)`
  - `_select_optuna_sampler(...)`
  - `_select_optuna_pruner(...)`
  - `_create_optuna_study(...)`
  - `_suggest_parameters(...)`
  - `_run_optuna(...)`
  - `_submit_trials(...)`
  - `TrialContext`
  - `_execute_trial_task(...)`
  - `run_optimizer(...)`
  - champion-promotion / validation orchestration
  - `config/**`
  - `src/core/backtest/**`
  - `mcp_server/**`
- **Expected changed files:** `6-8`
- **Max files touched:** `8`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `runner.py` must remain the SSOT facade/orchestrator.
- `run_trial(...)` must remain the facade owner of trial preparation and execution flow.
- Only prep/materialization helpers may move; **all branching that decides whether/how execution proceeds remains in `runner.py`.**
- Cache lookup/write **decision semantics** stay in `runner.py`; only preparatory path/payload helpers may move.
- Merge order, canonicalization inputs, fingerprint inputs, provenance fields, and artifact path generation must remain semantically identical.
- Module-level cache/lock semantics (`_TRIAL_KEY_CACHE*`, `_DEFAULT_CONFIG*`, `_BACKTEST_DEFAULTS*`, `_JSON_CACHE`) must remain unchanged in behavior.
- No circular imports: the new sibling module must not import `core.optimizer.runner`.
- No opportunistic cleanup outside this slice.

### Repo-local skill evidence

- `repo_clean_refactor` reviewed and applied for scope lock / minimal diff / no-behavior-change discipline.
- `python_engineering` reviewed and applied for type/style/test discipline.

### Gates required

#### PRE

- `python -m ruff check src/core/optimizer/runner.py tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optimizer_json_cache_env_flag.py tests/utils/test_optimizer_duplicate_fixes.py`
- `python -m pytest tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optimizer_json_cache_env_flag.py tests/utils/test_optimizer_duplicate_fixes.py tests/governance/test_import_smoke_backtest_optuna.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py -q`

#### POST

- `python -m ruff check src/core/optimizer/runner.py src/core/optimizer/runner_config.py tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optimizer_json_cache_env_flag.py tests/utils/test_optimizer_duplicate_fixes.py`
- `python -m pytest tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optimizer_json_cache_env_flag.py tests/utils/test_optimizer_duplicate_fixes.py tests/governance/test_import_smoke_backtest_optuna.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py -q`
- `python -m bandit -r src -c bandit.yaml -q`

### Stop Conditions

- Scope drift outside the defined slice or beyond the listed files
- Any fingerprint / trial-key / metadata / config payload drift without explicit approval
- Any execution-flow ownership drift out of `runner.py`
- Circular import introduced between `runner.py` and the extracted module
- Determinism / feature-cache / pipeline-invariant regression

### Output required

- **Implementation Report** with scope summary, file changes, exact commands, outcomes, and residual risks
- **PR evidence template** after Opus post-diff audit

### Pre-review outcome

- **Opus 4.6 verdict:** `APPROVED_WITH_NOTES`
- **Required notes applied in this packet:**
  - PRE upgraded to full STRICT baseline for this slice
  - `run_trial(...)` retained-ownership rule made explicit
  - cache lookup/write decision semantics explicitly retained in `runner.py`
  - identity-sensitive merge/provenance/fingerprint semantics called out as locked
