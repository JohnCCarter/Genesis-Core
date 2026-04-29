# SCPE RI V1 router replay metric semantics revision packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded research-only revision / reporting semantics only / default unchanged`
Supersedes: none
Related packet: `docs/governance/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`

Implementation report path: `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
Baseline scratch path: `C:/Users/fa06662/AppData/Local/Temp/genesis_scpe_ri_metric_semantics_baseline_20260420/`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only correction of replay metric semantics and wording; routing decisions must remain identical.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** correct the semantic mismatch where replay reporting currently labels proposal pressure as oscillation, while proving row-level routing parity and keeping recommendation framing no more permissive than before.
- **Candidate:** `SCPE RI V1 router replay metric semantics revision`
- **Base SHA:** `ef16cf539b45`
- **Skill Usage:** `python_engineering`

### Scope

- **Scope IN:**
  - `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
  - `tmp/scpe_ri_v1_router_replay_20260420.py`
  - `results/research/scpe_v1_ri/input_manifest.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/state_trace.json`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/veto_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/summary.md`
  - `results/research/scpe_v1_ri/manifest.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - existing governance packets unrelated to this metric semantics revision
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing
  - any import from `src/core/**`
  - any router/state/policy/veto threshold change
  - any routing decision change
  - any use of realized outcome columns in router/state/policy/veto/stability logic
  - any recommendation change to a more permissive state based on renaming or metric reframing alone
- **Expected changed files:**
  - `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
  - `tmp/scpe_ri_v1_router_replay_20260420.py`
  - `results/research/scpe_v1_ri/input_manifest.json`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/summary.md`
  - `results/research/scpe_v1_ri/manifest.json`
- **Max files touched:** `11`

## Revision delta and audit intent

This slice does not broaden the prior replay surface.
It revises only how already-derived stability metrics are named, summarized, and guarded.

Required delta intent:

1. preserve routing decisions exactly as-is
2. preserve row count exactly as-is
3. expose proposal pressure separately from realized policy changes
4. make blocked-switch pressure visible rather than burying it inside a misnamed oscillation metric
5. keep recommendation equal or stricter in severity than the baseline artifact version

## Fixed baseline semantics to preserve

The current artifact baseline has already been verified with:

- `row_count = 146`
- `switch_proposed_count = 78`
- `switch_proposed_rate = 0.537931`
- `switch_blocked_count = 49`
- `actual_policy_change_count = 29`
- `actual_policy_change_rate = 0.2`
- `recommendation = NEEDS_REVISION`

The revision may change reporting labels and derived metric keys, but it must not alter the underlying routing trace semantics.

Severity ordering for recommendation guard:

- `APPROACH_PROMISING` = more permissive
- `NEEDS_REVISION` = baseline severity for this slice
- `NOT_READY` = stricter

Any revision outcome must keep recommendation at `NEEDS_REVISION` or tighten it to `NOT_READY`.

## Allowed implementation work

The script may do only the following beyond the previous packet:

1. derive explicit metric splits for:
   - `proposed_switch_count`
   - `proposed_switch_rate`
   - `blocked_switch_count`
   - `blocked_switch_rate`
   - `actual_policy_change_count`
   - `actual_policy_change_rate`
2. stop presenting proposal pressure as realized oscillation
3. update `summary.md`, `policy_trace.json`, `replay_metrics.json`, and `manifest.json` wording/fields so metric semantics are explicit
4. optionally tighten recommendation logic, but only if the resulting recommendation is unchanged or more conservative than baseline
5. regenerate `routing_trace.ndjson`, `state_trace.json`, and `veto_trace.json` only as part of the normal replay run, with content required to remain identical by parity or hash proof

## Explicitly forbidden operations

- any change to `_build_raw_router_decision(...)`
- any change to `_apply_stability_control(...)` that alters selected policy outcomes
- any change to `_apply_veto(...)`
- any change that alters `selected_policy`, `switch_proposed`, `switch_blocked`, `final_routed_action`, or total `row_count` for any replay row
- any change that upgrades recommendation severity from `NEEDS_REVISION` to `APPROACH_PROMISING` without a separate contract exception

## Required parity proof

A targeted baseline-vs-rerun parity proof is mandatory.

The proof must verify identical row-level values for at least:

- `selected_policy`
- `switch_proposed`
- `switch_blocked`
- `final_routed_action`
- total `row_count`

The proof must also verify that:

- recommendation severity is unchanged or stricter than baseline
- containment remains limited to the approved output files only

## Gates required

1. `pre-commit run --files docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_packet_2026-04-20.md tmp/scpe_ri_v1_router_replay_20260420.py`
2. `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
3. `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
4. capture baseline copies of:
   - `results/research/scpe_v1_ri/routing_trace.ndjson`
   - `results/research/scpe_v1_ri/replay_metrics.json`
   - `results/research/scpe_v1_ri/policy_trace.json`

- copy destination must be exactly `C:/Users/fa06662/AppData/Local/Temp/genesis_scpe_ri_metric_semantics_baseline_20260420/`

5. first execution of `tmp/scpe_ri_v1_router_replay_20260420.py` as smoke run
6. explicit baseline-vs-rerun parity check on row-level routing fields and recommendation severity
7. second identical execution of `tmp/scpe_ri_v1_router_replay_20260420.py` as determinism rerun
8. verify stable output hashes across identical reruns for all approved output files
9. verify containment remains limited to the approved output files only

## Stop Conditions

- any routing parity mismatch
- any recommendation upgrade to a more permissive state
- any uncontrolled write outside the approved output file list
- any nondeterministic output hash across identical reruns
- any need to widen scope beyond reporting semantics and explicit parity proof

## Output required

- one revision packet for metric semantics
- one implementation report at `docs/governance/scpe_ri_v1_router_replay_metric_semantics_revision_report_2026-04-20.md`
- one bounded isolated updated `tmp/` script
- one refreshed approved replay output root under `results/research/scpe_v1_ri/`
- parity evidence showing `routing_trace.ndjson`, `state_trace.json`, and `veto_trace.json` are unchanged by design at the content level even if regenerated during the replay run

## Bottom line

This packet authorizes one narrow next step only:

- correct replay metric semantics and wording while proving row-level routing parity and preserving conservative recommendation framing

It does not authorize runtime integration, router threshold changes, policy behavior changes, or any recommendation upgrade based on semantics alone.
