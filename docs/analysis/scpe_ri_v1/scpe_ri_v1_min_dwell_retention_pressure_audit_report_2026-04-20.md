# SCPE RI V1 min-dwell retention pressure audit report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/decisions/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_packet_2026-04-20.md`
Skills used: `python_engineering`

This audit is observational only. It reconstructs min-dwell-retained raw defensive-candidate profiles from frozen research artifacts using a research-side analytical mirror of the existing replay behavior; it does not modify or supersede canonical replay logic and does not propose a new dwell rule.

The audit script executes helper definitions from `scripts/analyze/scpe_ri_v1_router_replay.py` via `runpy.run_path` only to reconstruct row-local raw target policy and decision-time state from frozen inputs. It does not regenerate canonical replay artifacts, and the run must fail if the frozen `results/research/scpe_v1_ri/**` replay-root surface changes.

The audit emits descriptive metrics, deterministic example rows, and bounded comparator tables only. Any `near-miss`, `observationally lower`, `mixed`, or `overlapping` phrasing in this report is a non-authoritative analyst summary over frozen metrics and does not constitute a new dwell rule, recommendation rule, or replay-quality reinterpretation.

If the emitted descriptive metrics do not show a clear separation, this report must fall back to `mixed/overlapping` wording rather than over-claiming a stronger separation than the frozen metrics support.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Scope summary

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py`
- `results/evaluation/scpe_ri_v1_min_dwell_retention_pressure_audit_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- `docs/scpe_ri_v1_architecture.md`
- runtime integration
- canonical replay regeneration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to `scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py`
- edits to `scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py`
- edits to prior audit/revision script logic
- any new threshold rule, defensive rule, or dwell rule
- any change to baseline or revision recommendation semantics

## File-level change summary

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_packet_2026-04-20.md`
  - Added the bounded contract for an observational min-dwell retention pressure audit.
- `scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py`
  - Added a tracked audit script that reconstructs raw defensive candidates from frozen inputs, profiles the min-dwell-retained comparator bucket, enforces frozen-input hashes, and writes one deterministic JSON summary.
- `results/evaluation/scpe_ri_v1_min_dwell_retention_pressure_audit_2026-04-20.json`
  - Added a commit-safe artifact with comparator summaries, metric deltas, and deterministic min-dwell example rows.
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_report_2026-04-20.md`
  - Added this implementation report.

## Audit method

- frozen inputs:
  - Phase C entry rows: `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - baseline routing trace: `results/research/scpe_v1_ri/routing_trace.ndjson`
  - baseline replay metrics: `results/research/scpe_v1_ri/replay_metrics.json`
  - baseline replay manifest: `results/research/scpe_v1_ri/manifest.json`
  - replay script reference: `scripts/analyze/scpe_ri_v1_router_replay.py`
- exact comparator selectors from one shared reconstructed frozen candidate table:
  - raw defensive candidates: `raw target policy = RI_defensive_transition_policy`
  - min-dwell-retained comparator: `selected_policy = RI_no_trade_policy` and `switch_reason = switch_blocked_by_min_dwell`
  - threshold-retained comparator: `selected_policy = RI_continuation_policy` and `switch_reason = confidence_below_threshold`
  - observed selected-defensive comparator: `selected_policy = RI_defensive_transition_policy`
- analytical mirror:
  - execute helper definitions from the unchanged research-side replay script via `runpy.run_path`
  - reconstruct row-local raw target policy and decision-time state from frozen inputs
  - fail closed on any missing mandatory field, hash mismatch, or row-identity drift between entry rows and replay trace rows
  - compute descriptive summary metrics and comparator deltas only
- deterministic output rules:
  - sorted JSON keys
  - stable bucket ordering
  - deterministic example-row sort by highest `action_edge`, then highest `conf_overall`, then highest `ri_clarity_score`, then lowest `row_index`
  - no timestamps generated by the script itself
  - no host/user metadata
  - no random inputs

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`

- Result: `PASS` (`No matches found`)

3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`

- Result: `PASS` (`2 passed in 2.19s`)
- Note: these selectors are unchanged-surface guardrails only; they do not validate the new audit logic directly.

4. Determinism + replay-root immutability proof:

- Result: `PASS`
- Evidence: after formatter/lint settlement, a second explicit rerun confirmed `artifact_before == artifact_after`, `report_before == report_after`, and unchanged hashes for the frozen replay-root surfaces (`routing_trace.ndjson`, `replay_metrics.json`, `manifest.json`) plus the frozen entry-row surface.

5. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py results/evaluation/scpe_ri_v1_min_dwell_retention_pressure_audit_2026-04-20.json`

- Result: `PASS` (`black`, `ruff`, `detect-secrets`, EOF/whitespace, JSON, merge-conflict, and large-file checks all passed; YAML hook skipped because no YAML files were in scope`)

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged and used only as an analysis reference.
- The canonical replay root `results/research/scpe_v1_ri/` is treated as frozen input only, and this audit claims replay-root-scoped immutability rather than full-repository immutability.
- Comparator buckets are descriptive reference cohorts from the same frozen reconstruction surface; they do not define an alternative acceptance policy, counterfactual recommendation rule, or dwell-retuning proposal.
- This slice introduces no new dwell rule, no new defensive rule, and no new recommendation semantics.
- The audit artifact is observational-only, summary-only, and non-authoritative.

## Min-dwell retention findings

### Min-dwell-retained rows are a smaller but coherent bounded comparator bucket

- raw defensive candidates: `30`
- min-dwell-retained comparator: `6`
- threshold-retained comparator: `12`
- observed selected-defensive comparator: `2`

Interpretation:

- The min-dwell-retained bucket is smaller than the threshold-retained bucket, but it is still a coherent comparator cohort rather than a one-off tail.
- All six rows sit in the same selected-policy / switch-reason pattern, so this bucket is structurally clean enough for a bounded audit.

### Min-dwell-retained rows look weaker than threshold-retained rows on the emitted score-like averages

Min-dwell-retained averages:

- `avg_ri_clarity_score = 25.0`
- `avg_conf_overall = 0.523857`
- `avg_action_edge = 0.047714`
- `avg_bars_since_regime_change = 189.166667`

Threshold-retained averages:

- `avg_ri_clarity_score = 25.5`
- `avg_conf_overall = 0.526986`
- `avg_action_edge = 0.053972`
- `avg_bars_since_regime_change = 251.333333`

Min-dwell minus threshold deltas:

- clarity: `-0.5`
- confidence: `-0.003129`
- action edge: `-0.006258`
- bars since regime change: `-62.166666`

Interpretation:

- The min-dwell-retained bucket is descriptively weaker than the threshold-retained bucket on every emitted score-like average.
- It also sits materially closer to no-trade-held behavior than to continuation-held behavior, because every row remains `RI_no_trade_policy` with `policy_no_trade` veto.

### Min-dwell-retained rows also look weaker than the broader raw defensive candidate table

Raw defensive candidate averages:

- `avg_ri_clarity_score = 25.5`
- `avg_conf_overall = 0.526244`
- `avg_action_edge = 0.052487`
- `avg_bars_since_regime_change = 252.466667`

Min-dwell minus raw defensive deltas:

- clarity: `-0.5`
- confidence: `-0.002387`
- action edge: `-0.004773`
- bars since regime change: `-63.3`

Interpretation:

- Relative to the full raw defensive table, min-dwell-retained rows are again weaker on every emitted score-like average.
- That supports a bounded descriptive conclusion that this bucket is not just a random slice of the raw defensive population.

### Min-dwell-retained rows remain structurally distinct from observed selected-defensive rows

Observed selected-defensive averages:

- `avg_ri_clarity_score = 26.0`
- `avg_conf_overall = 0.529631`
- `avg_action_edge = 0.059261`
- `avg_bars_since_regime_change = 3.0`

Min-dwell minus selected-defensive deltas:

- clarity: `-1.0`
- confidence: `-0.005774`
- action edge: `-0.011547`
- bars since regime change: `+186.166667`

Bucket structure contrast:

- min-dwell-retained transition buckets: `stable = 6`
- selected-defensive transition buckets: `acute = 1`, `recent = 1`
- min-dwell-retained zones: `mid = 5`, `low = 1`
- selected-defensive zones: `low = 2`
- min-dwell-retained veto reasons: `policy_no_trade = 6`
- selected-defensive veto reasons: `defensive_transition_cap = 1`, `state_below_veto_floor = 1`

Interpretation:

- The min-dwell-retained bucket is both score-wise weaker and structurally different from the small selected-defensive comparator.
- It does not look like a near-miss clone of observed selected-defensive rows.

### Min-dwell-retained rows are stable no-trade-held rows, not live continuation-held rows

- min-dwell-retained selected policy counts: `RI_no_trade_policy = 6`
- min-dwell-retained switch reason counts: `switch_blocked_by_min_dwell = 6`
- min-dwell-retained veto reasons: `policy_no_trade = 6`
- min-dwell-retained transition buckets: `stable = 6`
- strongest example row:
  - row `112`
  - `action_edge = 0.062481`
  - `conf_overall = 0.531241`
  - `ri_clarity_score = 26.0`
  - `bars_since_regime_change = 286.0`
  - `zone = mid`
  - `veto_reason = policy_no_trade`

Interpretation:

- Even the strongest min-dwell-retained examples remain no-trade-held and are still policy-no-trade-vetoed after the stability block.
- That makes this bucket look less like a continuation-ready near-miss population and more like a cleaner no-trade-hold suppression surface.

## Descriptive verdict

This slice does **not** recommend a new dwell rule. It only supports a bounded descriptive conclusion:

- The min-dwell-retained bucket looks **observationally lower on the emitted score-like averages** than the threshold-retained bucket.
- It also remains structurally separated from the selected-defensive comparator by transition recency, zone mix, and veto outcome.
- So this bucket does **not** read like a close near-miss proxy for observed selected-defensive routing; it reads more like a weaker, stable, no-trade-held defensive subpopulation.

## Roadmap implications

This slice still does **not** authorize dwell tuning. It sharpens the roadmap one step further:

1. Threshold retention remains the more interesting high-overlap bottleneck surface.
2. Min-dwell retention is still a valid suppressor, but it now looks less like the closest route to selected-defensive behavior and more like a weaker no-trade-held bucket.
3. Any future semantics-changing revision should treat dwell timing and threshold pressure as different bottleneck classes rather than one shared release problem.
4. Any next step beyond this audit remains only `föreslagen` and must be packeted separately.

## Residual risks

- This remains observational profile mapping, not execution evidence.
- The min-dwell comparator is small (`6` rows), so any “observationally lower” wording must remain bounded to the emitted metrics rather than turned into a rule claim.
- The selected-defensive comparator remains very small (`2` rows), so cross-bucket similarity claims must remain careful.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_min_dwell_retention_pressure_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_min_dwell_retention_pressure_audit.py`
  - `results/evaluation/scpe_ri_v1_min_dwell_retention_pressure_audit_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - `scripts/analyze/scpe_ri_v1_router_replay.py`

## Bottom line

The min-dwell-retained comparator bucket is smaller than the threshold-retained bucket and comes out descriptively weaker on the emitted score-like averages than both threshold-retained and raw-defensive comparators. It is also structurally different from the tiny selected-defensive comparator because it remains entirely stable, mostly mid-zone, and uniformly policy-no-trade-vetoed. So the most defensible summary for this slice is that min-dwell retention is a real suppressor, but a weaker and less overlap-rich one than threshold retention.
