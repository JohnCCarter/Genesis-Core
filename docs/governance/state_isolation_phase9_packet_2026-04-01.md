# COMMAND PACKET

- **Category:** `obs`
- **Mode:** `STRICT` — source: explicit current user request for Phase 9 state isolation test in STRICT mode
- **Risk:** `MED` — why: artifact-only observational state-isolation analysis over the locked baseline trade ledger; no runtime behavior changes allowed, but any claim that edge is state-conditional must be deterministic, reproducible, fail-closed, and must not be confused with signal validation or promotion authority
- **Required Path:** `Full`
- **Objective:** Assess whether observed edge is concentrated across packet-defined state dimensions within the locked baseline trade ledger by partitioning the population deterministically and measuring per-state trade performance without changing signals, thresholds, sizing, execution, or filtering
- **Candidate:** `baseline_current` Phase 9 state isolation
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\signal_candidates.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\signal_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\audit_feature_universe.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\state_isolation_phase9_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\state_edge_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\state_edge_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\audit_state_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - All files under `config/`
  - All files under `scripts/`
  - `results/research/fa_v2_adaptation_off/trace_adaptation_off.json`
  - Any runtime/config authority changes
  - Any signal changes
  - Any threshold/config/parameter changes
  - Any sizing changes
  - Any execution/filtering changes
  - Any backtest reruns
  - Any Optuna runs
  - Any edits to existing Phase 3–8 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/governance/state_isolation_phase9_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase9_state_isolation/state_edge_matrix.json`
  - `results/research/fa_v2_adaptation_off/phase9_state_isolation/state_edge_summary.md`
  - `results/research/fa_v2_adaptation_off/phase9_state_isolation/audit_state_determinism.json`
- **Max files touched:** `4`

### Implementation surface

- Scope IN is limited to the four named read-only inputs, this packet, and the three named output artifacts.
- Output root is fixed at `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase9_state_isolation\` only; no alternate output directory is allowed.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `pre-commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No signal changes, threshold tuning, sizing changes, redesign, or architecture changes
- The execution population is the locked baseline trade ledger only; Phase 9 may not substitute, expand, or merge in adaptation-off execution results for performance attribution
- State isolation must be observational only and must operate strictly by post-execution filtering of the already executed baseline trades
- Phase 9 must not validate, recover, or promote the signal layer
- Phase 6–7 invalidation remains active and may not be overturned, replaced, or softened by Phase 9 outputs
- Deterministic ordering and stable JSON / markdown formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must not be presented as deployment authority, runtime authority, signal validation, or promotion authority
- No bucket boundaries may be optimized, tuned, or data-mined beyond the packet-defined deterministic partition rules
- No rule combinations, ensemble constructions, or parameter search are allowed in this phase

### Canonical baseline population and join definitions

- **Trace-label rule:** `trace_baseline_current.json` must map canonically to embedded payload name `baseline_current`; if an embedded payload name exists and differs, stop and FAIL.
- **Primary trace-row key:** `(bar_index)` in canonical ascending `bar_index` order within the baseline trace; `timestamp` is a secondary consistency check only.
- **Sizing-eligible row:** a baseline trace row where `sizing_phase` is present and non-null.
- **Trade-key rule:** a trade is keyed canonically by `(entry_timestamp, exit_timestamp, side, size, pnl)` using the exact serialized values from `trade_signatures`.
- **Baseline trade population:** all trades from `trace_baseline_current.json.trade_signatures`.
- **Normalized timestamp rule:** normalize every sizing-eligible `trace_rows.timestamp` by removing the literal suffix `+00:00` exactly once if present; do not otherwise parse, round, or reinterpret timestamps.
- **Normalized trace-timestamp uniqueness rule:** after normalization, no two sizing-eligible baseline trace rows may share the same normalized timestamp. Any duplicate normalized trace timestamp is a hard failure.
- **Entry-row join rule:** each baseline trade must join to exactly one sizing-eligible baseline trace row by matching `trade_signatures.entry_timestamp` to the normalized `trace_rows.timestamp`. Any missing join or duplicate join is a hard failure.
- **Join-integrity counters:** the run must compute and emit exactly these counters:
  - `baseline_trade_count_raw`
  - `matched_trade_count`
  - `unmatched_trade_count`
  - `duplicate_trade_entry_timestamp_count`
  - `duplicate_normalized_trace_timestamp_count`
  - `join_status`
    where `duplicate_trade_entry_timestamp_count` is informational only, and `join_status = EXACT_ONE_MATCH_PER_TRADE` only if `matched_trade_count == baseline_trade_count_raw`, `unmatched_trade_count == 0`, and `duplicate_normalized_trace_timestamp_count == 0`. Otherwise stop and FAIL.
- **Observed trade population:** the canonical baseline trade population after exact entry-row join, ordered ascending by `(entry_timestamp, exit_timestamp, side, size, pnl)`.
- **Outcome class definitions:**
  - `WIN` if `pnl > 0`
  - `LOSS` if `pnl < 0`
  - `FLAT` if `pnl == 0`
- **Binary trade population rule:** all state metrics and state-concentration significance calculations must operate only on the `WIN`/`LOSS` trade population.
  - If any joined baseline trade has `FLAT` outcome, stop and FAIL.

### State dimensions

Phase 9 must analyze exactly these packet-defined baseline state dimensions:

- **ATR_Q4**
  - source field: `fib_phase.ltf_debug.atr`
  - partition rule: exactly 4 equal-count deterministic quantile buckets `Q1..Q4` on the binary trade population sorted by ascending `(atr_value, trade_key)`.
- **PRICE_Q4**
  - source field: `fib_phase.ltf_debug.price`
  - interpretation: observed price-level distribution quartiles only; no recalculation beyond packet-defined quartile partitioning is allowed
  - partition rule: exactly 4 equal-count deterministic quantile buckets `Q1..Q4` on the binary trade population sorted by ascending `(price_value, trade_key)`.
- **TOLERANCE_Q4**
  - source field: `fib_phase.ltf_debug.tolerance`
  - partition rule: exactly 4 equal-count deterministic quantile buckets `Q1..Q4` on the binary trade population sorted by ascending `(tolerance_value, trade_key)`.
- **FIB_ZONE_LTF**
  - source field: `final.zone_debug.zone`
  - interpretation: existing LTF fib/zone classification only; no recalculation allowed
  - partition rule: use the observed categorical labels directly with canonical bucket order `low`, `mid`, `high`; if any additional label appears, append it after the known labels in ascending lexicographic ordinal code-point order.

- **HTF availability check (mandatory):**
  - inspect `fib_phase.fib_gate_summary.htf.reason` on every joined baseline trade row.
  - If the field has exactly one observed value across the binary trade population and that value equals `UNAVAILABLE_PASS`, emit `FIB_ZONE_HTF` as omitted with reason `UNAVAILABLE_CONSTANT_STATE`.
  - Otherwise stop and FAIL with `HTF_ZONE_SOURCE_UNDEFINED`; this packet does not authorize HTF state analysis without a new pre-reviewed packet that names an explicit HTF zone source field.

### Partition rules

- **Stable sort rule:** all numeric partitioning must use a stable sort on ascending `(state_value, trade_key)` before bucket assignment.
- **Equal-count quantile rule:** for a numeric state dimension with `N` binary trades and `K = 4` buckets, compute `q = N // K` and `r = N % K`, assign buckets `Q1..Qr` exactly `q + 1` rows each, and assign the remaining buckets exactly `q` rows each.
- **No interpolation rule:** do not interpolate, smooth, rebalance, or optimize bucket boundaries.
- **Bucket support rule:** every analyzed bucket must have `trade_count >= 8`. If any required analyzed bucket has lower support, stop and FAIL.
- **Canonical bucket ordering rule:**
  - numeric quartiles must be emitted in order `Q1`, `Q2`, `Q3`, `Q4`
  - `FIB_ZONE_LTF` must be emitted in packet-defined canonical category order

### Metrics and concentration test definitions

- **Per-bucket metrics:** every analyzed bucket must emit:
  - `trade_count`
  - `profit_factor`
  - `profit_factor_status`
  - `expectancy`
  - `win_rate`
- **Profit factor definition:** let `gross_profit = sum(pnl_i for pnl_i in bucket_rows if pnl_i > 0)` and `gross_loss = abs(sum(pnl_i for pnl_i in bucket_rows if pnl_i < 0))`. If `gross_loss == 0`, emit `profit_factor = null` and `profit_factor_status = NO_LOSS_DENOMINATOR`; otherwise emit `profit_factor = gross_profit / gross_loss` and `profit_factor_status = FINITE`.
- **Bucket expectancy:** `mean(pnl)` over bucket rows.
- **Bucket win rate:** `wins / trade_count` over bucket rows.
- **Overall baseline metrics:** compute the same four metrics over the full binary baseline trade population.
- **State concentration metric:** for each analyzed state dimension, compute `expectancy_spread = max(bucket_expectancy) - min(bucket_expectancy)` across all analyzed buckets.
- **State concentration significance:** hold the binary trade `pnl` vector fixed, hold the bucket-size profile fixed, shuffle the state labels across trades only, recompute `expectancy_spread`, and compute one-sided permutation `p_value` using `shuffled_expectancy_spread >= actual_expectancy_spread`.
  - PRNG: Python stdlib `random.Random`
  - seed: `20260401`
  - iterations: `5000`
  - RNG lifecycle rule: for each analyzed state dimension, initialize a fresh `random.Random(20260401)` and use it only for that dimension's `5000` permutations; do not carry PRNG state across dimensions
  - p-value formula: `(extreme_count + 1) / (iterations + 1)`
- **Dimension concentration verdict:** `edge_concentrated = YES` only if `p_value <= 0.05`. Otherwise `NO`.
- **High-edge bucket rule:** for each analyzed dimension, `high_edge_bucket` is the bucket with the highest expectancy; ties break by higher finite profit factor first, then higher win rate, then canonical bucket order.
- **Null profit-factor tie rule:** in any tie-break comparison, a finite profit factor must rank ahead of `null`. If both compared profit factors are `null`, continue to the next tie-break key.
- **Low-edge bucket rule:** for each analyzed dimension, `low_edge_bucket` is the bucket with the lowest expectancy; ties break by lower finite profit factor first, then lower win rate, then canonical bucket order.
- **Overall Phase 9 verdict:**
  - `edge is state-conditional` only if at least one analyzed state dimension has `edge_concentrated = YES`
  - otherwise `edge is not state-dependent`
- **Verdict scope rule:** the Phase 9 final verdict is scoped only to the locked baseline trade ledger, the packet-defined state partitions, and the packet-defined permutation test. It must not be interpreted as signal validation, strategy validation, or an override of the active Phase 6–7 invalidation.
- **No unresolved verdict rule:** Phase 9 must emit exactly one of the two packet-defined final verdicts above; `unresolved` is forbidden.

### Phase task requirements

- **Phase 9.1 — State-axis attestation**
  - Prove that every analyzed state field exists on every joined baseline trade row.
  - Prove that every numeric state field is finite on every joined baseline trade row.
  - Prove the HTF availability check outcome deterministically.

- **Phase 9.2 — Deterministic partition construction**
  - Build the packet-defined buckets for ATR, price, tolerance, and LTF fib zone.
  - Do not build HTF state buckets in this phase; emit the HTF availability check result only.
  - Emit bucket ranges for numeric dimensions and category labels for categorical dimensions.

- **Phase 9.3 — Post-execution state isolation**
  - Compute bucket metrics by filtering the already executed baseline trades after execution only.
  - Do not alter the executed trade set, signal logic, thresholds, sizing, or entry conditions.

- **Phase 9.4 — State concentration significance**
  - Compute packet-defined `expectancy_spread` and permutation `p_value` for every analyzed state dimension.
  - Determine `edge_concentrated = YES/NO` for each dimension.

- **Phase 9.5 — Final interpretation**
  - Emit one final binary verdict with no ambiguity:
    - `edge is state-conditional`
    - `edge is not state-dependent`

### Output requirements

- **`state_edge_matrix.json`**
  - Must include:
    - `analysis_population`
    - `overall_baseline_metrics`
    - `omitted_dimensions`
    - `state_dimensions`
    - `final_verdict`
  - `state_dimensions` must be emitted in this exact order when present:
    - `ATR_Q4`
    - `PRICE_Q4`
    - `TOLERANCE_Q4`
    - `FIB_ZONE_LTF`
  - `omitted_dimensions` must be emitted in ascending `state_dimension` order.
  - `analysis_population` must include:
    - `baseline_trade_count`
    - `join_integrity`
    - `binary_trade_count`
    - `outcome_counts`
  - Every state-dimension record must include:
    - `state_dimension`
    - `state_field`
    - `partition_type`
    - `bucket_support_min`
    - `expectancy_spread`
    - `concentration_p_value`
    - `edge_concentrated`
    - `high_edge_bucket`
    - `low_edge_bucket`
    - `buckets`
  - Every bucket record must include:
    - `name`
    - `trade_count`
    - `profit_factor`
    - `profit_factor_status`
    - `expectancy`
    - `win_rate`
    - `bucket_lower_bound` and `bucket_upper_bound` for numeric dimensions, else `null`
    - `category_label` for categorical dimensions, else `null`

- **`state_edge_summary.md`**
  - Must include:
    - one short opening statement that Phase 9 is an observational state-isolation test only
    - one explicit statement that Phase 6–7 invalidation remains active and Phase 9 does not validate signals
    - overall baseline metrics
    - per-dimension concentration result
    - comparison between buckets
    - highlighted high-edge zones
    - highlighted low/no-edge zones
    - an explicit binary final statement using exactly one of:
      - `edge is state-conditional`
      - `edge is not state-dependent`

- **`audit_state_determinism.json`**
  - Must include:
    - `join_integrity`
    - `htf_availability_audit`
    - `non_self_outputs`
    - `run1_hashes`
    - `run2_hashes`
    - `run1_hash`
    - `run2_hash`
    - `match`
  - `run1_hash` and `run2_hash` must be the SHA256 hash of the canonical JSON manifest built from the sorted non-self output hashes for run 1 and run 2 respectively.
  - `match = true` only if `run1_hash == run2_hash` and every non-self output hash matches exactly.
  - `audit_state_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.
  - After the run-1/run-2 non-self hash comparison has passed, the final written `audit_state_determinism.json` may record a single informational `artifact_self_hash` for its own fully rendered bytes.

### Gates required

- STRICT baseline gates against locked HEAD must be executed and recorded using this exact command set; do not substitute alternative commands or selectors at run time:
  - `pre-commit run --all-files`
  - `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
  - `pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[default_legacy_replay] tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[regime_module_replay]`
  - `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

- Coverage assertions:
  - every baseline trade must join exactly once to a sizing-eligible baseline row
  - binary trade count must reconcile exactly to the baseline trade population filtered to `WIN`/`LOSS`
  - every analyzed bucket must account for every trade exactly once within its dimension
- State assertions:
  - all packet-defined state fields must exist on every joined baseline trade row
  - all packet-defined numeric state fields must be finite on every joined baseline trade row
  - HTF availability outcome must be emitted explicitly
- Join assertions:
  - `join_status` must equal `EXACT_ONE_MATCH_PER_TRADE`
  - `unmatched_trade_count == 0`
  - `duplicate_normalized_trace_timestamp_count == 0`
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 9 outputs must match exactly across both runs
- Audit assertions:
  - all three Phase 9 outputs must exist
  - all JSON artifacts must parse as valid JSON
  - per-dimension buckets, high-edge zones, low/no-edge zones, and the final binary verdict must all be present explicitly
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any baseline trade cannot be joined exactly once to an entry row
- any joined baseline trade has `FLAT` outcome
- any packet-defined state field is missing from any joined baseline trade row
- any packet-defined numeric state value is null, non-finite, or otherwise invalid
- any required analyzed bucket has `trade_count < 8`
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- the final outputs would omit per-bucket metrics, high-edge zones, low/no-edge zones, or the final binary verdict

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for deterministic selector posture and field-discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact integrity and non-self hash discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
