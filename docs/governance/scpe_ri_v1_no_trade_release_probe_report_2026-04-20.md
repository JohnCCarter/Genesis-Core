# SCPE RI V1 no-trade release probe report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
Skills used: `python_engineering`

This slice adds a summary-only, observational-only, non-authoritative probe on top of the unchanged SCPE RI V1 replay outputs and the already frozen no-trade / min-dwell audit artifact. It does not modify or regenerate the replay root and does not change router logic, thresholds, or recommendation state.

This probe is descriptive and observational only. It measures how many blocked `no_trade` release attempts fall inside the frozen `successful_exit_from_no_trade` cohort's observed categorical and numeric support envelope; it does not establish permissibility, routing defect, threshold change, or recommendation-state change.

Inside-envelope means descriptive overlap only, not “should have released”.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
- `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- any runtime integration
- any replay-router logic changes
- any threshold changes
- any change to the replay-root recommendation value or semantics

## File-level change summary

- `docs/governance/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
  - Tightened the bounded probe contract with explicit descriptive-only wording, explicit envelope method, and named smoke/immutability gates.
- `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
  - Added a tracked read-only probe script that validates frozen replay inputs, uses the prior no-trade audit only as a frozen count-consistency cross-check, proves replay-root immutability, and writes one summary-only artifact.
- `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - Added a commit-safe probe artifact summarizing categorical overlap, numeric overlap, median-floor overlap, and main mismatch reasons for blocked no-trade exits.
- `docs/governance/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md`
  - Added this implementation report.

## Probe method

- successful-release cohort = rows where `previous_policy = RI_no_trade_policy` and `selected_policy != RI_no_trade_policy`
- blocked-release cohort = rows where `previous_policy = RI_no_trade_policy`, `selected_policy = RI_no_trade_policy`, `switch_proposed = true`, `switch_blocked = true`, and `switch_reason = switch_blocked_by_min_dwell`
- categorical envelope = observed bucket membership present in the frozen successful-release cohort
- numeric envelope = observed min/max numeric range plus robust descriptive summaries from the frozen successful-release cohort
- overlap remains descriptive only and must not be interpreted as a policy defect judgment or a recommendation update
- the prior no-trade audit artifact is used only as a frozen count-consistency cross-check, not as policy authority or router-correctness proof

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`
   - Result: `PASS` (`No matches found`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
4. Determinism + replay-root immutability proof:
   - reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
   - `json_before = ec2691cea7b464f1c63f9d6ad5ee1eee81548b0f6b170c8ace26d1e864a94623`
   - `json_after = ec2691cea7b464f1c63f9d6ad5ee1eee81548b0f6b170c8ace26d1e864a94623`
   - `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - Result: `PASS`
5. `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_probe.py results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`

- Result: `PASS`

## Boundary proof

- The probe artifact is observational-only, summary-only, and non-authoritative.
- It is derived from unchanged replay outputs under `results/research/scpe_v1_ri/` and the prior frozen no-trade audit artifact.
- It contains no row-level replay extract and does not replace the replay-root artifacts.
- It must not be used to change router policy, router thresholds, or recommendation state.
- The script contains no imports from `src/core/**` and no runtime wiring.
- The script fails closed if required replay fields are missing, if unexpected replay-input keys appear, if the replay recommendation is not the expected `NEEDS_REVISION` passthrough value, or if the derived cohort counts drift away from the prior no-trade audit.

## Probe findings

### Cohort size and frozen support envelope

- blocked exits from no-trade: `26`
- successful exits from no-trade: `14`
- successful-release categorical envelope:
  - `clarity_bucket = {high, mid}`
  - `confidence_bucket = {high, mid}`
  - `edge_bucket = {mid, strong}`
  - `transition_bucket = {stable}`
  - `zone = {low, mid}`
  - `target_policy = {RI_continuation_policy}`
- successful-release numeric envelope:
  - `ri_clarity_score: min = 27.0, median = 29.0, max = 34.0`
  - `conf_overall: min = 0.539023, median = 0.550034, max = 0.586643`
  - `action_edge: min = 0.078046, median = 0.100068, max = 0.173287`
  - `bars_since_regime_change: min = 32.0, median = 373.5, max = 606.0`

Interpretation:

- The frozen successful-release cohort is narrow and highly continuation-shaped: every successful exit goes to `RI_continuation_policy`, all releases are `stable`, and support is concentrated in mid/high clarity-confidence buckets with mid/strong edge.

### Blocked-exit overlap with the successful-release envelope

- categorical envelope matches: `18 / 26` (`0.692308`)
- numeric min/max envelope matches: `18 / 26` (`0.692308`)
- release-strength floor matches (at or above the successful medians for clarity, confidence, and edge): `13 / 26` (`0.5`)
- categorical and numeric simultaneous matches: `15 / 26` (`0.576923`)

Interpretation:

- A substantial share of blocked no-trade exits already resembles the frozen successful-release cohort on descriptive support alone.
- But the overlap is not universal: roughly one-third of blocked rows still fall outside the successful-release categorical or numeric support envelope.
- This keeps the evidence pointed at a bounded release-timing question rather than at a blanket claim that blocked exits should simply have been released.

### Main mismatch reasons among blocked exits

- `confidence_below_success_min = 7`
- `edge_below_success_min = 7`
- `clarity_below_success_min = 6`
- `clarity_bucket_outside_success_support = 5`
- `edge_bucket_outside_success_support = 5`
- `confidence_bucket_outside_success_support = 4`
- `zone_outside_success_support = 3`

Interpretation:

- The main reasons blocked exits fall outside the successful-release envelope are mild shortfalls in clarity, confidence, or edge rather than obviously foreign transition structure.
- That pattern is consistent with a release-timing or release-strength calibration question inside a continuation-shaped subset, not with a broad family-misclassification story.

## Roadmap implications

This slice does **not** change the replay recommendation. It tightens the roadmap one step further:

1. The next semantics-changing research question can now be framed more narrowly as a bounded no-trade release test over a continuation-shaped subset, not as a global router rewrite.
2. Because only `15 / 26` blocked exits satisfy both the categorical and numeric successful-release envelope simultaneously, any future revision should stay selective and fail-closed rather than assuming all blocked exits are equivalent.
3. The main probe value is evidence shaping: it identifies that a material subset of blocked exits already looks success-adjacent, while preserving the need for a separately packeted semantics revision before any routing logic is touched.

## Residual risks

- This is still observational replay analysis, not execution evidence.
- The envelope is derived from only `14` successful releases, so descriptive support remains sample-bounded.
- Envelope overlap is not a permission surface and must not be mistaken for a correctness proof.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

The release probe strengthens the existing bottleneck thesis without over-claiming it: many blocked no-trade exits already overlap the frozen successful-release support envelope, but not all of them do. That is exactly the sort of bounded, continuation-shaped evidence that justifies a future packeted semantics-revision test around no-trade release timing—without pretending the current replay has already earned that change.
