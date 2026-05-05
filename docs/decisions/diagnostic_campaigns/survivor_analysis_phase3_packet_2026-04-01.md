# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 3 survivor analysis in STRICT mode
- **Risk:** `MED` — why: trace-only observational analysis over existing governed artifacts; no runtime behavior changes allowed, but survivor/collapse classification must be deterministic, exhaustive, and fail-closed
- **Required Path:** `Full`
- **Objective:** Build a deterministic survivor analysis that characterizes bars that survive sizing (`final_size > 0`) versus bars that collapse in sizing (`final_size == 0`), using existing artifacts only and without interpreting results as edge
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 3 survivor analysis
- **Base SHA:** `d9cc2026`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\compensation_map.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\collapse_taxonomy.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_partition.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_feature_stats.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_signatures.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\survivor_analysis_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\survivor_analysis_phase3_packet_2026-04-01.md`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any backtest reruns
  - Any threshold/config/parameter changes
  - Any architecture changes
  - `config/strategy/champions/**`
  - Existing trace/compensation/taxonomy artifacts except read-only consumption
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/survivor_analysis_phase3_packet_2026-04-01.md`
  - `results/research/fa_v2_adaptation_off/survivor_partition.json`
  - `results/research/fa_v2_adaptation_off/survivor_feature_stats.json`
  - `results/research/fa_v2_adaptation_off/survivor_signatures.json`
  - `results/research/fa_v2_adaptation_off/survivor_analysis_summary.md`
- **Max files touched:** `5`

### Implementation surface

- Scope IN is limited to the four named read-only inputs, this packet, and the four named output artifacts.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- Analysis may use ephemeral terminal-side computation only; if a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No new parameters, thresholds, tuning, or redesign
- Deterministic ordering and stable JSON formatting required
- No silent missing-field handling; required-field absence is a hard failure
- Final interpretation must remain observational and must not be presented as edge, alpha, or performance proof

### Canonical analysis definitions

- **Trace population:** the union of `trace_rows` from the two packet-locked trace artifacts, analyzed per trace and in combined rollups.
- **Allowed trace names:** exactly `baseline_current` and `adaptation_off`, as recorded by the packet-locked input artifacts. Any other trace label is a hard failure.
- **Primary row key:** `(trace_name, bar_index)` in canonical ascending `bar_index` order within each trace; `timestamp` is a secondary consistency check only.
- **Primary key uniqueness rule:** `(trace_name, bar_index)` must be unique within the trace population. Any duplicate key is a hard failure. If a duplicate key also carries a different `timestamp`, that is an immediate hard failure.
- **Sizing-eligible row:** a trace row where `sizing_phase` is present and non-null.
- **Sizing-ineligible row:** a trace row where `sizing_phase` is null. These rows must be accounted for separately and are outside the survivor/collapse denominator.
- **Survivor row:** a sizing-eligible row whose `sizing_phase.final_size > 0`.
- **Collapse row:** a sizing-eligible row whose `sizing_phase.final_size == 0`.
- **Consistency rule:** for every sizing-eligible row, `final.size` must exist and equal `sizing_phase.final_size`. Any mismatch is a hard failure.
- **Classification rule:** each sizing-eligible row must be classified into exactly one of `{SURVIVOR, COLLAPSE}`. Any negative size, null size, NaN, or multiple classification is a hard failure.
- **Candidate agreement rule:** if both `decision_phase.selected_candidate` and `sizing_phase.candidate` are present, they must match exactly. Any mismatch is a hard failure.
- **Required fields for every sizing-eligible row:**
  - top-level: `bar_index`, `timestamp`, `sizing_phase`, `final`, `decision_phase`, `post_fib_phase`
  - `decision_phase`: `selected_candidate`, `regime`, `thresholds_used.entry_conf_threshold`, `p_buy`, `p_sell`, `max_ev`
  - `post_fib_phase`: `candidate`, `confidence_threshold`, `min_edge`, `edge_value`, `blocked_reason`
  - `sizing_phase`: `candidate`, `confidence_gate`, `base_size`, `size_scale`, `volatility_adjustment`, `regime_multiplier`, `htf_regime_multiplier`, `combined_multiplier`, `final_size`
  - `final`: `action`, `regime`, `htf_regime`, `size`, `reasons`, `confidence.overall`
- **Optional context fields:** `fib_phase`, `state_in`, `config_surface`, Phase 2 compensation/taxonomy joins by `bar_index` may be included only when present in the packet-locked artifacts.
- **Join rule for Phase 2 context:** join to `compensation_map.json.bars` and `collapse_taxonomy.json.family_assignments` by canonical `bar_index` only. Missing join rows are allowed only if explicitly recorded as `NO_PHASE2_CONTEXT`; silent omission is forbidden.

### Survivor signature surface

The analysis must compute deterministic signatures and feature summaries over the following packet-locked observational fields:

- trace name
- candidate side (`decision_phase.selected_candidate` or `sizing_phase.candidate`, which must agree when both exist)
- decision regime (`decision_phase.regime`)
- final regime (`final.regime`)
- HTF regime (`final.htf_regime`)
- entry confidence threshold (`decision_phase.thresholds_used.entry_conf_threshold`)
- confidence gate (`sizing_phase.confidence_gate`)
- edge value (`post_fib_phase.edge_value`)
- base size (`sizing_phase.base_size`)
- volatility adjustment (`sizing_phase.volatility_adjustment`)
- regime multiplier (`sizing_phase.regime_multiplier`)
- HTF regime multiplier (`sizing_phase.htf_regime_multiplier`)
- combined multiplier (`sizing_phase.combined_multiplier`)
- final size (`sizing_phase.final_size`)
- post-fib blocked reason (`post_fib_phase.blocked_reason`)
- Phase 2 bucket, if present
- Phase 2.6 final family, if present

### Output requirements

- **`survivor_partition.json`**
  - Must contain per-trace and combined counts for:
    - total trace rows
    - sizing-eligible rows
    - sizing-ineligible rows
    - survivor rows
    - collapse rows
  - Must prove:
    - `sizing_eligible + sizing_ineligible == total_trace_rows`
    - `survivor + collapse == sizing_eligible`
  - Must include canonical ordering and explicit denominator definitions.
  - **Canonical ordering rule:** trace sections must appear in the fixed order `baseline_current`, `adaptation_off`, `combined`.

- **`survivor_feature_stats.json`**
  - Must contain deterministic per-trace and combined statistics comparing survivors vs collapses over the signature surface.
  - For numeric fields: count, min, max, mean.
  - For categorical fields: counts and proportions.
  - **Proportion denominator rule:** every reported proportion must use the cohort count of the exact bucket being described as denominator, where a cohort is one of:
    - `(trace_name=baseline_current, class=SURVIVOR)`
    - `(trace_name=baseline_current, class=COLLAPSE)`
    - `(trace_name=adaptation_off, class=SURVIVOR)`
    - `(trace_name=adaptation_off, class=COLLAPSE)`
    - `(trace_name=combined, class=SURVIVOR)`
    - `(trace_name=combined, class=COLLAPSE)`
  - Each categorical stats block must record its explicit `cohort_denominator`.
  - **Canonical ordering rule:** top-level trace sections must appear in the fixed order `baseline_current`, `adaptation_off`, `combined`; within each cohort, numeric fields and categorical fields must be emitted in ascending field-name order, and categorical values must be emitted in descending count order with alphabetical tie-break.
  - No inferential statistics, p-values, or edge claims.

- **`survivor_signatures.json`**
  - Must contain the complete deterministic signature inventory for survivors and collapses; `top signatures` in the markdown summary must be derived from this full inventory rather than from a truncated JSON output.
  - Each signature record must include `trace_name`, `class`, `count`, and `cohort_denominator`.
  - Signature ordering must be:
    1. descending count
    2. trace name ascending
    3. class order ascending with `SURVIVOR` before `COLLAPSE`
    4. canonical JSON string of the signature payload ascending
  - Ties must be resolved deterministically.

- **`survivor_analysis_summary.md`**
  - Must summarize the survivor/collapse partition, dominant signatures, dominant multipliers/families/regimes, and explicit non-interpretation boundary.
  - Must state clearly that findings are observational characteristics of already-generated traces, not evidence of tradable edge.
  - **Dominant-selection rule:** all “dominant” items in the markdown summary must be derived only from the packet-generated JSON outputs.
  - **Top-N rule:** markdown may show at most top `5` signatures per cohort, ranked by the same deterministic order used in `survivor_signatures.json`.
  - Every percentage shown in markdown must display or directly reference the correct `cohort_denominator`.

### Gates required

- Coverage assertions:
  - every trace row from both packet-locked traces is accounted for exactly once in `total_trace_rows`
  - `sizing_eligible + sizing_ineligible == total_trace_rows` for each trace and combined
  - `survivor + collapse == sizing_eligible` for each trace and combined
- Schema assertions:
  - both input traces expose `trace_rows`
  - all required fields exist on every sizing-eligible row
  - `final.size == sizing_phase.final_size` on every sizing-eligible row
  - `decision_phase.selected_candidate == sizing_phase.candidate` whenever both fields are present
- Determinism assertions:
  - run the full artifact-generation procedure twice from the same locked inputs
  - file hashes for all four outputs must match exactly across both runs
- Cross-artifact reconciliation assertions:
  - markdown counts and top-5 signature callouts must reconcile exactly to the generated JSON outputs
  - any mismatch between markdown claims and JSON outputs is a hard failure
- JSON assertions:
  - `survivor_partition.json`, `survivor_feature_stats.json`, and `survivor_signatures.json` must parse successfully as JSON
  - no NaN/Infinity/non-JSON values
- Join assertions:
  - Phase 2 joins, when used, must be explicit and deterministic
  - any absent Phase 2 join row must be counted and labeled, never silently dropped

### Stop conditions

Stop immediately and report FAIL if any of the following occur:

- a required field is missing from any sizing-eligible row
- `(trace_name, bar_index)` is duplicated in the trace population
- `final.size` and `sizing_phase.final_size` disagree on any sizing-eligible row
- `decision_phase.selected_candidate` and `sizing_phase.candidate` both exist and disagree
- any sizing-eligible row has negative, null, or non-numeric `final_size`
- any row cannot be accounted for exactly once
- deterministic re-run hashes do not match
- implementation would require modifying any file outside Scope IN

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- These anchors support evidence discipline and artifact integrity only; they do not replace STRICT verification gates.
