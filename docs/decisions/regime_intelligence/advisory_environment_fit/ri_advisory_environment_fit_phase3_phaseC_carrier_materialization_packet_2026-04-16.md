# RI advisory environment-fit Phase 3 phaseC carrier materialization packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `blocked / donor cfg fails ConfigAuthority validation when copied unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded creation of one inert config artifact under `config/strategy/candidates/3h/`; no `src/**`, no active runtime/champion change, no capture run.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json` into one fixed, inert research-carrier wrapper so a later slice can decide whether capture v2 should open.
- **Candidate:** `RI advisory environment-fit phaseC carrier materialization`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Repo skills invoked:** `python_engineering`, `config_authority_lifecycle_check`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_carrier_materialization_packet_2026-04-16.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_phaseC_oos_materialized_carrier_20260416.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `tmp/**`
  - `results/**`
  - donor artifact `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
  - any capture run
  - any baseline implementation
  - any ML/model work
  - any runtime/default/champion change
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_carrier_materialization_packet_2026-04-16.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_phaseC_oos_materialized_carrier_20260416.json`
- **Max files touched:** `2`

### Hard invariants

1. **Donor lock:** only donor `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json` is allowed.
2. **Executable payload lock:** new artifact top-level `cfg` must be deep-equal to donor top-level `merged_config`.
3. **No cfg authoring:** no new field, including `strategy_family`, may be added inside `cfg`.
4. **Inert metadata only:** all provenance / RI-intent classification must live at top level only and must not be runtime-authoritative.
5. **Hard stop:** if `cfg == donor.merged_config` cannot be preserved exactly, stop rather than patch semantics.
6. **Inertness:** artifact path under `config/strategy/candidates/3h/` must remain non-auto-loaded by runtime/champion selectors.

### Allowed inert metadata

Top-level inert metadata may include only:

- `trial_id`
- `source_artifact`
- `source_trial`
- `source_runtime_version`
- `materialized_carrier`
- `intended_strategy_family`

These fields are descriptive only.
They must not be consumed by runtime validation or loader paths in this slice.

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_carrier_materialization_packet_2026-04-16.md config/strategy/candidates/3h/tBTCUSD_3h_phaseC_oos_materialized_carrier_20260416.json`
- `python -c` validation that:
  - loads donor artifact,
  - asserts new artifact `cfg` deep-equals donor `merged_config`,
  - runs `ConfigAuthority().validate(new_artifact['cfg'])`,
  - asserts `ChampionLoader.CHAMPIONS_DIR` resolves only to `config/strategy/champions`
- `pytest tests/governance/test_config_ssot.py::test_regime_unified_alias_only_is_canonicalized_before_persist`
- `pytest tests/governance/test_config_ssot.py::test_regime_unified_alias_non_dict_is_rejected`
- `pytest tests/governance/test_config_ssot.py::test_regime_unified_alias_extra_key_is_rejected`
- `pytest tests/integration/test_config_api_e2e.py::test_runtime_endpoints_e2e_regime_unified_alias_bridge`
- `pytest tests/utils/test_champion_loader.py`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- any need to modify donor `merged_config`
- any need to add `strategy_family` or other new semantics inside `cfg`
- any evidence that `config/strategy/candidates/**` is auto-loaded by runtime/champion path
- any failed deep-equality / canonicalized-hash check between donor `merged_config` and new artifact `cfg`
- any failed config-authority validation

### Output required

- one governance packet
- one inert materialized carrier artifact
- verification evidence that `cfg` stayed donor-identical and runtime-inert

## Failure evidence

- `ConfigAuthority().validate(new_artifact['cfg'])` failed on an unchanged donor copy.
- First failing output:
  - `ValidationError: strategy_family - Field required`
- Root cause: donor `merged_config` from `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json` is not runtime-valid as a standalone config payload without authoring an extra field inside `cfg`.
- Contract consequence: because `cfg == donor.merged_config` and `ConfigAuthority.validate(cfg)` could not both be satisfied, the slice fail-closed before any carrier artifact could be admitted.

## Bottom line

This slice is blocked.
It does not authorize capture v2, baseline authoring, or semantic patching of the donor config.
