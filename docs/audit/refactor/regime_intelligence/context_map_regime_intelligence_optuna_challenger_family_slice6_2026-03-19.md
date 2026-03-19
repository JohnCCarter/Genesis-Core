## Context Map

### Slice Objective

Create the sixth Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- responds to slice-5 evidence that bounded exit/hold/override tuning did not break the plateau
- freezes the explicit slice-4 anchor baseline from `run_20260319_111953/trial_002`
- reopens only bounded entry-selectivity levers in an attempt to reduce overtrading / drawdown without reopening exit cadence, authority, clarity, or broad topology search
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                       | Purpose                             | Changes Needed                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`                          | RI challenger-family slice-6 config | Freeze the slice-4 anchor baseline and open only bounded entry-selectivity levers                      |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md` | Governance contract for slice 6     | Lock scope, gates, explicit slice-4 anchor rule, and the selectivity-only whitelist                    |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md`    | This context map                    | Record slice-4 / slice-5 evidence and justify the pivot from exit cadence to entry-selectivity testing |

### Evidence Base for the Slice-6 Hypothesis

| Artifact                                                                                                                             | Key finding                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `results/hparam_search/run_20260319_111953/validation/trial_002.json`                                                                | slice-4 anchor plateau `0.22516209452403432`, `66` trades, PF `1.6486`, max DD `3.1761%`; deterministic anchor via highest-train tied winner |
| `results/hparam_search/run_20260319_111953/run_meta.json`                                                                            | slice-4 used committed SHA `9566e8d9017d278356bcf086ee6f16db46ff231e`; 96 trials; best train value `0.28077646648091525`                     |
| `results/hparam_search/run_20260319_122140/validation/tBTCUSD_3h_trial_001.json`                                                     | slice-5 validation still produced `66` trades and `3.1761%` max DD even after reopening exit/hold/override cadence                           |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice5_execution_2026-03-19.md` | slice-5 execution is explicitly recorded as hypothesis not confirmed and not promotable                                                      |
| `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`                                                                    | incumbent still leads at validation score `0.2617` with only `37` trades and `1.47%` max DD                                                  |

### Deterministic anchor rule

Slice-4 produced a tied validation winner cluster at `0.22516209452403432`.

To avoid cherry-picking and keep slice-6 deterministic:

1. rank by validation score
2. if multiple tied winners remain, choose the member with highest train score
3. if train score also ties, fall back to the lexicographically smallest trial id

Under that rule, the explicit slice-6 anchor is `trial_002` from `run_20260319_111953`.

### Frozen anchor values carried into Slice 6

| Area                                                          | Fixed from slice-4 anchor |
| ------------------------------------------------------------- | ------------------------- |
| `htf_exit_config.partial_1_pct` / `partial_2_pct`             | `0.50 / 0.45`             |
| `htf_exit_config.fib_threshold_atr` / `trail_atr_multiplier`  | `0.90 / 2.5`              |
| `gates.hysteresis_steps` / `gates.cooldown_bars`              | `3 / 2`                   |
| `exit.max_hold_bars` / `trailing_stop_pct`                    | `8 / 0.022`               |
| `exit.stop_loss_pct` / `exit.exit_conf_threshold`             | `0.016 / 0.42`            |
| `multi_timeframe.ltf_override_threshold`                      | `0.40`                    |
| `risk_state` guard family                                     | explicit slice-4 values   |
| `risk.htf_regime_size_multipliers.bear`                       | `0.65`                    |
| `risk.volatility_sizing.high_vol_multiplier`                  | `0.70`                    |
| `canonical RI threshold cluster`                              | preserved exactly         |
| `authority_mode=regime_module`, `version=v2`, `clarity=false` | unchanged                 |
| `risk_state.enabled=true`, `atr_period=14`                    | unchanged                 |

### Why Slice 6 should NOT reopen exit / override / renewed risk breadth

- Slice-5 already reopened exit / hold / override cadence and still failed to break the slice-4 plateau.
- The slice-5 validation artifacts kept the same trade count (`66`) and the same max drawdown (`3.1761%`) despite differing merged-config values.
- That makes another pass on exit / override cadence low-value and weakly evidenced.
- The incumbent control remains materially lower-churn (`37` trades) and lower-drawdown (`1.47%`) than the RI challenger line.
- The remaining falsifiable hypothesis is therefore entry selectivity: RI may be entering too often rather than exiting too late.

### Why Slice 6 should still avoid broad threshold-topology reopening

- RI family validation still depends on the canonical threshold cluster and fixed family identity.
- The goal here is not to reopen arbitrary threshold search, but to test a narrow selectivity band around the exact canonical values.
- Every reopened threshold in slice-6 must include the canonical RI value exactly, and no additional threshold families may be opened.

### Slice-6 Hypothesis Shift

Slice-6 freezes the slice-4 anchor baseline and opens only bounded entry-selectivity families:

1. **Core selectivity**
   - `thresholds.entry_conf_overall`
   - `thresholds.regime_proba.balanced`
2. **Zone selectivity**
   - `thresholds.signal_adaptation.zones.low.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.high.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.low.regime_proba`
   - `thresholds.signal_adaptation.zones.mid.regime_proba`
   - `thresholds.signal_adaptation.zones.high.regime_proba`

This tests whether modestly tighter or better-aligned entry gating can lower churn and drawdown while preserving the RI family identity and the validated slice-4 anchor structure.

### Explicit search-space boundaries for Slice 6

| Area                     | Status in slice 6 | Rationale                                                            |
| ------------------------ | ----------------- | -------------------------------------------------------------------- |
| RI authority path        | fixed             | family identity already chosen                                       |
| clarity search           | fixed / out       | still unsupported by evidence                                        |
| risk_state guard tuning  | fixed             | frozen to the explicit slice-4 anchor                                |
| regime-aware sizing      | fixed             | frozen to the explicit slice-4 anchor                                |
| exit / hold cadence      | fixed             | already reopened in slice-5 without plateau break                    |
| override cadence         | fixed             | already reopened in slice-5 without plateau break                    |
| HTF exit cadence         | fixed             | already reopened in slice-5 without plateau break                    |
| core entry selectivity   | tunable (narrow)  | primary new hypothesis for reducing overtrading                      |
| zone entry selectivity   | tunable (narrow)  | bounded extension of the same selectivity hypothesis                 |
| broad threshold topology | out of scope      | too much family drift; canonical values must remain included exactly |
| blind 2025 execution     | deferred          | candidate freeze must happen first                                   |

### Reference Config Patterns

| File                                                                                              | Pattern / Relevance                                                                               |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml` | explicit slice-4 anchor values that slice-6 freezes                                               |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml` | immediate predecessor proving exit / hold / override cadence reopening did not achieve separation |
| `config/optimizer/README.md`                                                                      | canonical optimizer folder placement and path-stability rules                                     |

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
- No reopening into legacy-authority, clarity, renewed risk/sizing breadth, exit/override cadence, or broad threshold-topology search
- Every reopened selectivity threshold must still include the exact canonical RI value
- Any future execution step must be packeted separately under `optuna_run_guardrails`
