# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 4 survival-boundary extraction in STRICT mode
- **Risk:** `MED` — why: trace-only observational extraction of a deterministic survival boundary over already governed artifacts; no runtime behavior changes allowed, but the boundary claim must be exhaustive, unambiguous, reproducible, and fail-closed
- **Required Path:** `Full`
- **Objective:** Identify the deterministic observational survival boundary that separates sizing-eligible rows with `final_size > 0` from rows with `final_size == 0`, using existing artifacts only and without interpreting the result as edge
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 4 survival boundary
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_signatures.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\compensation_map.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\collapse_taxonomy.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survival_boundary_candidates.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survival_boundary_selected.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\boundary_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survival_boundary_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\audit_trace_coverage.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\audit_field_presence.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\audit_classification.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\audit_determinism.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\audit_sample_rows.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\survival_boundary_phase4_packet_2026-04-01.md`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any backtest reruns
  - Any threshold/config/parameter changes
  - Any architecture changes
  - Any edits to the existing Phase 2–3.5 artifacts
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/survival_boundary_phase4_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/survival_boundary_candidates.json`
  - `results/research/fa_v2_adaptation_off/survival_boundary_selected.json`
  - `results/research/fa_v2_adaptation_off/boundary_feature_stats.json`
  - `results/research/fa_v2_adaptation_off/survival_boundary_summary.md`
  - `results/research/fa_v2_adaptation_off/audit_trace_coverage.json`
  - `results/research/fa_v2_adaptation_off/audit_field_presence.json`
  - `results/research/fa_v2_adaptation_off/audit_classification.json`
  - `results/research/fa_v2_adaptation_off/audit_determinism.json`
  - `results/research/fa_v2_adaptation_off/audit_sample_rows.json`
- **Max files touched:** `10`

### Implementation surface

- Scope IN is limited to the seven named read-only inputs, this packet, and the nine named output artifacts.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No new thresholds, tuning, redesign, or architecture changes
- Boundary extraction must be observational only
- Deterministic ordering and stable JSON formatting required
- No silent missing-field handling; required-field absence is a hard failure
- No ambiguous final rule is allowed in the selected-boundary artifact
- Final interpretation must not be presented as edge, alpha, causality proof, or performance proof

### Canonical analysis definitions

- **Allowed trace names:** exactly `baseline_current` and `adaptation_off`. Any other trace label is a hard failure.
- **Primary row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Primary key uniqueness rule:** `(trace_name, bar_index)` must be unique within the trace population. Any duplicate key is a hard failure.
- **Sizing-eligible row:** a trace row where `sizing_phase` is present and non-null.
- **Survival:** `sizing_phase.final_size > 0`
- **Collapse:** `sizing_phase.final_size == 0`
- **Boundary target:** a condition or minimal set of conditions, derived only from packet-locked data, that reproduces the exact observed survivor/collapse split over all sizing-eligible rows.
- **Consistency rule:** for every sizing-eligible row, `final.size` must exist and equal `sizing_phase.final_size`. Any mismatch is a hard failure.
- **Candidate agreement rule:** if both `decision_phase.selected_candidate` and `sizing_phase.candidate` are present, they must match exactly. Any mismatch is a hard failure.
- **Required fields for every sizing-eligible row:**
  - top-level: `bar_index`, `timestamp`, `decision_phase`, `post_fib_phase`, `sizing_phase`, `final`
  - `decision_phase`: `selected_candidate`, `regime`, `thresholds_used.entry_conf_threshold`, `p_buy`, `p_sell`, `max_ev`
  - `post_fib_phase`: `candidate`, `confidence_threshold`, `min_edge`, `edge_value`, `blocked_reason`
  - `sizing_phase`: `candidate`, `confidence_gate`, `base_size`, `size_scale`, `volatility_adjustment`, `regime_multiplier`, `htf_regime_multiplier`, `combined_multiplier`, `final_size`
  - `final`: `action`, `regime`, `htf_regime`, `size`, `confidence.overall`
- **Required observable validity rule:** every packet-locked observable on every sizing-eligible row must be present, finite where numeric, and non-null. Any missing value, `null`, `NaN`, positive infinity, or negative infinity is a hard failure before candidate generation, ranking, audit derivation, or artifact write.
- **Multiplier chain rule:** `combined_multiplier` must equal `volatility_adjustment * regime_multiplier * htf_regime_multiplier` within exact float equality as stored or a deterministic recomputation check recorded in audit output. Any mismatch must be surfaced explicitly in audit.
- **Multiplier chain fail-closed rule:** if any sizing-eligible row has a stored `combined_multiplier` that does not match the deterministic recomputation from its component multipliers, stop and FAIL. In that case `combined_multiplier` becomes ineligible for boundary extraction and the packet run must terminate rather than degrade gracefully.
- **Deterministic recomputation formula:** `combined_multiplier_recomputed = volatility_adjustment * regime_multiplier * htf_regime_multiplier` using the three stored packet-locked sizing-phase numeric values only, with no rounding, no clamping, no normalization, and no substitution of defaults before equality comparison.
- **Minimality rule:** a selected boundary rule must not include redundant conditions if a strictly smaller rule reproduces the same exact survivor/collapse split on the full sizing-eligible population.
- **Authority rule:** Phase 4 outputs are derived artifacts only. They do not become runtime authority, threshold authority, or strategy authority.

### Phase task requirements

- **Phase 4.1 — Base Size Origin Analysis**
  - Analyze `base_size`, `edge_value`, and `confidence_gate` distributions across all sizing-eligible rows.
  - Partition the analysis by `SURVIVAL` and `COLLAPSE`, per trace and combined.
  - Explicitly test whether `base_size` alone already reproduces the survivor/collapse split.

- **Phase 4.2 — Multiplier Chain Decomposition**
  - Analyze `volatility_adjustment`, `regime_multiplier`, `htf_regime_multiplier`, and `combined_multiplier` across all sizing-eligible rows.
  - Identify observed suppressive combinations and any zero-producing or non-zero-preserving patterns.
  - No assumed cutoffs are allowed; only observed separations may be reported.

- **Phase 4.3 — Threshold Surface Detection**
  - Detect observed separations in:
    - `edge_value`
    - `confidence_gate`
    - `entry_conf_threshold`
    - multiplier-chain values
  - Any reported boundary surface must come from data separation only, not from inferred or imposed thresholds.

- **Phase 4.4 — Minimal Boundary Extraction**
  - Generate deterministic candidate rules from observed fields.
  - Evaluate candidate rules on the full sizing-eligible population.
  - Select the minimal rule that achieves exact survivor-set reproduction if such a rule exists.
  - If no exact minimal rule exists, fail selected-boundary validation.

- **Phase 4.5 — Deterministic Boundary Validation**
  - Apply the selected boundary to all sizing-eligible rows.
  - Verify exact equality between predicted and observed class labels.
  - Exact survivor-set reproduction is mandatory for a PASS.

### Candidate rule space

- Candidate rules may only use these packet-locked observable fields:
  - `base_size`
  - `edge_value`
  - `confidence_gate`
  - `entry_conf_threshold`
  - `volatility_adjustment`
  - `regime_multiplier`
  - `htf_regime_multiplier`
  - `combined_multiplier`
  - `decision_phase.regime`
  - `final.regime`
  - `final.htf_regime`
- `phase2_bucket` and `phase26_family` are annotation-only fields for audit and explanation. They are forbidden in the final selected boundary rule and forbidden as primary selectors in exact-boundary validation.
- Candidate rules must be emitted in a canonical textual grammar only.
- **Canonical rule grammar:**
  - atomic clause form: `<field> <operator> <value>`
  - allowed operators: `==`, `>`, `>=`, `<`, `<=`
  - allowed composition form: `ALL(<clause_1>; <clause_2>; ...; <clause_n>)`
  - no `OR`, no negation, no implicit grouping, no free-text commentary inside rule strings
  - field references must use exactly the packet-defined field names from the allowed observable list above
  - literal values must be rendered exactly as deterministic JSON scalars
- **Canonical clause ordering rule:** clauses inside `ALL(...)` must be sorted by ascending `(field, operator, canonical value text)`.
- **Canonical numeric literal rule:** every numeric literal used in rule strings and related ordering comparisons must be rendered in canonical decimal JSON form only:
  - finite values only
  - no exponent notation
  - normalize `-0` to `0`
  - trim trailing zeros after the decimal point
  - omit the decimal point entirely when the value is an integer
- **Canonical numeric normalization rule:** numeric compare inputs, canonical rule text, candidate ordering, and output serialization must all reuse the same single normalization procedure; locale, platform float formatting, or iteration order must not affect emitted text or sort order.
- **Canonical lexicographic order rule:** every packet-defined lexicographic comparison must use ordinal code-point order over the canonical ASCII text produced by the packet-defined normalization rules, independent of locale or platform collation.
- **Observed separating value rule:**
  - for numeric fields, the candidate literal universe is the sorted set of distinct observed values present across the full sizing-eligible population
  - for categorical fields, the candidate literal universe is the sorted set of distinct observed labels present across the full sizing-eligible population
- **Operator rule by field type:**
  - numeric fields may use `==`, `>`, `>=`, `<`, `<=`
  - categorical fields may use `==` only
- **Exhaustive search contract:**
  - build the full atomic clause universe from the allowed fields, allowed operators, and observed separating values
  - enumerate conjunction sizes in ascending order starting from `1`
  - within each conjunction size, enumerate candidate rules in lexicographic order of their canonically ordered clause lists
  - evaluate every candidate rule at the current conjunction size before considering the next larger conjunction size
  - stop the search at the first conjunction size that yields one or more exact rules
  - if all conjunction sizes up to the full atomic clause universe have been exhausted with no exact rule, stop and FAIL with `NO_EXACT_RULE`
- **Distinct-clause rule:** a candidate conjunction is formed from distinct atomic clauses drawn without repetition from the atomic clause universe; duplicate clauses inside the same `ALL(...)` rule are forbidden.
- **Driver-class rule:** every candidate rule must be assigned exactly one driver class from this closed set:
  - `base_size`: every clause uses `base_size` only
  - `multiplier`: every clause uses only `volatility_adjustment`, `regime_multiplier`, `htf_regime_multiplier`, or `combined_multiplier`
  - `upstream_threshold_proxy`: every clause uses only `edge_value`, `confidence_gate`, or `entry_conf_threshold`
  - `interaction`: every other allowed multi-field combination
- **Exact-rule alias-collapse rule:** after identifying all exact rules at the first conjunction size that yields exact reproduction, collapse exact rules in two deterministic stages before applying uniqueness:
  - first collapse numeric threshold aliases on the same field when they induce the exact same predicted survivor key set; keep only the earliest rule in packet-defined exhaustive search order as the field-local representative
  - then apply driver-class precedence and retain only exact rules from the highest-precedence driver class present in this order: `base_size`, `multiplier`, `interaction`, `upstream_threshold_proxy`
- **Upstream-proxy-only fail rule:** if the alias-collapsed exact-rule set at the first exact conjunction size contains only the `upstream_threshold_proxy` driver class and contains no exact rule in `base_size`, `multiplier`, or `interaction`, stop and FAIL before artifact write.
- **Exact-rule uniqueness rule after collapse:** after the packet-defined alias collapse and driver-class precedence filters have been applied, if more than one exact rule remains at the first exact conjunction size, stop and FAIL; do not choose one by discretion.
- Candidate rules must be generated deterministically in a fixed order.
- **Minimal exact-rule uniqueness rule:** the surviving exact rule after the packet-defined alias collapse, driver-class precedence, and uniqueness checks is the only admissible final selected boundary rule.
- **Minimality rank rule:** `minimality_rank` is the 1-based ordinal position of a candidate inside the packet-defined exhaustive search order.
- If a candidate requires a threshold not already present as an observed separating value in the data, that candidate is forbidden.

### Output requirements

- **`survival_boundary_candidates.json`**
  - Must contain deterministic candidate rules in fixed order.
  - Each candidate record must include:
    - `rule`
    - `coverage`
    - `accuracy`
    - `false_positives`
    - `false_negatives`
    - `predicted_survivors`
    - `predicted_collapses`
    - `minimality_rank`
  - `coverage` is survivor recall: `(true_positives / actual_survivors) * 100`.
  - `accuracy` is overall classification accuracy over the full sizing-eligible population: `((true_positives + true_negatives) / total_sizing_eligible) * 100`.
  - **Numeric serialization rule:** `coverage` and `accuracy` must be JSON numbers on the 0-100 scale, rounded to at most 6 decimal places using round-half-up, with trailing zeros removed and integral values serialized without a decimal suffix.

- **`survival_boundary_selected.json`**
  - Must contain exactly one final selected rule.
  - Fields required:
    - `final_rule`
    - `coverage`
    - `accuracy`
    - `validated`
    - `predicted_survivors`
    - `predicted_collapses`
    - `actual_survivors`
    - `actual_collapses`
    - `dominant_driver`
  - `validated` may be `true` only if the final rule reproduces the exact observed survivor/collapse split on the full sizing-eligible population.
  - `coverage` and `accuracy` must use the same packet-defined meaning and serialization rule as in `survival_boundary_candidates.json`.
  - `dominant_driver` must equal the packet-defined driver class of the final selected rule, except that `upstream_threshold_proxy` is forbidden as a final output value and must be reduced by the driver-class precedence rule before selection.

- **`boundary_feature_stats.json`**
  - Must contain deterministic distributions for:
    - `base_size`
    - `edge_value`
    - `confidence_gate`
    - `entry_conf_threshold`
    - `volatility_adjustment`
    - `regime_multiplier`
    - `htf_regime_multiplier`
    - `combined_multiplier`
  - Stats must be provided per trace and combined, partitioned by `SURVIVAL` and `COLLAPSE`.
  - For numeric fields: count, min, max, mean, and ordered distinct-value counts.
  - For categorical fields used in selected/candidate rules: ordered counts and proportions.

- **`survival_boundary_summary.md`**
  - Must include:
    - the final selected rule
    - a short explanation of why the exact dominant collapse-family share from the packet-generated JSON artifacts is so high
    - a short explanation of why `313` rows survive per trace
    - the required explicit statement: `This is an observational boundary, not proof of edge.`
    - the exact final output contract block below, copied verbatim:

      ```text
      SURVIVAL BOUNDARY STATUS:

      - Boundary identified: YES
      - Coverage: 100%
      - Accuracy: 100%
      - Dominant driver: <base_size | multiplier | interaction>
      - Validation: PASS

      Verdict:
      System survival is governed by deterministic sizing boundary.
      ```

  - All claims must reconcile exactly to the packet-generated JSON artifacts.

- **Audit artifacts (all mandatory):**
  - `audit_trace_coverage.json`
  - `audit_field_presence.json`
  - `audit_classification.json`
  - `audit_determinism.json`
  - `audit_sample_rows.json`
  - Missing any audit artifact is a hard failure.

### Audit artifact definitions

- **`audit_trace_coverage.json`**
  - Must prove:
    - total rows per trace
    - sizing-eligible rows per trace
    - sizing-ineligible rows per trace
    - combined totals
    - all rows accounted for exactly once

- **`audit_field_presence.json`**
  - Must record required-field presence checks across all sizing-eligible rows.
  - Any missing required field must be recorded and must trigger FAIL.

- **`audit_classification.json`**
  - Must record observed vs predicted counts and exact-match status for the selected boundary.
  - Must include confusion counts and exact survivor-set parity status.

- **`audit_determinism.json`**
  - Must record the SHA256 hash of every Phase 4 output other than `audit_determinism.json` itself for run 1 and run 2.
  - `audit_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.
  - After the run-1/run-2 non-self hash comparison has passed, the final written `audit_determinism.json` may record a single informational `artifact_self_hash` for its own fully rendered bytes.
  - Must record whether all non-self output hashes matched exactly.

- **`audit_sample_rows.json`**
  - Must contain a deterministic sample of rows illustrating:
    - survivors
    - collapses
    - rows nearest the separating boundary, if such a notion exists observationally
  - Sample ordering must be deterministic and packet-defined by ascending `(trace_name, bar_index)`.
  - **Sample-size rule:** the artifact must contain exactly:
    - the first `5` survivor rows by ascending `(trace_name, bar_index)`
    - the first `5` collapse rows by ascending `(trace_name, bar_index)`
    - the first `5` nearest-boundary rows by ascending `(trace_name, bar_index)` among rows with the smallest non-negative margin to the first numeric clause in the selected rule
  - **Sample tie-break rule:**
    - survivor and collapse samples use ascending `(trace_name, bar_index)` with `trace_name` ordered as `baseline_current`, `adaptation_off`
    - nearest-boundary rows use ascending `(margin, trace_name, bar_index)` with the same fixed trace-name order
  - **Nearest-boundary population rule:** if the selected rule contains one or more numeric clauses, nearest-boundary ranking must be computed only over rows that satisfy every non-numeric clause in the selected rule and every numeric clause in the selected rule except the first numeric clause in canonical clause order.
  - **First numeric clause rule:** the first numeric clause is the first numeric clause after applying the packet-defined canonical clause ordering inside the selected `ALL(...)` rule.
  - **Boundary-margin rule:** for the first numeric clause `<field> <operator> <value>`, let `x` be the row's observed value for `<field>` and `c` be the clause literal. The non-negative margin is defined as:
    - `==`: `abs(x - c)`
    - `>`: `max(0, c - x)`
    - `>=`: `max(0, c - x)`
    - `<`: `max(0, x - c)`
    - `<=`: `max(0, x - c)`
      Rows with negative, undefined, non-finite, or non-packet-computable margin are forbidden and must trigger FAIL before artifact write.
  - **Boundary-margin fallback rule:** if the selected rule contains no numeric clause, `nearest_boundary_rows` must be an empty list and the artifact must record `boundary_margin_reason = "NO_NUMERIC_CLAUSE"`.

### Gates required

- STRICT baseline gates against locked HEAD must be executed and recorded using this exact command set; do not substitute alternative commands or selectors at run time:
  - `pre-commit run --all-files`
  - `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
  - `pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[default_legacy_replay] tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode[regime_module_replay]`
  - `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

- Coverage assertions:
  - all trace rows accounted for exactly once
  - all sizing-eligible rows accounted for exactly once
  - Phase 4 survivor/collapse denominators must reconcile exactly to `survivor_partition.json`
- Schema assertions:
  - both traces expose `trace_rows`
  - all required fields exist on every sizing-eligible row
  - `final.size == sizing_phase.final_size` on every sizing-eligible row
  - candidate mismatch is forbidden when both candidate fields are present
- Boundary assertions:
  - the selected rule must reproduce the exact observed survivor set
  - `predicted_survivors == actual_survivors`
  - `predicted_collapses == actual_collapses`
  - `false_positives == 0`
  - `false_negatives == 0`
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 4 outputs must match exactly across both runs
- Audit assertions:
  - all five mandatory audit artifacts must exist
  - all audit artifacts must parse as valid JSON
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any required field is missing from any sizing-eligible row
- any packet-locked observable on a sizing-eligible row is `null`, non-finite, or otherwise invalid under the required observable validity rule
- `(trace_name, bar_index)` is duplicated in the trace population
- `final.size` and `sizing_phase.final_size` disagree on any sizing-eligible row
- stored `combined_multiplier` disagrees with the deterministic recomputation from its component multipliers on any sizing-eligible row
- the selected boundary does not reproduce the exact observed survivor set
- no exact rule exists after exhausting the full packet-defined candidate universe
- any mandatory audit artifact is missing
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN
- the selected rule remains ambiguous or non-minimal under packet-defined evidence

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- These anchors support evidence discipline and artifact integrity only; they do not replace STRICT verification gates.
