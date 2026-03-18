## Context Map

### Slice Objective

Create the second Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- develops the validated RI challenger family represented by `trial_001` / `trial_002` / `trial_005`
- fixes the family identity to `authority_mode=regime_module`
- keeps blind 2025 candidate freeze/evaluation out of scope for this slice
- does not change runtime defaults, champion files, or any `src/**` behavior

### Files to Modify

| File                                                                                                                       | Purpose                             | Changes Needed                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`                          | RI challenger-family slice-2 config | Narrow the search around the validated RI family while preserving the family identity and fixed train/validation windows |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md` | Governance contract for slice 2     | Lock scope, gates, stop conditions, smoke handling, and fail-closed boundaries                                           |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md`    | This context map                    | Record candidate-family evidence, search boundaries, and verification anchors                                            |
| `docs/features/feature-ri-optuna-train-validate-blind-1.md`                                                                | Higher-level feature plan           | Reference only; no edit required unless a tiny follow-up note becomes necessary                                          |

### Evidence Base for the Slice-2 Family

| Artifact                                                                          | Key finding                                                                                                       |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`                 | incumbent champion remains best current validated candidate; RI `trial_001/002/005` is the lead challenger family |
| `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md` | RI should be developed as a separate strategy family, not as a thin overlay on the incumbent champion             |
| `results/hparam_search/run_20260318_112046/validation/trial_001.json`             | lead challenger family member with score `0.22729723723866666`                                                    |
| `results/hparam_search/run_20260318_112046/validation/trial_002.json`             | equivalent family member with the same validation outcome as `trial_001`                                          |
| `results/hparam_search/run_20260318_112046/validation/trial_005.json`             | equivalent family member with the same validation outcome as `trial_001`                                          |
| `tmp/champion_validation_20260318.log`                                            | incumbent champion still leads the direct validation replay with score `0.2617`                                   |

### Candidate-Family Identity to Preserve

| Area                                                        | Slice-2 status        | Rationale                                                                                  |
| ----------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------ |
| `multi_timeframe.regime_intelligence.enabled`               | fixed `true`          | this slice remains RI-on challenger research                                               |
| `multi_timeframe.regime_intelligence.version`               | fixed `v2`            | preserve the validated RI family version                                                   |
| `multi_timeframe.regime_intelligence.authority_mode`        | fixed `regime_module` | slice 1 established the RI family identity; this slice is not re-testing the legacy branch |
| `multi_timeframe.regime_intelligence.clarity_score.enabled` | fixed `false`         | clarity stays excluded until the RI challenger family proves stronger core signal          |
| `multi_timeframe.regime_intelligence.risk_state.enabled`    | fixed `true`          | validated family kept `risk_state` on                                                      |
| `thresholds.signal_adaptation.atr_period`                   | fixed `14`            | part of the RI-compatible cluster identified in the compatibility analysis                 |
| `gates.hysteresis_steps` / `gates.cooldown_bars`            | fixed `3/2`           | preserve the validated RI family cadence                                                   |

### Proposed Search-Space Boundaries for Slice 2

| Area                                        | Status in slice 2 | Rationale                                                              |
| ------------------------------------------- | ----------------- | ---------------------------------------------------------------------- |
| RI authority path                           | fixed             | challenger-family identity already chosen                              |
| threshold family around `trial_001/002/005` | tunable, narrow   | refine inside the validated family rather than re-open topology search |
| selected `risk_state` guards                | tunable, narrow   | slice 1 showed only small differences here; keep exploration tight     |
| gating cadence                              | fixed             | avoid reopening a broader family-shape search in this slice            |
| clarity search                              | out of scope      | still unsupported by the current evidence                              |
| incumbent overlay migration                 | out of scope      | already disproven as the primary path                                  |
| blind 2025 execution                        | deferred          | candidate freeze must happen first                                     |

### Reference Config Patterns

| File                                                                                            | Pattern / Relevance                                                    |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml` | slice-1 baseline taxonomy, validation structure, and TPE configuration |
| `config/optimizer/README.md`                                                                    | canonical optimizer folder placement and path-stability rules          |
| `docs/templates/skills/optuna_run_guardrails.md`                                                | required preflight + validator flow and canonical mode rule            |

### Verification Anchors

| Anchor                                                                                                     | Role in this slice                                                                         |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `scripts/validate/validate_optimizer_config.py`                                                            | structural/config semantics validation for the new YAML                                    |
| `scripts/preflight/preflight_optuna_check.py`                                                              | Optuna/storage/pre-run guardrail validation                                                |
| temporary smoke config under `tmp/`                                                                        | proves the slice-2 config can start cleanly with unique temporary `study_name` and storage |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay anchor                                                                  |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | feature-cache invariance anchor                                                            |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant anchor                                                                  |
| `tests/governance/test_authority_mode_resolver.py`                                                         | explicit authority-mode resolver anchor for the fixed `regime_module` slice identity       |

### Non-Negotiable Boundaries

- No edits to `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- No committed `results/**` changes in this slice
- No blind 2025 fixed-candidate YAML in this slice
- No promotion/default/cutover claims
- No direct incumbent+RI overlay migration path
- No widening into clarity search
- Any temporary smoke YAML/DB must live under `tmp/` and remain out of commit scope
- Any future winner-freeze / blind-eval step must be a separate follow-up slice
