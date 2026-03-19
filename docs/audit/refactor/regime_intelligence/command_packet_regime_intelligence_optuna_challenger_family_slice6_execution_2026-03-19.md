## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-challenger-slice4-eval-2026-03-19`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice-6 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether its validation winner strictly exceeds the slice-4 plateau and meaningfully advances the RI challenger family.
- **Candidate:** `ri challenger family slice6 execution`
- **Base SHA:** `9566e8d9017d278356bcf086ee6f16db46ff231e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice6_execution_2026-03-19.md`
  - launch of `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
  - local outputs under `results/hparam_search/run_*`
  - local storage DB `results/hparam_search/storage/ri_challenger_family_slice6_3h_2024_v1.db`
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
- Dirty-tree launch is **not approved** for slice-6.
- Any dirty path blocks launch.
- If a clean tree cannot be obtained, stop and request fresh governance review before execution.

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
- verify that `results/hparam_search/storage/ri_challenger_family_slice6_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
- no blind-2025 run belongs to this packet

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
- Compare the slice-6 validation winner directly against:
  - slice-4 plateau `0.22516209452403432`
  - slice-3 plateau `0.22289051935876203`
- Treat incumbent `0.2617` as a governed current-head control **only if** same-HEAD + same-canonical-mode evidence is available; otherwise report it as a prior reference score only.

### Success rule for this packet

- Slice-6 counts as a meaningful validation advance only if its validation winner **strictly exceeds** the slice-4 plateau `0.22516209452403432` under the same score version, windows, constraints, and canonical mode.
- A tie at that level, or a repeated no-separation top validation cluster at or below that level, must be reported as **hypothesis not confirmed**.
- Blind-2025 or promotion escalation is **not allowed** inside this packet, and must not be triggered by a tie-level outcome.

### Gates required

- immediate pre-launch checks:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
  - storage DB absence check
- reuse-eligible anchor bundle from this branch session only if the reuse rules above remain true:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- working tree is not clean at launch time
- storage DB already exists while `resume=false`
- validator or preflight fails on the exact launch tree
- launch would require editing `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- comparison would rely on non-canonical mode
- slice-6 fails to strictly beat the slice-4 plateau and someone attempts to treat the result as successful validation separation
- anyone attempts to reinterpret the run as automatic promotion authority

### Output required

- **Implementation Report**
- exact launch command and env flags used
- exact `HEAD` SHA and clean/dirty state at launch time
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
