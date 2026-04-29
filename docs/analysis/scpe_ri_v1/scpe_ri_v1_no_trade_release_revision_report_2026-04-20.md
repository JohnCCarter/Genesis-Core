# SCPE RI V1 no-trade release revision report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: baseline runtime + canonical replay remain unchanged; behavior change candidate is confined to a research-only counterfactual analysis script
Packet: `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md`
Skills used: `python_engineering`

This slice adds a counterfactual replay-only research surface on top of the unchanged SCPE RI V1 baseline. It does not modify runtime, it does not edit `scripts/analyze/scpe_ri_v1_router_replay.py`, it does not modify the canonical replay root `results/research/scpe_v1_ri/`, and it does not change the baseline replay recommendation `NEEDS_REVISION`.

This revision is non-authoritative and counterfactual only. It evaluates a selective early-release exception for a frozen subset of baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` candidates using the release-probe artifact as a bounded evidence surface. It is not deployment approval, not policy authority, and not a runtime fix.

This slice is a research-only counterfactual replay probe. The early-release override is row-local, non-propagating, and does not modify runtime logic, canonical replay logic, or release recommendations; it is not a production proposal.

## Scope summary

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`

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
- edits to baseline replay recommendation semantics
- any threshold/config authority change outside the experimental script

## File-level change summary

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md`
  - Added the bounded contract for a selective no-trade release-timing counterfactual and tightened it with explicit subset-containment rules.
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
  - Added a tracked counterfactual analysis script that binds to the frozen release-probe artifact by path/hash, evaluates a non-propagating local override against frozen baseline route context, proves baseline replay-root immutability, and writes one commit-safe JSON summary.
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
  - Added a commit-safe revision artifact summarizing changed rows, containment proof, baseline vs revised metrics, and the counterfactual replay-quality assessment.
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md`
  - Added this implementation report.

## Revision method

- baseline inputs:
  - frozen Phase C entry rows
  - frozen baseline routing trace under `results/research/scpe_v1_ri/`
  - frozen baseline replay metrics and manifest
  - frozen release-probe artifact `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
- release-probe artifact binding:
  - path = `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - sha256 = `ec2691cea7b464f1c63f9d6ad5ee1eee81548b0f6b170c8ace26d1e864a94623`
- experimental rule:
  - previous selected policy must be `RI_no_trade_policy`
  - raw target policy must be `RI_continuation_policy`
  - baseline blocker must be exactly `switch_blocked_by_min_dwell`
  - the row must remain inside frozen successful-release categorical support
  - the row must remain inside frozen numeric support
  - the row must also clear the frozen median-floor for `ri_clarity_score`, `conf_overall`, and `action_edge`
- containment strategy:
  - evaluate candidate rows against frozen baseline route context only
  - do not propagate revised route state forward
  - require `changed_outside_allowed_count = 0`

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`
   - Result: `PASS` (`No matches found`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
4. Determinism + baseline replay-root immutability proof:
   - reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
   - `json_before = 6423bc2811a0ec7ee137acd5088b2602ea70440c4255cccced4e1024c12c9afe`
   - `json_after = 6423bc2811a0ec7ee137acd5088b2602ea70440c4255cccced4e1024c12c9afe`
   - `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
   - Result: `PASS`
5. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_revision.py results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`

- Result: `PASS`

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged.
- The canonical replay root `results/research/scpe_v1_ri/` remained unchanged before and after both revision runs.
- The baseline replay recommendation stays `NEEDS_REVISION` and is carried through as a passthrough reference only.
- The counterfactual script contains no imports from `src/core/**`.
- The counterfactual override is non-propagating and local to the changed row.
- The changed-row set is a strict subset of the frozen baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` cohort, with `changed_outside_allowed_count = 0`.
- Containment is exact: `allowed_candidate_count == changed_row_count == 10` and `changed_outside_allowed_count == 0`, so every revised row is an allowed baseline-blocked candidate and no disallowed row was changed.

## Counterfactual findings

### Selective changed-row subset

- allowed candidate count: `10`
- changed row count: `10`
- changed outside allowed subset: `0`

Interpretation:

- The fail-closed rule did exactly what it was supposed to do: it changed only a narrow frozen subset and produced no hidden drift outside that cohort.

### What the selective override actually released

All `10` changed rows share the same pattern:

- baseline selected policy = `RI_no_trade_policy`
- baseline switch reason = `switch_blocked_by_min_dwell`
- revised selected policy = `RI_continuation_policy`
- revised final routed action = `LONG`
- transition bucket = `stable`
- zone = `low` or `mid`
- clarity/confidence/edge all sit in the successful-release support and clear the median-floor

Interpretation:

- The revision did not open a fuzzy or mixed-quality cohort.
- It released a continuation-shaped subset with consistently strong state quality and stable transition context.

### Baseline vs revised routing impact

Baseline:

- `blocked_switch_count = 49`
- `actual_policy_change_count = 29`
- `no_trade_rate = 0.376712`
- `RI_continuation_policy` selection count = `93`

Revised:

- `blocked_switch_count = 39`
- `actual_policy_change_count = 39`
- `no_trade_rate = 0.308219`
- `RI_continuation_policy` selection count = `103`

Delta:

- `blocked_switch_count_delta = -10`
- `actual_policy_change_count_delta = +10`
- `no_trade_rate_delta = -0.068493`
- `continuation_trade_count_delta = +10`

Interpretation:

- The selective override achieved the intended local effect: fewer blocked switches, lower no-trade share, and more continuation trades.
- But the cost is immediate in the same metric family: actual policy changes rise from `29` to `39`, pushing the counterfactual change-rate above the baseline comfort zone.

### Counterfactual replay-quality assessment

- baseline replay recommendation passthrough: `NEEDS_REVISION`
- revised counterfactual replay-quality assessment: `NEEDS_REVISION`
- reason: the revised `actual_policy_change_rate = 0.268966`, which exceeds the `<= 0.25` threshold used by the replay-quality assessment logic

Interpretation:

- The selective release exception helps local release timing, but it does not yet clear the broader replay-quality bar.
- In other words: this is evidence for a narrower follow-up revision, not evidence that the no-trade issue is solved.

## Roadmap implications

This slice still does **not** change runtime or canonical replay semantics. It sharpens the roadmap again:

1. A selective early-release exception is directionally plausible: the bounded subset improves continuation participation and reduces no-trade share.
2. The first revision is still too aggressive for replay-quality comfort because it increases actual policy churn too much, even without any containment leak.
3. The next research question is therefore narrower than before: how to preserve most of these `10` releases while shaving back the added switch churn.
4. The likely next bounded axis is not “release more rows”, but “release fewer rows even more selectively” — for example by tightening the zone/strength floor or gating on a stricter slice of the successful-release support.

## Residual risks

- This remains counterfactual observational analysis, not execution evidence.
- The release-probe support envelope is sample-bounded (`14` successful exits).
- Because the override is intentionally non-propagating, this slice measures local release pressure rather than a full recursive alternate replay path.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

The first semantics-changing research revision is informative but not merge-convincing: a strict, continuation-shaped local early-release rule cleanly frees `10` blocked no-trade rows and lowers no-trade share, but it also increases policy churn enough that the counterfactual replay-quality assessment stays at `NEEDS_REVISION`. That means the roadmap is still moving in the right direction, but the next step should be a tighter second revision slice rather than a jump toward runtime integration.
