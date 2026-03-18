## COMMAND PACKET

- **Mode:** `STRICT` — source: explicit task override; branch `feature/*` would otherwise resolve to `RESEARCH`
- **Risk:** `MED` — why: config/docs-only experiment scaffolding under `config/optimizer/**`, with no runtime/default/champion changes permitted
- **Required Path:** `Full`
- **Objective:** Add the second narrow Regime Intelligence Optuna challenger-family campaign for `tBTCUSD 3h`, using the validated `trial_001/002/005` RI family as the baseline while explicitly deferring promotion/default/cutover decisions.
- **Candidate:** `ri challenger family slice2`
- **Base SHA:** `71db8e42`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
  - `docs/features/feature-ri-optuna-train-validate-blind-1.md` _(only if a tiny follow-up note becomes necessary)_
- **Scope OUT:**
  - `config/strategy/champions/**`
  - `config/runtime.json`
  - `src/**`
  - `tests/**`
  - committed `results/**`
  - promotion/default/cutover semantics
  - blind 2025 fixed-candidate execution
  - direct incumbent overlay migration path
  - committed `tmp/**`
- **Expected changed files:** `3-4`
- **Max files touched:** `4`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
- Temporary smoke-step before `READY_FOR_REVIEW`:
  - derive an uncommitted smoke YAML under `tmp/`
  - use unique temporary `study_name` + `storage`
  - run a reduced-budget optimizer start to prove the config boots cleanly without storage reuse ambiguity
- STRICT evidence anchors before `READY_FOR_REVIEW`:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- Any need to touch `src/**`, `tests/**`, `config/runtime.json`, or champion files
- Any need to widen the slice into clarity exploration
- Any implication that blind 2025 candidate freeze already exists
- Any reuse of an existing storage DB while `resume: false`
- Any need to commit `results/**` or temporary smoke artifacts as part of this slice
- Any evidence that the new YAML cannot be validated/preflighted/smoke-started cleanly

### Output required

- **Implementation Report**
- **PR evidence template**
- **Config artifact:** `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
- **Boundary note:** this slice preserves incumbent control and RI challenger-family research only; promotion/default/cutover remain out of scope

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice creates experiment scaffolding only; it must not alter runtime defaults or champion behavior.
- `authority_mode = regime_module` is fixed only inside this isolated optimizer experiment scaffold and must not be interpreted as a runtime/default change.
- Reduced verification is allowed only relative to a full-repo pytest sweep; STRICT minimum evidence still applies.
- The new YAML must pin fresh `study_name`, fresh `storage`, and explicit `score_version`.
- The new YAML must preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Blind 2025 remains a follow-up slice after candidate freeze.
