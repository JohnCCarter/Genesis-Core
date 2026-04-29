## Context Map

### Slice Objective

Create the fifth Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- responds to slice-4 evidence that validation improved only slightly and still collapsed into a tied top-5 plateau
- freezes the canonical RI threshold cluster together with an explicit slice-4 robustness anchor
- reopens only bounded exit/hold/override cadence levers in an attempt to break the validation plateau without reopening thresholds, authority, or clarity
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                       | Purpose                             | Changes Needed                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`                          | RI challenger-family slice-5 config | Freeze the slice-4 anchor baseline and open only bounded exit/hold/override cadence levers     |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice5_2026-03-19.md` | Governance contract for slice 5     | Lock scope, gates, explicit slice-4 anchor rule, and scaffolding-only constraints              |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice5_2026-03-19.md`    | This context map                    | Record slice-4 evidence, anchor selection rule, and the narrowed slice-5 hypothesis boundaries |

### Evidence Base for the Slice-5 Hypothesis

| Artifact                                                              | Key finding                                                                                                                   |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `results/hparam_search/run_20260319_111953/run_meta.json`             | slice-4 used committed SHA `9566e8d9017d278356bcf086ee6f16db46ff231e`; 96 trials; best train value `0.28077646648091525`      |
| `results/hparam_search/run_20260319_111953/best_trial.json`           | slice-4 best train candidate was `trial_002`                                                                                  |
| `results/hparam_search/run_20260319_111953/validation/trial_001.json` | validation score `0.22516209452403432`, with 66 trades, PF `1.6486`, max DD `3.1761%`; part of a tied winner cluster          |
| `results/hparam_search/run_20260319_111953/validation/trial_002.json` | same validation score as `trial_001`, but also the highest train score among the tied winners; chosen as deterministic anchor |
| `results/hparam_search/run_20260319_111953/validation/trial_003.json` | same validation score and metrics; confirms plateau persistence despite different risk/sizing values                          |
| `results/hparam_search/run_20260319_111953/validation/trial_004.json` | same validation score and metrics; confirms plateau persistence                                                               |
| `results/hparam_search/run_20260319_111953/validation/trial_005.json` | same validation score and metrics; confirms plateau persistence                                                               |
| `results/hparam_search/run_20260318_134535/validation/trial_001.json` | slice-3 validation score `0.22289051935876203`; slice 4 improved only marginally over this level                              |
| `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`     | incumbent champion remains stronger at validation score `0.2617`; RI family remains research track, not promotion             |

### Deterministic anchor rule

Slice-4 produced a tied validation winner cluster at `0.22516209452403432`.

To avoid cherry-picking and keep slice-5 deterministic:

1. rank by validation score
2. if multiple tied winners remain, choose the member with highest train score
3. if train score also ties, fall back to the lexicographically smallest trial id

Under that rule, the explicit slice-5 anchor is `trial_002`.

### Frozen anchor values carried into Slice 5

| Area                                                          | Fixed from slice-4 anchor |
| ------------------------------------------------------------- | ------------------------- |
| `risk_state.drawdown_guard.soft_threshold`                    | `0.04`                    |
| `risk_state.drawdown_guard.soft_mult`                         | `1.0`                     |
| `risk_state.transition_guard.mult`                            | `0.65`                    |
| `risk_state.drawdown_guard.hard_threshold`                    | `0.06`                    |
| `risk_state.drawdown_guard.hard_mult`                         | `0.65`                    |
| `risk_state.transition_guard.guard_bars`                      | `2`                       |
| `risk.htf_regime_size_multipliers.bear`                       | `0.65`                    |
| `risk.volatility_sizing.high_vol_multiplier`                  | `0.70`                    |
| `exit.stop_loss_pct`                                          | `0.016`                   |
| `htf_exit_config.partial_1_pct` / `partial_2_pct`             | `0.50 / 0.45`             |
| `canonical RI threshold cluster`                              | unchanged                 |
| `authority_mode=regime_module`, `version=v2`, `clarity=false` | unchanged                 |
| `risk_state.enabled=true`, `atr_period=14`, gates `3/2`       | unchanged                 |

### Why Slice 5 should NOT reopen thresholds or renewed risk/sizing breadth

- Slice-3 already opened exit, override, and Fib-adjacent surfaces without breaking the validation plateau.
- Slice-4 then opened `risk_state` plus regime-aware sizing and improved validation only marginally, from `0.22289051935876203` to `0.22516209452403432`.
- Slice-4 top-5 still collapsed to the same validation score, so reopening risk/sizing breadth again would likely just relitigate a family that already failed to separate.
- RI family validation still depends on the canonical RI threshold cluster, so thresholds should remain fixed.
- The next falsifiable hypothesis is therefore trade-management cadence, not another pass at family identity or threshold geometry.

### Slice-5 Hypothesis Shift

Slice-5 freezes the slice-4 anchor baseline and opens only bounded cadence families:

1. **Exit / hold cadence**
   - `exit.exit_conf_threshold`
   - `exit.max_hold_bars`
   - `exit.trailing_stop_pct`
2. **Override cadence**
   - `multi_timeframe.ltf_override_threshold`
3. **Secondary HTF exit cadence**
   - `htf_exit_config.trail_atr_multiplier`
   - `htf_exit_config.fib_threshold_atr`

This tests whether the remaining validation bottleneck sits in trade management timing rather than in thresholds or risk-state modulation.

### Explicit search-space boundaries for Slice 5

| Area                                | Status in slice 5 | Rationale                                                                                       |
| ----------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------- |
| RI authority path                   | fixed             | family identity already chosen                                                                  |
| threshold family                    | fixed             | RI family validation requires the canonical threshold cluster                                   |
| clarity search                      | fixed / out       | still unsupported by evidence                                                                   |
| risk_state guard tuning             | fixed             | frozen to the explicit slice-4 anchor rather than reopened                                      |
| regime-aware sizing                 | fixed             | frozen to the explicit slice-4 anchor rather than reopened                                      |
| exit cadence                        | tunable           | primary new hypothesis for breaking the plateau                                                 |
| `ltf_override_threshold`            | tunable (narrow)  | targeted cadence reopen, narrower than the broad slice-3 reopen                                 |
| HTF exit cadence                    | tunable (narrow)  | small secondary surface that can alter trade management timing without changing family topology |
| Fib entry tolerances / level bounds | fixed             | no evidence that broader Fib entry reopening helps                                              |
| blind 2025 execution                | deferred          | candidate freeze must happen first                                                              |

### Reference Config Patterns

| File                                                                                              | Pattern / Relevance                                                                                       |
| ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml` | baseline taxonomy and the slice-4 search family that is now being frozen into an explicit anchor          |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml` | prior generalization-focused reopen showing that exit/override/Fib breadth alone did not separate winners |
| `config/optimizer/README.md`                                                                      | canonical optimizer folder placement and path-stability rules                                             |

### Verification Anchors

| Anchor                                                                                                     | Role in this slice                                                    |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `scripts/validate/validate_optimizer_config.py`                                                            | structural/config semantics validation for the new YAML               |
| `scripts/preflight/preflight_optuna_check.py`                                                              | Optuna/storage/pre-run guardrail validation                           |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay anchor                                             |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | feature-cache invariance anchor                                       |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant anchor                                             |
| `tests/governance/test_authority_mode_resolver.py`                                                         | authority-mode resolver anchor for the fixed `regime_module` identity |

### Non-Negotiable Boundaries

- No edits to `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- No committed `results/**` changes in this slice
- No temp smoke YAML, temp DB, or run launch in this slice
- No blind 2025 fixed-candidate execution in this slice
- No promotion/default/cutover claims
- No reopening into legacy-authority, clarity, thresholds, or renewed risk/sizing breadth
- Any future execution step must be packeted separately under `optuna_run_guardrails`
