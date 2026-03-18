## COMMAND PACKET

- **Mode:** `STRICT` — source: explicit task override; branch `feature/*` would otherwise resolve to `RESEARCH`
- **Risk:** `MED` — why: config/docs-only experiment scaffolding under `config/optimizer/**`, with no runtime/default/champion changes permitted
- **Required Path:** `Full`
- **Objective:** Add the first minimal Regime Intelligence Optuna train+validation campaign for `tBTCUSD 3h`, using a narrow authority + risk-state search space, while explicitly deferring blind 2025 fixed-candidate evaluation to a later slice.
- **Candidate:** `ri optuna train validate slice1`
- **Base SHA:** `12c2a1cc`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md`
  - `config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
  - `docs/features/feature-ri-optuna-train-validate-blind-1.md` _(only if a tiny status/task update becomes necessary)_
- **Scope OUT:**
  - `config/strategy/champions/**`
  - `config/runtime.json`
  - `src/**`
  - `tests/**`
  - blind 2025 fixed-candidate config generation
  - promotion/default/cutover semantics
  - live/runtime behavior changes
- **Expected changed files:** `3-4`
- **Max files touched:** `4`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
- Focused STRICT evidence before `READY_FOR_REVIEW` claim:
  - document structural review of nested `runs.validation.*` against the runner's validation flow
  - cite or rerun a focused determinism/pipeline invariant anchor if needed for review confidence

### Stop Conditions

- Any need to touch `src/**`, `tests/**`, `config/runtime.json`, or champion files
- Any need to widen the search space to clarity in slice 1
- Any implication that blind 2025 candidate freeze already exists
- Any reuse of an old storage DB while `resume: false`
- Any evidence that the new YAML cannot be validated cleanly by validator/preflight

### Output required

- **Implementation Report**
- **PR evidence template**
- **Config artifact:** `config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
- **Boundary note:** blind 2025 fixed-candidate YAML is explicitly deferred until a train+validation winner is frozen

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice creates experiment scaffolding only; it must not alter runtime defaults or champion behavior.
- Reduced verification is allowed only relative to a full-repo pytest sweep; STRICT minimum evidence still applies.
- The new YAML must pin fresh `study_name`, fresh `storage`, and explicit `score_version`.
- The target plan remains train `2023-01-01..2024-06-30`, but slice 1 may clamp the actual train start to the first fully covered frozen `tBTCUSD_3h` calendar day if preflight proves the full span is unavailable.
- The new YAML must use validation `2024-07-01..2024-12-31`.
- Blind 2025 remains a follow-up slice after candidate freeze.
