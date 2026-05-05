# SCPE RI V1 router diagnostics report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
Skills used: `python_engineering`

This slice adds a summary-only, non-authoritative diagnostics surface on top of the already verified SCPE RI V1 replay outputs. It does not modify or regenerate the replay root and does not change any router logic, thresholds, or replay recommendation.

## Scope summary

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
- `results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- any runtime integration
- any backtest execution integration
- any cross-family routing
- any replay-router logic changes
- any threshold changes
- any change to the replay-root recommendation value or semantics

## File-level change summary

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
  - Added the bounded diagnostics contract for a summary-only, read-only research slice.
- `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
  - Added a tracked analysis script that reads the existing replay outputs, fails closed on schema drift, verifies that the replay root remains unchanged, and writes one summary-only diagnostics artifact.
- `results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`
  - Added a commit-safe diagnostics artifact summarizing policy support, switch blockers, no-trade decomposition, veto decomposition, and distinctness evidence.
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md`
  - Added this implementation report.

## Exact gates run and outcomes

### Commands executed

1. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_diagnostics.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`
   - Result: `PASS` (`No matches found`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
4. Determinism + replay-root immutability proof:

- `json_before = b2734027c880af4d19de81454a6b60e62fdaa5267fb01f79018fe7a9e6cbb92e`
- reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_diagnostics.py`
- `json_after = b2734027c880af4d19de81454a6b60e62fdaa5267fb01f79018fe7a9e6cbb92e`
- `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
- `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
- Result: `PASS`

5. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md scripts/analyze/scpe_ri_v1_router_diagnostics.py results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`

- Result: `PASS`

## Boundary proof

- The diagnostics artifact is observational-only, summary-only, and non-authoritative.
- It is derived from unchanged replay outputs under `results/research/scpe_v1_ri/`.
- It contains no row-level trace duplication and does not replace the replay-root artifacts.
- It must not be used to change router policy, router thresholds, or recommendation state.
- The script contains no imports from `src/core/**` and no runtime wiring.
- The script fails closed if required replay fields are missing, if unexpected top-level replay-input keys appear, or if the replay recommendation is not the expected `NEEDS_REVISION` passthrough value.

## Diagnostics findings

### Policy support

- `RI_continuation_policy`
  - `row_count = 93`
  - `row_share = 0.636986`
  - `trade_count = 89`
  - `non_pass_veto_rate = 0.129032`
- `RI_defensive_transition_policy`
  - `row_count = 3`
  - `row_share = 0.020548`
  - `trade_count = 2`
  - `non_pass_veto_rate = 0.666667`
- `RI_no_trade_policy`
  - `row_count = 50`
  - `row_share = 0.342466`
  - `trade_count = 0`
  - `non_pass_veto_rate = 1.0`

### Switch-block decomposition

- `proposed_switch_count = 78`
- `blocked_switch_count = 49`
- `actual_policy_change_count = 29`
- `blocked_share_of_proposed = 0.628205`
- `actual_change_share_of_proposed = 0.371795`

Blocked reason counts:

- `switch_blocked_by_min_dwell = 32`
- `confidence_below_threshold = 17`

Blocked previous-policy counts:

- `RI_no_trade_policy = 31`
- `RI_continuation_policy = 17`
- `RI_defensive_transition_policy = 1`

### No-trade source decomposition

- `router_selected_no_trade_rows = 50`
- `veto_forced_no_trade_on_non_no_trade_rows = 5`
- `total_final_no_trade_rows = 55`
- `router_selected_share_of_final_no_trade = 0.909091`
- `veto_forced_share_of_final_no_trade = 0.090909`

Forced no-trade on non-no-trade policies came from:

- `RI_continuation_policy = 4`
- `RI_defensive_transition_policy = 1`

### Distinctness evidence

The diagnostics surface shows that defensive rows are structurally different from continuation rows, but the sample is too small for a strong distinctness claim:

- defensive sample status: `sample_insufficient`
- defensive row count: `3`
- defensive trade count: `2`
- transition-heavy share:
  - `RI_defensive_transition_policy = 0.666667`
  - `RI_continuation_policy = 0.0`
- average metric delta (`defensive - continuation`):
  - `clarity_score = -1.612903`
  - `conf_overall = -0.011936`
  - `action_edge = -0.023873`
  - `bars_since_regime_change = -302.655914`

### Veto decomposition

- `non_pass_veto_rows = 64`
- `non_pass_veto_rate = 0.438356`

Veto action counts:

- `force_no_trade = 55`
- `reduce = 8`
- `cap = 1`
- `pass = 82`

Veto reason counts:

- `policy_no_trade = 50`
- `state_below_veto_floor = 5`
- `high_zone_continuation_cap = 8`
- `defensive_transition_cap = 1`
- `no_veto = 82`

Interpretation:

- The headline veto rate is inflated by explicit router-selected `RI_no_trade_policy` rows, not by downstream hidden rerouting.
- Downstream force-no-trade outside `RI_no_trade_policy` is present but bounded at `5` rows.
- The stronger near-term bottleneck is switch blockage by `min_dwell`, especially while sitting in `RI_no_trade_policy`.

## Roadmap implications

This diagnostics slice does **not** change the replay recommendation. It sharpens the roadmap instead:

1. The next research question should focus on the `RI_no_trade_policy` / `min_dwell` interaction rather than on generic veto dominance alone.
2. Defensive-policy distinctness is directionally visible but still under-evidenced because the routed sample is only `3` rows.
3. Any future revision slice should stay below runtime integration and treat these results as observational diagnostics, not causal performance proof.

## Residual risks

- Defensive-policy evidence remains too sparse for a strong distinctness claim.
- The diagnostics artifact is a summary layer, not a new authority surface.
- Any attempt to solve the distinctness problem by changing router logic would require a new packeted slice.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
  - `results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

This slice successfully turned the open replay questions into explicit diagnostics without changing the replay root. The evidence now points more specifically to sparse defensive support and `RI_no_trade_policy` / `min_dwell` blockage as the roadmap bottlenecks, while leaving the replay recommendation unchanged at `NEEDS_REVISION`.
