## Context Map

### Slice Objective

Create the fourth Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- responds to slice-3 evidence that train remained strong while validation plateaued below the incumbent
- freezes the canonical RI threshold cluster plus stable exit/override/fib baseline and instead tests whether bounded `risk_state` guard tuning plus regime-aware sizing can improve validation robustness
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                       | Purpose                             | Changes Needed                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`                          | RI challenger-family slice-4 config | Lock the canonical RI threshold cluster plus stable RI-compatible exit/fib baseline and open only bounded `risk_state` + sizing levers |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md` | Governance contract for slice 4     | Lock scope, gates, stop conditions, repo-skill invocation, and scaffolding-only constraints                                            |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`    | This context map                    | Record slice-3 evidence, new whitelist hypothesis, and boundaries that keep slice-4 out of topology/authority reopening                |

### Evidence Base for the Slice-4 Hypothesis

| Artifact                                                                          | Key finding                                                                                                              |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `results/hparam_search/run_20260318_134535/run_meta.json`                         | slice-3 used committed SHA `7d3c27dc9adb9bc1df5e824ec14cd74eb2cb54d7`; 200 trials; best train value `0.4240027152501049` |
| `results/hparam_search/run_20260318_134535/best_trial.json`                       | slice-3 best train candidate was `trial_035`, proving the RI family can still produce strong in-sample behavior          |
| `results/hparam_search/run_20260318_134535/validation/trial_001.json`             | slice-3 validation score `0.22289051935876203`, with 62 trades, PF `1.6982`, max DD `2.2768%`                            |
| `results/hparam_search/run_20260318_134535/validation/trial_002.json`             | same validation score and metrics as `trial_001`; small parameter changes did not separate out-of-sample                 |
| `results/hparam_search/run_20260318_134535/validation/trial_003.json`             | same validation score and metrics; another confirmation of plateau                                                       |
| `results/hparam_search/run_20260318_134535/validation/trial_004.json`             | same validation score and metrics; threshold micro-variation did not change validation result                            |
| `results/hparam_search/run_20260318_134535/validation/trial_005.json`             | same validation score and metrics; exit/fib-adjacent variations still collapsed to the same validation cluster           |
| `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`                 | incumbent champion remains stronger at validation score `0.2617`; RI family remains research track, not promotion        |
| `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md` | RI should be treated as a new strategy family; champion overlay is not the main path                                     |

### Why slice-4 should NOT reopen thresholds / exits / override / fib breadth

- Slice-3 already moved away from pure threshold-only refinement by opening exit, override, and Fib-tolerance surfaces.
- Despite that, the top-5 validation candidates all collapsed to the same score `0.22289051935876203`.
- That pattern suggests slice-3 found a stable RI candidate family but not a stronger validation separator.
- Reopening broad threshold search would likely generate more train winners without directly attacking the observed validation plateau.
- Because `strategy_family=ri` is validated against the canonical RI threshold cluster, slice-4 should keep those thresholds fixed and move the hypothesis into robustness levers that remain family-safe.

### RI Family Identity to Preserve

| Area                                                        | Slice-4 status        | Rationale                                                         |
| ----------------------------------------------------------- | --------------------- | ----------------------------------------------------------------- |
| `multi_timeframe.regime_intelligence.enabled`               | fixed `true`          | slice-4 remains RI-on challenger research                         |
| `multi_timeframe.regime_intelligence.version`               | fixed `v2`            | preserve the validated RI family version                          |
| `multi_timeframe.regime_intelligence.authority_mode`        | fixed `regime_module` | slice-4 does not reopen legacy authority                          |
| `multi_timeframe.regime_intelligence.clarity_score.enabled` | fixed `false`         | clarity remains out of scope until core RI family beats incumbent |
| `multi_timeframe.regime_intelligence.risk_state.enabled`    | fixed `true`          | slice-4 focuses on bounded tuning inside the validated RI family  |
| `thresholds.signal_adaptation.atr_period`                   | fixed `14`            | part of the RI-compatible preparation cluster                     |
| `gates.hysteresis_steps` / `gates.cooldown_bars`            | fixed `3/2`           | preserve the RI family gating cadence                             |

### Slice-4 Hypothesis Shift

Slice-4 freezes the canonical RI threshold cluster together with a stable RI-compatible exit/override/fib baseline and opens only two bounded families:

1. **Risk-state guard tuning**
   - drawdown soft threshold / multiplier
   - drawdown hard threshold / multiplier
   - transition guard multiplier / guard bars
2. **Regime-aware sizing**
   - `risk.htf_regime_size_multipliers.bear`
   - `risk.volatility_sizing.high_vol_multiplier`

This tests whether validation robustness is being limited more by how RI risk state modulates exposure than by further entry/exit micro-tuning.

### Explicit search-space boundaries for Slice 4

| Area                                 | Status in slice 4 | Rationale                                                                                                                     |
| ------------------------------------ | ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| RI authority path                    | fixed             | family identity already chosen                                                                                                |
| threshold family                     | fixed             | RI family validation requires the canonical threshold cluster; slice-3 plateau also argues against reopening threshold search |
| exit surface                         | fixed             | already opened in slice-3 without validation separation                                                                       |
| `ltf_override_threshold`             | fixed             | already part of slice-3 surface; no evidence yet that broader reopening helps                                                 |
| Fib entry tolerances                 | fixed             | already opened in slice-3 without validation separation                                                                       |
| `risk_state` guard tuning            | tunable           | new primary hypothesis for robustness differentiation                                                                         |
| regime-aware sizing                  | tunable           | bounded secondary family aligned with RI behavior without topology drift                                                      |
| clarity search                       | out of scope      | still unsupported by evidence                                                                                                 |
| legacy authority / incumbent overlay | out of scope      | already rejected as the primary path                                                                                          |
| blind 2025 execution                 | deferred          | candidate freeze must happen first                                                                                            |

### Reference Config Patterns

| File                                                                                              | Pattern / Relevance                                                                                                |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml` | slice-3 baseline taxonomy, fixed windows, and evidence for the validation plateau                                  |
| `config/optimizer/3h/phased_v3/best_trials/phaseB_v2_best_trial.json`                             | confirms existing family-safe use of `ltf_override_adaptive`, `risk_map`, `R_default`, and baseline exit structure |
| `config/optimizer/README.md`                                                                      | canonical optimizer folder placement and path-stability rules                                                      |

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
- No reopening into legacy-authority, clarity, or broad threshold-topology search
- Any future execution step must be packeted separately under `optuna_run_guardrails`
