## Context Map

### Slice Objective

Create the eighth Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- declares explicit `meta.runs.run_intent: research_slice` so the slice remains tooling-admitted as RI research rather than candidate/promotion semantics
- responds to slice-7 evidence that bounded gating cadence improved validation score but also produced an extreme duplicate ratio
- freezes the slice-7 reviewed RI backbone while reopening only a bounded nearby widen-search surface
- reopens only gated cadence and two core selectivity levers to test robustness of the slice-7 gain before any new anchor is declared
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                                 | Purpose                             | Changes Needed                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`                                    | RI challenger-family slice-8 config | Freeze the slice-7 backbone and open only bounded gating + core-selectivity levers                               |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md`           | Governance contract for slice 8     | Lock scope, gates, hard-stop compatibility rules, concrete success thresholds, and explicit no-anchor discipline |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md`              | This context map                    | Record slice-7 evidence and justify the bounded widen-search pivot                                               |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_execution_2026-03-24.md` | Governance contract for slice 8 run | Lock launch prerequisites, fresh DB requirement, exact comparison rules, and explicit post-run anchor deferral   |

### Evidence Base for the Slice-8 Hypothesis

| Artifact                                                                                                              | Key finding                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`                                             | slice-7 validation winner scored `0.26974911658712664`, beating slice6, slice4, slice3, and incumbent same-head control on score         |
| `docs/decisions/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md` | slice-7 counts as successful challenger evidence only; promotion/anchor/freeze remained explicitly out of scope                          |
| `results/hparam_search/run_20260324_171511/validation/trial_001.json`                                                 | slice-7 validation winner used `gates.hysteresis_steps=4` and `gates.cooldown_bars=1` with validation score `0.26974911658712664`        |
| `results/hparam_search/run_20260324_171511/run_meta.json`                                                             | slice-7 attempted `96` trials but produced `87` duplicates (`0.90625` ratio), indicating a narrow and sampler-inefficient search surface |
| `results/backtests/tBTCUSD_3h_20260324_170603.json`                                                                   | incumbent same-head control remains the governed operational baseline until a separate candidate/freeze path is approved                 |
| `tests/utils/test_validate_optimizer_config.py` and `tests/utils/test_preflight_optuna_check.py`                      | current repo validation/preflight already admit `strategy_family=ri` + `run_intent=research_slice` with integer gate sweeps              |

### Slice-7 backbone carried into Slice 8

Slice-8 does **not** canonize slice-7 as a new family anchor.

It only reuses the slice-7 reviewed backbone as the bounded local search neighborhood:

| Area                                                          | Fixed in slice 8 |
| ------------------------------------------------------------- | ---------------- |
| `authority_mode=regime_module`, `version=v2`, `clarity=false` | unchanged        |
| `risk_state.enabled=true`, `atr_period=14`                    | unchanged        |
| zone selectivity cluster (`low/mid/high`)                     | frozen           |
| exit / hold cadence                                           | frozen           |
| override cadence                                              | frozen           |
| HTF entry / exit cadence                                      | frozen           |
| risk-state guard family                                       | frozen           |
| regime-aware sizing                                           | frozen           |
| `meta.runs.run_intent`                                        | `research_slice` |

### Why Slice 8 should widen search only slightly

- Slice-7 already proved that the bounded gating pivot can produce a materially higher RI validation winner than slice6.
- The same slice also produced a duplicate ratio of `0.90625`, which is too high to treat the result as broad local robustness.
- Reopening the whole RI topology would destroy interpretability and violate the packet’s bounded-search discipline.
- The cleanest next falsifiable step is therefore to preserve the slice-7 backbone while widening only the local neighborhood around:
  - gating cadence (`hysteresis_steps`, `cooldown_bars`)
  - core selectivity (`entry_conf_overall`, `regime_proba.balanced`)

### Slice-8 Hypothesis Shift

Slice-8 freezes the slice-7 reviewed backbone and opens only four bounded families:

1. **Regime hysteresis**
   - `gates.hysteresis_steps`
2. **Cooldown cadence**
   - `gates.cooldown_bars`
3. **Core entry selectivity**
   - `thresholds.entry_conf_overall`
4. **Balanced-regime selectivity**
   - `thresholds.regime_proba.balanced`

This tests whether a slightly wider but still nearby RI neighborhood can:

- preserve or improve slice-7’s validation advantage, and/or
- reduce duplicate collapse enough to justify a later anchor decision packet

### Explicit search-space boundaries for Slice 8

| Area                     | Status in slice 8 | Rationale                                                                   |
| ------------------------ | ----------------- | --------------------------------------------------------------------------- |
| RI authority path        | fixed             | family identity already chosen                                              |
| clarity search           | fixed / out       | still unsupported by evidence                                               |
| risk_state guard tuning  | fixed             | no need to relitigate beyond slice6/7 backbone                              |
| regime-aware sizing      | fixed             | no need to relitigate beyond slice6/7 backbone                              |
| exit / hold cadence      | fixed             | already reopened earlier; not the current hypothesis                        |
| override cadence         | fixed             | already reopened earlier; not the current hypothesis                        |
| HTF exit cadence         | fixed             | already reopened earlier; not the current hypothesis                        |
| zone selectivity cluster | fixed             | slice8 targets only core selectivity, not the adaptation topology           |
| gating hysteresis        | tunable (bounded) | keeps slice6 canonical `3` and slice7 winner `4` in scope, adds nearby `5`  |
| gating cooldown          | tunable (bounded) | keeps slice6 canonical `2` and slice7 winner `1` in scope, keeps nearby `3` |
| entry_conf_overall       | tunable (bounded) | keeps slice6/7 reviewed `0.28` in scope and allows nearby `0.26..0.30`      |
| balanced regime proba    | tunable (bounded) | keeps slice6/7 reviewed `0.36` in scope and allows nearby `0.34..0.38`      |
| broad threshold topology | out of scope      | too much family drift                                                       |
| blind 2025 execution     | deferred          | anchor/candidate decision must happen first                                 |

### Success interpretation boundary

For slice-8, “recordable evidence” and “successful widen-search” are not the same thing.

- A **successful widen-search** requires either:
  1. a validation winner strictly above slice-7 score `0.26974911658712664`, or
  2. duplicate ratio `<= 0.70` while keeping the validation winner at or above the slice6 plateau `0.23646934335498004`
- Any weaker outcome may still be recorded, but it does **not** authorize anchor language.

### Verification Anchors

| Anchor                                                                                                     | Role in this slice                                                |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `scripts/validate/validate_optimizer_config.py`                                                            | structural/config semantics validation for the new YAML           |
| `scripts/preflight/preflight_optuna_check.py`                                                              | Optuna/storage/pre-run guardrail validation                       |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay anchor                                         |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | feature-cache invariance anchor                                   |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant anchor                                         |
| `tests/governance/test_authority_mode_resolver.py`                                                         | authority-mode resolver anchor for fixed `regime_module` identity |

### Non-Negotiable Boundaries

- No edits to `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- No committed `results/**` changes in this slice before execution outcome is known
- No temp smoke YAML or temp DB creation in this slice
- No blind 2025 fixed-candidate execution in this slice
- No promotion/default/cutover claims
- No implicit `run_intent` defaulting; RI admission for this slice is explicit `research_slice`
- No reopening into legacy-authority, clarity, renewed risk/sizing breadth, exit/override cadence, zone-selectivity breadth, or broad threshold-topology search
- If validator or preflight rejects the exact scoped YAML, the slice is blocked; do not widen scope to “fix it” in code/tests
- Any future execution step must be packeted separately under `optuna_run_guardrails` and must end with explicit anchor deferral
