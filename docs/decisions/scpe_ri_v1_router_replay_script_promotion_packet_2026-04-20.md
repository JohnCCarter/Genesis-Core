# SCPE RI V1 router replay script promotion packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded research-only promotion / tracked-script + curated-evidence / default unchanged`
Related packets:

- `docs/decisions/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`
- `docs/decisions/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`

Implementation report path: `docs/analysis/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
Baseline scratch path: `C:/Users/fa06662/AppData/Local/Temp/genesis_scpe_ri_script_promotion_baseline_20260420/`
Curated evaluation artifact path: `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded promotion of a previously verified research replay from ignored scratch space to a tracked analysis script, plus a curated machine-readable evidence artifact.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** promote the verified SCPE RI replay implementation to a tracked canonical script under `scripts/analyze/` and emit one curated, commit-safe evaluation summary under `results/evaluation/`, without changing routing logic, recommendation value, recommendation severity, or runtime surfaces.
- **Candidate:** `SCPE RI V1 router replay script promotion`
- **Base SHA:** `5fe2a94f`
- **Skill Usage:** `repo_clean_refactor`, `python_engineering`

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_replay.py`
  - `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `tmp/**`
  - existing governance packets and reports from prior SCPE slices
  - `results/research/**`
  - runtime integration
  - backtest execution integration
  - cross-family routing
  - any import from `src/core/**`
  - any router/state/policy/veto threshold change
  - any routing decision change
  - any recommendation upgrade to a more permissive state
  - any `.gitignore` relaxation for `tmp/` or `results/research/`
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_replay.py`
  - `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`
- **Max files touched:** `4`

## Intent and non-intent

This slice is a repo-placement and evidence-curation promotion only.
It exists because the verified replay script currently lives under ignored `tmp/`, which makes the research lane hard to reproduce from git alone.

This slice does:

1. create one tracked canonical analysis script path
2. preserve the verified replay behavior
3. curate one machine-readable evidence artifact under a results path explicitly allowed by repo policy

This slice does not:

- redesign the router
- re-open metric semantics
- promote runtime readiness
- widen the artifact surface under `results/research/`

## Allowed implementation work

The slice may do only the following:

1. copy or port the verified replay implementation from ignored `tmp/` to `scripts/analyze/scpe_ri_v1_router_replay.py`
2. adjust internal path handling only as needed for the new canonical script location
3. adjust containment watch surfaces only as needed to watch the tracked script location instead of the ignored scratch location
4. emit one curated JSON summary under `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json`
5. write one implementation report under the report path above

Allowed metadata-only drift:

- `input_manifest.json` may record the canonical tracked replay-script path under `scripts/analyze/scpe_ri_v1_router_replay.py` instead of the ignored `tmp/` path.
- `manifest.json` may differ only where required to reflect the canonical tracked script path, updated script content hash, or the new containment watch-surface path.

## Explicitly forbidden operations

- any change to routing decisions for any replay row
- any change to `_build_raw_router_decision(...)`
- any change to `_apply_stability_control(...)` that alters selected-policy outcomes
- any change to `_apply_veto(...)`
- any change to recommendation value from `NEEDS_REVISION` to any other value
- any direct tracking of ignored `results/research/scpe_v1_ri/*` artifacts
- any weakening of `.gitignore` policy for scratch or research output zones

## Required parity proof

A targeted tmp-vs-tracked-script parity proof is mandatory.

The proof must verify identical row-level values for at least:

- `selected_policy`
- `switch_proposed`
- `switch_blocked`
- `final_routed_action`
- total `row_count`

The proof must also verify that:

- recommendation value is identical to baseline (`NEEDS_REVISION`)
- `policy_trace.json` preserves:
  - `proposed_switch_count = 78`
  - `blocked_switch_count = 49`
  - `actual_policy_change_count = 29`
  - `actual_policy_change_rate = 0.2`
- containment for the replay run remains limited to the approved eight replay output files under `results/research/scpe_v1_ri/`
- the separate curated evaluation artifact at `results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` is produced only outside the replay-script containment surface and is validated separately as a commit-safe summary file

## Curated evaluation artifact contract

`results/evaluation/scpe_ri_v1_router_replay_2026-04-20.json` must be machine-readable and may contain only summary/evidence metadata, for example:

- branch / date / git commit
- canonical script path
- source packet/report references
- replay output root reference
- recommendation and scope flags
- key routing metrics
- per-year observational metrics summary
- parity verdict
- determinism verdict
- containment verdict
- approved output hashes copied from final `manifest.json`

It must not embed the full ignored research artifacts inline.
It is a curated handoff/evidence summary only.
It is not part of the eight-file replay-root containment allowlist.

## Gates required

1. `pre-commit run --files docs/decisions/scpe_ri_v1_router_replay_script_promotion_packet_2026-04-20.md scripts/analyze/scpe_ri_v1_router_replay.py`
2. `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
3. `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
4. capture baseline copies to the exact scratch path of:
   - `results/research/scpe_v1_ri/routing_trace.ndjson`
   - `results/research/scpe_v1_ri/policy_trace.json`
   - `results/research/scpe_v1_ri/replay_metrics.json`
5. first execution of `scripts/analyze/scpe_ri_v1_router_replay.py` as smoke run
6. explicit baseline-vs-rerun parity check on row-level routing fields and identical recommendation value
7. second identical execution of `scripts/analyze/scpe_ri_v1_router_replay.py` as determinism rerun
8. verify stable output hashes across identical reruns for all eight approved replay output files
9. verify containment remains limited to the approved replay output files only, excluding the separately created curated evaluation artifact
10. validate curated evaluation artifact JSON via repo checks

## Stop Conditions

- any routing parity mismatch
- any recommendation value drift away from `NEEDS_REVISION`
- any uncontrolled write outside the approved replay output files
- any need to touch `.gitignore` to make the slice work
- any nondeterministic output hash across identical reruns
- any need to widen scope beyond tracked script promotion and curated evidence summary

## Output required

- one promotion packet
- one tracked canonical analysis script
- one curated evaluation artifact under `results/evaluation/`
- one implementation report with parity, determinism, and containment evidence

## Bottom line

This packet authorizes one narrow next step only:

- promote the verified SCPE RI replay implementation from ignored scratch space to a tracked analysis-script path and curate one commit-safe evaluation artifact

It does not authorize runtime integration, routing redesign, or direct tracking of ignored research output files.
