# COMMAND PACKET

- **Category:** `obs`
- **Mode:** `STRICT` — source: explicit current user request to continue by locking a Phase 11 packet without leaving the active governance track
- **Risk:** `MED` — why: artifact-only stability classification can still overclaim robustness if temporal splits, bootstrap semantics, or sensitivity omissions are underdefined; no runtime behavior changes are allowed
- **Required Path:** `Full`
- **Objective:** Test whether the observed baseline edge survives packet-defined temporal and resampling perturbations using only locked artifacts and deterministic post-execution analysis, and classify the edge as `stable`, `fragile`, or `noise-driven` within the scope of the packet-authorized tests
- **Candidate:** `baseline_current` Phase 11 edge stability and generalization
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\GENESIS-CORE-POST PHASE-9-ROADMAP.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\execution_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\sizing_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\path_dependency.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\selection_attribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\counterfactual_matrix.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase10_edge_origin_isolation\audit_phase10_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\edge_stability_phase11_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\edge_stability.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\bootstrap_distribution.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\edge_stability_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\audit_phase11_determinism.json`
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
  - Any edits to existing Phase 1–10 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/edge_stability_phase11_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase11_edge_stability/edge_stability.json`
  - `results/research/fa_v2_adaptation_off/phase11_edge_stability/bootstrap_distribution.json`
  - `results/research/fa_v2_adaptation_off/phase11_edge_stability/edge_stability_summary.md`
  - `results/research/fa_v2_adaptation_off/phase11_edge_stability/audit_phase11_determinism.json`
- **Max files touched:** `5`

### Implementation surface

- Scope IN is limited to the named roadmap/context inputs, the locked baseline trace, the locked Phase 10 outputs, this packet, and the named Phase 11 output artifacts.
- All Scope IN inputs other than this packet during pre-approval hardening and the named Phase 11 outputs are read-only for the duration of the run.
- Output root is fixed at `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase11_edge_stability\` only; no alternate output directory is allowed.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `python -m pre_commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests.
- No strategy logic changes.
- No signal changes, feature engineering, threshold tuning, sizing changes, redesign, or architecture changes.
- Phase 11 must remain observational and must operate strictly by post-execution stability analysis over the already executed baseline trades.
- Phase 11 must not return to signal-space and must not claim prediction, feature validity, or signal validity.
- Phase 6–7 invalidation remains active, Phase 8 remains candidate-only, Phase 9 remains `edge is not state-dependent`, and Phase 10 remains artifact-only edge-origin attribution; Phase 11 may not overturn or soften those locked conclusions.
- Deterministic ordering and stable JSON / markdown formatting required.
- No silent missing-field handling; required-field absence is a hard failure.
- Final interpretation must not be presented as deployment authority, runtime authority, signal validation, or promotion authority.
- Any roadmap experiment that requires unavailable artifact fields must be omitted explicitly with a deterministic omission reason; it may not be approximated from unstated assumptions.
- Phase 11 final classification is scoped only to the packet-defined temporal, bootstrap, and sensitivity probes.

### Canonical population and join definitions

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
- **Binary trade population rule:** all Phase 11 metrics and perturbation tests must operate only on the `WIN`/`LOSS` trade population.
  - If any joined baseline trade has `FLAT` outcome, stop and FAIL.

### Phase 11 analysis surfaces

- **11.1 Temporal stability (authorized)**
  - Sort the binary trade population in canonical trade-key order.
  - Partition the sorted population into exactly three equal-count deterministic chronological trade-sequence slices `EARLY`, `MID`, `LATE`.
  - Equal-count rule: for `N` trades and `K = 3`, compute `q = N // K` and `r = N % K`; assign slices `EARLY..` in order with the first `r` slices receiving `q + 1` trades and the remaining slices receiving `q` trades.
  - Minimum support rule: every temporal slice must have `trade_count >= 20`; otherwise stop and FAIL.
  - Compute per-slice metrics:
    - `trade_count`
    - `profit_factor`
    - `profit_factor_status`
    - `expectancy`
    - `win_rate`
    - `entry_timestamp_min`
    - `entry_timestamp_max`
  - `EARLY`, `MID`, and `LATE` refer only to chronological trade-sequence terciles by canonical entry ordering; they must not be interpreted as calendar windows, regime windows, or state partitions.
  - **Temporal stability verdict:** `PASS` only if every slice has `expectancy > 0` and finite `profit_factor > 1`. Otherwise `FAIL`.

- **11.2 Bootstrap / resampling (authorized)**
  - Use the full binary baseline trade population only.
  - Bootstrap sample size must equal the binary trade count `N`.
  - Draw with replacement from the fixed observed pnl vector only; do not perturb fields other than row selection.
  - Every bootstrap iteration used in executed subtests must yield finite metrics under the packet-defined metric rules.
  - If any bootstrap iteration yields `gross_loss == 0` and therefore null `profit_factor`, stop and FAIL with `BOOTSTRAP_NULL_PROFIT_FACTOR`; no null-bootstrap-profit-factor handling is authorized in this packet.
  - PRNG: Python stdlib `random.Random`
  - seed: `20260401`
  - iterations: `5000`
  - Compute per-iteration metrics:
    - `expectancy`
    - `profit_factor`
    - `win_rate`
  - Emit deterministic summary statistics for the bootstrap distribution:
    - `expectancy_mean`
    - `expectancy_median`
    - `expectancy_p05`
    - `expectancy_p95`
    - `profit_factor_median`
    - `profit_factor_p05`
    - `profit_factor_p95`
    - `win_rate_median`
    - `probability_expectancy_positive`
    - `probability_profit_factor_gt_1`
  - Percentile rule: nearest-rank on the ascending sorted bootstrap metric vector, using `rank = ceil(p * n) - 1` clamped to `[0, n - 1]`.
  - **Bootstrap stability verdict:** `PASS` only if `probability_expectancy_positive >= 0.80` and `probability_profit_factor_gt_1 >= 0.80`.
  - **Bootstrap strong-fail flag:** `YES` only if `probability_expectancy_positive < 0.50` and `probability_profit_factor_gt_1 < 0.50`; otherwise `NO`.

- **11.3 Sensitivity analysis (authorized in limited form)**
  - Packet-authorized sensitivity probes are limited to artifact-surface availability checks only.
  - `price_noise_probe` is omitted in this packet because no predeclared price-path perturbation surface is authorized.
  - `latency_shift_probe` is omitted in this packet because no predeclared execution-latency perturbation surface is authorized.
  - Any other environment-perturbation probe is forbidden in this packet unless a new pre-reviewed packet authorizes the exact artifact field source and exact perturbation semantics.
  - **Sensitivity surface status:** `LIMITED_ARTIFACT_SURFACE`.

### Metric definitions

- **Profit factor definition:** let `gross_profit = sum(pnl_i for pnl_i in rows if pnl_i > 0)` and `gross_loss = abs(sum(pnl_i for pnl_i in rows if pnl_i < 0))`. If `gross_loss == 0`, emit `profit_factor = null` and `profit_factor_status = NO_LOSS_DENOMINATOR`; otherwise emit `profit_factor = gross_profit / gross_loss` and `profit_factor_status = FINITE`.
- **Expectancy:** `mean(pnl)` over the target row set.
- **Win rate:** `wins / trade_count` over the target row set.

### Phase 11 final classification

- **Classification universe:** the final label must be exactly one of:
  - `stable`
  - `fragile`
  - `noise-driven`
- **Stable rule:** emit `stable` only if `temporal_stability_verdict = PASS` and `bootstrap_stability_verdict = PASS`.
- **Noise-driven rule:** emit `noise-driven` only if `temporal_stability_verdict = FAIL` and `bootstrap_strong_fail = YES`.
- **Fragile rule:** otherwise emit `fragile`.
- **No unresolved rule:** `unresolved` is forbidden.
- **Verdict scope rule:** the final Phase 11 classification is scoped only to the packet-defined temporal slices, bootstrap distribution, and sensitivity-surface omissions; it must not be interpreted as signal validation, strategy validation, or runtime authority.

### Output requirements

- **`edge_stability.json`**
  - Must include:
    - `analysis_population`
    - `baseline_metrics`
    - `temporal_stability`
    - `bootstrap_stability`
    - `sensitivity_surface`
    - `phase11_classification`
  - `temporal_stability` must include:
    - `slice_rule`
    - `slice_support_min`
    - `slices`
    - `temporal_stability_verdict`
  - `bootstrap_stability` must include:
    - `iterations`
    - `sample_size`
    - `summary`
    - `bootstrap_stability_verdict`
    - `bootstrap_strong_fail`
  - `sensitivity_surface` must include:
    - `status`
    - `omitted_probes`
  - `phase11_classification` must include:
    - `label`
    - `reason`
  - `phase11_classification.reason` must state explicitly that the label is scoped only to the packet-authorized temporal and bootstrap probes, and that environmental sensitivity probes were omitted under limited artifact surface.

- **`bootstrap_distribution.json`**
  - Must include:
    - `iterations`
    - `sample_size`
    - `seed`
    - `expectancy_values`
    - `profit_factor_values`
    - `win_rate_values`
    - `summary`

- **`edge_stability_summary.md`**
  - Must include:
    - one short statement that Phase 11 is an observational stability analysis only
    - one explicit statement that Phase 6–7 invalidation remains active and Phase 11 does not validate signals
    - baseline metrics
    - temporal stability results
    - bootstrap summary results
    - omitted sensitivity probes
    - one explicit final label using exactly one of:
      - `stable`
      - `fragile`
      - `noise-driven`

- **`audit_phase11_determinism.json`**
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
  - `audit_phase11_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.

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
  - every temporal slice must account for every trade exactly once
  - every bootstrap sample must have size exactly `N`
- Field assertions:
  - all packet-defined required fields must exist on every relevant joined row
  - all numeric fields used in executed subtests must be finite
  - every executed bootstrap iteration must yield finite `profit_factor`
  - every omitted sensitivity probe must emit an explicit omission reason
  - no executed subtest may rely on a field or formula not predeclared in this packet
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 11 outputs must match exactly across both runs
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any baseline trade cannot be joined exactly once to an entry row
- any joined baseline trade has `FLAT` outcome
- any packet-defined required field for an executed subtest is missing from any relevant row
- any packet-defined numeric value used in an executed subtest is null, non-finite, or otherwise invalid
- any temporal slice falls below minimum support
- any bootstrap iteration yields null `profit_factor`
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- any output would omit required conclusions or omission reasons
- any analysis step attempts to infer unavailable artifact fields instead of omitting the probe explicitly

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for deterministic selector posture and field-discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact integrity and non-self hash discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
