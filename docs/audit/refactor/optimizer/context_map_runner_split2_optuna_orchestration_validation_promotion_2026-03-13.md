# Context Map — runner split-2 Optuna orchestration / validation / promotion

## Objective

Extract and semantically structure Optuna orchestration, validation-flow, resume-safety,
comparability, and champion-promotion responsibilities from `src/core/optimizer/runner.py`
while preserving `runner.py` as SSOT facade/orchestrator and preserving all default behavior.

## Files to Modify

| File                                                                                                                 | Purpose                                                               | Planned change                                                                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/core/optimizer/runner.py`                                                                                       | SSOT facade/orchestrator for optimizer flow                           | Retain top-level orchestration in `run_optimizer(...)`, import extracted helpers, and keep boundary ownership explicit                                                                     |
| `src/core/optimizer/runner_optuna_orchestration.py`                                                                  | New flat sibling module for split-2 concerns                          | Hold extracted helpers for resume-signature checks, score-version/comparability checks, sampler/pruner/study selection, Optuna objective orchestration, and validation candidate selection |
| `tests/utils/test_optimizer_runner.py`                                                                               | Main focused coverage for optimizer orchestration                     | Update imports/patch surfaces and add scoped parity tests for validation/promotion/comparability/facade ownership only where needed                                                        |
| `tests/utils/test_optuna_resume_signature.py`                                                                        | Resume-safety regression surface                                      | Keep signature verification semantics and score-version policy stable after extraction                                                                                                     |
| `tests/utils/test_optuna_rdbstorage_engine_kwargs.py`                                                                | Study creation / RDB storage configuration coverage                   | Keep `_create_optuna_study(...)` engine-kwargs and heartbeat semantics stable                                                                                                              |
| `tests/utils/test_optimizer_duplicate_fixes.py`                                                                      | `_run_optuna(...)` / sampler defaults / validation objective behavior | Keep sampler/pruner choice, objective duplicate handling, timeout/end_at, and validation-related behavior stable                                                                           |
| `docs/audit/refactor/optimizer/context_map_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md`    | Governance context map                                                | New slice-local context map                                                                                                                                                                |
| `docs/audit/refactor/optimizer/command_packet_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md` | Commit contract / governance evidence                                 | New slice-local command packet                                                                                                                                                             |

## In-scope symbols

- `_compute_optuna_resume_signature(...)`
- `_verify_or_set_optuna_study_signature(...)`
- `_verify_or_set_optuna_study_score_version(...)`
- `_select_top_n_from_optuna_storage(...)`
- `_resolve_score_version_for_optimizer(...)`
- `_extract_score_version_from_result_payload(...)`
- `_extract_score_version_from_champion_record(...)`
- `_extract_results_path_from_champion_record(...)`
- `_enforce_score_version_compatibility(...)`
- `_dig(...)`
- `_load_backtest_info_from_results_path(...)`
- `_collect_comparability_warnings(...)`
- `_select_optuna_sampler(...)`
- `_select_optuna_pruner(...)`
- `_create_optuna_study(...)`
- `_run_optuna(...)`
- split-2-owned portions of `run_optimizer(...)` required to keep it as facade/orchestrator

### Borderline read-only contract reference

- `_candidate_from_result(...)` may be referenced only to preserve the candidate contract at the
  validation/promotion boundary.
- Ownership of trial-result payload construction remains out of scope and must not migrate into
  this slice.

## Explicit scope OUT

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
- `_suggest_parameters(...)`
- `_create_run_id(...)`
- `_submit_trials(...)`
- `TrialContext`
- `_execute_trial_task(...)`
- `_extract_results_path_from_log(...)`
- `_extract_num_trades(...)`
- `_check_abort_heuristic(...)`
- `_trial_requests_htf_exits(...)`
- `_run_backtest_direct(...)`
- `_build_backtest_cmd(...)`
- `run_trial(...)`
- any config-/metadata-/parameter-space split concerns that belong to split-1
- any trial-result-pipeline ownership beyond respecting `_candidate_from_result(...)` contract

## Direct dependencies

| File                                     | Relationship                                                                                         |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `src/core/optimizer/champion.py`         | Provides `ChampionCandidate` / `ChampionManager` consumed at promotion boundary                      |
| `src/core/optimizer/scoring.py`          | Existing score payload shape constrains score-version/comparability helpers                          |
| `src/core/utils/diffing/canonical.py`    | Resume-signature canonicalization dependency                                                         |
| `src/core/utils/diffing/results_diff.py` | Existing `_dig(...)` analogue provides external reference pattern only; no ownership move planned    |
| `src/core/utils/optuna_helpers.py`       | `param_signature(...)`, `NoDupeGuard`, and seeding helpers remain dependencies of `_run_optuna(...)` |

## Test files

| Test                                                                                                       | Coverage                                                                                                               |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `tests/utils/test_optimizer_runner.py`                                                                     | `run_optimizer(...)` facade, validation selection, promotion gate, comparability warnings, score-version compatibility |
| `tests/utils/test_optuna_resume_signature.py`                                                              | resume-signature verification + external/repo-relative signature semantics                                             |
| `tests/utils/test_optuna_rdbstorage_engine_kwargs.py`                                                      | sampler/pruner/study creation heartbeat + SQLite engine kwargs                                                         |
| `tests/utils/test_optimizer_duplicate_fixes.py`                                                            | `_run_optuna(...)`, sampler defaults, duplicate handling, timeout/end_at, validation fallback surface                  |
| `tests/governance/test_import_smoke_backtest_optuna.py`                                                    | import smoke / circular-import guard for optimizer module split                                                        |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | named STRICT determinism replay selector                                                                               |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant guard required by STRICT path                                                                       |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | deterministic hash / feature-cache invariance selector required by STRICT path                                         |

## Planned module boundary

### Retained in `runner.py`

- public entrypoint / facade role of `run_optimizer(...)`
- top-level choice between grid and Optuna strategies
- top-level decision to run validation and champion promotion
- selection of `results_for_promotion`
- final champion decision via `ChampionManager.should_replace(...)` / `write_champion(...)`
- orchestration order and user-visible logging semantics
- boundary ownership for anything ambiguous between split-2 and split-1
- patch/import compatibility surface through `core.optimizer.runner` for moved helpers used by tests/hidden callers

### Candidate extraction target: `runner_optuna_orchestration.py`

- study/sampler/pruner selection
- resume-safety signature and score-version study guards
- validation top-N recovery from Optuna storage
- score-version / comparability extraction and warning helpers
- Optuna objective orchestration (`_run_optuna(...)`)

## Risks

- Public test surfaces currently patch/import `core.optimizer.runner` directly, so re-export and
  monkeypatch compatibility must remain stable.
- `run_optimizer(...)` mixes facade responsibilities with slice-owned subflows; extraction must not
  accidentally move top-level orchestration out of `runner.py`.
- Existing tests patch `core.optimizer.runner._create_optuna_study` and related helpers directly;
  extraction must preserve `core.optimizer.runner` as the effective patch surface.
- `_run_optuna(...)` touches both study creation and objective semantics; wrapper-only extraction is
  insufficient, but over-extraction would drift into split-1/trial-result ownership.
- Promotion/comparability logic depends on persisted result payload shapes and champion metadata;
  any field-shape drift would be behavior change.
- Validation fallback through `_select_top_n_from_optuna_storage(...)` is the seam that answers
  "var sker validation-urvalet?" and must stay traceable after extraction.

## Refactor notes

- Prefer one flat sibling module under `src/core/optimizer/`.
- No new package/subfolder is justified for this slice.
- `runner.py` remains the public entrypoint and orchestrator.
- If a helper looks shared between slices, keep the facade/anropsyta in `runner.py` and move only
  the unambiguous internal logic.
