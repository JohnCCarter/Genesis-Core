# SCPE RI V1 router replay metric semantics revision report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
Skill used: `python_engineering`

`metrics_semantics_version = scpe-ri-v1-metric-semantics-2026-04-20b` is a reporting-schema / metric-semantics revision only and is not a routing or policy-logic revision.

## Scope summary

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
- `tmp/scpe_ri_v1_router_replay_20260420.py`
- approved replay outputs under `results/research/scpe_v1_ri/`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- runtime integration
- backtest execution integration
- cross-family routing
- imports from `src/core/**`
- router/state/policy/veto threshold changes
- routing decision changes
- recommendation upgrades based on semantics relabeling alone

## File-level change summary

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
  - Added the bounded revision contract, explicit scratch path, recommendation severity ordering, and parity/hash proof requirements.
- `tmp/scpe_ri_v1_router_replay_20260420.py`
  - Split reporting semantics into proposal pressure, blocked-switch pressure, and actual realized policy-change metrics.
  - Preserved routing logic and veto logic unchanged.
  - Added `metrics_semantics_version = scpe-ri-v1-metric-semantics-2026-04-20b` to derived outputs.
- `results/research/scpe_v1_ri/input_manifest.json`
  - Refreshed to record the updated metric semantics version.
- `results/research/scpe_v1_ri/policy_trace.json`
  - Replaced ambiguous `switch_count` / `oscillation_rate` reporting with:
    - `proposed_switch_count`
    - `proposed_switch_rate`
    - `blocked_switch_count`
    - `blocked_switch_rate`
    - `actual_policy_change_count`
    - `actual_policy_change_rate`
- `results/research/scpe_v1_ri/replay_metrics.json`
  - Mirrored the new routing-metric semantics in the summary layer.
- `results/research/scpe_v1_ri/summary.md`
  - Updated wording so proposal pressure cannot be mistaken for realized oscillation.
- `results/research/scpe_v1_ri/manifest.json`
  - Refreshed with the updated metric semantics version and final approved output hashes.
- `results/research/scpe_v1_ri/routing_trace.ndjson`
- `results/research/scpe_v1_ri/state_trace.json`
- `results/research/scpe_v1_ri/veto_trace.json`
  - Regenerated as part of the replay run; verified unchanged by parity or stable value checks.

## Exact gates run and outcomes

### Baseline capture

Scratch path used exactly as packeted:

- `C:/Users/fa06662/AppData/Local/Temp/genesis_scpe_ri_metric_semantics_baseline_20260420/`

Baseline artifact hashes captured before the revision replay:

- `routing_trace.ndjson`: `D01EBC7457DA902FCDCFF93EA78EADF5036BE464908A2B45C0CDB7BFB0F61DA8`
- `replay_metrics.json`: `5DB475ADDE63080B48643138600C33655B031482BE12265D3949152B2954F48E`
- `policy_trace.json`: `77E6F3F89EEAE449CFBE196153FEA74F1EB1AA54EF9E7E04959A655D42BDD085`

### Commands executed

1. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md tmp/scpe_ri_v1_router_replay_20260420.py`
   - Result: `PASS`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/scpe_ri_v1_router_replay_20260420.py`
   - Result: `PASS` (smoke run)
4. Explicit baseline-vs-rerun parity check on row-level routing fields and recommendation severity
   - Result: `PASS`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/scpe_ri_v1_router_replay_20260420.py`
   - Result: `PASS` (determinism rerun)
6. Approved output hash comparison against the first post-smoke hash baseline
   - Result: `PASS`
7. Containment check from final `manifest.json`
   - Result: `PASS` with `unexpected_events = []`

The identical-rerun hash PASS covered exactly these eight approved artifact paths:

- `results/research/scpe_v1_ri/input_manifest.json`
- `results/research/scpe_v1_ri/routing_trace.ndjson`
- `results/research/scpe_v1_ri/state_trace.json`
- `results/research/scpe_v1_ri/policy_trace.json`
- `results/research/scpe_v1_ri/veto_trace.json`
- `results/research/scpe_v1_ri/replay_metrics.json`
- `results/research/scpe_v1_ri/summary.md`
- `results/research/scpe_v1_ri/manifest.json`

## Parity evidence

### Row-level routing parity

Baseline vs rerun parity passed for every replay row across these fields:

- `selected_policy`
- `switch_proposed`
- `switch_blocked`
- `final_routed_action`
- total `row_count`

Row-count remained:

- `146`

### Recommendation guard

Baseline recommendation:

- `NEEDS_REVISION`

Final recommendation:

- `NEEDS_REVISION`

Severity was therefore unchanged and not more permissive.

### Stable unchanged-by-design surfaces

Verified unchanged or value-equivalent after rerun:

- `routing_trace.ndjson`
- `state_trace.json`
- `veto_trace.json`

Observed stable values:

- `actual_policy_change_count = 29`
- `actual_policy_change_rate = 0.2`
- `proposed_switch_count = 78`
- `proposed_switch_rate = 0.537931`
- `blocked_switch_count = 49`
- `blocked_switch_rate = 0.337931`
- `state_trace.counts_by_year` matched baseline expectations
- `veto_trace.action_counts` matched baseline expectations
- `veto_trace.reason_counts` matched baseline expectations

## Final artifact state

### Policy semantics now exposed explicitly

From `results/research/scpe_v1_ri/policy_trace.json`:

- `proposed_switch_count = 78`
- `proposed_switch_rate = 0.537931`
- `blocked_switch_count = 49`
- `blocked_switch_rate = 0.337931`
- `actual_policy_change_count = 29`
- `actual_policy_change_rate = 0.2`

Interpretation:

- `0.537931` is proposal pressure, not realized oscillation.
- Actual realized policy change rate is `0.2`.

### Observational replay posture remains unchanged

From `results/research/scpe_v1_ri/replay_metrics.json`:

- `row_count = 146`
- `veto_rate = 0.438356`
- `no_trade_rate = 0.376712`
- `recommendation = NEEDS_REVISION`
- `recommendation_scope = observed_replay_quality_only`
- `observational_only = true`

Per-year observational outcomes remain:

- `2024 profit_factor = 2.016598`
- `2025 profit_factor = 1.244162`

### Final manifest evidence

From `results/research/scpe_v1_ri/manifest.json`:

- `containment.verdict = PASS`
- `containment.unexpected_events = []`
- `metrics_semantics_version = scpe-ri-v1-metric-semantics-2026-04-20b`

Final approved output hashes:

- `input_manifest.json`: `00f4d28481b07bd882e87042179d9ad0737b6c0bb868b585cb49a9fc99778c2e`
- `policy_trace.json`: `7003d539476726f5e4c77d0f0803e4f879e2fdefcfb6b897a317fe8bcf944337`
- `replay_metrics.json`: `f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60`
- `routing_trace.ndjson`: `d01ebc7457da902fcdcff93ea78eadf5036be464908a2b45c0cdb7bfb0f61da8`
- `state_trace.json`: `01164b57bfc88dcf0cc073b8183b9aeb5a2532426023cf99242db0aeedf52d6b`
- `summary.md`: `cefb2a57b0617fd009a8b555f657251c141cf6e65e468a839b640851d7fe7eee`
- `veto_trace.json`: `5006af4f816e924d25428404544290680aed2ea08db8b97908c0cd62025d49c7`

## Residual risks

- This remains a reporting-semantics fix on a research-only replay surface, not runtime evidence.
- The defensive policy is still sparsely selected (`3` rows), so policy distinctness remains a live research question.
- High proposal pressure (`78`) versus lower realized policy changes (`29`) suggests meaningful router friction, but that friction has not yet been redesigned in this slice.
- Any future attempt to turn these observations into router tuning would require a new contract, fresh governance review, and separate parity expectations.

## READY_FOR_REVIEW evidence completeness

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact gates and outcomes: captured above
- Artifact selectors and evidence paths:
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
  - `tmp/scpe_ri_v1_router_replay_20260420.py`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/summary.md`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

This revision corrected the replay metric semantics without changing routing behavior.

The key correction is simple but important:

- previous `oscillation_rate = 0.537931` was actually proposal pressure
- actual realized policy-change rate is `0.2`

Routing decisions, recommendation severity, containment, and deterministic reruns all remained within the approved research-only boundary.
