# SCPE RI V1 no-trade / min-dwell audit report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
Skills used: `python_engineering`

This slice adds a summary-only, observational-only, non-authoritative audit surface on top of the unchanged SCPE RI V1 replay outputs. It does not modify or regenerate the replay root and does not change router logic, thresholds, or recommendation state.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
- `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`

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

- `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
  - Added the bounded audit contract for the no-trade / min-dwell bottleneck.
- `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
  - Added a tracked audit script that reads frozen replay outputs, fails closed on schema drift, proves replay-root immutability, and writes one summary-only audit artifact.
- `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
  - Added a commit-safe audit artifact summarizing no-trade segment lengths, blocked exits from no-trade, successful releases, and descriptive state deltas.
- `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - Added this implementation report.

## Exact gates run and outcomes

### Commands executed

1. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`
   - Result: `PASS` (`No matches found`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
4. Determinism + replay-root immutability proof:
   - `json_before = d19c46550872eb52f214c6299bd1bfd0dc9528ea10540be652f49a21b15f0f9b`
   - reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
   - `json_after = d19c46550872eb52f214c6299bd1bfd0dc9528ea10540be652f49a21b15f0f9b`
   - `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - Result: `PASS`
5. `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`

- Result: `PASS`

## Boundary proof

- The audit artifact is observational-only, summary-only, and non-authoritative.
- It is derived from unchanged replay outputs under `results/research/scpe_v1_ri/`.
- It contains no row-level replay extract and does not replace the replay-root artifacts.
- It must not be used to change router policy, router thresholds, or recommendation state.
- The script contains no imports from `src/core/**` and no runtime wiring.
- The script fails closed if required replay fields are missing, if unexpected top-level replay-input keys appear, or if the replay recommendation is not the expected `NEEDS_REVISION` passthrough value.

## Audit findings

### No-trade segment structure

- no-trade segment count: `14`
- total no-trade rows across segments: `50`
- length stats:
  - `min = 3`
  - `median = 3`
  - `mean = 3.571429`
  - `max = 7`
- histogram:
  - `3 -> 9`
  - `4 -> 4`
  - `7 -> 1`

Interpretation:

- The minimum no-trade segment length is exactly `3`, which is consistent with the configured `min_dwell` pressure showing up in the replay rather than as a hypothetical concern.
- Most no-trade episodes are short and cluster at `3` rows, but they recur often enough to become a material routing bottleneck.

### Rows after previous no-trade

Among rows with `previous_policy = RI_no_trade_policy`:

- total previous-no-trade rows: `50`
- blocked exits from no-trade: `26` (`0.52` share)
- successful exits from no-trade: `14` (`0.28` share)
- quiet no-trade stays: `5` (`0.1` share)
- other previous-no-trade rows: `5`

Interpretation:

- Previous-no-trade rows are dominated by blocked persistence rather than successful release.
- The small residual `other` bucket means no-trade persistence is not exclusively a `min_dwell` story, but `min_dwell` is still the dominant observed blocker.

### Blocked exits from no-trade

Blocked-exit cohort definition in this slice:

- `previous_policy = RI_no_trade_policy`
- `selected_policy = RI_no_trade_policy`
- `switch_proposed = true`
- `switch_blocked = true`
- `switch_reason = switch_blocked_by_min_dwell`

Observed blocked-exit count:

- `26`

Blocked-exit state summary:

- `avg_clarity_score = 29.0`
- `avg_conf_overall = 0.550192`
- `avg_action_edge = 0.100385`
- `avg_bars_since_regime_change = 314.038462`
- transition buckets:
  - `stable = 26`
- confidence buckets:
  - `high = 15`
  - `mid = 7`
  - `low = 4`
- clarity buckets:
  - `high = 12`
  - `mid = 9`
  - `low = 5`

Interpretation:

- The blocked-exit cohort is not weak, noisy, transition-heavy clutter.
- It is mostly stable-state data with mid/high clarity and confidence, which strongly suggests that no-trade lock-in is being held open by stability controls rather than by obviously poor state quality.

### Successful exits from no-trade

Successful-exit cohort definition in this slice:

- `previous_policy = RI_no_trade_policy`
- `selected_policy != RI_no_trade_policy`

Observed successful-exit count:

- `14`

Successful-exit state summary:

- `avg_clarity_score = 29.428571`
- `avg_conf_overall = 0.553786`
- `avg_action_edge = 0.107572`
- `avg_bars_since_regime_change = 346.071429`
- target policy counts:
  - `RI_continuation_policy = 14`
- transition buckets:
  - `stable = 14`

Interpretation:

- Every successful release from no-trade in this replay goes to `RI_continuation_policy`.
- Successful releases are only modestly stronger than blocked exits on clarity/confidence/edge, not radically different.

### Blocked vs successful state delta

Blocked minus successful averages:

- `clarity_score = -0.428571`
- `conf_overall = -0.003594`
- `action_edge = -0.007187`
- `bars_since_regime_change = -32.032967`

Interpretation:

- The blocked and successful no-trade exit cohorts are directionally different, but only slightly.
- This is more consistent with a release-threshold / dwell-timing bottleneck than with a cleanly separable state-quality boundary.

### Quiet no-trade stays

Quiet no-trade stay count:

- `5`

Quiet-stay state summary:

- `avg_clarity_score = 23.6`
- `avg_conf_overall = 0.51307`
- `avg_action_edge = 0.02614`
- all five rows sit in:
  - `clarity_bucket = low`
  - `confidence_bucket = low`
  - `edge_bucket = weak`

Interpretation:

- Quiet persistence in no-trade looks like genuinely weak state.
- The more interesting problem is not these rows, but the `26` blocked no-trade exits whose state quality already looks broadly continuation-compatible.

## Roadmap implications

This slice does **not** change the replay recommendation. It sharpens the roadmap again:

1. The next bounded revision question is no longer “is no-trade too common?” but rather “why are broadly continuation-compatible no-trade exits still being held by dwell timing?”
2. The evidence suggests Genesis is closer to a no-trade release bottleneck than to a generic state-quality bottleneck for these rows.
3. Any future router-adjustment slice should be packeted explicitly as a semantics-changing research revision, because this audit now shows a concrete mechanism worth testing rather than a vague suspicion.

## Residual risks

- This is still observational replay analysis, not execution evidence.
- The audit does not prove that changing `min_dwell` would improve outcomes; it only localizes the bottleneck.
- The small `other_previous_no_trade_count = 5` tail means no-trade persistence is not purely one-dimensional.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
  - `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

This slice localizes the main replay bottleneck more tightly than the prior diagnostics pass: no-trade persistence is recurring, min-dwell-blocked exits are common, and many blocked exits already look broadly continuation-compatible. The roadmap is now pointing toward a packeted semantics-revision test around no-trade release timing, not toward generic veto cleanup or broad policy reclassification.
