## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice-7 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether bounded gating cadence can improve on the slice-6 RI plateau while remaining below promotion authority semantics.
- **Candidate:** `ri challenger family slice7 execution`
- **Base SHA:** `601efdd00552a4de9e5d6cce54a58c84725e593c`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_execution_2026-03-24.md`
  - launch of `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - local outputs under `results/hparam_search/run_*`
  - local storage DB `results/hparam_search/storage/ri_challenger_family_slice7_3h_2024_v1.db`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
  - blind-2025 execution
  - YAML parameter changes unless a pure typo/path fix is required before launch

### Execution provenance

- Preferred launch state: clean working tree.
- Dirty-tree launch is **not approved** for slice-7.
- Any dirty path blocks launch.
- If a clean tree cannot be obtained, stop and request fresh governance review before execution.
- Launch is **gated by post-diff audit**: do not execute until the four slice-7 files have passed post-code governance review and all required gates below are green.

### Baseline anchor for comparison

Slice-7 comparisons must use the deterministic slice-6 anchor rule:

1. rank by validation score
2. if multiple tied winners remain, choose the member with highest train score
3. if train score also ties, fall back to the lexicographically smallest trial id

Under that rule, the explicit slice-6 anchor is `results/hparam_search/run_20260324_155438/validation/trial_005.json` with validation score `0.23646934335498004`.

### Preconditions

- canonical env flags must be set exactly:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- exact launch YAML must still declare `meta.runs.run_intent: research_slice`
- rerun `validate_optimizer_config.py` on the exact launch tree immediately before launch
- rerun `preflight_optuna_check.py` on the exact launch tree immediately before launch
- verify that `results/hparam_search/storage/ri_challenger_family_slice7_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
- no blind-2025 run belongs to this packet

### Evidence rules

- Compare the slice-7 validation winner directly against:
  - slice-6 plateau `0.23646934335498004`
  - slice-4 plateau `0.22516209452403432`
  - slice-3 plateau `0.22289051935876203`
- Treat incumbent `0.2616884080730424` as the governed current-head same-window same-canonical-mode control.
- Fresh launch evidence is mandatory; older pytest evidence is not sufficient by itself for execution approval.

### Success rule for this packet

- Slice-7 counts as a meaningful RI validation advance only if its validation winner **strictly exceeds** the slice-6 plateau `0.23646934335498004` under the same score version, windows, constraints, and canonical mode.
- A tie at that level, or a repeated no-separation top validation cluster at or below that level, must be reported as **hypothesis not confirmed**.
- Beating slice-6 does **not** imply promotion authority; incumbent control remains a separate governed comparison threshold.
- Blind-2025 or promotion escalation is **not allowed** inside this packet.

### Gates required

- file-scoped pre-launch checks:
  - `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_execution_2026-03-24.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - storage DB absence check
- mandatory runtime-governance anchors before launch:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- working tree is not clean at launch time
- storage DB already exists while `resume=false`
- validator or preflight fails on the exact launch tree
- any mandatory runtime-governance anchor fails
- launch would require editing `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- comparison would rely on non-canonical mode
- slice-7 fails to strictly beat the slice-6 plateau and someone attempts to treat the result as successful validation separation
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
- comparison versus slice-6 plateau, slice-4 plateau, slice-3 plateau, and incumbent same-head control status

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This packet approves only challenger evidence collection, not promotion.
- No edits to runtime defaults, champion files, or source/test logic are allowed as part of this execution step.
- Use fresh `study_name`, fresh sqlite path, `resume=false`, `n_jobs=1`, and `promotion.enabled=false` exactly as declared in the slice-7 YAML.
- If the run surfaces a promising winner, any blind-2025 or promotion discussion must be packeted separately.
