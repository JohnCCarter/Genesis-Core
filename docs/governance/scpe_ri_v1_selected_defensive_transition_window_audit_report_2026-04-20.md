# SCPE RI V1 selected-defensive transition window audit report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md`
Skills used: `python_engineering`, `ri_off_parity_artifact_check`

This audit is observational only. It reconstructs selected-defensive and comparator-bucket profiles from frozen research artifacts using a research-side analytical mirror of the existing replay behavior; it does not modify or supersede canonical replay logic and does not propose a new threshold, defensive, or dwell rule.

The audit script executes helper definitions from `scripts/analyze/scpe_ri_v1_router_replay.py` via `runpy.run_path` only to reconstruct row-local raw target policy and decision-time state from frozen inputs. It does not regenerate canonical replay artifacts, and the run must fail if the frozen `results/research/scpe_v1_ri/**` replay-root surface changes.

The audit emits descriptive metrics, deterministic example rows, bounded comparator tables, and explicit recency-gap summaries only. Any `observed fresh-transition recency pocket`, `mixed`, or `overlapping` phrasing in this report is a non-authoritative analyst summary over frozen metrics and does not constitute a new rule, recommendation rule, or replay-quality reinterpretation.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
- `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`

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
- edits to prior audit/revision script logic
- any new threshold rule, defensive rule, or dwell rule
- any change to baseline or revision recommendation semantics

## File-level change summary

- `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md`
  - Added the bounded contract for an observational selected-defensive transition-window audit.
- `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
  - Added a tracked audit script that reconstructs raw defensive candidates from frozen inputs, profiles the selected-defensive comparator bucket, enforces frozen-input hashes, and writes one deterministic JSON summary.
- `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`
  - Added a commit-safe artifact with comparator summaries, recency-gap evidence, and deterministic example rows.
- `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
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
  - observed selected-defensive comparator: `selected_policy = RI_defensive_transition_policy`
  - threshold-retained comparator: `selected_policy = RI_continuation_policy` and `switch_reason = confidence_below_threshold`
  - min-dwell-retained comparator: `selected_policy = RI_no_trade_policy` and `switch_reason = switch_blocked_by_min_dwell`
- analytical mirror:
  - execute helper definitions from the unchanged research-side replay script via `runpy.run_path`
  - reconstruct row-local raw target policy and decision-time state from frozen inputs
  - fail closed on any missing mandatory field, hash mismatch, or row-identity drift between entry rows and replay trace rows
  - compute descriptive summary metrics and explicit recency-gap evidence only
- deterministic output rules:
  - sorted JSON keys
  - stable bucket ordering
  - selected-defensive examples sorted by lowest `bars_since_regime_change`, then highest `action_edge`, then highest `conf_overall`, then lowest `row_index`
  - comparator nearest-by-recency examples sorted by lowest `bars_since_regime_change`, then highest `action_edge`, then highest `conf_overall`, then lowest `row_index`
  - no timestamps generated by the script itself
  - no host/user metadata
  - no random inputs

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
   - Result: `PASS`
2. Static import proof on `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`

- Result: `PASS` (`No matches found`)

3. Explicit frozen decision-parity / replay-root identity gate
   - Surfaces:
     - `results/research/scpe_v1_ri/manifest.json`
     - `results/research/scpe_v1_ri/replay_metrics.json`
     - `results/research/scpe_v1_ri/routing_trace.ndjson`

- Result: `PASS`
- Evidence: manifest, replay-metrics, and routing-trace SHA256 values matched the expected frozen roots before the first run and remained unchanged after the second run.

4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`

- Result: `PASS` (`2 passed in 1.64s`)
- Note: these selectors are unchanged-surface guardrails only; they do not validate the new audit logic directly.

5. Determinism + replay-root immutability proof:

- Result: `PASS`
- Evidence: after formatter/lint settlement, a second explicit rerun confirmed `artifact_before == artifact_after`, `report_before == report_after`, unchanged hashes for the frozen replay-root surfaces, and unchanged hash for the frozen entry-row surface.

6. `pre-commit run --files docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`

- Result: `PASS` (`black`, `ruff`, `detect-secrets`, EOF/whitespace, JSON, merge-conflict, and large-file checks all passed; YAML hook skipped because no YAML files were in scope`)

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged and used only as an analysis reference.
- The canonical replay root `results/research/scpe_v1_ri/` is treated as frozen input only, and this audit claims replay-root-scoped immutability rather than full-repository immutability.
- Comparator buckets are descriptive reference cohorts from the same frozen reconstruction surface; they do not define an alternative acceptance policy, counterfactual routing rule, or new transition rule.
- This slice introduces no new threshold rule, no new defensive rule, no new dwell rule, and no new recommendation semantics.
- The audit artifact is observational-only, summary-only, and non-authoritative.

## Selected-defensive transition-window findings

### Observed selected-defensive routing is tiny but structurally coherent

- raw defensive candidates: `30`
- observed selected-defensive comparator: `2`
- threshold-retained comparator: `12`
- min-dwell-retained comparator: `6`

Interpretation:

- The observed selected-defensive bucket is tiny, but it is still coherent enough to profile because both rows sit in the same narrow structural region of the frozen replay surface.
- This slice therefore asks whether that tiny bucket is merely the strongest tail of the broad stable defensive-candidate population, or a separate observed fresh-transition recency pocket.

### Selected-defensive rows are fully contained within an extremely fresh recency range on the frozen replay surface

Observed selected-defensive recency summary:

- `min_bars_since_regime_change = 1.0`
- `avg_bars_since_regime_change = 3.0`
- `max_bars_since_regime_change = 5.0`
- transition buckets: `acute = 1`, `recent = 1`
- zones: `low = 2`

Selected-defensive example rows:

- row `1`
  - `bars_since_regime_change = 1.0`
  - `transition_bucket = acute`
  - `zone = low`
  - `switch_reason = transition_pressure_detected`
- row `2`
  - `bars_since_regime_change = 5.0`
  - `transition_bucket = recent`
  - `zone = low`
  - `switch_reason = defensive_transition_state`

Interpretation:

- The entire observed selected-defensive comparator appears only inside a very fresh recency range from `1` to `5` bars since regime change on the frozen replay surface.
- This is a much sharper structural signal than the score-like averages alone.

### The nearest threshold-retained rows remain far outside the selected-defensive recency range

Threshold-retained recency summary:

- `min_bars_since_regime_change = 119.0`
- `avg_bars_since_regime_change = 251.333333`
- `max_bars_since_regime_change = 528.0`
- transition buckets: `stable = 12`
- zones: `low = 8`, `mid = 4`

Nearest threshold rows by recency:

- row `13`: `119.0` bars, `zone = low`, `transition_bucket = stable`
- row `100`: `153.0` bars, `zone = low`, `transition_bucket = stable`
- row `101`: `154.0` bars, `zone = low`, `transition_bucket = stable`
- row `102`: `175.0` bars, `zone = low`, `transition_bucket = stable`
- row `103`: `176.0` bars, `zone = low`, `transition_bucket = stable`

Explicit gap evidence:

- selected-defensive ceiling: `5.0` bars
- nearest threshold row: `119.0` bars
- threshold gap from selected-defensive ceiling: `114.0` bars

Interpretation:

- Even the closest threshold-retained row is still `114` bars outside the observed selected-defensive recency ceiling.
- Threshold-retained rows can overlap on low-zone location and score-like strength, but they do not overlap on transition freshness.

### Min-dwell-retained rows get closer in recency than threshold-retained rows, but still remain outside the observed selected-defensive window

Min-dwell-retained recency summary:

- `min_bars_since_regime_change = 21.0`
- `avg_bars_since_regime_change = 189.166667`
- `max_bars_since_regime_change = 478.0`
- transition buckets: `stable = 6`
- zones: `mid = 5`, `low = 1`

Nearest min-dwell rows by recency:

- row `74`: `21.0` bars, `zone = mid`, `transition_bucket = stable`
- row `7`: `81.0` bars, `zone = mid`, `transition_bucket = stable`
- row `90`: `125.0` bars, `zone = mid`, `transition_bucket = stable`
- row `16`: `144.0` bars, `zone = mid`, `transition_bucket = stable`
- row `112`: `286.0` bars, `zone = mid`, `transition_bucket = stable`

Explicit gap evidence:

- selected-defensive ceiling: `5.0` bars
- nearest min-dwell row: `21.0` bars
- min-dwell gap from selected-defensive ceiling: `16.0` bars

Interpretation:

- Min-dwell-retained rows approach the selected-defensive window more closely than threshold-retained rows do.
- But they still begin outside the observed selected-defensive recency range, and they remain structurally stable rather than acute/recent.

### Score-like strength alone does not explain observed selected-defensive routing

Observed selected-defensive averages:

- `avg_ri_clarity_score = 26.0`
- `avg_conf_overall = 0.529631`
- `avg_action_edge = 0.059261`

Threshold-retained averages:

- `avg_ri_clarity_score = 25.5`
- `avg_conf_overall = 0.526986`
- `avg_action_edge = 0.053972`

Min-dwell-retained averages:

- `avg_ri_clarity_score = 25.0`
- `avg_conf_overall = 0.523857`
- `avg_action_edge = 0.047714`

Interpretation:

- Threshold-retained rows remain reasonably close to observed selected-defensive rows on score-like averages.
- The much stronger separation signal is transition freshness, not simple average score advantage.
- Low zone alone is also insufficient, because the nearest threshold rows are likewise low-zone but still structurally stable and far older in recency.

## Descriptive verdict

This slice does **not** recommend a new rule. It only supports a bounded descriptive conclusion:

- Observed selected-defensive routing appears only within an **observed fresh-transition recency pocket** on the frozen replay surface.
- That window is structurally distinct from the larger threshold-retained bucket and still distinct from the nearer min-dwell-retained bucket.
- So the selected-defensive comparator does **not** read like the strongest score-like tail of the same broad stable defensive-candidate population.
- It reads more like a tiny acute/recent transition pocket that the stable retained comparator buckets do not enter on the frozen baseline replay surface.

## Roadmap implications

This slice still does **not** authorize a new threshold, defensive, or dwell rule. It sharpens the roadmap one step further:

1. Threshold retention remains a meaningful bottleneck, but it should not be judged as a simple missed-selected-defensive clone because its rows are far outside the observed selected-defensive recency window.
2. Min-dwell retention sits closer in recency than threshold retention, but it still remains outside the selected-defensive window and stays fully stable/no-trade-held.
3. Any future semantics-changing revision should treat transition freshness as a distinct explanatory axis rather than assuming score-like strength alone explains selected-defensive routing.
4. Any next step beyond this audit remains only `föreslagen` and must be packeted separately.

## Residual risks

- This remains observational profile mapping, not execution evidence.
- The selected-defensive comparator is very small (`2` rows), so the recency-pocket conclusion must remain bounded to the frozen evidence rather than turned into a runtime rule.
- The audit shows structural separation, not causal proof that any comparator row should have switched.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
  - `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - `scripts/analyze/scpe_ri_v1_router_replay.py`

## Bottom line

The frozen baseline replay shows observed selected-defensive routing only inside a tiny fresh-transition recency range: `1` to `5` bars since regime change, with `acute/recent` transition buckets and `low` zone on both rows. The nearest threshold-retained row starts at `119` bars and the nearest min-dwell-retained row starts at `21` bars, so neither retained comparator bucket actually enters that observed selected-defensive range. That makes the most defensible summary for this slice an observed recency-pocket interpretation rather than a broad score-tail interpretation.
