# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 7 probability-edge validation in STRICT mode
- **Risk:** `MED` — why: trace-only observational validation over locked artifacts and trade ledgers; no runtime behavior changes allowed, but any claim that `p_buy` / `p_sell` contain predictive edge must be deterministic, reproducible, fail-closed, and explicitly scoped to the audited trade population
- **Required Path:** `Full`
- **Objective:** Determine whether `p_buy` / `p_sell` contain real predictive edge on the audited trade population by validating calibration, directional validity, gap-performance structure, and shuffled-probability baselines using locked artifacts only and without interpreting results as runtime authority
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 7 probability-edge validation
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\probability_edge_validation_phase7_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\probability_edge_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\calibration_curve.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\gap_performance.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\probability_edge_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\audit_trade_mapping.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\audit_field_presence.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\audit_significance.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase7_probability_edge_validation\audit_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - All files under `config/`
  - All files under `scripts/`
  - Any runtime/config authority changes
  - Any threshold/config/parameter changes
  - Any backtest reruns
  - Any architecture changes
  - Any edits to existing Phase 3–6 artifacts outside the packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/governance/probability_edge_validation_phase7_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/probability_edge_stats.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/calibration_curve.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/gap_performance.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/probability_edge_summary.md`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/audit_trade_mapping.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/audit_field_presence.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/audit_significance.json`
  - `results/research/fa_v2_adaptation_off/phase7_probability_edge_validation/audit_determinism.json`
- **Max files touched:** `9`

### Implementation surface

- Scope IN is limited to the three named read-only inputs, this packet, and the eight named output artifacts.
- This packet may be edited only during pre-execution hardening before Opus pre-review approval. After approval, the packet becomes execution-locked and read-only for the remainder of the run; any further packet edit requires stopping the run and restarting governance review from pre-review.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.
- If `pre-commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No threshold tuning, redesign, or architecture changes
- Probability-edge validation must be observational only
- Deterministic ordering and stable JSON formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must not be presented as edge proof, deployment authority, or generalized runtime-performance claim beyond the audited trade population
- The locked trade population must be auditable back to trace-local trade ledgers and entry-row joins
- Statistical significance procedures must be packet-defined and deterministic; ad hoc test substitution is forbidden

### Canonical analysis definitions

- **Trace-label mapping rule:** `trace_baseline_current.json` maps canonically to `baseline_current`, and `trace_adaptation_off.json` maps canonically to `adaptation_off`. If an embedded payload trace label exists and disagrees with this file-bound mapping, stop and FAIL.
- **Primary trace-row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Trade-key rule:** a trade is keyed canonically by `(entry_timestamp, exit_timestamp, side, size, pnl)` using the exact serialized values from `trade_signatures`.
- **Entry-row join rule:** each trade must join to exactly one sizing-eligible trace row by matching `trade_signatures.entry_timestamp` to `trace_rows.timestamp` after normalizing `trace_rows.timestamp` by removing the literal suffix `+00:00`. Any missing join or duplicate join is a hard failure.
- **Per-trace trade population:** all joined trades from one locked trace ledger.
- **Unique audited trade population:** the canonical deduplicated union of per-trace trade populations by packet-defined trade key, ordered ascending by `(entry_timestamp, exit_timestamp, side, size, pnl)`.
- **Duplicate-ledger rule:** if the same canonical trade key appears in more than one trace, the joined Phase 7 analysis fields for that trade must match exactly across traces on:
  - `decision_phase.p_buy`
  - `decision_phase.p_sell`
  - `decision_phase.max_ev`
  - `decision_phase.selected_candidate`
  - `post_fib_phase.edge_value`
  - `sizing_phase.base_size`
    Any mismatch is a hard failure.
- **Outcome class definitions:**
  - `WIN` if `pnl > 0`
  - `LOSS` if `pnl < 0`
  - `FLAT` if `pnl == 0`
- **Binary audited trade population rule:** all calibration, gap-bucket, directional-validity, and significance computations must operate on a binary-outcome audited trade population containing only `WIN` and `LOSS` observations.
  - If any joined trade in the unique audited trade population has outcome class `FLAT`, stop and FAIL. No silent dropping, re-labeling, or side-channel handling of `FLAT` trades is allowed.
- **Directional signal definitions:**
  - `LONG_SIGNAL` if `p_buy > p_sell`
  - `SHORT_SIGNAL` if `p_sell > p_buy`
  - `TIE_SIGNAL` if `p_buy == p_sell`
- **Executed-direction validity rule:** executed-direction support is assessed only on the binary audited trade population.
  - If any executed trade in the binary audited trade population resolves to `TIE_SIGNAL`, stop and FAIL.
  - Any direction with zero executed support in the binary audited trade population must be emitted explicitly with `status = UNOBSERVED` and may not contribute to a PASS decision.
- **Required joined fields:**
  - trade ledger: `entry_timestamp`, `exit_timestamp`, `side`, `size`, `pnl`
  - `decision_phase`: `p_buy`, `p_sell`, `max_ev`, `selected_candidate`, `regime`
  - `post_fib_phase`: `edge_value`
  - `sizing_phase`: `base_size`, `final_size`
- **Required observable validity rule:** every packet-locked or derived observable used for calibration, gap buckets, directional validation, significance testing, or summary claims must be present, finite where numeric, and non-null. Any missing value, `null`, `NaN`, positive infinity, or negative infinity is a hard failure.

### Statistical method definitions

- **Calibration-bin rule:** calibration uses exactly 10 fixed equal-width bins over `p_buy` on the interval `[0.0, 1.0]` on the binary audited trade population.
  - Empty bins must still be emitted explicitly with `trade_count = 0` and `status = EMPTY`.
- **Calibration metrics:**
  - per bin: `trade_count`, `mean_p_buy`, `win_rate`
  - overall: `brier_score`, `expected_calibration_error`
  - `expected_calibration_error` must be computed exactly as:
    - `ECE = sum((n_b / N) * abs(win_rate_b - mean_p_buy_b) for b in bins_1_to_10)`
    - where `N` is the binary audited trade count, `n_b` is the bin trade count, and empty bins contribute exactly `0`
- **Gap-bucket rule:** gap performance uses exactly 5 equal-count buckets over the binary audited trade population after sorting by ascending `(probability_gap, trade_key)`.
  - Let `N` be the binary audited trade count, `q = N // 5`, and `r = N % 5`.
  - The sorted population must be partitioned into 5 contiguous buckets in order, where buckets `1..r` contain `q + 1` trades each and buckets `(r+1)..5` contain `q` trades each.
  - No alternative remainder distribution, balancing rule, or interpolation is allowed.
- **Gap-bucket metrics:**
  - `trade_count`
  - `gap_min`
  - `gap_max`
  - `win_rate`
  - `expectancy`
  - `profit_factor`
  - `profit_factor_status`
  - If a bucket has `gross_loss = 0`, emit `profit_factor = null` and `profit_factor_status = NO_LOSS_DENOMINATOR`.
  - Otherwise emit numeric `profit_factor` and `profit_factor_status = FINITE`.
  - `profit_factor` is descriptive only and must not be used directly in PASS/FAIL or monotonicity logic.
- **Directional-validity rule:** directional validity is assessed on observed executed directions only.
  - Any unobserved direction must be emitted explicitly with `status = UNOBSERVED`.
  - In this audited slice, any short-side result without executed `SHORT_SIGNAL` support must be reported as `UNOBSERVED` rather than as evidence for or against `p_sell` predictive edge.
  - `Directional accuracy = PASS` only if every observed executed direction has empirical win rate strictly greater than `0.5` and one-sided exact binomial `p_value <= 0.05` against the null `p = 0.5`.
  - Otherwise `Directional accuracy = FAIL`.
- **Calibration-pass rule:** `Calibration = PASS` only if both of the following are true on the binary audited trade population:
  - actual `brier_score` is strictly better (lower) than the shuffled baseline at one-sided permutation `p_value <= 0.05`
  - actual `expected_calibration_error` is strictly better (lower) than the shuffled baseline at one-sided permutation `p_value <= 0.05`
  - Otherwise `Calibration = FAIL`.
- **Gap-monotonicity rule:** `Gap monotonicity = YES` only if gap buckets, ordered from lowest to highest `probability_gap`, have weakly non-decreasing `expectancy` and weakly non-decreasing `win_rate`, with at least one strict increase across the full ordered series for one of those two metrics. Otherwise `Gap monotonicity = NO`.
- **Statistical-edge rule:** `Statistical edge = YES` only if at least one of the following gap-performance tests is significant at one-sided permutation `p_value <= 0.05` on the binary audited trade population:
  - `spearman(probability_gap, pnl)` greater than shuffled baseline
  - `top_minus_bottom_expectancy_spread` greater than shuffled baseline
  - Otherwise `Statistical edge = NO`.
- **Permutation baseline rule:** shuffled-probability baseline must use the binary audited trade population only and the packet-locked deterministic procedure below:
  - PRNG: Python stdlib `random.Random`
  - seed: `20260401`
  - iterations: `5000`
  - Brier/ECE baseline: shuffle the vector of `p_buy` values across the fixed win/loss outcomes
  - gap-performance baseline: shuffle the vector of `probability_gap` values across the fixed realized outcomes
  - p-value formula: `(extreme_count + 1) / (iterations + 1)`
  - baseline summary percentiles must use nearest-rank on the ascending sorted permutation distribution with 1-indexed rank `ceil(p * iterations)` for percentile `p`, clamped to `[1, iterations]`

### Phase task requirements

- **Phase 7.1 — Outcome Mapping**
  - For each joined trade in each per-trace population and in the unique audited trade population, map:
    - `p_buy`
    - `probability_gap`
    - actual outcome (`WIN` / `LOSS` / `FLAT`)
  - Prove that the binary audited trade population is derived deterministically from the unique audited trade population.

- **Phase 7.2 — Calibration Test**
  - Build the 10 fixed `p_buy` calibration bins on the binary audited trade population.
  - Emit bin-level trade count, mean probability, realized win rate, and EMPTY status where applicable.
  - Compute overall Brier score and expected calibration error.
  - Compare both metrics to the packet-defined shuffled baseline.

- **Phase 7.3 — Edge vs Gap**
  - Build the 5 equal-count probability-gap buckets on the binary audited trade population.
  - Emit win rate, expectancy, profit factor, and profit-factor status for each bucket.
  - Evaluate packet-defined gap monotonicity on expectancy and win rate only.
  - Compare actual gap-performance metrics to the shuffled baseline.

- **Phase 7.4 — Directional Validity**
  - Evaluate whether executed `LONG_SIGNAL` trades win more often than `0.5`.
  - Evaluate executed `SHORT_SIGNAL` trades if any exist; otherwise emit `UNOBSERVED`.
  - Emit exact binomial p-values.

- **Phase 7.5 — Random Baseline**
  - Compare real signal assignment to the packet-defined shuffled-probability baselines.
  - Emit p-values and baseline summary quantiles for every significance metric used in the final verdict.

### Output requirements

- **`probability_edge_stats.json`**
  - Must include:
    - per-trace trade counts
    - unique audited trade count
    - binary audited trade count
    - outcome counts
    - observed directional-support counts
    - directional-validity results with exact binomial p-values
    - final contract fields:
      - `calibration`
      - `directional_accuracy`
      - `gap_monotonicity`
      - `statistical_edge`
      - `verdict`
  - `verdict` may be only one of: `real edge`, `no edge`, `uncertain edge`.
  - `verdict = real edge` only if:
    - `calibration = PASS`
    - `directional_accuracy = PASS`
    - `gap_monotonicity = YES`
    - `statistical_edge = YES`
  - `verdict = no edge` only if:
    - `calibration = FAIL`
    - `statistical_edge = NO`
  - Otherwise `verdict = uncertain edge`.

- **`calibration_curve.json`**
  - Must include exactly the 10 packet-defined bins in order.
  - For each bin include:
    - `bin_label`
    - `lower_bound`
    - `upper_bound`
    - `trade_count`
    - `mean_p_buy`
    - `win_rate`
    - `status`
  - Must also include overall:
    - `brier_score`
    - `expected_calibration_error`
    - shuffled-baseline mean, median, 5th percentile, 95th percentile, and p-values for both metrics

- **`gap_performance.json`**
  - Must include exactly the 5 packet-defined equal-count buckets in order.
  - For each bucket include:
    - `bucket_index`
    - `trade_count`
    - `gap_min`
    - `gap_max`
    - `win_rate`
    - `expectancy`
    - `profit_factor`
    - `profit_factor_status`
  - Must also include overall:
    - `spearman_gap_vs_pnl`
    - `top_minus_bottom_expectancy_spread`
    - shuffled-baseline mean, median, 5th percentile, 95th percentile, and p-values for both metrics
    - `gap_monotonicity`

- **`probability_edge_summary.md`**
  - Must include:
    - calibration curve summary
    - PF per gap bucket
    - win rate vs probability summary
    - statistical-significance summary
    - random-baseline comparison summary
    - explicit statement that the results are scoped to the audited unique trade population only
    - explicit statement that short-side (`p_sell`) predictive validity is `UNOBSERVED` on this audited slice if no executed short-support trades exist
    - explicit statement that identical trace ledgers were deduplicated for significance to avoid sample inflation
    - the exact final output contract block below, copied verbatim:

      ```text
      PROBABILITY EDGE STATUS:

      - Calibration: PASS/FAIL
      - Directional accuracy: PASS/FAIL
      - Gap monotonicity: YES/NO
      - Statistical edge: YES/NO

      Verdict:
      Model has (real / no / uncertain) edge.
      ```

- **Audit artifacts (all mandatory):**
  - `audit_trade_mapping.json`
  - `audit_field_presence.json`
  - `audit_significance.json`
  - `audit_determinism.json`
  - Missing any audit artifact is a hard failure.

### Audit artifact definitions

- **`audit_trade_mapping.json`**
  - Must prove:
    - trade counts per trace
    - unique audited trade count
    - binary audited trade count
    - exact entry-row join success for every trade
    - duplicate-ledger consistency across traces
    - canonical ordering of the unique audited trade population

- **`audit_field_presence.json`**
  - Must record required-field presence checks across all joined trades and all required joined trace fields.
  - Must record packet-locked and derived observable validity checks.
  - Any missing required field or invalid packet-locked observable must trigger FAIL.

- **`audit_significance.json`**
  - Must record:
    - permutation seed
    - permutation iterations
    - all actual metrics used for significance
    - all p-values used in the final contract
    - directional exact binomial p-values
    - baseline summary quantiles used in `calibration_curve.json` and `gap_performance.json`

- **`audit_determinism.json`**
  - Must record the SHA256 hash of every Phase 7 output other than `audit_determinism.json` itself for run 1 and run 2.
  - `audit_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.
  - After the run-1/run-2 non-self hash comparison has passed, the final written `audit_determinism.json` may record a single informational `artifact_self_hash` for its own fully rendered bytes.
  - Must record whether all non-self output hashes matched exactly.

### Gates required

- STRICT baseline gates against locked HEAD must be executed and recorded using this exact command set; do not substitute alternative commands or selectors at run time:
  - `pre-commit run --all-files`
  - `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
  - `pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[default_legacy_replay] tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[regime_module_replay]`
  - `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

- Coverage assertions:
  - every trade in every per-trace ledger must join exactly once to an entry row
  - per-trace trade counts must reconcile to the locked trade ledgers
  - unique audited trade count must reconcile to the canonical deduplicated union of per-trace trade populations
  - binary audited trade count must reconcile to the packet-defined WIN/LOSS-only filtered population
- Schema assertions:
  - both traces expose `trade_signatures` and `trace_rows`
  - all required fields exist on every joined trade row
  - `decision_phase.max_ev == post_fib_phase.edge_value` on every joined trade row
- Statistical assertions:
  - all significance metrics must be computed on the binary audited trade population only
  - permutation seed and iteration count must match the packet exactly
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 7 outputs must match exactly across both runs
- Audit assertions:
  - all four mandatory audit artifacts must exist
  - all audit artifacts must parse as valid JSON
  - calibration curve, PF per gap bucket, win rate vs probability, statistical significance, and random baseline comparison must all be present explicitly
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any trade cannot be joined exactly once to an entry row
- duplicate trade keys disagree on any packet-locked joined field across traces
- any required field is missing from any joined trade row
- any packet-locked or derived observable is null, non-finite, or otherwise invalid under the required observable validity rule
- any joined trade resolves to `FLAT` outcome in the unique audited trade population
- any executed trade resolves to `TIE_SIGNAL`
- `trade_signatures` or `trace_rows` is missing from either trace
- permutation configuration differs from the packet-defined seed or iteration count
- any mandatory audit artifact is missing
- deterministic re-run hashes do not match
- the final summary would omit calibration curve, PF per gap bucket, win rate vs probability, statistical significance, or random baseline comparison
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for exact-set parity and selector discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact-field integrity plus deterministic reporting discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
