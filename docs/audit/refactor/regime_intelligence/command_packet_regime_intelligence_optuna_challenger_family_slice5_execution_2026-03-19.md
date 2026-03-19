## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-challenger-slice4-eval-2026-03-19`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice-5 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether its validation winner strictly exceeds the slice-4 plateau and meaningfully advances the RI challenger family.
- **Candidate:** `ri challenger family slice5 execution`
- **Base SHA:** `9566e8d9017d278356bcf086ee6f16db46ff231e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice5_execution_2026-03-19.md`
  - launch of `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - local outputs under `results/hparam_search/run_*`
  - local storage DB `results/hparam_search/storage/ri_challenger_family_slice5_3h_2024_v1.db`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
  - blind-2025 execution
  - YAML parameter changes unless a pure typo/path fix is required before launch

### Execution provenance

- Preferred launch state: clean working tree.
- Allowed fallback launch state: dirty working tree containing **exactly** these eight paths and nothing else:
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_execution_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice5_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice5_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice5_execution_2026-03-19.md`
- This exception is provenance-only; the effective launch configuration remains solely `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`.
- Any out-of-scope dirty path blocks launch.
- If launched from a dirty tree, record exact `HEAD` SHA and the exact dirty path list in the execution report.

### Preconditions

- canonical env flags must be set exactly:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- rerun `validate_optimizer_config.py` on the exact launch tree immediately before launch
- rerun `preflight_optuna_check.py` on the exact launch tree immediately before launch
- verify that `results/hparam_search/storage/ri_challenger_family_slice5_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`

### Evidence rules

- Prior anchor-pytest evidence from this branch session may be reused only if `HEAD` is unchanged and no runtime-affecting files changed since pass.
- Runtime-affecting paths include at minimum:
  - `src/**`
  - `tests/**`
  - `scripts/preflight/**`
  - `scripts/validate/**`
  - `config/runtime.json`
  - `conftest.py`
  - `pyproject.toml`
- If any runtime-affecting path changed, rerun the full anchor bundle before launch.
- Validator, preflight, and storage-absence checks must be rerun immediately before launch.
- Compare the slice-5 validation winner directly against:
  - slice-4 plateau `0.22516209452403432`
  - slice-3 plateau `0.22289051935876203`
- Treat incumbent `0.2617` as a governed current-head control **only if** same-HEAD + same-canonical-mode evidence is available; otherwise report it as a prior reference score only.

### Success rule for this packet

- Slice-5 counts as a meaningful validation advance only if its validation winner **strictly exceeds** the slice-4 plateau `0.22516209452403432` under the same score version, windows, constraints, and canonical mode.
- A tie at that level, or a repeated no-separation top validation cluster at or below that level, must be reported as **hypothesis not confirmed**.
- Blind-2025 or promotion escalation is **not allowed** inside this packet, and must not be triggered by a tie-level outcome.

### Gates required

- immediate pre-launch checks:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - storage DB absence check
- reuse-eligible anchor bundle from this branch session only if the reuse rules above remain true:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- storage DB already exists while `resume=false`
- any out-of-scope dirty path appears before launch
- validator or preflight fails on the exact launch tree
- launch would require editing `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- comparison would rely on non-canonical mode
- slice-5 fails to strictly beat the slice-4 plateau and someone attempts to treat the result as successful validation separation
- anyone attempts to reinterpret the run as automatic promotion authority

### Output required

- **Implementation Report**
- exact launch command and env flags used
- exact `HEAD` SHA and dirty/clean state at launch time
- exact dirty path list if dirty launch is used
- storage DB path
- created run directory path
- `run_meta.json` path
- `best_trial.json` path
- validation winner summary
- comparison versus slice-4 plateau, slice-3 plateau, and incumbent prior reference/control status

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This packet approves only challenger evidence collection, not promotion.
- No edits to runtime defaults, champion files, or source/test logic are allowed as part of this execution step.
- If the run surfaces a promising winner, any blind-2025 or promotion discussion must be packeted separately.

### Execution summary (2026-03-19)

- Run completed under `results/hparam_search/run_20260319_122140` with `run_meta.json` and `best_trial.json` recorded at that path.
- `run_meta.json` reports `git_commit=9566e8d9017d278356bcf086ee6f16db46ff231e`, `score_version=v2`, `n_trials=96`, `best_value=0.28077646648091525`, and `validated=5` for the validation window `2024-07-01` -> `2024-12-31`.
- Validation artifact `results/hparam_search/run_20260319_122140/validation/tBTCUSD_3h_trial_001.json` reports `total_return_pct=1.3106194350188525`, `profit_factor=1.8562597317394178`, `max_drawdown=0.03176056588418942`, and `num_trades=66`.
- Spot checks on `validation/tBTCUSD_3h_trial_002.json` and `validation/tBTCUSD_3h_trial_003.json` showed the same validation metrics despite differing merged-config values and fingerprints, so slice-5 did not demonstrate usable separation inside the reopened exit/hold/override surface.
- Result: hypothesis not confirmed. Slice-5 did **not** strictly beat the slice-4 plateau `0.22516209452403432`, so it is **not promotable** and slice-4 remains the current RI challenger winner.
