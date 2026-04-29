# COMMAND PACKET

- **Category:** `obs`
- **Mode:** `STRICT` — source: explicit current user request to continue autonomously from the completed Phase 11 lane without leaving the active governance track
- **Risk:** `HIGH` — why: Phase 12 can easily overclaim “minimal system” authority if it drifts from system-level ablation into subgroup mining or label-pocket search; no runtime behavior changes are allowed
- **Required Path:** `Full`
- **Objective:** Identify the smallest packet-authorized component-authority stack that preserves positive realized edge by progressively removing only already attested sizing-amplitude and path-order authority from the locked baseline trade system, while explicitly omitting unavailable execution, selection-membership, signal, and state-pocket ablations
- **Candidate:** `baseline_current` Phase 12 edge minimality
- **Base SHA:** `d9cc2026f9c119d1fe7010c4b7b1606553c2990b`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\GENESIS-CORE-POST PHASE-9-ROADMAP.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\sizing_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\path_dependency.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\selection_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\counterfactual_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\audit_phase10_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\edge_stability.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\bootstrap_distribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\edge_stability_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\audit_phase11_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\edge_minimality_phase12_packet_2026-04-02.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\minimal_system.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\ablation_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\audit_phase12_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - All files under `config/`
  - All files under `scripts/`
  - Any runtime/config authority changes
  - Any signal redesign or signal-space expansion
  - Any feature engineering
  - Any threshold/config/parameter changes
  - Any sizing logic changes
  - Any execution/filtering changes
  - Any backtest reruns
  - Any Optuna runs
  - Any edits to existing Phase 1–11 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/edge_minimality_phase12_packet_2026-04-02.md`
  - `results/research/fa_v2_adaptation_off/phase12_edge_minimality/minimal_system.json`
  - `results/research/fa_v2_adaptation_off/phase12_edge_minimality/ablation_summary.md`
  - `results/research/fa_v2_adaptation_off/phase12_edge_minimality/audit_phase12_determinism.json`
- **Max files touched:** `4`

### Implementation surface

- Scope IN is limited to the named roadmap/context inputs, the locked baseline trace, the locked Phase 10 outputs, the locked Phase 11 outputs, this packet, and the named Phase 12 output artifacts.
- All Scope IN inputs other than this packet during pre-approval hardening and the named Phase 12 outputs are read-only for the duration of the run.
- `selection_attribution.json` is context-only and may not contribute to candidate-system eligibility, preservation verdicts, redundant-authority findings, critical-authority findings, or minimal-system selection.
- Output root is fixed at `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase12_edge_minimality\` only; no alternate output directory is allowed.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `python -m pre_commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests.
- No strategy logic changes.
- No signal changes, feature engineering, threshold tuning, sizing changes, redesign, or architecture changes.
- Phase 12 must remain observational and must operate strictly by carry-forward and recombination of already attested Phase 10 / Phase 11 component-authority surfaces.
- Phase 12 must not return to signal-space and must not claim prediction, feature validity, or signal validity.
- Phase 6–7 invalidation remains active, Phase 8 remains candidate-only, Phase 9 remains `edge is not state-dependent`, Phase 10 remains artifact-only edge-origin attribution, and Phase 11 remains a scoped stability result; Phase 12 may not overturn or soften those locked conclusions.
- Deterministic ordering and stable JSON / markdown formatting required.
- No silent missing-field handling; required-field absence is a hard failure.
- Final interpretation must not be presented as deployment authority, runtime authority, signal validation, or promotion authority.
- Any roadmap ablation that requires unavailable artifact fields, new execution, or hypothetical pricing must be omitted explicitly with a deterministic omission reason; it may not be approximated from unstated assumptions.
- State-, regime-, zone-, or label-pocket subgroup search is forbidden in this packet. Such labels may be reported descriptively only and may not define candidate systems, preservation verdicts, or criticality verdicts.
- Phase 12 minimality claims are scoped only to the packet-defined component-authority removals below.

### Canonical baseline population and precondition definitions

- **Trace-label rule:** `trace_baseline_current.json` must map canonically to embedded payload name `baseline_current`; if an embedded payload name exists and differs, stop and FAIL.
- **Primary baseline trace-row key:** `(bar_index)` in canonical ascending `bar_index` order within the baseline trace; `timestamp` is a secondary consistency check only.
- **Sizing-eligible baseline row:** a baseline trace row where `sizing_phase` is present and non-null.
- **Trade-key rule:** a trade is keyed canonically by `(entry_timestamp, exit_timestamp, side, size, pnl)` using the exact serialized values from `trade_signatures`.
- **Baseline trade population:** all trades from `trace_baseline_current.json.trade_signatures`.
- **Normalized timestamp rule:** normalize every baseline `trace_rows.timestamp`, every baseline `trade_signatures.entry_timestamp`, and every baseline `trade_signatures.exit_timestamp` by removing the literal suffix `+00:00` exactly once if present; do not otherwise parse, round, or reinterpret timestamps.
- **Normalized baseline trace-timestamp uniqueness rule:** after normalization, no two sizing-eligible baseline trace rows may share the same normalized timestamp. Any duplicate normalized baseline trace timestamp is a hard failure.
- **Baseline entry-row join rule:** each baseline trade must join to exactly one sizing-eligible baseline trace row by matching normalized `trade_signatures.entry_timestamp` to the normalized baseline `trace_rows.timestamp`. Any missing join or duplicate join is a hard failure.
- **Join-integrity counters:** the run must compute and emit exactly these counters:
  - `baseline_trade_count_raw`
  - `matched_trade_count`
  - `unmatched_trade_count`
  - `duplicate_trade_entry_timestamp_count`
  - `duplicate_normalized_trace_timestamp_count`
  - `join_status`
    where `duplicate_trade_entry_timestamp_count` is informational only, and `join_status = EXACT_ONE_MATCH_PER_TRADE` only if `matched_trade_count == baseline_trade_count_raw`, `unmatched_trade_count == 0`, and `duplicate_normalized_trace_timestamp_count == 0`. Otherwise stop and FAIL.
- **Observed baseline trade population:** the canonical baseline trade population after exact entry-row join, ordered ascending by `(entry_timestamp, exit_timestamp, side, size, pnl)`.
- **Outcome class definitions:**
  - `WIN` if `pnl > 0`
  - `LOSS` if `pnl < 0`
  - `FLAT` if `pnl == 0`
- **Binary trade population rule:** all Phase 12 metrics must operate only on the `WIN`/`LOSS` trade population.
  - If any joined baseline trade has `FLAT` outcome, stop and FAIL.
- **Phase 10 / Phase 11 precondition rule:**
  - `audit_phase10_determinism.json.match` must equal `true`
  - `audit_phase11_determinism.json.match` must equal `true`
  - `edge_stability.json.phase11_classification.label` must equal `stable`
  - `edge_stability.json.temporal_stability.temporal_stability_verdict` must equal `PASS`
  - `edge_stability.json.bootstrap_stability.bootstrap_stability_verdict` must equal `PASS`
    Otherwise stop and FAIL.
- **Required artifact fields for Phase 12:**
  - `trade_signatures.entry_timestamp`
  - `trade_signatures.exit_timestamp`
  - `trade_signatures.side`
  - `trade_signatures.size`
  - `trade_signatures.pnl`
  - `phase10.sizing_attribution.baseline_metrics`
  - `phase10.sizing_attribution.unit_size_metrics`
  - `phase10.path_dependency.path_dependency_detected`
  - `phase10.path_dependency.shuffle_distribution_summary.max_drawdown_p_value`
  - `phase10.counterfactual_matrix.control_name`
  - `phase10.counterfactual_matrix.status`
  - `phase11.edge_stability.baseline_metrics`
  - `phase11.edge_stability.temporal_stability.temporal_stability_verdict`
  - `phase11.edge_stability.bootstrap_stability.bootstrap_stability_verdict`

### Authorized Phase 12 component-authority removals

- **Component-authority surface 1: `size_amplitude_authority`**
  - Meaning in this packet: whether realized edge sign depends on the original realized trade-size amplitudes rather than the unit-size normalized pnl vector already attested in Phase 10.
  - Authorized source artifacts:
    - `phase10_edge_origin_isolation/sizing_attribution.json`
    - `phase10_edge_origin_isolation/counterfactual_matrix.json`
- **Counterfactual lookup rule:** resolve counterfactual controls only by exact `control_name`. Exactly one record must exist for `unit_size_normalization` and exactly one for `trade_order_shuffle`; missing or duplicate matches are a hard failure.
- **Component-authority surface 2: `path_order_authority`**
  - Meaning in this packet: whether realized edge sign depends on trade ordering rather than the ordered-independent trade multiset, limited to the Phase 10 path-dependency test already attested under trade-order shuffle.
  - Authorized source artifacts:
    - `phase10_edge_origin_isolation/path_dependency.json`
    - `phase10_edge_origin_isolation/counterfactual_matrix.json`
- **Path-dependency verdict rule:** `phase10.path_dependency.path_dependency_detected` must be read using its serialized artifact type only; no string/boolean coercion is allowed. If the artifact does not present the field in the packet-declared form, stop and FAIL.
- **Stability precondition surface: `baseline_edge_stability_context`**
  - Meaning in this packet: whether the locked baseline realized system was already stable under the scoped Phase 11 temporal/bootstrap lane before any Phase 12 removal claim is made.
  - Authorized source artifacts:
    - `phase11_edge_stability/edge_stability.json`
    - `phase11_edge_stability/audit_phase11_determinism.json`
- **Selection-membership authority is omitted in this packet:** Phase 10 attests only aggregate availability counts, not a packet-authorized per-trade shared-opportunity membership ledger for the realized baseline trades.
- **Execution-timing / exit-path authority is omitted in this packet:** fixed exits, deterministic entry shifts, MAE/MFE, and intratrade path-authority surfaces remain packet-forbidden or artifact-unavailable from Phase 10.
- **Signal authority is omitted in this packet:** signal inversion and signal-space return remain forbidden.
- **State/zone/regime pocket authority is omitted in this packet:** Phase 9 already locked the state-dependence question, so such labels may not define candidate systems or authority-bearing ablations here.

### Candidate system universe

- **Candidate systems are fixed and closed in this exact order:**
  1. `BASELINE_REALIZED_SYSTEM`
  2. `UNIT_SIZE_REALIZED_SYSTEM`
  3. `ORDER_NEUTRAL_REALIZED_SYSTEM`
  4. `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`
- **`BASELINE_REALIZED_SYSTEM`**
  - retained authorities: `size_amplitude_authority`, `path_order_authority`
  - removed authorities: none
  - metrics source: `phase11.edge_stability.baseline_metrics`
- **`UNIT_SIZE_REALIZED_SYSTEM`**
  - retained authorities: `path_order_authority`
  - removed authorities: `size_amplitude_authority`
  - metrics source: `phase10.sizing_attribution.unit_size_metrics`
  - eligibility precondition: `phase10.counterfactual_matrix[unit_size_normalization].status = PASS`
- **`ORDER_NEUTRAL_REALIZED_SYSTEM`**
  - retained authorities: `size_amplitude_authority`
  - removed authorities: `path_order_authority`
  - metrics source: the realized baseline metric vector from `phase11.edge_stability.baseline_metrics`
  - path-order removal evidence source: `phase10.path_dependency.path_dependency_detected`
  - eligibility precondition: `phase10.counterfactual_matrix[trade_order_shuffle].status = PASS`
- **`UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`**
  - retained authorities: none of the two packet-authorized removable authorities
  - removed authorities: `size_amplitude_authority`, `path_order_authority`
  - metric source: `phase10.sizing_attribution.unit_size_metrics`
  - path-order removal evidence source: `phase10.path_dependency.path_dependency_detected`
  - eligibility precondition: both single-removal candidate eligibility preconditions hold

### Metric and preservation definitions

- **System metrics:** every candidate system with executed metrics must emit:
  - `trade_count`
  - `gross_profit`
  - `gross_loss`
  - `profit_factor`
  - `profit_factor_status`
  - `expectancy`
  - `win_rate`
- **Metric source rule:** Phase 12 may only reuse metric values already attested in Phase 10 / Phase 11 artifacts or directly recomputable from the locked baseline trade pnl vector without introducing new execution semantics.
- **Preservation PASS rule for `BASELINE_REALIZED_SYSTEM`:** `preserves_edge = YES` only if all are true:
  - `phase11.edge_stability.temporal_stability.temporal_stability_verdict = PASS`
  - `phase11.edge_stability.bootstrap_stability.bootstrap_stability_verdict = PASS`
  - `baseline expectancy > 0`
  - `baseline profit_factor_status = FINITE`
  - `baseline profit_factor > 1`
- **Preservation PASS rule for `UNIT_SIZE_REALIZED_SYSTEM`:** `preserves_edge = YES` only if all are true:
  - `phase10.counterfactual_matrix[unit_size_normalization].status = PASS`
  - `unit_size expectancy > 0`
  - `unit_size profit_factor_status = FINITE`
  - `unit_size profit_factor > 1`
- **Preservation PASS rule for `ORDER_NEUTRAL_REALIZED_SYSTEM`:** `preserves_edge = YES` only if all are true:
  - `phase10.counterfactual_matrix[trade_order_shuffle].status = PASS`
  - `phase10.path_dependency.path_dependency_detected = NO`
  - `baseline expectancy > 0`
  - `baseline profit_factor_status = FINITE`
  - `baseline profit_factor > 1`
- **Preservation PASS rule for `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`:** `preserves_edge = YES` only if both are true:
  - `UNIT_SIZE_REALIZED_SYSTEM.preserves_edge = YES`
  - `ORDER_NEUTRAL_REALIZED_SYSTEM.preserves_edge = YES`
- **Preservation FAIL rule:** otherwise `preserves_edge = NO`.

### Minimality and authority interpretation rules

- **Minimal-system ordering rule:** choose the first candidate in this exact order if `preserves_edge = YES`:
  1. `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`
  2. `UNIT_SIZE_REALIZED_SYSTEM`
  3. `ORDER_NEUTRAL_REALIZED_SYSTEM`
  4. `BASELINE_REALIZED_SYSTEM`
- **Minimal-system status:**
  - `IDENTIFIED` only if at least one candidate system has `preserves_edge = YES`
  - otherwise `UNRESOLVED`
- **Redundant-authority rule:**
  - `size_amplitude_authority` is `REDUNDANT` only if `UNIT_SIZE_REALIZED_SYSTEM.preserves_edge = YES`
  - `path_order_authority` is `REDUNDANT` only if `ORDER_NEUTRAL_REALIZED_SYSTEM.preserves_edge = YES`
- **Critical-authority rule:**
  - `size_amplitude_authority` is `CRITICAL` only if `BASELINE_REALIZED_SYSTEM.preserves_edge = YES` and `UNIT_SIZE_REALIZED_SYSTEM.preserves_edge = NO`
  - `path_order_authority` is `CRITICAL` only if `BASELINE_REALIZED_SYSTEM.preserves_edge = YES` and `ORDER_NEUTRAL_REALIZED_SYSTEM.preserves_edge = NO`
  - `size_amplitude_and_path_order_interaction` is `CRITICAL` only if both single-removal systems preserve edge but `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM.preserves_edge = NO`
- **Final Phase 12 interpretation is scoped only to the two packet-authorized removable component-authority surfaces above; it must not be interpreted as a claim about omitted execution, selection-membership, signal, or state-pocket surfaces.**

### Output requirements

- **`minimal_system.json`**
  - Must include:
    - `analysis_population`
    - `phase10_phase11_preconditions`
    - `baseline_metrics`
    - `candidate_systems`
    - `omitted_ablations`
    - `minimal_system_status`
    - `minimal_system_candidate`
    - `redundant_authorities`
    - `critical_authorities`
    - `phase12_conclusion`
  - Every `candidate_systems` record must include:
    - `candidate_label`
    - `removed_authorities`
    - `retained_authorities`
    - `metrics`
    - `source_artifacts`
    - `status`
    - `preserves_edge`
  - `omitted_ablations` must include explicit omission reasons for:
    - selection-membership authority
    - fixed exits
    - deterministic entry shifts
    - MAE/MFE / intratrade path authority
    - signal inversion
    - price-noise probe
    - latency-shift probe
    - state / zone / regime pocket ablation
  - `minimal_system_candidate` must be `null` only if `minimal_system_status = UNRESOLVED`; otherwise it must include the selected candidate record plus a one-line `selection_reason`.

- **`ablation_summary.md`**
  - Must include:
    - one short opening statement that Phase 12 is an observational edge-minimality analysis only
    - one explicit statement that Phase 6–7 invalidation remains active and Phase 12 does not validate signals
    - the locked Phase 11 stability precondition
    - the two packet-authorized removable authorities and their outcomes
    - omitted ablations and reasons
    - the minimal-system status and candidate, if any
    - redundant-authority findings
    - critical-authority findings
    - one explicit statement that the conclusion is scoped only to packet-authorized component-authority removals over the locked baseline trade population
    - the exact final output contract block below, copied verbatim:

      ```text
      EDGE MINIMALITY STATUS:

      - Minimal system identified: YES/NO
      - Redundant authority detected: YES/NO
      - Critical authority identified: YES/NO

      Verdict:
      Minimal preserved system is (identified / unresolved).
      ```

- **`audit_phase12_determinism.json`**
  - Must include:
    - `join_integrity`
    - `non_self_outputs`
    - `run1_hashes`
    - `run2_hashes`
    - `run1_hash`
    - `run2_hash`
    - `match`
  - `run1_hash` and `run2_hash` must be the SHA256 hash of the canonical JSON manifest built from the sorted non-self output hashes for run 1 and run 2 respectively.
  - For Phase 12 determinism, the non-self output set is exactly `minimal_system.json` and `ablation_summary.md`. `audit_phase12_determinism.json` must exclude itself and the packet file from the run-hash manifest.
  - `match = true` only if `run1_hash == run2_hash` and every non-self output hash matches exactly.
  - `audit_phase12_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.

### Gates required

- STRICT baseline gates against locked HEAD must be executed and recorded using this exact command set; do not substitute alternative commands or selectors at run time:
  - `python -m pre_commit run --all-files`
  - `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
  - `python -m pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[default_legacy_replay] tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[regime_module_replay]`
  - `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

- Coverage assertions:
  - every baseline trade must join exactly once to a sizing-eligible baseline row
  - binary trade count must reconcile exactly to the baseline trade population filtered to `WIN`/`LOSS`
  - every candidate system must reconcile exactly to its packet-defined metric source and source-artifact precondition
- Field assertions:
  - all packet-defined required artifact fields must exist
  - all numeric fields used in executed non-omitted subtests must be finite
  - every omitted ablation must emit an explicit omission reason
  - no executed candidate system may rely on a field or formula not predeclared in this packet
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 12 outputs must match exactly across both runs
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any baseline trade cannot be joined exactly once to an entry row
- any joined baseline trade has `FLAT` outcome
- any packet-defined required artifact field for an executed subtest is missing
- any packet-defined numeric value used in an executed non-omitted subtest is null, non-finite, or otherwise invalid
- any Phase 10 / Phase 11 precondition fails
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- any output would omit required conclusions or omission reasons
- any analysis step attempts to infer unavailable artifact fields instead of omitting the ablation explicitly

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for deterministic selector posture and field-discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact integrity and non-self hash discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
