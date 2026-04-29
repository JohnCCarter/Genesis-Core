# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 6 edge-value decomposition in STRICT mode
- **Risk:** `MED` — why: trace-only observational decomposition over locked artifacts; no runtime behavior changes allowed, but any claim about the origin of `edge_value` or its threshold crossing must be deterministic, reproducible, fail-closed, and exact on the full sizing-eligible population
- **Required Path:** `Full`
- **Objective:** Identify the deterministic observational dependency structure of `edge_value` and the minimal upstream condition that reproduces `edge_value > 0.19995318442513305` exactly, using locked artifacts only and without interpreting the result as edge
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 6 edge-value decomposition
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase5_base_size_origin\base_size_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\edge_value_decomposition_phase6_packet_2026-04-01.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\edge_value_boundary.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\edge_value_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\edge_value_dependency_map.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\edge_value_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\audit_trace_coverage.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\audit_field_presence.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\audit_classification.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\phase6_edge_value_decomposition\audit_determinism.json`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any backtest reruns
  - Any threshold/config/parameter changes
  - Any architecture changes
  - Any edits to existing Phase 3–5 artifacts outside the packet file itself
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/edge_value_decomposition_phase6_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/edge_value_boundary.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/edge_value_feature_stats.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/edge_value_dependency_map.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/edge_value_summary.md`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/audit_trace_coverage.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/audit_field_presence.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/audit_classification.json`
  - `results/research/fa_v2_adaptation_off/phase6_edge_value_decomposition/audit_determinism.json`
- **Max files touched:** `9`

### Implementation surface

- Scope IN is limited to the five named read-only inputs, this packet, and the eight named output artifacts.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No new thresholds, tuning, redesign, or architecture changes
- Edge-value decomposition must be observational only
- Deterministic ordering and stable JSON formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must not be presented as edge, alpha, causality proof, or performance proof
- Final interpretation must not present the selected rule as an exclusive causal origin when one or more exact upstream aliases remain after packet-defined collapse and ranking
- The locked threshold literal `0.19995318442513305` is Phase-5-derived context and may be reused only as an observational classification boundary; it must not be promoted to runtime or tuning authority

### Canonical analysis definitions

- **Allowed trace names:** exactly `baseline_current` and `adaptation_off`. Any other trace label is a hard failure.
- **Trace-label mapping rule:** `trace_baseline_current.json` maps canonically to `baseline_current`, and `trace_adaptation_off.json` maps canonically to `adaptation_off`. If an embedded payload trace label exists and disagrees with this file-bound mapping, stop and FAIL.
- **Primary row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Primary key uniqueness rule:** `(trace_name, bar_index)` must be unique within the trace population. Any duplicate key is a hard failure.
- **Sizing-eligible row:** a trace row where `sizing_phase` is present and non-null.
- **EDGE_ABOVE_THRESHOLD row:** a sizing-eligible row where `post_fib_phase.edge_value > 0.19995318442513305`.
- **EDGE_AT_OR_BELOW_THRESHOLD row:** a sizing-eligible row where `post_fib_phase.edge_value <= 0.19995318442513305`.
- **Phase-parity rule:** `EDGE_ABOVE_THRESHOLD` must equal the Phase 5 `BASE_SIZE_POSITIVE` set exactly, meaning `post_fib_phase.edge_value > 0.19995318442513305` if and only if `sizing_phase.base_size > 0` and if and only if `sizing_phase.final_size > 0`. Any mismatch is a hard failure.
- **Consistency rule:** for every sizing-eligible row, `final.size` must exist and equal `sizing_phase.final_size`. Any mismatch is a hard failure.
- **Candidate agreement rule:** if both `decision_phase.selected_candidate` and `sizing_phase.candidate` are present, they must match exactly. Any mismatch is a hard failure.
- **Required fields for every sizing-eligible row:**
  - top-level: `bar_index`, `timestamp`, `decision_phase`, `post_fib_phase`, `sizing_phase`, `final`
  - `decision_phase`: `selected_candidate`, `regime`, `thresholds_used.entry_conf_threshold`, `p_buy`, `p_sell`, `max_ev`
  - `post_fib_phase`: `candidate`, `confidence_threshold`, `min_edge`, `edge_value`, `blocked_reason`, `confidence_data.conf_val_gate`
  - `sizing_phase`: `candidate`, `confidence_gate`, `base_size`, `final_size`
  - `final`: `regime`, `size`
- **Metadata-only nullable-field rule:** `post_fib_phase.blocked_reason` is a required presence-only metadata field. It may be `null`, is excluded from packet-locked observable validity checks, is excluded from candidate generation, and may be reported for audit context only.
- **Packet-locked upstream observables:**
  - `decision_phase.p_buy`
  - `decision_phase.p_sell`
  - `decision_phase.max_ev`
  - `decision_phase.selected_candidate`
  - `decision_phase.regime`
  - `post_fib_phase.min_edge`
- **Packet-locked derived observables:**
  - `decision_phase.probability_gap = abs(decision_phase.p_buy - decision_phase.p_sell)`
  - `decision_phase.argmax_candidate = LONG if decision_phase.p_buy >= decision_phase.p_sell else SHORT`
- **Required observable validity rule:** every packet-locked upstream or derived observable used for dependency mapping, feature separation, boundary assertions, correlation tables, candidate generation, or deterministic ranking on every sizing-eligible row must be present, finite where numeric, and non-null. Any missing value, `null`, `NaN`, positive infinity, or negative infinity is a hard failure before dependency derivation, candidate generation, ranking, audit derivation, or artifact write.
- **Observed classes for Phase 6 feature separation:**
  - `EDGE_ABOVE_THRESHOLD`
  - `EDGE_AT_OR_BELOW_THRESHOLD`
  - `BASE_SIZE_POSITIVE_EQUIVALENT = EDGE_ABOVE_THRESHOLD`
  - `BASE_SIZE_ZERO_EQUIVALENT = EDGE_AT_OR_BELOW_THRESHOLD`
- **Correlation class definitions:**
  - `exact_identity`: numeric equality to `post_fib_phase.edge_value` on every sizing-eligible row
  - `exact_classifier_alias`: exact reproduction of the `EDGE_ABOVE_THRESHOLD` set under the packet-defined candidate rule search
  - `partial_classifier`: non-exact classifier with non-zero error
  - `constant_context`: field has exactly one observed value on the full sizing-eligible population
  - `independent_context`: field is present but neither an exact identity nor an exact classifier alias

### Phase task requirements

- **Phase 6.1 — Edge Distribution Analysis**
  - Compare `post_fib_phase.edge_value` for `EDGE_ABOVE_THRESHOLD` versus `EDGE_AT_OR_BELOW_THRESHOLD` per trace and combined.
  - Determine whether the threshold behaves as a sharp boundary, a clustered step, or a gradient with overlap.
  - Report ordered distinct values near the threshold and the nearest-above / nearest-below margins per trace and combined.

- **Phase 6.2 — Upstream Dependency Mapping**
  - Trace `post_fib_phase.edge_value` against:
    - `decision_phase.p_buy`
    - `decision_phase.p_sell`
    - `decision_phase.max_ev`
    - `post_fib_phase.min_edge`
    - `decision_phase.regime`
    - `decision_phase.selected_candidate`
  - Also derive and test:
    - `decision_phase.probability_gap`
    - `decision_phase.argmax_candidate`
  - Determine whether `edge_value` is observationally identical to any upstream or derived variable.
  - Emit an explicit dependency graph in artifact form.

- **Phase 6.3 — Feature Separation**
  - For each packet-locked upstream or derived variable, test whether it can separate `EDGE_ABOVE_THRESHOLD` from `EDGE_AT_OR_BELOW_THRESHOLD`.
  - Measure, at minimum:
    - coverage
    - accuracy
    - false positives
    - false negatives
    - first exact conjunction size when applicable
    - minimality rank when applicable

- **Phase 6.4 — Minimal Edge Driver Extraction**
  - Generate deterministic candidate rules from packet-locked upstream and derived observables only.
  - Find the minimal rule set that reproduces exactly the `626` combined `EDGE_ABOVE_THRESHOLD` rows with no false positives and no false negatives.
  - The final selected rule must be expressed entirely upstream of `post_fib_phase.edge_value` whenever an exact upstream alias exists.

- **Phase 6.5 — Alias & Dependency Resolution**
  - Identify:
    - variables perfectly correlated with `edge_value`
    - variables partially correlated with `edge_value`
    - variables that are independent contextual annotations only
  - Distinguish exact identity from exact threshold-classifier alias and from constant context.

### Candidate rule space

- Candidate rules may only use these packet-locked upstream or derived observables:
  - `decision_phase.p_buy`
  - `decision_phase.p_sell`
  - `decision_phase.max_ev`
  - `decision_phase.selected_candidate`
  - `decision_phase.regime`
  - `post_fib_phase.min_edge`
  - `decision_phase.probability_gap`
  - `decision_phase.argmax_candidate`
- `post_fib_phase.edge_value`, `sizing_phase.base_size`, `sizing_phase.final_size`, `sizing_phase.confidence_gate`, and any downstream multiplier or final-regime field are forbidden in the candidate rule space.
- Candidate rules must be emitted in canonical textual grammar only.
- **Canonical rule grammar:**
  - literal clause form: `<field> <operator> <value>`
  - relation clause form: `<field_left> <operator> <field_right>`
  - allowed operators: `==`, `>`, `>=`, `<`, `<=`
  - allowed composition form: `ALL(<clause_1>; <clause_2>; ...; <clause_n>)`
  - no `OR`, no negation, no implicit grouping, no free-text commentary inside rule strings
- **Allowed literal-clause universe:**
  - numeric upstream or derived fields may use `==`, `>`, `>=`, `<`, `<=` against observed values present in the full sizing-eligible population
  - categorical upstream or derived fields may use `==` only against observed labels present in the full sizing-eligible population
- **Allowed relation-clause universe:**
  - `decision_phase.max_ev <op> decision_phase.probability_gap`
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
- **Exact-rule alias-collapse rule:** after identifying all exact rules at the first conjunction size that yields exact reproduction, collapse exact rules in deterministic stages before ranking alternatives:
  - first collapse numeric threshold aliases on the same literal field when they induce the exact same predicted positive key set; keep only the earliest rule in packet-defined exhaustive search order as the field-local representative
  - then collapse exact rules across exact-identity fields when their rule text differs only by substituting one field from the same exact-identity equivalence class; keep the earliest rule in packet-defined exhaustive search order as the class representative
  - do not collapse across categorical versus numeric clause types unless they are in the same packet-defined exact-identity equivalence class
- **Final-rule selection rule:** after alias collapse, select the earliest exact upstream rule in packet-defined exhaustive search order as `final_rule`.
- **Alternative-rule ranking rule:** after alias collapse and final-rule selection, rank all remaining exact upstream rules by packet-defined exhaustive search order and retain at most the first `5` as `alternative_rules_top5`.
- **Minimality rank rule:** `minimality_rank` is the 1-based ordinal position of a candidate inside the packet-defined exhaustive search order.

### Output requirements

- **`edge_value_boundary.json`**
  - Must contain exactly one final selected rule.
  - Required fields:
    - `final_rule`
    - `coverage`
    - `accuracy`
    - `validated`
    - `dependency_resolved`
    - `predicted_above_threshold_rows`
    - `predicted_at_or_below_threshold_rows`
    - `actual_above_threshold_rows`
    - `actual_at_or_below_threshold_rows`
    - `first_exact_conjunction_size`
    - `selected_minimality_rank`
    - `confusion_matrix`
    - `alternative_rules_top5`
  - `coverage` is positive-class recall: `(true_positives / actual_above_threshold_rows) * 100`.
  - `accuracy` is overall classification accuracy over the full sizing-eligible population: `((true_positives + true_negatives) / total_sizing_eligible) * 100`.
  - `coverage` and `accuracy` must be JSON numbers on the 0-100 scale, rounded to at most 6 decimal places using round-half-up, with trailing zeros removed and integral values serialized without a decimal suffix.
  - `dependency_resolved` may be `YES` only if at least one exact identity or exact upstream classifier alias is established and audited explicitly.
  - `alternative_rules_top5` must exclude the final selected rule.

- **`edge_value_feature_stats.json`**
  - Must contain deterministic per-trace and combined statistics comparing `EDGE_ABOVE_THRESHOLD` versus `EDGE_AT_OR_BELOW_THRESHOLD` over the required Phase 6 comparison surface.
  - Must include an `edge_distribution` block with ordered distinct-value counts, minimum margin below threshold, and minimum margin above threshold.
  - For numeric fields: count, min, max, mean, ordered distinct-value counts.
  - For categorical fields: ordered counts and proportions.
  - Top-level trace sections must appear in the fixed order `baseline_current`, `adaptation_off`, `combined`.

- **`edge_value_dependency_map.json`**
  - Must include:
    - `dependency_graph`
    - `exact_identity_relations`
    - `exact_classifier_aliases`
    - `partial_classifier_summary`
    - `constant_context_fields`
    - `independent_context_fields`
    - `correlation_table`
  - `dependency_graph` must be explicit, deterministic, and acyclic as emitted text or adjacency records.
  - `correlation_table` must include, for every packet-locked upstream or derived variable:
    - variable name
    - variable class (`upstream` or `derived`)
    - correlation class
    - exact equality status versus `edge_value`
    - exact classifier status versus `EDGE_ABOVE_THRESHOLD`
    - coverage
    - accuracy
    - `false_positives`
    - `false_negatives`
    - `minimal_rule_size` if exact classifier, else `null`

- **`edge_value_summary.md`**
  - Must include:
    - the final selected rule
    - the confusion matrix
    - the selected minimality rank
    - the top `5` alternative rules if any exist
    - an explicit dependency graph summary
    - an explicit correlation-table summary
    - the explicit caveat that the final selected rule is the earliest alias-collapsed exact upstream classifier inside the packet-locked candidate universe and does not by itself prove exclusive causal origin when alternative exact rules remain
    - the required explicit statement: `This is an observational boundary, not proof of edge.`
    - the exact final output contract block below, copied verbatim:

      ```text
      EDGE VALUE STATUS:

      - Boundary identified: YES
      - Coverage: 100%
      - Accuracy: 100%
      - Dependency resolved: YES/NO

      Verdict:
      Edge value origin is (resolved / unresolved).
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
    - `EDGE_ABOVE_THRESHOLD` rows per trace
    - `EDGE_AT_OR_BELOW_THRESHOLD` rows per trace
    - combined totals
    - all rows accounted for exactly once
    - exact reconciliation to Phase 5 class counts implied by the locked traces

- **`audit_field_presence.json`**
  - Must record required-field presence checks across all sizing-eligible rows.
  - Must record packet-locked upstream and derived observable validity checks.
  - Must treat `post_fib_phase.blocked_reason` as required presence-only nullable metadata rather than a packet-locked observable.
  - Any missing required field or invalid packet-locked observable must trigger FAIL.

- **`audit_classification.json`**
  - Must record observed versus predicted counts and exact-match status for the final selected rule.
  - Must include:
    - confusion matrix
    - exact threshold-set parity status
    - first exact conjunction size
    - selected minimality rank
    - pre-collapse exact rules
    - post-collapse exact rules
    - `alternative_rules_top5`
    - exact identity findings
    - classifier alias findings

- **`audit_determinism.json`**
  - Must record the SHA256 hash of every Phase 6 output other than `audit_determinism.json` itself for run 1 and run 2.
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
  - all trace rows accounted for exactly once
  - all sizing-eligible rows accounted for exactly once
  - `EDGE_ABOVE_THRESHOLD + EDGE_AT_OR_BELOW_THRESHOLD == sizing_eligible` for each trace and combined
  - `EDGE_ABOVE_THRESHOLD` counts must reconcile exactly to the Phase 5 `BASE_SIZE_POSITIVE` counts implied by the locked trace artifacts
- Schema assertions:
  - both traces expose `trace_rows`
  - all required fields exist on every sizing-eligible row
  - `final.size == sizing_phase.final_size` on every sizing-eligible row
  - candidate mismatch is forbidden when both candidate fields are present
- Dependency assertions:
  - every exact identity claim must be proven on the full sizing-eligible population
  - every exact classifier alias claim must be proven on the full sizing-eligible population
  - every constant-context claim must be proven on the full sizing-eligible population
- Boundary assertions:
  - the selected rule must reproduce the exact observed above-threshold set
  - `predicted_above_threshold_rows == actual_above_threshold_rows`
  - `predicted_at_or_below_threshold_rows == actual_at_or_below_threshold_rows`
  - `false_positives == 0`
  - `false_negatives == 0`
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all non-self Phase 6 outputs must match exactly across both runs
- Audit assertions:
  - all four mandatory audit artifacts must exist
  - all audit artifacts must parse as valid JSON
  - final rule(s), confusion matrix, minimality ranking, dependency graph, top `5` alternative rules, and correlation table must all be present explicitly
- Scope assertions:
  - no files outside Scope IN may be modified
  - if `pre-commit run --all-files` or any artifact-generation step writes a path outside Scope IN, revert those edits immediately and FAIL the packet; out-of-scope mutations may not be retained, staged, or normalized into the run

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- any required field is missing from any sizing-eligible row
- any packet-locked upstream or derived observable on a sizing-eligible row is `null`, non-finite, or otherwise invalid under the required observable validity rule
- `(trace_name, bar_index)` is duplicated in the trace population
- `final.size` and `sizing_phase.final_size` disagree on any sizing-eligible row
- `EDGE_ABOVE_THRESHOLD` does not equal the packet-defined Phase 5 positive-equivalent set exactly
- no exact rule exists after exhausting the full packet-defined candidate universe
- any mandatory audit artifact is missing
- deterministic re-run hashes do not match
- final rule(s), confusion matrix, minimality ranking, dependency graph, top `5` alternative rules, or correlation table would be missing from the final outputs
- implementation would require modifying any file outside Scope IN
- implementation would require a committed helper file outside Scope IN

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill anchors used for governance review: `.github/skills/feature_parity_check.json` for exact-set parity and selector discipline, and `.github/skills/ri_off_parity_artifact_check.json` for artifact-field integrity plus metadata-only nullable-field handling.
- These anchors supplement, and do not replace, the locked STRICT verification gates.
