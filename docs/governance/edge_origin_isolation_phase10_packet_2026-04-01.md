# COMMAND PACKET

- **Category:** `obs`
- **Mode:** `STRICT` — source: explicit current user request to continue from the post-Phase 9 roadmap under the locked governance posture
- **Risk:** `MED` — why: artifact-only edge-origin attribution over the locked baseline ledger can still create false mechanistic claims if joins, counterfactual definitions, or determinism are underdefined; no runtime behavior changes are allowed
- **Required Path:** `Full`
- **Objective:** Decompose observed baseline edge into packet-authorized execution, sizing, path, selection, and counterfactual attribution surfaces using only locked artifacts and deterministic post-execution analysis without modifying strategy logic, signals, thresholds, sizing, execution, or filtering
- **Candidate:** `baseline_current` Phase 10 edge origin isolation
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\GENESIS-CORE-POST PHASE-9-ROADMAP.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\state_edge_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\state_edge_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\edge_origin_isolation_phase10_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\execution_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\execution_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\sizing_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\sizing_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\path_dependency.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\path_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\selection_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\selection_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\counterfactual_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\audit_phase10_determinism.json`
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
  - Any edits to existing Phase 1–9 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/governance/edge_origin_isolation_phase10_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/execution_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/execution_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/sizing_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/sizing_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/path_dependency.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/path_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/selection_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/selection_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/counterfactual_matrix.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation/audit_phase10_determinism.json`
- **Max files touched:** `11`

### Implementation surface

- Scope IN is limited to the named roadmap/context inputs, the two locked trace artifacts, the Phase 9 state-isolation outputs, this packet, and the named Phase 10 output artifacts.
- All Scope IN inputs other than this packet during pre-approval hardening and the named Phase 10 outputs are read-only for the duration of the run.
- Output root is fixed at `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\` only; no alternate output directory is allowed.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `pre-commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests.
- No strategy logic changes.
- No signal changes, feature engineering, threshold tuning, sizing changes, redesign, or architecture changes.
- Phase 10 must remain observational and must operate strictly by post-execution attribution over the already executed baseline trades.
- Phase 10 must not return to signal-space and must not claim prediction, feature validity, or signal validity.
- Phase 6–7 invalidation remains active, Phase 8 remains candidate-only, and Phase 9 remains `edge is not state-dependent`; Phase 10 may not overturn or soften those locked conclusions.
- Deterministic ordering and stable JSON / markdown formatting required.
- No silent missing-field handling; required-field absence is a hard failure.
- Final interpretation must not be presented as deployment authority, runtime authority, signal validation, or promotion authority.
- Any roadmap experiment that requires unavailable artifact fields must be omitted explicitly with a deterministic omission reason; it may not be approximated from unstated assumptions.

### Canonical populations and join definitions

- **Trace-label rules:**
  - `trace_baseline_current.json` must map canonically to embedded payload name `baseline_current`; if an embedded payload name exists and differs, stop and FAIL.
  - `trace_adaptation_off.json` may be inspected only for admission/selection contrast metadata and must not replace the baseline population for realized edge attribution.
- **Primary baseline trace-row key:** `(bar_index)` in canonical ascending `bar_index` order within the baseline trace; `timestamp` is a secondary consistency check only.
- **Sizing-eligible baseline row:** a baseline trace row where `sizing_phase` is present and non-null.
- **Trade-key rule:** a trade is keyed canonically by `(entry_timestamp, exit_timestamp, side, size, pnl)` using the exact serialized values from `trade_signatures`.
- **Baseline trade population:** all trades from `trace_baseline_current.json.trade_signatures`.
- **Normalized timestamp rule:** normalize every baseline `trace_rows.timestamp`, every adaptation-off `trace_rows.timestamp`, and every baseline `trade_signatures.entry_timestamp` by removing the literal suffix `+00:00` exactly once if present; do not otherwise parse, round, or reinterpret timestamps.
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
- **Exit-row resolution rule:** a baseline trade exit row is resolved only if normalized `trade_signatures.exit_timestamp` maps to exactly one normalized baseline `trace_rows.timestamp` in canonical trace ordering. If exact exit-row resolution fails for any trade, any exit-row-dependent metric must be emitted as `OMITTED_EXIT_ROW_UNATTESTED` and may not be inferred.
- **Outcome class definitions:**
  - `WIN` if `pnl > 0`
  - `LOSS` if `pnl < 0`
  - `FLAT` if `pnl == 0`
- **Binary trade population rule:** all attribution metrics must operate only on the `WIN`/`LOSS` trade population.
  - If any joined baseline trade has `FLAT` outcome, stop and FAIL.

### Authorized artifact fields

Phase 10 may rely only on the following directly attested artifact fields unless a later packet extends the contract:

- **Trade-signature fields:**
  - `trade_signatures.entry_timestamp`
  - `trade_signatures.exit_timestamp`
  - `trade_signatures.side`
  - `trade_signatures.size`
  - `trade_signatures.pnl`
- **Baseline decision/sizing linkage fields on joined entry rows:**
  - `trace_rows.bar_index`
  - `trace_rows.timestamp`
  - `trace_rows.decision_phase.selected_candidate`
  - `trace_rows.decision_phase.p_buy`
  - `trace_rows.decision_phase.p_sell`
  - `trace_rows.decision_phase.ev_long`
  - `trace_rows.decision_phase.ev_short`
  - `trace_rows.decision_phase.max_ev`
  - `trace_rows.sizing_phase.candidate`
  - `trace_rows.sizing_phase.base_size`
  - `trace_rows.sizing_phase.size_scale`
  - `trace_rows.sizing_phase.volatility_adjustment`
  - `trace_rows.sizing_phase.regime_multiplier`
  - `trace_rows.sizing_phase.htf_regime_multiplier`
  - `trace_rows.sizing_phase.combined_multiplier`
  - `trace_rows.sizing_phase.final_size`
  - `trace_rows.final.action`
  - `trace_rows.final.size`
  - `trace_rows.final.regime`
  - `trace_rows.final.htf_regime`
  - `trace_rows.final.reasons`
  - `trace_rows.final.zone_debug.zone`
  - `trace_rows.final.zone_debug.atr`
  - `trace_rows.fib_phase.ltf_debug.price`
  - `trace_rows.fib_phase.ltf_debug.atr`
  - `trace_rows.fib_phase.ltf_debug.tolerance`
- **Unavailable in this packet unless authorized by a new pre-reviewed packet:**
  - intratrade MAE/MFE paths
  - per-bar OHLC paths for full holding windows
  - realized entry_price or exit_price fields at trade granularity
  - alternative candidate-universe ledgers at trade granularity
  - any signal inversion field beyond the existing selected candidate labels
- **Interpretation guard for decision fields:** `trace_rows.decision_phase.p_buy`, `p_sell`, `ev_long`, `ev_short`, and `max_ev` may be emitted descriptively in Phase 10 outputs only if needed for field-attestation context; they must not be used for signal-validity claims, predictive-validity claims, causal attribution claims, or runtime-authority claims.

### Phase 10 analysis surfaces

- **10.1 Execution attribution (authorized in limited form)**
  - Allowed realized baseline metrics:
    - `trade_count`
    - `profit_factor`
    - `expectancy`
    - `win_rate`
    - `holding_period_bars`, but only for trades whose exit row resolves exactly under the packet-defined exit-row resolution rule
  - Allowed derived comparisons:
    - descriptive holding-period distribution over the realized baseline trade population only
  - Forbidden in this packet:
    - MAE/MFE
    - intratrade realized-vs-unrealized edge
    - price-path-dependent fixed exits
    - `deterministic_entry_shift`
    - `fixed_horizon_exit_k_bars`
  - Execution attribution must emit `analysis_status = LIMITED_ARTIFACT_SURFACE` and mark all forbidden execution counterfactuals as omitted with explicit reasons.

- **10.2 Sizing attribution (authorized)**
  - Use observed baseline trade population only.
  - Compute `unit_pnl = pnl / size` for every trade; if any `size <= 0`, stop and FAIL.
  - Compute unit-size normalized portfolio metrics by treating each trade as size 1 with the same `unit_pnl`.
  - Compute realized baseline metrics using original `pnl`.
  - Report `expectancy_delta_actual_minus_unit`, `profit_factor_delta_actual_minus_unit`, and `win_rate_delta_actual_minus_unit`.
  - Decompose against joined entry-row sizing fields (`base_size`, `size_scale`, `volatility_adjustment`, `regime_multiplier`, `htf_regime_multiplier`, `combined_multiplier`, `final_size`) descriptively only; do not optimize or regress.

- **10.3 Path dependency (authorized)**
  - Preserve the exact baseline trade multiset.
  - Deterministically reshuffle trade order only; do not alter pnl values or trade membership.
  - Primary path metric is equity-curve path shape, not trade-level PF, because PF is order-invariant for a fixed trade multiset.
  - Compute and emit for baseline order and shuffled orders:
    - final cumulative pnl
    - max drawdown on cumulative pnl path
    - longest loss streak
    - longest win streak
    - time-under-water in trades
  - Inferential metric set is frozen to `max_drawdown` only; all other path metrics are descriptive only.
  - Permutation test:
    - shuffle trade order with fresh `random.Random(20260401)`
    - iterations: `5000`
    - compute shuffled `max_drawdown` distribution only
    - let `shuffled_median_max_drawdown` be the median of the shuffled `max_drawdown` values
    - let `actual_distance = abs(actual_max_drawdown - shuffled_median_max_drawdown)`
    - let `shuffled_distance_i = abs(shuffled_max_drawdown_i - shuffled_median_max_drawdown)`
    - one two-sided empirical p-value formula for path inference is `(extreme_count + 1) / (iterations + 1)`, where `extreme_count` counts `shuffled_distance_i >= actual_distance`
  - Report `path_dependency_detected = YES` only if the frozen inferential `max_drawdown` p-value is `<= 0.05`; otherwise `NO`.

- **10.4 Selection / admission attribution (authorized in contrast form)**
  - Baseline realized edge attribution must stay on the baseline trade population.
  - Adaptation-off trace may be used only as a contrast source for admission opportunity counts at timestamp level, not as a replacement realized ledger.
  - `adaptation_off_eligible_row` is defined exactly as a `trace_adaptation_off.json.trace_rows` row where `sizing_phase` is present and non-null.
  - `baseline_eligible_row` is defined exactly as a `trace_baseline_current.json.trace_rows` row where `sizing_phase` is present and non-null.
  - `eligible_timestamp_key` is the normalized row timestamp only.
  - `contrast_population` is defined exactly as the set comparison of `eligible_timestamp_key` values between baseline eligible rows and adaptation-off eligible rows.
  - The only authorized selection contrast in this packet is timestamp-level opportunity availability. When the required adaptation-off fields are present and normalized timestamps are unique, emit:
    - shared opportunity count
    - baseline-only opportunity count
    - adaptation-off-only opportunity count
  - Random subset sampling is not authorized in this packet.
  - If adaptation-off timestamp uniqueness, required row fields, or contrast-set construction cannot be attested exactly from current artifacts, selection attribution must emit `selection_surface_status = CONTRAST_UNAVAILABLE` and stop short of stronger selection claims.
  - Stronger selection causality claims are forbidden in this packet.

- **10.5 Counterfactual matrix (authorized only for packet-defined controls)**
  - Allowed controls:
    - `unit_size_normalization`
    - `trade_order_shuffle`
  - Forbidden controls in this phase:
    - `deterministic_entry_shift`
    - `fixed_horizon_exit_k_bars`
    - signal inversion if inversion would imply signal redesign or require un-attested candidate semantics beyond `selected_candidate`
    - any control requiring rerun, new execution, or synthetic pricing not directly derivable from attested artifact fields
  - Every control must emit one of:
    - `PASS`
    - `OMITTED_<REASON>`
    - `FAIL_<REASON>`

### Metric definitions

- **Profit factor definition:** let `gross_profit = sum(pnl_i for pnl_i in rows if pnl_i > 0)` and `gross_loss = abs(sum(pnl_i for pnl_i in rows if pnl_i < 0))`. If `gross_loss == 0`, emit `profit_factor = null` and `profit_factor_status = NO_LOSS_DENOMINATOR`; otherwise emit `profit_factor = gross_profit / gross_loss` and `profit_factor_status = FINITE`.
- **Expectancy:** `mean(pnl)` over the target row set.
- **Win rate:** `wins / trade_count` over the target row set.
- **Equity path:** cumulative sum of ordered pnl values.
- **Max drawdown:** peak-to-trough drop on the cumulative pnl path in absolute pnl units.
- **Longest loss streak / longest win streak:** longest contiguous run of negative / positive pnl values in the examined ordering.
- **Time under water in trades:** number of trade steps spent below the prior cumulative pnl peak.

### Output requirements

- **`execution_attribution.json`**
  - Must include:
    - `analysis_population`
    - `baseline_metrics`
    - `authorized_subtests`
    - `omitted_subtests`
    - `execution_conclusion`
  - Must state explicitly that `MAE_MFE`, `price_path_fixed_exit`, `deterministic_entry_shift`, and `fixed_horizon_exit_k_bars` are omitted in this packet.

- **`execution_summary.md`**
  - Must include:
    - one short statement that execution attribution is observational only
    - executed versus omitted execution subtests
    - explicit limitation note if artifact surface is limited
    - one short execution conclusion

- **`sizing_attribution.json`**
  - Must include:
    - `analysis_population`
    - `baseline_metrics`
    - `unit_size_metrics`
    - `deltas`
    - `sizing_surface_summary`
    - `sizing_conclusion`

- **`sizing_summary.md`**
  - Must include:
    - baseline versus unit-size metrics
    - attribution deltas
    - one short sizing conclusion

- **`path_dependency.json`**
  - Must include:
    - `analysis_population`
    - `baseline_path_metrics`
    - `shuffle_distribution_summary`
    - `path_dependency_detected`
    - `path_conclusion`

- **`path_summary.md`**
  - Must include:
    - baseline path metrics
    - shuffled-order comparison
    - explicit statement that PF is order-invariant and path inference is based on path metrics instead
    - one short path conclusion

- **`selection_attribution.json`**
  - Must include:
    - `analysis_population`
    - `contrast_source`
    - `selection_surface_status`
    - `selection_metrics`
    - `selection_conclusion`
  - If `selection_surface_status = CONTRAST_UNAVAILABLE`, `selection_metrics` may include only omission diagnostics and not inferred attribution metrics.

- **`selection_summary.md`**
  - Must include:
    - whether deterministic contrast population was available
    - executed versus omitted selection tests
    - one short selection conclusion

- **`counterfactual_matrix.json`**
  - Must include one record for each packet-authorized control with:
    - `control_name`
    - `status`
    - `reason`
    - `metrics` when executed, else `null`

- **`audit_phase10_determinism.json`**
  - Must include:
    - `join_integrity`
    - `non_self_outputs`
    - `run1_hashes`
    - `run2_hashes`
    - `run1_hash`
    - `run2_hash`
    - `match`
  - `run1_hash` and `run2_hash` must be the SHA256 hash of the canonical JSON manifest built from the sorted non-self output hashes for run 1 and run 2 respectively.
  - `match = true` only if `run1_hash == run2_hash` and every non-self output hash matches exactly.
  - `audit_phase10_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.

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
  - every executed attribution surface must account for its full declared trade population exactly once
- Field assertions:
  - all packet-defined required fields must exist on every relevant joined row
  - all numeric fields used in executed subtests must be finite
  - every omitted subtest must emit an explicit omission reason
  - no executed subtest may rely on a field or formula not predeclared in this packet
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 10 outputs must match exactly across both runs
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any baseline trade cannot be joined exactly once to an entry row
- any joined baseline trade has `FLAT` outcome
- any packet-defined required field for an executed subtest is missing from any relevant row
- any packet-defined numeric value used in an executed subtest is null, non-finite, or otherwise invalid
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- any output would omit required conclusions or omission reasons
- any analysis step attempts to infer unavailable artifact fields instead of omitting the subtest explicitly

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for deterministic selector posture and field-discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact integrity and non-self hash discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
