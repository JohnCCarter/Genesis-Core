# SCPE RI V1 research closeout report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: baseline runtime + canonical replay remain unchanged; closeout remains synthesis-only and non-authoritative
Packet: `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
Skills used: `python_engineering`

This document closes the current bounded SCPE RI V1 research roadmap. It records research-only findings over frozen evidence artifacts and does not open, approve, authorize, or inherit any runtime/integration roadmap. It grants no runtime, backtest, config, deployment, or promotion approval.

Any future runtime or integration follow-up would require a new governance packet, fresh scope approval, and separate verification; none is approved here.

## Scope summary

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md`
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
- runtime integration
- backtest execution integration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to baseline replay recommendation semantics
- any inherited approval claim for a future runtime/integration lane

## What this research lane resolved

### Foundations are complete

The bounded RI-only research lane now has all of the foundational surfaces it set out to build:

- architecture packet for an RI-only, default-OFF, research-only router lane
- canonical tracked replay script under `scripts/analyze/scpe_ri_v1_router_replay.py`
- deterministic frozen replay root under `results/research/scpe_v1_ri/`
- clarified replay metric semantics that distinguish proposal pressure from realized policy churn
- diagnostics, defensive-scarcity, threshold-retention, min-dwell-retention, selected-defensive recency-pocket, no-trade release-probe, and two release-revision surfaces

Interpretation:

- The lane is not missing foundational observability or replay machinery anymore.
- What remained at the end was explanatory tightening, not missing architecture.

### The main replay bottleneck is localized

Across the diagnostics and no-trade slices, the lane consistently localized the most important bounded bottleneck to the interaction between:

- `RI_no_trade_policy`
- `switch_blocked_by_min_dwell`
- continuation-shaped rows that already look broadly release-compatible

Supporting evidence already on record includes:

- previous-no-trade rows are dominated by blocked persistence rather than successful release
- blocked exits from no-trade are mostly stable, mid/high-quality rows rather than noisy weak-state clutter
- `15 / 26` blocked exits overlap both the categorical and numeric successful-release envelope

Interpretation:

- The research problem ended up much narrower than “router generally bad”.
- It is specifically a bounded release-timing question on a continuation-shaped subset.

### Defensive scarcity is understood more clearly

The lane also resolved that defensive scarcity is not caused by lack of raw defensive states:

- raw defensive candidates = `30`
- observed selected defensive = `2`

The strongest observed compression paths are:

- retention in continuation via `confidence_below_threshold`
- retention in no-trade via `switch_blocked_by_min_dwell`

Interpretation:

- The lane no longer needs another explanatory slice merely to prove that raw defensive states exist.
- The selected-defensive comparator is also now bounded structurally: it appears only inside a tiny fresh-transition recency pocket (`1` to `5` bars since regime change), not as a broad stable score-tail.

## How the final revision changed the picture

### First revision vs tighter v2 revision

First revision:

- changed rows = `10`
- `actual_policy_change_rate = 0.268966`
- replay-quality assessment stayed `NEEDS_REVISION`
- result: informative, but too aggressive on churn

Tighter v2 revision:

- changed rows = `7`
- `actual_policy_change_rate = 0.241379`
- `blocked_switch_count_delta = -7`
- `no_trade_rate_delta = -0.047945`
- `continuation_trade_count_delta = +7`
- replay-quality assessment still `NEEDS_REVISION`

Interpretation:

- The lane now contains both sides of the no-trade release question:
  - an over-aggressive version that freed more rows but pushed churn too far
  - a tighter version that kept churn inside the lane's comfort ceiling while still freeing a meaningful subset
- That is enough to close the current bounded research question without pretending the replay is now promotion-ready.

## Final lane status

### Research-roadmap completion verdict

The current bounded SCPE RI V1 research roadmap is considered **complete** in the following sense:

- the planned research-only replay lane was successfully built
- its main bottlenecks were localized
- the main open no-trade release hypothesis was tested twice, once broadly and once more selectively
- the final tighter revision removed the most obvious remaining “one more small slice” pressure inside this same lane

### Replay-root status

The canonical replay root remains:

- `observational_only = true`
- `recommendation = NEEDS_REVISION`
- `recommendation_scope = observed_replay_quality_only`

Interpretation:

- The lane closes with bounded explanatory success, not with runtime readiness.
- Closing the research roadmap here means the explanatory lane is sufficiently complete, not that the system is approved for integration.

## What remains unresolved but bounded

These points remain unresolved, but they are no longer vague:

1. Defensive routed support is still sparse.
2. The replay root still does not clear the bar for `APPROACH_PROMISING`.
3. Any future attempt to carry the no-trade release insight into a runtime or integrated path would need a new decision about acceptable trade-offs, rather than more evidence from this same frozen replay lane.

Interpretation:

- Remaining uncertainty is now a governance and product-direction question, not a missing-observability question.

## Prerequisites for any future runtime/integration roadmap proposal

A future proposal to define a runtime/integration roadmap should treat the following as bounded prerequisites and decision inputs, not as inherited approval:

1. **New governance lane required**
   - a separate packet with fresh Scope IN/OUT and its own gates
2. **No inherited runtime approval**
   - this closeout grants no permission to wire the replay rule into runtime, backtest, config, or deployment surfaces
3. **Objective must be explicit**
   - any future lane must say whether it is:
     - shadow-only integration,
     - observational runtime instrumentation,
     - or an actual behavior-changing integration proposal
4. **Default behavior must remain unchanged unless separately authorized**
   - especially because the current lane closes under `RESEARCH` with the replay root still at `NEEDS_REVISION`
5. **Family boundary must stay explicit unless separately re-approved**
   - this lane is RI-only and does not authorize cross-family routing
6. **Parity and determinism requirements must be redefined for the new lane**
   - this closeout's artifact determinism proof does not substitute for runtime or integrated decision parity
7. **Trade-off decision must be made explicitly**
   - future work must state how it will handle the now-demonstrated tension between releasing blocked continuation-shaped rows and preserving broader replay-quality confidence

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged.
- The canonical replay root `results/research/scpe_v1_ri/` remains the baseline frozen evidence surface.
- This closeout does not change the replay-root recommendation value or semantics.
- This closeout does not authorize runtime, backtest, config, deployment, or integration work.

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
5. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`
   - Result: `PASS` (`black`, `ruff`, `detect-secrets`, EOF/whitespace, JSON, merge-conflict, and large-file checks all passed; YAML hook skipped because no YAML files were in scope`)

## Residual risks

- The replay root still remains `NEEDS_REVISION`.
- Defensive support remains sparse.
- A future runtime/integration roadmap could easily over-read the research evidence if it does not restate the scope boundaries from scratch.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

The current SCPE RI V1 research roadmap is complete enough to close as a bounded research lane. It successfully built the replay/evidence surface, localized the main bottlenecks, and tested the key no-trade release question with both an over-aggressive and a tighter revision. But it does **not** end in runtime approval: the canonical replay root still remains `NEEDS_REVISION`, and any runtime/integration roadmap would have to start as a brand-new governance lane with explicit prerequisites and fresh approval.
