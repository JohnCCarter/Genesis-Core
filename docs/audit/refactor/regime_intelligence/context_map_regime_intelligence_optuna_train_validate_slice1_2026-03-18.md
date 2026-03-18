## Context Map

### Slice Objective

Create the first minimal Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- tunes only a narrow authority + risk-state search space
- ranks candidates on a separate validation window
- keeps blind 2025 candidate freeze/evaluation out of scope for this slice
- does not change runtime defaults, champion files, or any `src/**` behavior

### Files to Modify

| File                                                                                                                    | Purpose                                   | Changes Needed                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`                         | First RI train+validation campaign config | Define train window, validation window, narrow RI search space, storage/study naming, and strict constraints without touching runtime defaults |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md` | Governance contract for the slice         | Lock scope, gates, deferred blind step, and verification evidence                                                                              |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_train_validate_slice1_2026-03-18.md`    | This context map                          | Record boundaries, reference patterns, and non-negotiable exclusions                                                                           |
| `docs/features/feature-ri-optuna-train-validate-blind-1.md`                                                             | Higher-level feature plan                 | Reference only; no edit required unless a tiny status update becomes necessary                                                                 |

### Reference Config Patterns

| File                                                                 | Pattern / Relevance                                                                                               |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/tBTCUSD_3h_explore_validate_2024_2025.yaml`     | Existing 3h explore+validate layout with nested `runs.validation.*`, `top_n`, and separate validation constraints |
| `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseD.yaml`     | Existing 3h authority/risk_state optimization pattern using flat dotted parameter paths                           |
| `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseE_oos.yaml` | Existing fixed OOS validation pattern; useful as deferred blind-step template only                                |
| `config/optimizer/README.md`                                         | Canonical optimizer folder placement and resume-signature path sensitivity                                        |
| `docs/templates/skills/optuna_run_guardrails.md`                     | Required preflight + validator flow and canonical mode rule                                                       |

### Ablation Anchors Used to Narrow the Search Space

| Artifact                                                       | Key finding                                                                                              |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `tmp/ri_ablation_authority_only_tBTCUSD_3h_20260318.json`      | `authority_mode=regime_module` alone produced the main improvement signal                                |
| `tmp/ri_ablation_authority_clarity_tBTCUSD_3h_20260318.json`   | clarity bundle was neutral-to-slightly-negative on the observed window                                   |
| `tmp/ri_ablation_authority_riskstate_tBTCUSD_3h_20260318.json` | adding `risk_state` to authority produced a small additional lift                                        |
| `tmp/ri_on_shadow_experiment_summary_20260318.json`            | summary anchor stating primary driver = authority switch, best observed variant = authority + risk_state |

### Data Availability Constraint Discovered During Slice Validation

| Constraint                                                               | Evidence                                                                                                                                        | Slice-1 implication                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frozen `tBTCUSD_3h` parquet does not cover full `2023-01-01..2024-06-30` | `scripts/preflight/preflight_optuna_check.py` plus parquet inspection showed actual timestamp coverage `2023-12-20 12:00Z .. 2026-01-08 12:00Z` | slice 1 train window must start at the first fully covered calendar day, `2023-12-21`; the broader 2023 target remains a future/backfill concern rather than a blocker for this config-only scaffold |

### Proposed Search-Space Boundaries for Slice 1

| Area                                                        | Status in slice 1       | Rationale                                                                |
| ----------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------ | ------------------------------------- |
| `multi_timeframe.regime_intelligence.enabled`               | fixed `true`            | this experiment explicitly tests RI-on candidate behavior                |
| `multi_timeframe.regime_intelligence.version`               | fixed `v2`              | match observed RI v2 experiment surface                                  |
| `multi_timeframe.regime_intelligence.authority_mode`        | tunable grid `legacy    | regime_module`                                                           | primary observed driver from ablation |
| `multi_timeframe.regime_intelligence.clarity_score.enabled` | fixed `false`           | excluded in first slice due to neutral/slightly-negative ablation signal |
| `multi_timeframe.regime_intelligence.risk_state.enabled`    | fixed `true`            | keep risk-state in play because it added a small positive increment      |
| `multi_timeframe.regime_intelligence.risk_state.*` guards   | tunable                 | small bounded exploration around observed positive settings              |
| blind 2025 fixed candidate config                           | deferred / out of scope | candidate freeze must happen after train+validation evidence exists      |

### Verification Anchors

| Anchor                                                                                                     | Role in this slice                                                                          |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `scripts/validate/validate_optimizer_config.py`                                                            | structural/config semantics validation for the new YAML                                     |
| `scripts/preflight/preflight_optuna_check.py`                                                              | Optuna/storage/pre-run guardrail validation                                                 |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | focused STRICT evidence anchor to cite/re-run if needed before READY_FOR_REVIEW             |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | focused pipeline invariant evidence anchor to cite/re-run if needed before READY_FOR_REVIEW |

### Non-Negotiable Boundaries

- No edits to `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- No blind 2025 fixed-candidate YAML in this slice
- No promotion/default/cutover claims
- No reuse of old storage DBs when `resume: false`
- No widening into clarity search space in slice 1
- Any future winner-freeze / blind-eval step must be a separate follow-up slice
