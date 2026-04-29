## Context Map

### Slice Objective

Create the ninth Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- declares explicit `meta.runs.run_intent: research_slice` so the slice remains tooling-admitted as RI research rather than promotion/freeze semantics
- uses the slice8 local winner only as a provisional research baseline, not as a canonical anchor declaration
- responds to slice8 evidence that the local winner survived bounded entry/gating reopen with materially lower duplicate collapse
- freezes the slice8 entry/gating backbone while reopening only a narrow exit/override management surface
- does not change runtime defaults, champion files, `src/**`, or `tests/**`

### Files to Modify

| File                                                                                                                                 | Purpose                             | Changes Needed                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`                                    | RI challenger-family slice-9 config | Freeze the slice8 local baseline and open only bounded exit/override management levers                          |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md`           | Governance contract for slice 9     | Lock scope, gates, provisional-baseline wording, hard-stop compatibility rules, and success interpretation      |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md`              | This context map                    | Record slice7/slice8 evidence and justify the move from entry/gating reopen to management-surface falsification |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_execution_2026-03-26.md` | Governance contract for slice 9 run | Lock launch prerequisites, fresh DB requirement, exact comparison rules, and explicit anchor deferral           |

### Evidence Base for the Slice-9 Hypothesis

| Artifact                                                                                                              | Key finding                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`                                             | slice7 validation winner scored `0.26974911658712664`, establishing the current best reproduced RI validation level                           |
| `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`                                             | slice8 matched the slice7 validation winner at `0.26974911658712664` while lowering duplicate ratio to `0.2604166666666667`                   |
| `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md` | slice8 counts as successful widen-search evidence only; no canonical anchor, promotion, or freeze meaning was approved                        |
| `docs/decisions/regime_intelligence_optuna_challenger_family_anchor_decision_candidate_packet_2026-03-24.md`         | current packet-level recommendation favors using slice8 as a research anchor only, subject to separate governance approval                    |
| `results/backtests/tBTCUSD_3h_20260324_170603.json`                                                                   | incumbent same-head control remains the governed operational baseline until a separate candidate/freeze path is approved                      |
| `tests/utils/test_validate_optimizer_config.py` and `tests/utils/test_preflight_optuna_check.py`                      | current repo validation/preflight already admit `strategy_family=ri` + `run_intent=research_slice` under bounded parameter reopening surfaces |

### Provisional slice-8 baseline carried into Slice 9

Slice9 does **not** canonize slice8 as a new family anchor.

It only uses the slice8 local winner as the provisional research baseline for this bounded falsification step:

| Area                                                          | Fixed in slice 9 |
| ------------------------------------------------------------- | ---------------- |
| `thresholds.entry_conf_overall`                               | `0.27`           |
| `thresholds.regime_proba.balanced`                            | `0.36`           |
| `gates.hysteresis_steps`                                      | `4`              |
| `gates.cooldown_bars`                                         | `1`              |
| `authority_mode=regime_module`, `version=v2`, `clarity=false` | unchanged        |
| `risk_state.enabled=true`, `atr_period=14`                    | unchanged        |
| zone selectivity cluster (`low/mid/high`)                     | frozen           |
| HTF entry / exit cadence                                      | frozen           |
| risk-state guard family                                       | frozen           |
| regime-aware sizing                                           | frozen           |
| `meta.runs.run_intent`                                        | `research_slice` |

### Why Slice 9 should reopen only a narrow exit/override management surface

- Slice8 already answered the local entry/gating robustness question by reproducing the slice7 winner under a broader nearby search while sharply reducing duplicate collapse.
- That makes another entry/gating/selectivity reopen low-value and harder to interpret.
- The next falsifiable question is whether the slice8 local winner depends too strongly on inherited management settings such as hold horizon, exit confidence, and LTF override sensitivity.
- Reopening broad RI topology, risk-state breadth, or selectivity again would destroy interpretability and violate the packet’s bounded-falsification discipline.
- The cleanest next test is therefore to keep the slice8 backbone fixed and perturb only a very small management surface around `max_hold_bars`, `exit_conf_threshold`, and `ltf_override_threshold`.

### Slice-9 Hypothesis Shift

Slice9 freezes the slice8 reviewed backbone and opens only three bounded families:

1. **Exit hold horizon**
   - `exit.max_hold_bars`
2. **Exit confirmation threshold**
   - `exit.exit_conf_threshold`
3. **LTF override threshold**
   - `multi_timeframe.ltf_override_threshold`

This tests whether the slice8 local backbone remains competitive when small nearby management settings are allowed to move, rather than remaining dependent on one inherited management tuple.

### Explicit search-space boundaries for Slice 9

| Area                     | Status in slice 9 | Rationale                                                                 |
| ------------------------ | ----------------- | ------------------------------------------------------------------------- |
| RI authority path        | fixed             | family identity already chosen                                            |
| clarity search           | fixed / out       | still unsupported by evidence                                             |
| risk_state guard tuning  | fixed             | no need to relitigate beyond slice8 backbone                              |
| regime-aware sizing      | fixed             | no need to relitigate beyond slice8 backbone                              |
| entry/gating geometry    | fixed             | slice8 already answered the local widen-search question                   |
| zone selectivity cluster | fixed             | not the current hypothesis                                                |
| HTF exit cadence         | fixed             | not the current hypothesis                                                |
| exit max_hold_bars       | tunable (bounded) | probes whether hold horizon matters around the slice8 management baseline |
| exit exit_conf_threshold | tunable (bounded) | probes whether exit confirmation strictness drives the local winner       |
| ltf_override_threshold   | tunable (bounded) | probes whether override sensitivity drives the local winner               |
| broad threshold topology | out of scope      | too much family drift                                                     |
| blind 2025 execution     | deferred          | candidate / freeze discussion must happen first                           |

### Success interpretation boundary

For slice9, “recordable evidence” and “successful bounded falsification” are not the same thing.

- A **successful bounded falsification** requires either:
  1. a validation winner strictly above slice7/slice8 score `0.26974911658712664`, or
  2. a validation winner at or above the incumbent same-head control `0.2616884080730424` together with a validated winner that differs from the slice8 management tuple on at least one reopened parameter
- Any weaker outcome may still be recorded, but it does **not** authorize canonical-anchor language

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
- No canonical-anchor declaration claims
- No implicit `run_intent` defaulting; RI admission for this slice is explicit `research_slice`
- No reopening into legacy-authority, clarity, renewed risk/sizing breadth, entry/gating/selectivity breadth, or broad threshold-topology search
- If validator or preflight rejects the exact scoped YAML, the slice is blocked; do not widen scope to “fix it” in code/tests
- Any future execution step must be packeted separately under `optuna_run_guardrails` and must end with explicit canonical-anchor deferral
