# Context Map — runner split-3 config / metadata / parameter-space

## Objective

Extract and semantically structure config-, metadata-, parameter-space-, and trial-artifact-preparation responsibilities from `src/core/optimizer/runner.py` while preserving `runner.py` as SSOT facade/orchestrator and keeping all execution semantics in place.

## Files to Modify

| File                                                | Purpose                                                                        | Planned change                                                                                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `src/core/optimizer/runner.py`                      | SSOT facade/orchestrator for optimizer flow                                    | Import extracted helpers, retain orchestration and execution ownership, keep `run_trial(...)` as facade owner |
| `src/core/optimizer/runner_config.py`               | New flat sibling module for config/metadata/parameter-space/trial-prep helpers | Hold extracted in-scope helpers and minimal preparation helpers used by `runner.py`                           |
| `tests/utils/test_optimizer_runner.py`              | Existing focused optimizer behavior coverage                                   | Update imports/expectations and add facade-owner / parity assertions only if required                         |
| `tests/utils/test_optuna_resume_signature.py`       | Signature/resume regression coverage                                           | Keep coverage green after helper extraction; no semantic changes                                              |
| `tests/utils/test_optimizer_json_cache_env_flag.py` | JSON cache flag semantics                                                      | Keep cache behavior stable after helper move                                                                  |
| `tests/utils/test_optimizer_duplicate_fixes.py`     | Search-space diagnostics / duplicate handling coverage                         | Keep `_estimate_optuna_search_space` semantics stable                                                         |

## In-scope symbols

- `_json_default(...)`
- `_load_json_with_retries(...)`
- `_read_json_cached(...)`
- `_atomic_write_text(...)`
- `OptimizerStrategy`
- `TrialConfig`
- `load_search_config(...)`
- `_trial_key(...)`
- `_get_default_config(...)`
- `_get_default_runtime_version(...)`
- `_get_backtest_defaults(...)`
- `_get_backtest_economics(...)`
- `_as_bool(...)`
- `_validate_date_range(...)`
- `_normalize_date(...)`
- `_resolve_sample_range(...)`
- `_load_existing_trials(...)`
- `_ensure_run_metadata(...)`
- `_serialize_meta(...)`
- `_deep_merge(...)`
- `_expand_value(...)`
- `_expand_dict(...)`
- `expand_parameters(...)`
- `_estimate_optuna_search_space(...)`
- `_derive_dates(...)`

### `run_trial(...)` scope-limited prep surface

Only these responsibilities may be extracted or reorganized behind helpers:

- trial key / fingerprint preparation
- config payload creation
- merged config preparation
- runtime/config provenance payload preparation
- cache lookup / cache write preparatory payload/path helpers
- artifact path preparation for trial/config/log files

### Ownership retained in `runner.py`

The following must stay in `runner.py` even if prep helpers are extracted:

- all branching that decides whether or how execution proceeds
- all subprocess/direct execution selection semantics
- retry/error/prune/abort/result parsing flow
- cache lookup/write decision semantics
- `run_trial(...)` facade/orchestration ownership
- `run_optimizer(...)` orchestration ownership

## Explicit scope OUT

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

## Direct dependencies

| File                                     | Relationship                                                       |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `src/core/config/authority.py`           | Provides `ConfigAuthority` used by `_get_default_config(...)`      |
| `src/core/utils/dict_merge.py`           | Provides `deep_merge_dicts(...)` used by `_deep_merge(...)`        |
| `src/core/utils/diffing/canonical.py`    | Provides `canonicalize_config(...)` used by `_trial_key(...)`      |
| `src/core/utils/diffing/trial_cache.py`  | Cache object used by `run_trial(...)` prep surface                 |
| `src/core/optimizer/param_transforms.py` | Provides transformed params consumed by merged config payload prep |

## Test files

| Test                                                                                                       | Coverage                                                                   |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `tests/utils/test_optimizer_runner.py`                                                                     | `run_trial(...)`, metadata, config payloads, date parsing, helper behavior |
| `tests/utils/test_optuna_resume_signature.py`                                                              | Resume-signature semantics that must remain import-stable                  |
| `tests/utils/test_optimizer_json_cache_env_flag.py`                                                        | `_read_json_cached(...)` flag behavior                                     |
| `tests/utils/test_optimizer_duplicate_fixes.py`                                                            | `_estimate_optuna_search_space(...)` stability                             |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                    | Import smoke / circular import guard                                       |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | Pipeline invariant guard                                                   |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | Feature-cache invariance / deterministic hash selector                     |

## Risks

- Trial-key / fingerprint drift if canonicalization inputs or JSON shape change.
- Cache/global lock drift if module-level state is split incorrectly.
- Provenance/config payload drift if field content or preparation ordering changes.
- Circular imports if the new sibling module imports back from `runner.py`.
- Scope drift if prep extraction starts moving execution decisions.

## Refactor notes

- Prefer one flat sibling module under `src/core/optimizer/`.
- No new package/subfolder is justified for this slice.
- `runner.py` remains the public entrypoint and orchestrator.
- Any borderline helper with mixed slice ownership should stay in `runner.py` until ownership is unambiguous.
