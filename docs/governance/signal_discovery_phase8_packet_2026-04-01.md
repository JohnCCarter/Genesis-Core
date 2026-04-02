# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 8 signal discovery in STRICT mode
- **Risk:** `MED` — why: trace-only observational discovery over locked artifacts and full trace feature surfaces; no runtime behavior changes allowed, but any claim that a new signal produces real edge must be deterministic, reproducible, statistically explicit, fail-closed, and scoped to the audited data populations only
- **Required Path:** `Full`
- **Objective:** Discover new signal candidates from the full available trace feature set by comparing `BASE_SIZE_POSITIVE` versus `BASE_SIZE_ZERO`, measuring trade-level predictive power on the audited unique trade population, and testing statistically significant simple and pairwise interaction rules without changing thresholds, sizing, architecture, or running Optuna
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 8 signal discovery
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\signal_discovery_phase8_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\signal_candidates.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\feature_edge_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\signal_rules.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\signal_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\audit_feature_universe.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\audit_trade_mapping.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\audit_significance.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase8_signal_discovery\audit_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - All files under `config/`
  - All files under `scripts/`
  - Any runtime/config authority changes
  - Any threshold/config/parameter changes
  - Any sizing changes
  - Any architecture changes
  - Any backtest reruns
  - Any Optuna runs
  - Any edits to existing Phase 3–7 artifacts outside this packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/governance/signal_discovery_phase8_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/signal_candidates.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/feature_edge_stats.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/signal_rules.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/signal_summary.md`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/audit_feature_universe.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/audit_trade_mapping.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/audit_significance.json`
  - `results/research/fa_v2_adaptation_off/phase8_signal_discovery/audit_determinism.json`
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
- No threshold tuning, sizing changes, redesign, or architecture changes
- No Optuna, optimizer, or parameter-search execution
- Signal discovery must be observational only
- Phase 8 is discovery-only and may not overturn, replace, or supersede the locked Phase 6–7 conclusion that the prior signal layer is invalid
- Deterministic ordering and stable JSON / markdown formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must not be presented as deployment authority, runtime authority, or generalized performance proof beyond the audited populations
- The full feature set means the full packet-defined common scalar feature universe extracted from the locked traces after packet-defined exclusions only; ad hoc feature invention is forbidden
- Statistical significance procedures must be packet-defined and deterministic; ad hoc test substitution is forbidden

### Canonical populations and join definitions

- **Trace-label mapping rule:** `trace_baseline_current.json` maps canonically to `baseline_current`, and `trace_adaptation_off.json` maps canonically to `adaptation_off`. If an embedded payload trace label exists and disagrees with this file-bound mapping, stop and FAIL.
- **Primary trace-row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Sizing-eligible row:** a trace row where `sizing_phase` is present and non-null.
- **BASE_SIZE_POSITIVE row:** a sizing-eligible row where `sizing_phase.base_size > 0`.
- **BASE_SIZE_ZERO row:** a sizing-eligible row where `sizing_phase.base_size == 0`.
- **Trade-key rule:** a trade is keyed canonically by `(entry_timestamp, exit_timestamp, side, size, pnl)` using the exact serialized values from `trade_signatures`.
- **Entry-row join rule:** each trade must join to exactly one sizing-eligible trace row by matching `trade_signatures.entry_timestamp` to `trace_rows.timestamp` after normalizing `trace_rows.timestamp` by removing the literal suffix `+00:00`. Any missing join or duplicate join is a hard failure.
- **Per-trace trade population:** all joined trades from one locked trace ledger.
- **Unique audited trade population:** the canonical deduplicated union of per-trace trade populations by packet-defined trade key, ordered ascending by `(entry_timestamp, exit_timestamp, side, size, pnl)`.
- **Binary audited trade population:** the unique audited trade population filtered to `WIN` and `LOSS` outcomes only.
- **Outcome class definitions:**
  - `WIN` if `pnl > 0`
  - `LOSS` if `pnl < 0`
  - `FLAT` if `pnl == 0`
- **Trade-side rule:** if `side` differs across duplicate trade keys, stop and FAIL.
- **Binary audited trade fail-closed rule:** if any joined trade in the unique audited trade population has outcome class `FLAT`, stop and FAIL.

### Full feature-set definitions

- **Scalar leaf extraction rule:** flatten every sizing-eligible trace row into dotted-path leaf fields from the top-level containers `config_surface`, `decision_phase`, `fib_phase`, `final`, `post_fib_phase`, `sizing_phase`, and `state_in` only.
- **Scalar leaf rule:** a field is a scalar leaf only if its observed value is a JSON scalar (`number`, `boolean`, or `string`) rather than an object, list, or null-only structure.
- **Common scalar feature universe:** the feature universe is the intersection of scalar leaf paths present on every sizing-eligible row in both locked traces after packet-defined exclusions. Every feature must be present and non-null on every analyzed row of the population where it is used.
- **Packet-defined excluded paths:**
  - identifiers: `bar_index`, `timestamp`
  - direct targets / labels: `sizing_phase.base_size`, `sizing_phase.final_size`, `final.size`, trade-ledger fields, outcome labels, rule-pass/fail labels derived from `pnl`
  - free-text detail dumps and list/object containers
  - any path ending in `.details`
  - any path ending in `.reasons`
- **Feature-type rule:**
  - `numeric_bool` if all observed values across the relevant analysis population are finite numbers or booleans only
  - `categorical` otherwise
  - booleans must be represented numerically as `0` / `1` in numeric calculations while preserving original labels in outputs
- **Trade-stable feature universe:** a feature may participate in trade-level predictive analysis only if, for every duplicate trade key across traces, the joined feature value matches exactly across traces. Any feature with duplicate-trade disagreement must be emitted as `TRACE_VARIANT` and excluded from trade-level predictive discovery.
- **Required joined field rule for trade-level discovery:** every trade-eligible feature used in predictive analysis must be present, non-null, and valid on every joined trade row in the binary audited trade population.
- **Deterministic ordering rule:** unless a stricter packet-local ordering is stated otherwise, all feature-name lists, category-label lists, and output arrays must be sorted in ascending lexicographic ordinal code-point order over canonical UTF-8 text.

### Statistical method definitions

- **Phase 8.1 row-diff metrics:**
  - for `numeric_bool` features: compute `mean_positive`, `mean_zero`, `absolute_mean_gap`, and standardized mean difference `smd = (mean_positive - mean_zero) / pooled_std`; if `pooled_std == 0`, emit `smd = 0`
  - for `categorical` features: compute category counts/proportions by class and `dominant_positive_label`, `dominant_zero_label`, plus `dominant_label_gap = positive_proportion(dominant_positive_label) - zero_proportion(dominant_positive_label)`
- **Trade-level correlation metric:**
  - for `numeric_bool` features: Spearman correlation between feature value and realized `pnl`
  - for `categorical` features: one-way correlation ratio `eta_squared = SSB / SST` over realized `pnl`, where `SSB = sum(n_g * (mean_g - mean_all)^2)` across feature groups and `SST = sum((pnl_i - mean_all)^2)`; if `SST == 0`, emit `0`
- **Trade-level correlation significance:**
  - for `numeric_bool` features: hold the feature vector fixed, shuffle the realized `pnl` vector only, recompute Spearman correlation, and compute two-sided permutation p-value using `abs(shuffled_corr) >= abs(actual_corr)`
  - for `categorical` features: hold the feature labels fixed, shuffle the realized `pnl` vector only, recompute `eta_squared`, and compute one-sided permutation p-value using `shuffled_eta_squared >= actual_eta_squared`
  - PRNG: Python stdlib `random.Random`
  - seed: `20260401`
  - iterations: `5000`
  - p-value formula: `(extreme_count + 1) / (iterations + 1)`
- **Trade-level separation metric:**
  - for `numeric_bool` features: best simple threshold rule from the packet-defined threshold universe evaluated by expectancy
  - for `categorical` features: best equality rule `feature == label` evaluated by expectancy
- **Numeric threshold universe:** for each `numeric_bool` feature, the threshold universe is the sorted set of distinct observed feature values on the binary audited trade population, evaluated in ascending order.
- **Numeric simple rule grammar:** only `feature > threshold` and `feature < threshold` are allowed for numeric features.
- **Categorical simple rule grammar:** only `feature == label` is allowed for categorical features.
- **Minimum support rule:** any simple rule or interaction rule must have `rule_support >= 8` and `complement_support >= 8`. Otherwise it is emitted as `INSUFFICIENT_SUPPORT` and may not qualify as a candidate signal.
- **Rule expectancy:** `expectancy = mean(pnl)` on rows satisfying the rule.
- **Rule win rate:** `wins / support`.
- **Rule profit factor:** let `gross_profit = sum(pnl_i for pnl_i in rule_rows if pnl_i > 0)` and `gross_loss = abs(sum(pnl_i for pnl_i in rule_rows if pnl_i < 0))`. If `gross_loss == 0`, emit `profit_factor = null` and `profit_factor_status = NO_LOSS_DENOMINATOR`; otherwise emit `profit_factor = gross_profit / gross_loss` and `profit_factor_status = FINITE`.
- **Simple-rule statistical significance:** hold the rule mask fixed on the binary audited trade population, shuffle the realized `pnl` vector only, and compute one-sided permutation p-value for rule expectancy using:
  - PRNG: Python stdlib `random.Random`
  - seed: `20260401`
  - iterations: `5000`
  - p-value formula: `(extreme_count + 1) / (iterations + 1)`, where `extreme_count` counts shuffled expectancies greater than or equal to the actual expectancy
  - baseline summary percentiles for passing-rule audit output must use nearest-rank on the ascending sorted permutation distribution with 1-indexed rank `ceil(p * iterations)` for percentile `p`, clamped to `[1, iterations]`
- **Simple-rule candidate-pass rule:** a simple rule qualifies as a `PASS` candidate only if all are true:
  - `rule_support >= 8`
  - `complement_support >= 8`
  - `expectancy > 0`
  - `profit_factor_status = FINITE` and `profit_factor > 1`
  - permutation `p_value <= 0.05`
- **Numeric monotonicity rule:** for each `numeric_bool` feature, sort the binary audited trade population by ascending `(feature_value, trade_key)` and split into exactly 5 equal-count contiguous buckets using `q = N // 5`, `r = N % 5`, with buckets `1..r` receiving `q + 1` rows and the rest `q` rows. `monotonicity = YES` only if bucket expectancies or bucket win rates are weakly monotone with at least one strict improvement in one direction. Otherwise `NO`.
- **Categorical monotonicity rule:** `NOT_APPLICABLE`.
- **Pairwise interaction universe:** pairwise interactions are evaluated only between two distinct simple rules drawn from the top `20` simple rules after sorting by `(p_value ascending, expectancy descending, support descending, rule_text ascending)`.
- **Pairwise interaction grammar:** `ALL(rule_a; rule_b)` where `rule_a` and `rule_b` come from distinct feature names.
- **Pairwise interaction pass rule:** an interaction rule qualifies as a `PASS` candidate only if all are true:
  - it satisfies the same minimum support, expectancy, profit factor, and permutation p-value requirements as a simple rule
  - its expectancy is strictly greater than the expectancy of each parent rule
  - its permutation `p_value <= 0.05`
- **Robustness split rule:** chronological robustness is assessed on the binary audited trade population sorted by ascending `entry_timestamp`; split into first half and second half, with the first half receiving `ceil(N / 2)` rows.
- **Rule robustness PASS rule:** a candidate rule has `robustness = PASS` only if:
  - rule support in each chronological half is at least `4`
  - expectancy in each chronological half is strictly positive
  - overall candidate pass rule is already satisfied
  - otherwise `robustness = FAIL`

### Phase task requirements

- **Phase 8.1 — Survivor vs Collapse Feature Diff**
  - Compare `BASE_SIZE_POSITIVE` versus `BASE_SIZE_ZERO` over the full common scalar feature universe.
  - Emit deterministic row-level difference metrics for every feature.
  - Identify row-diff leaders by absolute effect size only; do not promote row-diff alone as signal proof.

- **Phase 8.2 — Feature Predictive Power**
  - Build the trade-stable feature universe on the binary audited trade population.
  - For every trade-stable feature, emit:
    - correlation metric and p-value status
    - best simple rule and its metrics
    - monotonicity status where applicable
    - eligibility / failure reason where applicable

- **Phase 8.3 — Simple Rule Discovery**
  - Search the packet-defined simple-rule universe for every trade-stable feature.
  - Rank simple rules by `(p_value ascending, expectancy descending, support descending, rule_text ascending)`.
  - Retain all passing simple rules in deterministic order.

- **Phase 8.4 — Multi-feature Interaction**
  - Build the pairwise interaction universe from the top `20` simple rules only.
  - Evaluate packet-defined conjunction rules.
  - Retain all passing interaction rules in deterministic order.

### Output requirements

- **`feature_edge_stats.json`**
  - Must include one deterministic record for every feature in the full common scalar feature universe.
  - Required per-feature fields:
    - `feature_name`
    - `feature_type`
    - `row_diff_status`
    - `row_diff_metrics`
    - `trade_level_status`
    - `trade_stability_status`
    - `correlation_metric_name`
    - `correlation_metric_value`
    - `correlation_p_value`
    - `monotonicity`
    - `best_simple_rule`
    - `best_simple_rule_status`
    - `best_simple_rule_metrics`
  - `trade_level_status` may be only `ELIGIBLE`, `TRACE_VARIANT`, `MISSING_ON_TRADES`, or `INVALID`.

- **`signal_rules.json`**
  - Must include:
    - `simple_rules_all`
    - `simple_rules_passing`
    - `interaction_rules_all`
    - `interaction_rules_passing`
  - Every rule record must include:
    - `rule_text`
    - `rule_type` (`simple` or `interaction`)
    - `feature_names`
    - `support`
    - `complement_support`
    - `expectancy`
    - `win_rate`
    - `profit_factor`
    - `profit_factor_status`
    - `p_value`
    - `robustness`
    - `status`
    - `failure_reason`

- **`signal_candidates.json`**
  - Must include:
    - `candidate_signals_found`
    - `statistical_edge`
    - `robustness`
    - `verdict`
    - `top10_candidate_signals`
    - `passing_simple_rule_count`
    - `passing_interaction_rule_count`
  - `top10_candidate_signals` must contain at most the first `10` passing rules after sorting all passing simple and interaction rules by `(p_value ascending, robustness PASS before FAIL, expectancy descending, support descending, rule_text ascending)`.
  - `candidate_signals_found = YES` only if at least one passing simple or interaction rule exists.
  - `statistical_edge = YES` only if at least one passing rule exists.
  - `robustness = PASS` only if at least one passing rule also has `robustness = PASS`.
  - `verdict` may be only one of: `valid`, `invalid`, `unresolved`.
  - `verdict = valid` is forbidden in Phase 8 because this phase is discovery-only and not confirmatory.
  - `verdict = invalid` only if:
    - `candidate_signals_found = NO`
    - `statistical_edge = NO`
  - Otherwise `verdict = unresolved`.

- **`signal_summary.md`**
  - Must include:
    - top `10` candidate signals
    - statistical significance
    - PF per signal
    - robustness checks
    - failure cases
    - explicit statement that discovery is observational only over the audited populations
    - explicit statement that Phase 8 is discovery-only and cannot by itself mark the signal layer as valid
    - explicit statement that previously invalidated `p_buy` / `p_sell` / `probability_gap` layer remains a reference surface, not an approved recovered signal unless it independently passes the Phase 8 contract
    - the exact final output contract block below, copied verbatim:

      ```text
      SIGNAL STATUS:

      - Candidate signals found: YES/NO
      - Statistical edge: YES/NO
      - Robustness: PASS/FAIL

      Verdict:
      Signal layer is (valid / invalid / unresolved)
      ```

- **Audit artifacts (all mandatory):**
  - `audit_feature_universe.json`
  - `audit_trade_mapping.json`
  - `audit_significance.json`
  - `audit_determinism.json`
  - Missing any audit artifact is a hard failure.

### Audit artifact definitions

- **`audit_feature_universe.json`**
  - Must record:
    - common scalar feature universe
    - excluded paths and exclusion reasons
    - feature types
    - trade-stable vs trace-variant classification
    - counts of numeric_bool and categorical features

- **`audit_trade_mapping.json`**
  - Must prove:
    - per-trace trade counts
    - unique audited trade count
    - binary audited trade count
    - exact entry-row join success for every trade
    - duplicate-ledger consistency on required trade join fields
    - feature-level trade-stability counts

- **`audit_significance.json`**
  - Must record:
    - permutation seed
    - permutation iterations
    - actual correlation metrics for all eligible trade-stable features
    - actual p-values for every passing simple and interaction rule
    - baseline summary quantiles for passing rules

- **`audit_determinism.json`**
  - Must record the SHA256 hash of every Phase 8 output other than `audit_determinism.json` itself for run 1 and run 2.
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
  - every sizing-eligible row in both traces must be classified exactly once into `BASE_SIZE_POSITIVE` or `BASE_SIZE_ZERO`
  - every trade in every per-trace ledger must join exactly once to an entry row
  - unique audited trade count must reconcile to the canonical deduplicated union of per-trace trade populations
  - binary audited trade count must reconcile to the packet-defined WIN/LOSS-only filtered population
- Feature assertions:
  - the common scalar feature universe must be emitted explicitly
  - every trade-stable feature used in predictive analysis must be emitted explicitly
  - every trace-variant feature must be excluded explicitly rather than silently dropped
- Statistical assertions:
  - all rule p-values must use the packet-defined permutation procedure only
  - all numeric monotonicity checks must use the packet-defined 5-bucket split only
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 8 outputs must match exactly across both runs
- Audit assertions:
  - all four mandatory audit artifacts must exist
  - all audit artifacts must parse as valid JSON
  - top `10` candidate signals, statistical significance, PF per signal, robustness checks, and failure cases must all be present explicitly
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any sizing-eligible row is missing a packet-required feature path needed for the common scalar feature universe
- any trade cannot be joined exactly once to an entry row
- duplicate trade keys disagree on any required join field
- any binary audited trade has `FLAT` outcome
- any mandatory audit artifact is missing
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- the final outputs would omit top `10` candidate signals, statistical significance, PF per signal, robustness checks, or failure cases

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for exact-set discipline and deterministic selector posture, and `.github/skills/ri_off_parity_artifact_check.json` for artifact-field integrity plus deterministic reporting discipline.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
