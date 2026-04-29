# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 5 base-size-origin extraction in STRICT mode
- **Risk:** `MED` — why: trace-only observational extraction over locked artifacts; no runtime behavior changes allowed, but the upstream rule claim for `base_size > 0` must be deterministic, reproducible, fail-closed, and exact on the survivor-equivalent cohort
- **Required Path:** `Full`
- **Objective:** Identify the deterministic observational boundary that separates sizing-eligible rows with `base_size > 0` from rows with `base_size == 0`, using existing artifacts only and without interpreting the result as edge
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 5 base-size-origin boundary
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_signatures.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\base_size_origin_phase5_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\base_size_boundary.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\base_size_boundary_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\base_size_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\audit_trace_coverage.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\audit_field_presence.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\audit_classification.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\audit_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any backtest reruns
  - Any threshold/config/parameter changes
  - Any architecture changes
  - Any edits to existing Phase 3 or Phase 4 artifacts outside the packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/base_size_origin_phase5_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/base_size_boundary.json`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/base_size_boundary_summary.md`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/base_size_feature_stats.json`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/audit_trace_coverage.json`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/audit_field_presence.json`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/audit_classification.json`
  - `results/research/fa_v2_adaptation_off/phase5_base_size_origin/audit_determinism.json`
- **Max files touched:** `8`

### Implementation surface

- Scope IN is limited to the five named read-only inputs, this packet, and the seven named output artifacts.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No new thresholds, tuning, redesign, or architecture changes
- Base-size-origin extraction must be observational only
- Deterministic ordering and stable JSON formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must not be presented as edge, alpha, causality proof, or performance proof
- Final interpretation must not present the selected rule as an exclusive causal origin when one or more alias-collapsed exact alternative rules remain inside the packet-locked candidate universe
- Final selected rule must be packet-derivable from upstream observables only; `base_size` itself is forbidden in the candidate rule space

### Canonical analysis definitions

- **Allowed trace names:** exactly `baseline_current` and `adaptation_off`. Any other trace label is a hard failure.
- **Primary row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Primary key uniqueness rule:** `(trace_name, bar_index)` must be unique within the trace population. Any duplicate key is a hard failure.
- **Sizing-eligible row:** a trace row where `sizing_phase` is present and non-null.
- **BASE_SIZE_POSITIVE row:** a sizing-eligible row whose `sizing_phase.base_size > 0`.
- **BASE_SIZE_ZERO row:** a sizing-eligible row whose `sizing_phase.base_size == 0`.
- **Base-size/survivor parity rule:** `BASE_SIZE_POSITIVE` must equal the Phase 4 survivor set exactly, meaning `sizing_phase.base_size > 0` if and only if `sizing_phase.final_size > 0`. Any mismatch is a hard failure.
- **Consistency rule:** for every sizing-eligible row, `final.size` must exist and equal `sizing_phase.final_size`. Any mismatch is a hard failure.
- **Candidate agreement rule:** if both `decision_phase.selected_candidate` and `sizing_phase.candidate` are present, they must match exactly. Any mismatch is a hard failure.
- **Required fields for every sizing-eligible row:**
  - top-level: `bar_index`, `timestamp`, `decision_phase`, `post_fib_phase`, `sizing_phase`, `final`
  - `decision_phase`: `selected_candidate`, `regime`, `thresholds_used.entry_conf_threshold`, `p_buy`, `p_sell`, `max_ev`
  - `post_fib_phase`: `candidate`, `confidence_threshold`, `min_edge`, `edge_value`, `blocked_reason`
  - `sizing_phase`: `candidate`, `confidence_gate`, `base_size`, `final_size`
  - `final`: `regime`, `size`
- **Metadata-only nullable-field rule:** `post_fib_phase.blocked_reason` is a required presence-only metadata field. It may be `null`, is excluded from packet-locked observable validity checks, is excluded from candidate generation, and may be reported for audit context only.
- **Required observable validity rule:** every packet-locked observable used for candidate generation, feature separation, boundary assertions, or deterministic ranking on every sizing-eligible row must be present, finite where numeric, and non-null. Any missing value, `null`, `NaN`, positive infinity, or negative infinity is a hard failure before candidate generation, ranking, audit derivation, or artifact write.
- **Observed classes for Phase 5 feature separation:**
  - `BASE_SIZE_POSITIVE`
  - `BASE_SIZE_ZERO`
  - `SURVIVOR_EQUIVALENT = BASE_SIZE_POSITIVE`
  - `ALL_OTHERS = BASE_SIZE_ZERO`

### Phase task requirements

- **Phase 5.1 — Base Size Generation Path**
  - Trace upstream behavior for:
    - `decision_phase.selected_candidate`
    - `post_fib_phase.edge_value`
    - `sizing_phase.confidence_gate`
    - `post_fib_phase.min_edge`
    - `decision_phase.thresholds_used.entry_conf_threshold`
  - Determine which exact packet-observable condition set produces `base_size > 0` versus `base_size == 0`.

- **Phase 5.2 — Feature Separation**
  - Compare `BASE_SIZE_POSITIVE` versus `BASE_SIZE_ZERO` per trace and combined.
  - The required comparison surface is:
    - `decision_phase.selected_candidate`
    - `decision_phase.regime`
    - `post_fib_phase.edge_value`
    - `post_fib_phase.min_edge`
    - `sizing_phase.confidence_gate`
    - `decision_phase.thresholds_used.entry_conf_threshold`

- **Phase 5.3 — Minimal Rule Extraction**
  - Generate deterministic candidate rules from packet-locked upstream fields only.
  - Find the smallest conjunction size that yields one or more exact rules for `BASE_SIZE_POSITIVE`.
  - The final selected rule must reproduce exactly `313` positive rows per trace and `626` combined positives with no false positives and no false negatives.

- **Phase 5.4 — Deterministic Validation**
  - Apply the final selected rule to all sizing-eligible rows.
  - Verify exact equality between predicted and observed `BASE_SIZE_POSITIVE` / `BASE_SIZE_ZERO` class labels.
  - Run the full artifact-generation procedure twice from the same locked inputs.
  - Double-run output hashes must match exactly for all non-self outputs.

### Candidate rule space

- Candidate rules may only use these packet-locked upstream observables:
  - `decision_phase.selected_candidate`
  - `decision_phase.regime`
  - `post_fib_phase.edge_value`
  - `post_fib_phase.min_edge`
  - `sizing_phase.confidence_gate`
  - `decision_phase.thresholds_used.entry_conf_threshold`
- `base_size`, `final_size`, and any downstream multiplier or final-regime field are forbidden in the candidate rule space.
- Candidate rules must be emitted in canonical textual grammar only.
- **Canonical rule grammar:**
  - literal clause form: `<field> <operator> <value>`
  - relation clause form: `<field_left> <operator> <field_right>`
  - allowed operators: `==`, `>`, `>=`, `<`, `<=`
  - allowed composition form: `ALL(<clause_1>; <clause_2>; ...; <clause_n>)`
  - no `OR`, no negation, no implicit grouping, no free-text commentary inside rule strings
- **Allowed literal-clause universe:**
  - numeric upstream fields may use `==`, `>`, `>=`, `<`, `<=` against observed values present in the full sizing-eligible population
  - categorical upstream fields may use `==` only against observed labels present in the full sizing-eligible population
- **Allowed relation-clause universe:**
  - `post_fib_phase.edge_value <op> post_fib_phase.min_edge`
  - `sizing_phase.confidence_gate <op> decision_phase.thresholds_used.entry_conf_threshold`
  - where `<op>` may be `==`, `>`, `>=`, `<`, `<=`
- **Canonical numeric literal rule:** every numeric literal used in rule strings and ordering comparisons must be rendered in canonical decimal JSON form only:
  - finite values only
  - no exponent notation
  - normalize `-0` to `0`
  - trim trailing zeros after the decimal point
  - omit the decimal point entirely when the value is an integer
- **Canonical clause ordering rule:** clauses inside `ALL(...)` must be sorted by ascending canonical clause text using ordinal code-point order over canonical ASCII text only.
- **Exhaustive search contract:**
  - build the full clause universe from the allowed literal clauses and allowed relation clauses
  - enumerate conjunction sizes in ascending order starting from `1`
  - within each conjunction size, enumerate candidate rules in lexicographic order of their canonically ordered clause lists
  - evaluate every candidate rule at the current conjunction size before considering the next larger conjunction size
  - stop the search at the first conjunction size that yields one or more exact rules
  - if all conjunction sizes up to the full clause universe have been exhausted with no exact rule, stop and FAIL with `NO_EXACT_RULE`
- **Distinct-clause rule:** a candidate conjunction is formed from distinct clauses drawn without repetition from the clause universe; duplicate clauses inside the same `ALL(...)` rule are forbidden.
- **Exact-rule alias-collapse rule:** after identifying all exact rules at the first conjunction size that yields exact reproduction, collapse exact rules in one deterministic stage before ranking alternatives:
  - collapse numeric threshold aliases on the same literal field when they induce the exact same predicted positive key set; keep only the earliest rule in packet-defined exhaustive search order as the field-local representative
  - do not collapse across different fields or across literal-versus-relation clause types
- **Final-rule selection rule:** after alias collapse, select the earliest exact rule in packet-defined exhaustive search order as `final_rule`.
- **Alternative-rule ranking rule:** after alias collapse and final-rule selection, rank all remaining exact rules by packet-defined exhaustive search order and retain at most the first `5` as `alternative_rules_top5`.
- **Minimality rank rule:** `minimality_rank` is the 1-based ordinal position of a candidate inside the packet-defined exhaustive search order.
- **Closest-boundary-row rule:** the final selected rule must contain at least one numeric literal clause or one relation clause; otherwise stop and FAIL because the required `10` closest boundary rows would be undefined.

### Output requirements

- **`base_size_boundary.json`**
  - Must contain exactly one final selected rule.
  - Required fields:
    - `final_rule`
    - `coverage`
    - `accuracy`
    - `validated`
    - `predicted_positive_rows`
    - `predicted_zero_rows`
    - `actual_positive_rows`
    - `actual_zero_rows`
    - `first_exact_conjunction_size`
    - `selected_minimality_rank`
    - `confusion_matrix`
    - `alternative_rules_top5`
    - `closest_boundary_rows_top10`
  - `coverage` is positive-class recall: `(true_positives / actual_positive_rows) * 100`.
  - `accuracy` is overall classification accuracy over the full sizing-eligible population: `((true_positives + true_negatives) / total_sizing_eligible) * 100`.
  - `coverage` and `accuracy` must be JSON numbers on the 0-100 scale, rounded to at most 6 decimal places using round-half-up, with trailing zeros removed and integral values serialized without a decimal suffix.
  - `alternative_rules_top5` must exclude the final selected rule.
  - `closest_boundary_rows_top10` must contain exactly `10` rows in deterministic order.

- **`base_size_feature_stats.json`**
  - Must contain deterministic per-trace and combined statistics comparing `BASE_SIZE_POSITIVE` versus `BASE_SIZE_ZERO` over the required Phase 5 comparison surface.
  - For numeric fields: count, min, max, mean, ordered distinct-value counts.
  - For categorical fields: ordered counts and proportions.
  - Top-level trace sections must appear in the fixed order `baseline_current`, `adaptation_off`, `combined`.

- **`base_size_boundary_summary.md`**
  - Must include:
    - the final selected rule
    - the confusion matrix
    - the selected minimality rank
    - the top `5` alternative rules if any exist
    - the explicit caveat that the final selected rule is the earliest alias-collapsed exact classifier inside the packet-locked candidate universe and does not by itself prove exclusive causal origin when alternative exact rules remain
    - a short explanation of why the selected rule is upstream of `base_size` generation rather than a downstream restatement
    - the required explicit statement: `This is an observational boundary, not proof of edge.`
    - the scope sentence immediately before the required status block: `The following status block is a packet-local exact-classification summary over the locked sizing-eligible cohort only; it is not a causal or runtime-general claim.`
    - the exact final output contract block below, copied verbatim:

      ```text
      BASE SIZE BOUNDARY STATUS:

      - Boundary identified: YES
      - Coverage: 100%
      - Accuracy: 100%
      - Validation: PASS

      Verdict:
      System behavior is fully determined by base_size generation.
      ```

- **Audit artifacts (all mandatory):**
  - `audit_trace_coverage.json`
  - `audit_field_presence.json`
  - `audit_classification.json`
  - `audit_determinism.json`
  - Missing any audit artifact is a hard failure.

### Audit artifact definitions

- **`audit_trace_coverage.json`**
  - Must prove:
    - total rows per trace
    - sizing-eligible rows per trace
    - sizing-ineligible rows per trace
    - `BASE_SIZE_POSITIVE` rows per trace
    - `BASE_SIZE_ZERO` rows per trace
    - combined totals
    - all rows accounted for exactly once

- **`audit_field_presence.json`**
  - Must record required-field presence checks across all sizing-eligible rows.
  - Must record packet-locked observable validity checks.
  - Must treat `post_fib_phase.blocked_reason` as required presence-only nullable metadata rather than a packet-locked observable.
  - Any missing required field or invalid packet-locked observable must trigger FAIL.

- **`audit_classification.json`**
  - Must record observed versus predicted counts and exact-match status for the final selected rule.
  - Must include:
    - confusion matrix
    - exact positive-set parity status
    - first exact conjunction size
    - selected minimality rank
    - pre-collapse exact rules
    - post-collapse exact rules
    - `alternative_rules_top5`
    - `closest_boundary_rows_top10`

- **`audit_determinism.json`**
  - Must record the SHA256 hash of every Phase 5 output other than `audit_determinism.json` itself for run 1 and run 2.
  - `audit_determinism.json` must not attempt to carry its own run-1 or run-2 hash inside the run-comparison manifest; that would be self-referential and is forbidden.
  - After the run-1/run-2 non-self hash comparison has passed, the final written `audit_determinism.json` may record a single informational `artifact_self_hash` for its own fully rendered bytes.
  - Must record whether all non-self output hashes matched exactly.

### Boundary-row proximity definitions

- Absolute-distance proximity in this section is ranking-only for `closest_boundary_rows_top10`; it does not alter rule truth, class labels, candidate generation, or exact-match validation.

- **Closest-boundary source population:**
  - if the final selected rule contains a relation clause, evaluate proximity over all sizing-eligible rows satisfying every other clause in the final selected rule
  - else evaluate proximity over all sizing-eligible rows using the first numeric literal clause in canonical clause order
- **Relation-clause margin rule:** for relation clause `<field_left> <operator> <field_right>`, let `l` be the observed left value and `r` the observed right value. The non-negative margin is:
  - `==`: `abs(l - r)`
  - `>`: `abs(l - r)`
  - `>=`: `abs(l - r)`
  - `<`: `abs(l - r)`
  - `<=`: `abs(l - r)`
- **Literal-clause margin rule:** for literal numeric clause `<field> <operator> <value>`, let `x` be the observed field value and `c` be the literal. The non-negative margin is:
  - `==`: `abs(x - c)`
  - `>`: `abs(x - c)`
  - `>=`: `abs(x - c)`
  - `<`: `abs(x - c)`
  - `<=`: `abs(x - c)`
- **Closest-boundary ordering rule:** rank rows by ascending `(margin, trace_name_order, bar_index)` with `trace_name_order = baseline_current, adaptation_off` and retain exactly the first `10` rows.
- Any negative, undefined, non-finite, or otherwise non-packet-computable margin is a hard failure before artifact write.

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
  - `BASE_SIZE_POSITIVE + BASE_SIZE_ZERO == sizing_eligible` for each trace and combined
  - `BASE_SIZE_POSITIVE` counts must reconcile exactly to the survivor-equivalent counts implied by the locked trace artifacts and `survivor_partition.json`
- Schema assertions:
  - both traces expose `trace_rows`
  - all required fields exist on every sizing-eligible row
  - `final.size == sizing_phase.final_size` on every sizing-eligible row
  - candidate mismatch is forbidden when both candidate fields are present
- Boundary assertions:
  - the selected rule must reproduce the exact observed positive set
  - `predicted_positive_rows == actual_positive_rows`
  - `predicted_zero_rows == actual_zero_rows`
  - `false_positives == 0`
  - `false_negatives == 0`
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 5 outputs must match exactly across both runs
- Audit assertions:
  - all four mandatory audit artifacts must exist
  - all audit artifacts must parse as valid JSON
  - final rule, confusion matrix, selected minimality rank, top `5` alternative rules, and `10` closest boundary rows must all be present explicitly
- Scope assertions:
  - no files outside Scope IN may be modified

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any required field is missing from any sizing-eligible row
- any packet-locked observable on a sizing-eligible row is `null`, non-finite, or otherwise invalid under the required observable validity rule
- `(trace_name, bar_index)` is duplicated in the trace population
- `final.size` and `sizing_phase.final_size` disagree on any sizing-eligible row
- `BASE_SIZE_POSITIVE` does not equal the survivor-equivalent set exactly
- no exact rule exists after exhausting the full packet-defined candidate universe
- any mandatory audit artifact is missing
- deterministic re-run hashes do not match
- final rule, confusion matrix, minimality ranking, top `5` alternative rules, or `10` closest boundary rows would be missing from the final outputs
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for exact-set parity and selector discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact-field integrity plus metadata-only nullable-field handling.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
