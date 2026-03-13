# Command Packet — runner split-2 Optuna orchestration / validation / promotion

## COMMAND PACKET

- **Mode:** `STRICT` — source: user-required HIGH-risk / full gated protocol override
- **Risk:** `HIGH` — why: touches optimizer-core orchestration in `src/core/optimizer/*`, including Optuna study creation, resume-safety, validation candidate selection, score-version comparability, and champion-promotion veto/selection logic
- **Required Path:** `Full`
- **Objective:** Extract and semantically structure Optuna orchestration, validation-flow, resume-safety, comparability, and champion-promotion responsibilities from `src/core/optimizer/runner.py` into one flat sibling module while preserving `runner.py` as SSOT facade/orchestrator and preserving all default behavior.
- **Candidate:** `runner split-2 optuna-orchestration-validation-promotion`
- **Base SHA:** `5549ad69223a2ddde9a2b04f552069475f971342`

### Scope

- **Scope IN:**
  - `src/core/optimizer/runner.py`
  - `src/core/optimizer/runner_optuna_orchestration.py`
  - `tests/utils/test_optimizer_runner.py`
  - `tests/utils/test_optuna_resume_signature.py`
  - `tests/utils/test_optuna_rdbstorage_engine_kwargs.py`
  - `tests/utils/test_optimizer_duplicate_fixes.py`
  - `docs/audit/refactor/optimizer/context_map_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md`
  - `docs/audit/refactor/optimizer/command_packet_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md`
- **Scope OUT:**
  - Any other file under `src/core/optimizer/` unless required by import repair within Scope IN
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
  - trial execution / backtest-result pipeline ownership
  - config-/metadata-/parameter-space split concerns owned by split-1
  - `config/**`
  - `src/core/backtest/**`
  - `mcp_server/**`
- **Expected changed files:** `6-8`
- **Max files touched:** `8`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `runner.py` must remain the SSOT facade/orchestrator.
- `run_optimizer(...)` must remain the top-level owner of optimizer orchestration and public entrypoint behavior.
- Validation and champion promotion may delegate internal helpers, but the answer to "var sker champion-beslutet?" must still be traceable from `run_optimizer(...)`.
- `runner.py` must retain top-level validation-on/off decision, top-level promotion-on/off decision, `results_for_promotion` selection, and final `ChampionManager.should_replace(...)` / `write_champion(...)` decision.
- The answers to these questions must remain explicit after extraction:
  - var väljs study/sampler/pruner?
  - var verifieras resume-säkerhet?
  - var avgörs comparability?
  - vilken komponent vetoade promotion eller validation?
  - var sker champion-beslutet?
- `_candidate_from_result(...)` contract must remain untouched; split-2 may only respect it at the validation/promotion boundary.
- Public import/patch surfaces through `core.optimizer.runner` must remain compatible for existing tests and hidden callers.
- Moved helpers must remain re-exported/late-bound so patching `core.optimizer.runner._create_optuna_study`, `core.optimizer.runner._run_optuna`, `_select_optuna_sampler`, or resume-signature helpers still affects the behavior exercised through `core.optimizer.runner`.
- No circular imports: the new sibling module must not import runtime execution helpers from split-1-owned concerns in a way that creates boundary drift.
- No opportunistic cleanup outside this slice.

### Repo-local skill evidence

- `repo_clean_refactor` reviewed and applied for scope lock / minimal reversible diff / no-behavior-change discipline.
- `optuna_run_guardrails` reviewed and applied for study/resume/validation/objective guardrails.

### Gates required

#### PRE

- `python -m ruff check src/core/optimizer/runner.py tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optuna_rdbstorage_engine_kwargs.py tests/utils/test_optimizer_duplicate_fixes.py`
- `python -m pytest tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optuna_rdbstorage_engine_kwargs.py tests/utils/test_optimizer_duplicate_fixes.py tests/backtest/test_backtest_determinism_smoke.py tests/governance/test_import_smoke_backtest_optuna.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py -q`

#### POST

- `python -m ruff check src/core/optimizer/runner.py src/core/optimizer/runner_optuna_orchestration.py tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optuna_rdbstorage_engine_kwargs.py tests/utils/test_optimizer_duplicate_fixes.py`
- `python -m pytest tests/utils/test_optimizer_runner.py tests/utils/test_optuna_resume_signature.py tests/utils/test_optuna_rdbstorage_engine_kwargs.py tests/utils/test_optimizer_duplicate_fixes.py tests/backtest/test_backtest_determinism_smoke.py tests/governance/test_import_smoke_backtest_optuna.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py -q`
- `python -m bandit -r src -c bandit.yaml -q`

### Stop Conditions

- Scope drift outside the defined slice or beyond the listed files
- Any drift in study/sampler/pruner selection, resume-signature verification, score-version policy, validation candidate selection, comparability warning semantics, or champion-promotion veto semantics
- Any ownership drift that moves top-level optimizer orchestration out of `runner.py`
- Any change that entangles split-2 with split-1-owned config/metadata/parameter-space or trial-result pipeline responsibilities
- Any loss of patch/import compatibility through `core.optimizer.runner` for moved helpers
- Determinism / feature-cache / pipeline-invariant regression

### Output required

- **Implementation Report** with scope summary, file changes, exact commands, outcomes, and residual risks
- **PR evidence template** after Opus post-diff audit

### Pre-review request focus

Opus should specifically confirm that the proposed extraction boundary is semantically strong enough to answer:

1. Var väljs study/sampler/pruner?
2. Var verifieras resume-säkerhet?
3. Var avgörs comparability?
4. Vilken komponent vetoade promotion eller validation?
5. Var sker champion-beslutet?

And reject the plan if the boundary is too thin, too wrapper-heavy, or crosses into split-1/trial-result ownership.
