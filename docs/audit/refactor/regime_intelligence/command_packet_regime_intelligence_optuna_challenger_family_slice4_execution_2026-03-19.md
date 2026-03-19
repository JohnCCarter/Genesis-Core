## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-challenger-slice4-eval-2026-03-19`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice-4 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether its validation winner beats the slice-3 plateau and, if same-HEAD control evidence is available, the incumbent control.
- **Candidate:** `ri challenger family slice4 execution`
- **Base SHA:** `9566e8d9017d278356bcf086ee6f16db46ff231e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_execution_2026-03-19.md`
  - launch of `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - local outputs under `results/hparam_search/run_*`
  - local storage DB `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_v1.db`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
  - YAML parameter changes unless a pure typo/path fix is required before launch

### Execution provenance

- Preferred launch state: clean working tree.
- Allowed fallback launch state: dirty working tree containing **only** these slice-4 scoped files:
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_execution_2026-03-19.md`
- If launched from a dirty tree, that fact must be recorded in the execution report.

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
- verify that `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
- no blind-2025 run belongs to this packet

### Evidence rules

- Prior anchor-pytest evidence from this branch session may be reused only if HEAD and runtime-affecting files are unchanged since pass.
- Validator, preflight, and storage-absence checks must be rerun immediately before launch.
- Compare the slice-4 validation winner directly against the slice-3 plateau `0.22289051935876203`.
- Treat incumbent `0.2617` as a governed current-head control **only if** same-HEAD + same-canonical-mode evidence is available; otherwise report it as a prior reference score pending current-head control replay.

### Gates required

- immediate pre-launch checks:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - storage DB absence check
- reuse-eligible anchor bundle from this branch session:
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
- anyone attempts to reinterpret the run as automatic promotion authority

### Output required

- **Implementation Report**
- exact launch command and env flags used
- exact HEAD SHA and dirty/clean state at launch time
- storage DB path
- created run directory path
- `run_meta.json` path
- `best_trial.json` path
- validation winner summary
- comparison versus slice-3 plateau and incumbent reference/control status

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This packet approves only challenger evidence collection, not promotion.
- No edits to runtime defaults, champion files, or source/test logic are allowed as part of this execution step.
- If the run surfaces a promising winner, any blind-2025 or promotion discussion must be packeted separately.
