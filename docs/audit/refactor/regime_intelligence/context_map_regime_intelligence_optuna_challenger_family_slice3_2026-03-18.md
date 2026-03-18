## Context Map

### Slice Objective

Create the third Regime Intelligence Optuna campaign for `tBTCUSD` on `3h` that:

- keeps the incumbent champion as the control baseline
- preserves the validated RI challenger-family identity (`regime_module`, `v2`, clarity off, risk_state on)
- responds to slice-2 evidence that train improved while validation plateaued below the incumbent
- opens generalization-sensitive surfaces (exit, override, Fib tolerance) instead of rerunning an unchanged slice-2 threshold search
- does not change runtime defaults, champion files, or any `src/**` behavior

### Files to Modify

| File                                                                                                                       | Purpose                             | Changes Needed                                                                                                                     |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`                          | RI challenger-family slice-3 config | Change the hypothesis toward generalization-sensitive surfaces while preserving RI family identity and fixed train/validation windows |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md` | Governance contract for slice 3     | Lock scope, gates, execution preconditions, storage rules, baseline reuse, and background-launch constraints                        |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md`    | This context map                    | Record slice-2 evidence, diff-driven hypothesis, and search boundaries                                                               |

### Evidence Base for the Slice-3 Hypothesis

| Artifact                                                                          | Key finding                                                                                                                        |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `results/hparam_search/run_20260318_131831/run_meta.json`                         | slice-2 used committed SHA `eb005af43ec243c65e8226f7d0096f259bf9ac03`; 48 trials; best train value `0.41198145928409136`         |
| `results/hparam_search/run_20260318_131831/best_trial.json`                       | slice-2 best train candidate was `trial_006`, proving the RI family can produce strong train behavior                               |
| `results/hparam_search/run_20260318_131831/validation/trial_001.json`             | slice-2 top validation score tied at `0.21086175290248949`, below incumbent                                                         |
| `tmp/champion_validation_eb005af4.log`                                             | incumbent champion still leads validation on same HEAD/canonical flags with score `0.2617`                                          |
| `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md` | RI should be treated as a `new strategy family`; overlaying RI onto the incumbent is not the main path                             |
| `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`                 | next search should continue inside the RI challenger family, but must beat incumbent on stronger standards                          |

### Why slice-2 should NOT just be rerun with 200 trials

- Slice-2 already showed a strong train winner (`trial_006`) but the validation cluster flattened at `0.2109`.
- The incumbent control remained stronger at `0.2617` on the same validation window and same canonical flags.
- This suggests that simply increasing trial count in the same slice-2 search space is more likely to produce additional train winners than a materially better validation candidate.

### RI Family Identity to Preserve

| Area                                                        | Slice-3 status        | Rationale                                                                                   |
| ----------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------- |
| `multi_timeframe.regime_intelligence.enabled`               | fixed `true`          | slice-3 remains RI-on challenger research                                                   |
| `multi_timeframe.regime_intelligence.version`               | fixed `v2`            | preserve the validated RI family version                                                    |
| `multi_timeframe.regime_intelligence.authority_mode`        | fixed `regime_module` | slice-3 does not reopen the legacy branch                                                   |
| `multi_timeframe.regime_intelligence.clarity_score.enabled` | fixed `false`         | clarity remains excluded until core RI signal beats incumbent                               |
| `multi_timeframe.regime_intelligence.risk_state.enabled`    | fixed `true`          | validated family kept `risk_state` on                                                       |
| `thresholds.signal_adaptation.atr_period`                   | fixed `14`            | part of the RI-compatible compatibility cluster                                              |
| `gates.hysteresis_steps` / `gates.cooldown_bars`            | fixed `3/2`           | preserve the RI family gating cadence                                                        |

### Slice-3 Hypothesis Shift

The slice-3 search space should keep the threshold family narrower than slice-2 and instead open parameters more likely to affect out-of-sample robustness:

1. **Exit surface**
   - `exit.max_hold_bars`
   - `exit.trailing_stop_pct`
   - `exit.stop_loss_pct`
2. **LTF override policy**
   - `multi_timeframe.ltf_override_threshold`
3. **Fib tolerance surface**
   - `htf_fib.entry.tolerance_atr`
   - `ltf_fib.entry.tolerance_atr`
4. **Threshold family retained, but narrower**
   - keep the RI-family threshold shape around `trial_006`
   - do not reopen a wide topology search
5. **Risk-state guards**
   - keep fixed to the slice-2 best-train values to reduce search noise unless later evidence says otherwise

### Proposed Search-Space Boundaries for Slice 3

| Area                                 | Status in slice 3 | Rationale                                                                 |
| ------------------------------------ | ----------------- | ------------------------------------------------------------------------- |
| RI authority path                    | fixed             | family identity already chosen                                            |
| threshold family near `trial_006`    | tunable, narrow   | preserve candidate identity while reducing threshold-only overfitting      |
| exit surface                         | tunable           | likely stronger effect on generalization than more threshold micro-tuning  |
| `ltf_override_threshold`             | tunable           | may improve transfer across validation without reopening full topology     |
| Fib entry tolerances                 | tunable           | candidate-vs-incumbent diff suggests this is a meaningful but bounded axis |
| risk-state guards                    | fixed             | remove unnecessary noise after slice-2 plateau                            |
| clarity search                       | out of scope      | still unsupported by evidence                                             |
| legacy authority / incumbent overlay | out of scope      | already rejected as the primary path                                      |
| blind 2025 execution                 | deferred          | candidate freeze must happen first                                        |

### Reference Config Patterns

| File                                                                                            | Pattern / Relevance                                                    |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml` | slice-2 baseline taxonomy and fixed RI-family identity                 |
| `config/optimizer/README.md`                                                                    | canonical optimizer folder placement and path-stability rules          |
| `docs/templates/skills/optuna_run_guardrails.md`                                                | required validator + preflight + canonical mode rules                  |

### Verification Anchors

| Anchor                                                                                                     | Role in this slice                                                                           |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `scripts/validate/validate_optimizer_config.py`                                                            | structural/config semantics validation for the new YAML                                      |
| `scripts/preflight/preflight_optuna_check.py`                                                              | Optuna/storage/pre-run guardrail validation                                                  |
| temporary smoke config under `tmp/`                                                                        | proves the slice-3 config can start cleanly with unique temporary `study_name` and storage   |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay anchor                                                                    |
| `tests/utils/test_features_asof_cache_key_deterministic.py`                                                | feature-cache invariance anchor                                                              |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant anchor                                                                    |
| `tests/governance/test_authority_mode_resolver.py`                                                         | explicit authority-mode resolver anchor for the fixed `regime_module` family identity        |

### Non-Negotiable Boundaries

- No edits to `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- No committed `results/**` changes in this slice
- No blind 2025 fixed-candidate execution in this slice
- No promotion/default/cutover claims
- No reopening into legacy-authority or clarity search
- Any temporary smoke YAML/DB must live under `tmp/` and remain out of commit scope
- Any future winner-freeze / blind-eval step must be a separate follow-up slice
