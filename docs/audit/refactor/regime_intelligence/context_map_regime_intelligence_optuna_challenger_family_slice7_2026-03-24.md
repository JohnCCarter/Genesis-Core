## Context Map

### Slice Objective

Create the seventh Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- declares explicit `meta.runs.run_intent: research_slice` so the slice is admitted as RI research rather than misread as promotion/freeze semantics
- responds to slice-6 evidence that bounded entry selectivity improved the RI validation plateau but still left the RI line behind the incumbent same-head control
- freezes the explicit slice-6 anchor baseline from `run_20260324_155438/trial_005`
- reopens only bounded gating-cadence levers in an attempt to reduce churn / drawdown without reopening selectivity, exit cadence, authority, clarity, or broad topology search
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                                 | Purpose                             | Changes Needed                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`                                    | RI challenger-family slice-7 config | Freeze the slice-6 deterministic anchor and open only bounded gating-cadence levers                          |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md`           | Governance contract for slice 7     | Lock scope, gates, explicit slice-6 anchor rule, and the gating-only whitelist                               |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md`              | This context map                    | Record slice-6 evidence and justify the pivot from selectivity to gating cadence                             |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_execution_2026-03-24.md` | Governance contract for slice 7 run | Lock launch prerequisites, post-diff-audit gate, fresh DB requirement, and exact comparison rules before run |

### Evidence Base for the Slice-7 Hypothesis

| Artifact                                                                                                                | Key finding                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `results/hparam_search/run_20260324_155438/run_meta.json`                                                               | slice-6 used committed SHA `601efdd00552a4de9e5d6cce54a58c84725e593c`; 96 trials; best train value `0.42486961448854577`; validated `5` winners |
| `results/hparam_search/run_20260324_155438/validation/trial_001.json`                                                   | slice-6 validation plateau `0.23646934335498004`, `62` trades, PF `1.7489`, max DD `2.3601%`; confirms the improved RI plateau metrics          |
| `results/hparam_search/run_20260324_155438/validation/trial_005.json`                                                   | same validation plateau as `trial_001`, but also the highest train score among the tied winners; chosen as deterministic slice-7 anchor         |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md` | slice-6 already reopened only bounded selectivity; exit/override/risk breadth and topology were intentionally kept fixed                        |
| `results/backtests/tBTCUSD_3h_20260324_170603.json`                                                                     | incumbent same-head control still leads at score `0.2616884080730424` with only `37` trades and `1.4705%` max drawdown                          |
| `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`                                                       | incumbent remains the governed control baseline until a challenger beats it on a direct comparison path                                         |

### Deterministic anchor rule

Slice-6 produced a tied validation winner cluster at `0.23646934335498004`.

To avoid cherry-picking and keep slice-7 deterministic:

1. rank by validation score
2. if multiple tied winners remain, choose the member with highest train score
3. if train score also ties, fall back to the lexicographically smallest trial id

Under that rule, the explicit slice-7 anchor is `trial_005` from `run_20260324_155438`.

### Frozen anchor values carried into Slice 7

| Area                                                          | Fixed from slice-6 anchor |
| ------------------------------------------------------------- | ------------------------- |
| `thresholds.entry_conf_overall`                               | `0.28`                    |
| `thresholds.regime_proba.balanced`                            | `0.36`                    |
| `signal_adaptation.zones.low/mid/high.entry_conf_overall`     | `0.14 / 0.42 / 0.34`      |
| `signal_adaptation.zones.low/mid/high.regime_proba`           | `0.32 / 0.52 / 0.58`      |
| `htf_exit_config.partial_1_pct` / `partial_2_pct`             | `0.50 / 0.45`             |
| `htf_exit_config.fib_threshold_atr` / `trail_atr_multiplier`  | `0.90 / 2.5`              |
| `exit.max_hold_bars` / `trailing_stop_pct`                    | `8 / 0.022`               |
| `exit.stop_loss_pct` / `exit.exit_conf_threshold`             | `0.016 / 0.42`            |
| `multi_timeframe.ltf_override_threshold`                      | `0.40`                    |
| `risk_state` guard family                                     | explicit slice-6 values   |
| `risk.htf_regime_size_multipliers.bear`                       | `0.65`                    |
| `risk.volatility_sizing.high_vol_multiplier`                  | `0.70`                    |
| `authority_mode=regime_module`, `version=v2`, `clarity=false` | unchanged                 |
| `risk_state.enabled=true`, `atr_period=14`                    | unchanged                 |
| `meta.runs.run_intent`                                        | `research_slice`          |

### Why Slice 7 should NOT reopen selectivity or exit / override breadth

- Slice-6 already reopened only bounded selectivity and produced a higher RI validation plateau than slice 4, which means that surface already delivered its measurable gain.
- All top-5 validated slice-6 winners tied at the same validation score and metrics, so broadening selectivity again would risk relitigating a surface that already converged into a robust plateau.
- Slice-5 already reopened exit / hold / override cadence and did not break the earlier plateau.
- The incumbent same-head control still leads materially on score, trade count, and drawdown, so the next falsifiable RI mechanism is cadence discipline rather than another pass on already-tested breadth.

### Why Slice 7 should target gating cadence specifically

- `gates.hysteresis_steps` and `gates.cooldown_bars` remained fixed at `3 / 2` through slices 2-6.
- These gates directly control regime-entry cadence without reopening family identity, exit management, or selectivity geometry.
- If slice-6 already found a better entry threshold cluster, the remaining question is whether RI still over-commits because transitions are accepted too quickly or allowed to re-fire too soon.
- A narrow gating reopen is therefore the cleanest remaining Fas A-style RI mechanism test.

### Slice-7 Hypothesis Shift

Slice-7 freezes the slice-6 anchor baseline and opens only bounded gating-cadence families:

1. **Regime hysteresis**
   - `gates.hysteresis_steps`
2. **Cooldown cadence**
   - `gates.cooldown_bars`

This tests whether modestly slower or slightly faster gating cadence can lower churn and drawdown while preserving the slice-6 selectivity gains and the RI family identity.

### Explicit search-space boundaries for Slice 7

| Area                     | Status in slice 7 | Rationale                                                          |
| ------------------------ | ----------------- | ------------------------------------------------------------------ |
| RI authority path        | fixed             | family identity already chosen                                     |
| clarity search           | fixed / out       | still unsupported by evidence                                      |
| risk_state guard tuning  | fixed             | frozen to the explicit slice-6 anchor                              |
| regime-aware sizing      | fixed             | frozen to the explicit slice-6 anchor                              |
| exit / hold cadence      | fixed             | already reopened in slice-5 without decisive separation            |
| override cadence         | fixed             | already reopened in slice-5 without decisive separation            |
| HTF exit cadence         | fixed             | already reopened in slice-5 without decisive separation            |
| selectivity thresholds   | fixed             | already reopened in slice-6 and frozen to the deterministic anchor |
| gating hysteresis        | tunable (narrow)  | primary new hypothesis for reducing overtrading                    |
| gating cooldown          | tunable (narrow)  | bounded companion surface to the same cadence hypothesis           |
| broad threshold topology | out of scope      | too much family drift; canonical values must remain fixed exactly  |
| blind 2025 execution     | deferred          | candidate freeze must happen first                                 |

### Reference Config Patterns

| File                                                                                              | Pattern / Relevance                                                                |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml` | explicit slice-6 anchor values that slice-7 freezes                                |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml` | immediate predecessor showing exit/override cadence reopening already had its turn |
| `config/optimizer/README.md`                                                                      | canonical optimizer folder placement and path-stability rules                      |

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
- No temp smoke YAML or temp DB creation in this slice
- No blind 2025 fixed-candidate execution in this slice
- No promotion/default/cutover claims
- No implicit `run_intent` defaulting; RI admission for this slice is explicit `research_slice`
- No reopening into legacy-authority, clarity, renewed risk/sizing breadth, exit/override cadence, selectivity breadth, or broad threshold-topology search
- Every reopened gating value must still include the exact canonical slice-6 values `3 / 2`
- Any future execution step must be packeted separately under `optuna_run_guardrails` and remain gated by post-diff audit
