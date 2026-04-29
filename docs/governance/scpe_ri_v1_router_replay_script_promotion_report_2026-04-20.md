# SCPE RI V1 router replay script promotion report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
Skills used: `repo_clean_refactor`, `python_engineering`

This slice promotes the previously verified replay from ignored scratch space to `scripts/analyze/scpe_ri_v1_router_replay.py` and curates one commit-safe evidence artifact at `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_router_replay.py`
- `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- runtime integration
- backtest execution integration
- cross-family routing
- imports from `src/core/**`
- router/state/policy/veto threshold changes
- any recommendation value drift away from `NEEDS_REVISION`

## File-level change summary

- `docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
  - Added the bounded promotion contract for a tracked script path and a curated evaluation artifact.
- `scripts/analyze/scpe_ri_v1_router_replay.py`
  - Ported the verified replay implementation from ignored `tmp/` to a tracked canonical analysis path.
  - Kept router, stability, and veto behavior unchanged.
  - Adjusted containment watch surfaces from `tmp/` to `scripts/`.
  - Fixed Ruff-specific issues (`zip(..., strict=False)` and removed one unused local binding) without changing behavior.
- `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`
  - Added a commit-safe machine-readable evidence summary referencing the approved ignored replay outputs.
- `docs/governance/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
  - Added this implementation report.

## Exact gates run and outcomes

### Baseline capture

Scratch path used exactly as packeted:

- `C:/Users/fa06662/AppData/Local/Temp/genesis_scpe_ri_script_promotion_baseline_20260420/`

Baseline artifacts copied before the tracked replay run:

- `results/research/scpe_v1_ri/routing_trace.ndjson`
- `results/research/scpe_v1_ri/policy_trace.json`
- `results/research/scpe_v1_ri/replay_metrics.json`

### Commands executed

1. `pre-commit run --files docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md scripts/analyze/scpe_ri_v1_router_replay.py`
   - Result: `PASS`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_replay.py`
   - Result: `PASS` (tracked-script smoke run)
4. Explicit tmp-vs-tracked parity check on row-level routing fields plus recommendation identity
   - Result: `PASS`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_replay.py`
   - Result: `PASS` (tracked-script determinism rerun)
6. Approved replay-output hash comparison against the first tracked post-smoke hash baseline
   - Result: `PASS`
7. Replay-root containment check from final `results/research/scpe_v1_ri/manifest.json`
   - Result: `PASS` with `unexpected_events = []`
8. JSON validation for the curated evaluation artifact
   - Result: `PASS`

## Parity evidence

### Tmp-vs-tracked row parity

Parity passed for every replay row across these fields:

- `selected_policy`
- `switch_proposed`
- `switch_blocked`
- `final_routed_action`
- total `row_count`

Row-count remained:

- `146`

### Recommendation identity

Baseline recommendation copied from the ignored replay evidence:

- `NEEDS_REVISION`

Tracked-script replay recommendation:

- `NEEDS_REVISION`

Recommendation value was therefore identical, not merely equally severe.

### Preserved routing metrics

The tracked replay preserved:

- `proposed_switch_count = 78`
- `blocked_switch_count = 49`
- `actual_policy_change_count = 29`
- `actual_policy_change_rate = 0.2`

### Determinism and containment

Tracked-rerun identical-hash PASS covered exactly these eight replay artifacts:

- `results/research/scpe_v1_ri/input_manifest.json`
- `results/research/scpe_v1_ri/routing_trace.ndjson`
- `results/research/scpe_v1_ri/state_trace.json`
- `results/research/scpe_v1_ri/policy_trace.json`
- `results/research/scpe_v1_ri/veto_trace.json`
- `results/research/scpe_v1_ri/replay_metrics.json`
- `results/research/scpe_v1_ri/summary.md`
- `results/research/scpe_v1_ri/manifest.json`

Containment remained:

- replay-root only
- `verdict = PASS`
- `unexpected_events = []`

The curated artifact `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` is intentionally outside the replay-script containment allowlist and is validated separately as a commit-safe summary file.

`results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` is a summary-only, non-authoritative evidence artifact derived from unchanged replay outputs under `results/research/scpe_v1_ri/`; it contains no row-level trace and does not replace the research-root artifacts.

## Metadata-only drift allowed and observed

The tracked promotion intentionally changed only metadata tied to script provenance:

- `input_manifest.json` now records `scripts/analyze/scpe_ri_v1_router_replay.py` in `input_hashes` instead of the ignored `tmp` path.
- `manifest.json` now records the tracked script hash:
  - `scripts/analyze/scpe_ri_v1_router_replay.py = 6f9d93f26ab5544a51cd1546f68f405596ad82e5341dbe8c352eba049b462b06`

No row-level routing drift was observed.

## Final replay evidence snapshot

From the final replay outputs:

- `row_count = 146`
- `recommendation = NEEDS_REVISION`
- `recommendation_scope = observed_replay_quality_only`
- `observational_only = true`
- `proposed_switch_rate = 0.537931`
- `blocked_switch_rate = 0.337931`
- `actual_policy_change_rate = 0.2`
- `veto_rate = 0.438356`
- `no_trade_rate = 0.376712`
- `2024 profit_factor = 2.016598`
- `2025 profit_factor = 1.244162`

Final approved replay-output hashes:

- `results/research/scpe_v1_ri/input_manifest.json`: `1fb7bfe833091e8c3828a4a519297aef12e3a371d619e4602ec4dbad198429ec`
- `results/research/scpe_v1_ri/policy_trace.json`: `7003d539476726f5e4c77d0f0803e4f879e2fdefcfb6b897a317fe8bcf944337`
- `results/research/scpe_v1_ri/replay_metrics.json`: `f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60`
- `results/research/scpe_v1_ri/routing_trace.ndjson`: `d01ebc7457da902fcdcff93ea78eadf5036be464908a2b45c0cdb7bfb0f61da8`
- `results/research/scpe_v1_ri/state_trace.json`: `01164b57bfc88dcf0cc073b8183b9aeb5a2532426023cf99242db0aeedf52d6b`
- `results/research/scpe_v1_ri/summary.md`: `cefb2a57b0617fd009a8b555f657251c141cf6e65e468a839b640851d7fe7eee`
- `results/research/scpe_v1_ri/veto_trace.json`: `5006af4f816e924d25428404544290680aed2ea08db8b97908c0cd62025d49c7`

## Residual risks

- This is still a research-only replay lane and not runtime evidence.
- The defensive policy remains sparse (`3` rows), so policy distinctness is still not fully satisfying from a research perspective.
- Proposal pressure remains high relative to realized policy-change rate, which is an observation for future router work, not a fix in this slice.
- `docs/scpe_ri_v1_architecture.md` remains an unrelated untracked docs file outside this packet scope and should not be silently absorbed into this promotion commit.

## READY_FOR_REVIEW evidence completeness

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact gates and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_replay.py`
  - `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

This slice successfully promoted the verified replay to a tracked canonical script path and produced one commit-safe evidence artifact without changing routing behavior or recommendation value.
