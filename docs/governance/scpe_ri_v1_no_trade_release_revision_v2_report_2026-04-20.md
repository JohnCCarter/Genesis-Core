# SCPE RI V1 no-trade release revision v2 report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: baseline runtime + canonical replay remain unchanged; behavior change candidate is confined to a research-only counterfactual analysis script
Packet: `docs/governance/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
Skills used: `python_engineering`

This slice adds a tighter counterfactual replay-only research surface on top of the unchanged SCPE RI V1 baseline. It does not modify runtime, it does not edit `scripts/analyze/scpe_ri_v1_router_replay.py`, it does not modify the canonical replay root `results/research/scpe_v1_ri/`, and it does not change the baseline replay recommendation `NEEDS_REVISION`.

This revision is non-authoritative and counterfactual only. It evaluates a stricter early-release exception for a frozen subset of baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` candidates using the release-probe artifact as a bounded evidence surface. It is not deployment approval, not policy authority, and not a runtime fix.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- `docs/scpe_ri_v1_architecture.md`
- `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
- runtime integration
- canonical replay regeneration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to prior audit/revision script logic
- edits to baseline replay recommendation semantics
- any threshold/config/runtime authority change outside the experimental script

## File-level change summary

- `docs/governance/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
  - Added the bounded closeout contract for the final v2 release-timing revision plus lane-level closeout.
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
  - Added a tracked counterfactual analysis script that binds to the frozen release-probe artifact by path/hash, applies a tighter non-propagating local override against frozen baseline route context, proves replay-root immutability, and writes one commit-safe JSON summary.
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`
  - Added a commit-safe revision artifact summarizing changed rows, containment proof, baseline vs revised metrics, and the counterfactual replay-quality assessment.
- `docs/governance/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
  - Added this implementation report.
- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`
  - Added the lane-level closeout synthesis that explicitly keeps runtime/integration work in a separate future governance lane.

## Revision method

- baseline inputs:
  - frozen Phase C entry rows
  - frozen baseline routing trace under `results/research/scpe_v1_ri/`
  - frozen baseline replay metrics and manifest
  - frozen release-probe artifact `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
- release-probe artifact binding:
  - path = `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - sha256 = `ec2691cea7b464f1c63f9d6ad5ee1eee81548b0f6b170c8ace26d1e864a94623`
- experimental v2 rule:
  - previous selected policy must be `RI_no_trade_policy`
  - raw target policy must be `RI_continuation_policy`
  - baseline blocker must be exactly `switch_blocked_by_min_dwell`
  - the row must remain inside frozen successful-release categorical support
  - the row must remain inside frozen numeric support
  - the row must also clear the frozen median-floor for `ri_clarity_score`, `conf_overall`, and `action_edge`
  - the row must be `zone = mid`
  - the row must satisfy `bars_since_regime_change >= 92.0`
- containment strategy:
  - evaluate candidate rows against frozen baseline route context only
  - do not propagate revised route state forward
  - require `changed_outside_allowed_count = 0`

## Counterfactual findings

### Tighter changed-row subset

- allowed candidate count: `7`
- changed row count: `7`
- changed outside allowed subset: `0`

Interpretation:

- The tighter fail-closed rule kept the release exception narrow and produced no hidden drift outside the allowed cohort.
- Compared with the first revision's `10` changed rows, this v2 rule removes the low-zone row and the freshest mid-zone stable rows while preserving a continuation-shaped mature subset.

### What the tighter override actually released

All `7` changed rows share the same pattern:

- baseline selected policy = `RI_no_trade_policy`
- baseline switch reason = `switch_blocked_by_min_dwell`
- revised selected policy = `RI_continuation_policy`
- revised final routed action = `LONG`
- transition bucket = `stable`
- zone = `mid`
- `bars_since_regime_change` range = `92.0` to `597.0`
- confidence bucket = `high`
- edge bucket = `strong`

Interpretation:

- The v2 rule is even more selective than the first revision: it keeps only mature stable mid-zone rows inside the successful-release support surface.
- This is a continuation-shaped, high-confidence, strong-edge subset rather than a mixed release cohort.

### Baseline vs revised routing impact

Baseline:

- `blocked_switch_count = 49`
- `actual_policy_change_count = 29`
- `actual_policy_change_rate = 0.2`
- `no_trade_rate = 0.376712`
- `RI_continuation_policy` selection count = `93`
- `RI_continuation_policy` trade count = `89`

Revised v2:

- `blocked_switch_count = 42`
- `actual_policy_change_count = 35`
- `actual_policy_change_rate = 0.241379`
- `no_trade_rate = 0.328767`
- `RI_continuation_policy` selection count = `100`
- `RI_continuation_policy` trade count = `96`

Delta:

- `blocked_switch_count_delta = -7`
- `actual_policy_change_count_delta = +6`
- `no_trade_rate_delta = -0.047945`
- `continuation_trade_count_delta = +7`

Interpretation:

- The tighter override still achieves the intended local effect: fewer blocked switches, lower no-trade share, and more continuation trades.
- Unlike the first revision, the v2 subset keeps `actual_policy_change_rate` inside the `<= 0.25` comfort ceiling used by this research lane.
- The churn trade-off is therefore improved, even though it is not eliminated.

### Counterfactual replay-quality assessment

- baseline replay recommendation passthrough: `NEEDS_REVISION`
- revised v2 counterfactual replay-quality assessment: `NEEDS_REVISION`
- main reason: even though `actual_policy_change_rate = 0.241379` stays inside the comfort ceiling, defensive routed support remains sparse (`RI_defensive_transition_policy` trade count = `2`)

Interpretation:

- The tighter release exception fixes the first revision's main churn problem, but it does not by itself convert the full replay-quality picture into `APPROACH_PROMISING`.
- This means the research lane has reached a bounded explanatory close rather than a promotion-ready green light.

## Roadmap implications

This slice still does **not** change runtime or canonical replay semantics. It closes the current bounded research question more cleanly:

1. A selective early-release exception is directionally plausible and can be narrowed enough to avoid breaching the replay-quality churn ceiling.
2. The no-trade / `min_dwell` bottleneck is therefore no longer a vague suspicion; it now has both an over-aggressive first revision and a tighter, better-behaved second revision on record.
3. Even so, the full replay root remains at `NEEDS_REVISION`, so this slice does **not** authorize runtime promotion or integration.
4. The remaining work is not another obvious micro-slice inside the current lane, but a separate decision about whether to open a future runtime/integration roadmap under new governance.

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged.
- The canonical replay root `results/research/scpe_v1_ri/` remained unchanged before and after both v2 revision runs.
- The baseline replay recommendation stays `NEEDS_REVISION` and is carried through as a passthrough reference only.
- The counterfactual script contains no imports from `src/core/**` or `scripts.analyze.scpe_ri_v1_router_replay`.
- The counterfactual override is non-propagating and local to the changed row.
- The changed-row set is a strict subset of the frozen baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` cohort, with `changed_outside_allowed_count = 0`.
- This report grants no runtime, backtest, config, deployment, or integration approval.

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
- Result: `PASS`

2. Explicit import-isolation proof on `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`

- Search pattern: `^(from|import)\s+core(\.|$)|src/core|scripts\.analyze\.scpe_ri_v1_router_replay`
- Result: `PASS` (`No matches found`)

3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`

- Result: `PASS` (`2 passed in 2.11s`)

4. Determinism gate + baseline replay-root immutability proof after formatter/lint settlement:

- reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
- `artifact_before = 1490daa4ed2f1eb74c8f0eae244e471d83e2a2cd5aea9a2f06e1a3aa1cfd70d3`
- `artifact_after = 1490daa4ed2f1eb74c8f0eae244e471d83e2a2cd5aea9a2f06e1a3aa1cfd70d3`
- `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
- `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
- `replay_metrics_before = f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60`
- `replay_metrics_after = f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60`
- `routing_trace_before = d01ebc7457da902fcdcff93ea78eadf5036be464908a2b45c0cdb7bfb0f61da8`
- `routing_trace_after = d01ebc7457da902fcdcff93ea78eadf5036be464908a2b45c0cdb7bfb0f61da8`
- Result: `PASS`

5. `pre-commit run --files docs/governance/scpe_ri_v1_research_closeout_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`

- Result: `PASS` (`black`, `ruff`, `detect-secrets`, EOF/whitespace, JSON, merge-conflict, and large-file checks all passed; YAML hook skipped because no YAML files were in scope`)

## Residual risks

- This remains counterfactual observational analysis, not execution evidence.
- The release-probe support envelope is still sample-bounded (`14` successful exits).
- Defensive-policy support remains sparse in the replay root, so the lane closes with bounded evidence rather than with promotion-ready confidence.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

The v2 revision shows that the no-trade release exception can be tightened enough to keep policy churn inside the lane's comfort ceiling while still releasing a meaningful subset of blocked continuation-shaped rows. That resolves the current research bottleneck more completely than the first revision did, but the replay root still remains `NEEDS_REVISION`, so the result is a clean research closeout, not runtime approval.
