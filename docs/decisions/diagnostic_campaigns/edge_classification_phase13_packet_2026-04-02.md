# COMMAND PACKET

- **Category:** `obs`
- **Mode:** `STRICT` — source: explicit current user request to continue autonomously from completed Phase 12 without leaving the active governance lane
- **Risk:** `HIGH` — why: Phase 13 can easily overclaim explanatory authority by collapsing limited artifact evidence into an overconfident edge-type label; no runtime behavior changes are allowed
- **Required Path:** `Full`
- **Objective:** Classify the observed edge type from the locked Phase 7, Phase 9, Phase 10, Phase 11, and Phase 12 artifacts only, using a fail-closed evidence matrix that selects at most one primary class and any packet-compatible supporting traits without returning to signal-space, feature-space, or new execution experiments
- **Candidate:** `baseline_current` Phase 13 edge classification
- **Base SHA:** `d9cc2026f9c119d1fe7010c4b7b1606553c2990b`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\GENESIS-CORE-POST PHASE-9-ROADMAP.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\probability_edge_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\state_edge_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\execution_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\sizing_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\path_dependency.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\selection_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\counterfactual_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\audit_phase10_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\edge_stability.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\audit_phase11_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\minimal_system.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\ablation_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\audit_phase12_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\edge_classification_phase13_packet_2026-04-02.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase13_edge_classification\edge_classification.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase13_edge_classification\edge_classification.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase13_edge_classification\audit_phase13_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - All files under `config/`
  - All files under `scripts/`
  - Any runtime/config authority changes
  - Any signal redesign or signal-space expansion
  - Any feature engineering
  - Any threshold/config/parameter changes
  - Any sizing-rule changes
  - Any execution/filtering changes
  - Any backtest reruns
  - Any Optuna runs
  - Any edits to existing Phase 1–12 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/edge_classification_phase13_packet_2026-04-02.md`
  - `results/research/fa_v2_adaptation_off/phase13_edge_classification/edge_classification.json`
  - `results/research/fa_v2_adaptation_off/phase13_edge_classification/edge_classification.md`
  - `results/research/fa_v2_adaptation_off/phase13_edge_classification/audit_phase13_determinism.json`
- **Max files touched:** `4`

### Implementation surface

- Scope IN is limited to the named roadmap/context inputs, the locked Phase 7/9/10/11/12 artifacts, this packet, and the named Phase 13 outputs.
- All Scope IN inputs other than this packet during pre-approval hardening and the named Phase 13 outputs are read-only for the duration of the run.
- Output root is fixed at `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase13_edge_classification\` only; no alternate output directory is allowed.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `python -m pre_commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests.
- No strategy logic changes.
- No signal changes, feature engineering, threshold tuning, sizing changes, redesign, or architecture changes.
- Phase 13 must remain observational and must classify edge type strictly from already locked evidence rather than from new experiments, interpolations, or unstated priors.
- Phase 13 must not return to signal-space and must not reinterpret Phase 7 signal invalidation as if it were runtime signal recovery.
- Phase 6–7 invalidation remains active, Phase 8 remains candidate-only, Phase 9 remains `edge is not state-dependent`, Phase 10 remains artifact-only edge-origin attribution, Phase 11 remains a scoped stability result, and Phase 12 remains a scoped minimality result; Phase 13 may not overturn or soften those locked conclusions.
- Deterministic ordering and stable JSON / markdown formatting required.
- No silent missing-field handling; required-field absence is a hard failure.
- Final interpretation must not be presented as deployment authority, runtime authority, signal validation, or promotion authority.
- Any edge class that requires packet-forbidden or artifact-unavailable surfaces must be emitted as `UNATTESTED`, not approximated.
- Phase 13 must distinguish between a **primary classification** and any **supporting traits**; descriptive traits may not be silently promoted to primary explanatory authority.
- Limited execution and selection attribution surfaces from Phase 10 must actively constrain positive class support; they may not be listed as caveats while leaving explanatory classes effectively unconstrained.

### Canonical evidence preconditions

- `audit_phase10_determinism.json.match` must equal `true`.
- `audit_phase11_determinism.json.match` must equal `true`.
- `audit_phase12_determinism.json.match` must equal `true`.
- `edge_stability.json.phase11_classification.label` must equal one of `stable`, `fragile`, or `noise-driven`.
- `state_edge_matrix.json.final_verdict` must equal one of `edge is state-conditional` or `edge is not state-dependent`.
- `probability_edge_stats.json.verdict` must equal one of `real edge`, `no edge`, or `uncertain edge`.
- `minimal_system.json.minimal_system_status` must equal one of `IDENTIFIED` or `UNRESOLVED`.
- Otherwise stop and FAIL.

### Required artifact fields for Phase 13

- `phase7.probability_edge_stats.calibration`
- `phase7.probability_edge_stats.gap_monotonicity`
- `phase7.probability_edge_stats.statistical_edge`
- `phase7.probability_edge_stats.verdict`
- `phase9.state_edge_matrix.final_verdict`
- `phase10.execution_attribution.analysis_status`
- `phase10.execution_attribution.execution_conclusion`
- `phase10.sizing_attribution.deltas.expectancy_delta_actual_minus_unit`
- `phase10.path_dependency.path_dependency_detected`
- `phase10.selection_attribution.selection_surface_status`
- `phase10.counterfactual_matrix.control_name`
- `phase10.counterfactual_matrix.status`
- `phase11.edge_stability.phase11_classification.label`
- `phase11.edge_stability.temporal_stability.temporal_stability_verdict`
- `phase11.edge_stability.bootstrap_stability.bootstrap_stability_verdict`
- `phase12.minimal_system.minimal_system_status`
- `phase12.minimal_system.minimal_system_candidate.candidate_label`
- `phase12.minimal_system.redundant_authorities.authority`
- `phase12.minimal_system.redundant_authorities.status`
- `phase12.minimal_system.critical_authorities.authority`
- `phase12.minimal_system.critical_authorities.status`

### Classification universe

- The only packet-authorized edge classes are this exact closed set:
  - `structural_market_microstructure`
  - `statistical_artifact`
  - `regime_independent_drift`
  - `execution_inefficiency`
  - `emergent_system_behavior`
- The only packet-authorized class statuses are:
  - `SUPPORTED`
  - `REJECTED`
  - `UNATTESTED`
- The only packet-authorized final classification statuses are:
  - `IDENTIFIED`
  - `UNRESOLVED`

### Evidence predicates

- `phase7_signal_edge_rejected = TRUE` only if all are true:
  - `probability_edge_stats.json.verdict = no edge`
  - `probability_edge_stats.json.calibration = FAIL`
  - `probability_edge_stats.json.statistical_edge = NO`
- `phase9_state_dependence_rejected = TRUE` only if `state_edge_matrix.json.final_verdict = edge is not state-dependent`.
- `phase11_stability_supported = TRUE` only if all are true:
  - `edge_stability.json.phase11_classification.label = stable`
  - `edge_stability.json.temporal_stability.temporal_stability_verdict = PASS`
  - `edge_stability.json.bootstrap_stability.bootstrap_stability_verdict = PASS`
- `phase10_execution_surface_limited = TRUE` only if `execution_attribution.json.analysis_status = LIMITED_ARTIFACT_SURFACE`.
- `phase10_selection_surface_limited = TRUE` only if `selection_attribution.json.selection_surface_status = AVAILABILITY_CONTRAST_ONLY`.
- `phase12_size_amplitude_redundant = TRUE` only if `minimal_system.json.redundant_authorities` contains exactly one record with `authority = size_amplitude_authority` and `status = REDUNDANT`.
- `phase12_path_order_redundant = TRUE` only if `minimal_system.json.redundant_authorities` contains exactly one record with `authority = path_order_authority` and `status = REDUNDANT`.
- `phase12_minimal_packet_system_identified = TRUE` only if all are true:
  - `minimal_system.json.minimal_system_status = IDENTIFIED`
  - `minimal_system.json.minimal_system_candidate.candidate_label = UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`
- `phase12_tested_local_authorities_noncritical = TRUE` only if all are true:
  - `minimal_system.json.critical_authorities` contains exactly one record with `authority = size_amplitude_authority` and `status = NOT_CRITICAL`
  - `minimal_system.json.critical_authorities` contains exactly one record with `authority = path_order_authority` and `status = NOT_CRITICAL`
  - `minimal_system.json.critical_authorities` contains exactly one record with `authority = size_amplitude_and_path_order_interaction` and `status = NOT_CRITICAL`
- `phase10_trade_order_counterfactual_pass = TRUE` only if `counterfactual_matrix.json` contains exactly one `trade_order_shuffle` record and its `status = PASS`.
- `phase10_unit_size_counterfactual_pass = TRUE` only if `counterfactual_matrix.json` contains exactly one `unit_size_normalization` record and its `status = PASS`.

### Class assessment rules

- **`statistical_artifact`**
  - `SUPPORTED` only if `edge_stability.json.phase11_classification.label = noise-driven`.
  - `REJECTED` only if `phase11_stability_supported = TRUE`.
  - Otherwise `UNATTESTED`.

- **`execution_inefficiency`**
  - `SUPPORTED` is forbidden in this packet because the locked execution artifact surface is explicitly limited and does not authorize price-path-dependent execution counterfactual attribution.
  - `UNATTESTED` only if `phase10_execution_surface_limited = TRUE`.
  - Otherwise stop and FAIL.

- **`structural_market_microstructure`**
  - `SUPPORTED` is forbidden in this packet because no packet-authorized market-microstructure artifact surface exists in the locked inputs.
  - `UNATTESTED` must be emitted.

- **`regime_independent_drift`**
  - `SUPPORTED` is forbidden in this packet because the locked artifact surface does not directly attribute residual edge to a drift mechanism after Phase 10 execution and selection surfaces remained limited.
  - `REJECTED` only if `state_edge_matrix.json.final_verdict = edge is state-conditional`.
  - `UNATTESTED` only if all are true:
    - `phase9_state_dependence_rejected = TRUE`
    - `phase11_stability_supported = TRUE`
    - `phase10_execution_surface_limited = TRUE`
    - `phase10_selection_surface_limited = TRUE`
  - Otherwise stop and FAIL.

- **`emergent_system_behavior`**
  - `SUPPORTED` only if all are true:
    - `phase7_signal_edge_rejected = TRUE`
    - `phase9_state_dependence_rejected = TRUE`
    - `phase11_stability_supported = TRUE`
    - `phase12_minimal_packet_system_identified = TRUE`
    - `phase12_size_amplitude_redundant = TRUE`
    - `phase12_path_order_redundant = TRUE`
    - `phase12_tested_local_authorities_noncritical = TRUE`
    - `phase10_trade_order_counterfactual_pass = TRUE`
    - `phase10_unit_size_counterfactual_pass = TRUE`
  - `REJECTED` only if `statistical_artifact = SUPPORTED`.
  - Otherwise `UNATTESTED`.

### Primary classification and supporting trait rules

- Primary classification must be chosen from the class statuses above using this exact precedence over `SUPPORTED` classes only:
  1. `statistical_artifact`
  2. `execution_inefficiency`
  3. `structural_market_microstructure`
  4. `emergent_system_behavior`
  5. `regime_independent_drift`
- `primary_classification_status = IDENTIFIED` only if at least one class is `SUPPORTED`.
- Otherwise `primary_classification_status = UNRESOLVED`.
- `supporting_traits` may contain only packet-authorized classes that are `SUPPORTED` but not selected as primary.
- `UNATTESTED` classes may not appear in `supporting_traits`.
- Final interpretation must state explicitly that `UNATTESTED` is not equivalent to `REJECTED`.

### Output requirements

- **`edge_classification.json`**
  - Must include:
    - `analysis_population`
    - `phase13_preconditions`
    - `evidence_predicates`
    - `class_assessments`
    - `primary_classification_status`
    - `primary_classification`
    - `supporting_traits`
    - `unattested_classes`
    - `rejected_classes`
    - `phase13_conclusion`
  - `class_assessments` records must be emitted in this exact order:
    1. `structural_market_microstructure`
    2. `statistical_artifact`
    3. `regime_independent_drift`
    4. `execution_inefficiency`
    5. `emergent_system_behavior`
  - `class_assessments` must contain exactly one record for each class in the packet-defined classification universe.
  - Every class-assessment record must include:
    - `class_label`
    - `status`
    - `basis`
    - `source_artifacts`
  - `primary_classification` must be `null` only if `primary_classification_status = UNRESOLVED`.
  - `unattested_classes` and `rejected_classes` must be emitted in the same fixed class-universe order shown above.

- **`edge_classification.md`**
  - Must include:
    - one short opening statement that Phase 13 is an observational classification only
    - one explicit statement that Phase 6–7 invalidation remains active and Phase 13 does not validate signals
    - one explicit statement that `UNATTESTED` is not the same as `REJECTED`
    - the selected primary classification, if any
    - any supporting traits
    - the unattested classes and why they remain unattested
    - the rejected classes and why they were rejected
    - one explicit scope statement that the conclusion is limited to packet-authorized artifact surfaces from Phases 7/9/10/11/12
    - the exact final output contract block below, copied verbatim:

      ```text
      EDGE CLASSIFICATION STATUS:

      - Primary classification identified: YES/NO
      - Supporting trait identified: YES/NO
      - Statistical artifact supported: YES/NO
      - Emergent system behavior supported: YES/NO

      Verdict:
      Edge classification is (identified / unresolved).
      ```

- **`audit_phase13_determinism.json`**
  - Must include:
    - `non_self_outputs`
    - `run1_hashes`
    - `run2_hashes`
    - `run1_hash`
    - `run2_hash`
    - `match`
  - For Phase 13 determinism, the non-self output set is exactly `edge_classification.json` and `edge_classification.md`. `audit_phase13_determinism.json` must exclude itself and the packet file from the run-hash manifest.
  - `match = true` only if `run1_hash == run2_hash` and every non-self output hash matches exactly.
  - `audit_phase13_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.

### Gates required

- STRICT baseline gates against locked HEAD must be executed and recorded using this exact command set; do not substitute alternative commands or selectors at run time:
  - `python -m pre_commit run --all-files`
  - `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
  - `python -m pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[default_legacy_replay] tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[regime_module_replay]`
  - `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Field assertions:
  - all packet-defined required artifact fields must exist
  - every class assessment must use only packet-declared evidence predicates
  - every emitted `SUPPORTED`, `REJECTED`, or `UNATTESTED` status must satisfy its packet-defined rule exactly
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 13 outputs must match exactly across both runs
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any packet-defined required artifact field is missing
- any class assessment would require packet-forbidden or artifact-unavailable evidence
- any output would silently treat `UNATTESTED` as `REJECTED`
- more than one primary classification is selected outside the packet-defined precedence rule
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for deterministic selector posture and `.github/skills/ri_off_parity_artifact_check.json` for artifact integrity and non-self hash discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
