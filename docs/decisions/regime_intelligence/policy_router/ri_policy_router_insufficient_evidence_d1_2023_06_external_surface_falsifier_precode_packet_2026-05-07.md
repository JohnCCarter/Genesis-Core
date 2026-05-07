# RI policy router insufficient-evidence D1 2023-06 external surface falsifier precode packet

Date: 2026-05-07
Branch: `feature/cloud/deepdive/d1-2023-06-falsifier`
Mode: `RESEARCH`
Status: `dispatch-ready / implementation-prepared / non-authoritative`
Change class: `helper-backed research-evidence slice`
Lane: `research-evidence`
Skill usage: `python_engineering`

## Authority fence

This precode packet is Agent A's implementation-prepared dispatch contract.
It is not new governance, not merge authority, and not shared-truth authority.

All worker outputs remain bounded evidence only.
They must not be promoted to repo truth, readiness, or runtime authority without
explicit control/integration review.

## Ownership tuple

- **Window:** `2023-06`
- **Question class:** `D1 external falsifier`
- **Output class:** `implementation-prepared deep-dive`
- **Activation state:** `primary`

## Dispatch pins

- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Question fingerprint:** `qfp_d1_2023_06_external_falsifier_v1`

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: branch `feature/next-slice-2026-05-06` maps to RESEARCH
- **Risk:** `LOW`
- **Required Path:** `approved non-trivial RESEARCH helper-backed evidence path`
- **Lane:** `research-evidence`
- **Objective:** materialize one exact `2023-06` low-zone `insufficient_evidence` external surface
  and transport the frozen D1 bank ceilings from the committed context-clean artifact onto that
  surface, reporting an honest `external_surface_survivor`, `external_surface_falsified`, or
  `source_data_unavailable` result without reopening March, July `2024`, late-2024, or any
  annual-wide search.
- **Candidate:** `frozen D1 bank ceilings on exact 2023-06 low-zone insufficient_evidence surface`
- **Opus pre-code verdict:** `not requested — cloud dispatch, governed by dispatch contract`

## Exact question

Can one exact `2023-06` low-zone `insufficient_evidence` external surface support a bounded D1
external falsifier slice without reopening March, July `2024`, late-2024, or any annual-wide search?

## Source anchors (cloud-visible on base branch)

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json` _(committed on base branch)_

## Frozen D1 bank ceilings (from admitted 2026-05-05 context-clean artifact)

These ceilings must remain unchanged. No threshold search. No new feature-family search.

| field | target_bank_ceiling | context_bank_min | descriptive_only |
| --- | --- | --- | --- |
| `action_edge` | `0.033803` | `0.042122` | `False` |
| `confidence_gate` | `0.516902` | `0.521061` | `False` |
| `clarity_raw` | `0.364914` | `0.369952` | `False` |
| `clarity_score` | `36.0` | `37.0` | `True` |

## Target surface definition

- **Symbol:** `tBTCUSD`
- **Timeframe:** `3h`
- **Month:** `2023-06`
- **Zone:** `low`
- **Target cohort:** `absent_action=LONG`, `enabled_action=NONE`, `switch_reason=insufficient_evidence`
- **Anti-target/context cohort:** all remaining June `2023` low-zone shared-shape rows:
  - `absent_action=LONG`, `enabled_action=NONE`, `switch_reason=AGED_WEAK_CONTINUATION_GUARD`
  - `absent_action=NONE`, `enabled_action=LONG`, `switch_reason=stable_continuation_state`

## Source data

The target surface rows come from:
`results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`

This file is `results/backtests/**` (git-ignored). It is not committed on the base branch.

**Cloud input rule:** if the source file is absent, the helper must fail closed with status
`source_data_unavailable`. No backfill, no inference, no rescue.

The markdown source anchors above are the cloud-visible evidence anchors. The raw artifact is
regenerate-on-demand.

## Allowed inputs

- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json` (committed on base branch)
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json` (regenerate-on-demand; absent in cloud context)

## Fail-closed contract

1. Bank ceilings loaded exclusively from the committed context-clean artifact.
2. Annual diff source loaded from the standard backtests path; missing file → `source_data_unavailable`.
3. Target and anti-target cohorts derived dynamically from June `2023` rows using the fixed
   family definition; no hardcoded timestamps.
4. `clarity_raw` is not present in annual diff `router_debug`; treat as `not_evaluable` for that
   field, no backfill or inferred rescue.
5. `clarity_score` remains descriptive-only; excluded from PASS/FAIL.
6. Transport rubric: admitted claim field passes iff all target rows have `field_value ≤ ceiling`
   AND no anti-target row is selected.

## Transport rubric

- Each admitted claim field (`action_edge`, `confidence_gate`) is evaluated independently.
- `clarity_raw` is always `not_evaluable` on this surface (not in annual diff router_debug).
- `clarity_score` is always `descriptive_only` per frozen D1 bank contract.
- `external_surface_survivor` iff at least one admitted claim field passes the full transport test.
- `external_surface_falsified` iff all admitted claim fields are either `transport_falsified` or
  `not_evaluable` (with at least one `transport_falsified`).
- `source_data_unavailable` iff the annual diff source cannot be loaded.

## Scope IN

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_precode_packet_2026-05-07.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_20260507.py`
- `tests/backtest/test_ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier.py`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_2026-05-07.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_2026-05-07.md`

## Scope OUT

- all `2017-06` corroborative files
- all `2023-04` fallback files
- `GENESIS_WORKING_CONTRACT.md`
- `workforce_roadmap.md`
- `docs/governance/**`
- `src/**`
- `config/**`
- March subjects as primary loop
- July `2024` as primary subject
- late-2024 as reopened transport loop
- annual-wide search beyond `2023-06`
- new threshold search
- new feature-family search

## Done criteria

- the exact `2023-06` target and anti-target/context surface is row-locked explicitly in the output
- the D1 bank ceilings remain frozen from the admitted 2026-05-05 context-clean artifact
- helper, targeted test, and analysis note exist only inside Scope IN
- deterministic rerun hash proof exists for the emitted JSON artifact
- output explicitly separates `observed`, `inferred`, and `unverified`
- the note states what the slice does **not** prove
- `clarity_raw` absence → `not_evaluable` with no backfill
- `clarity_score` → `descriptive_only` in all outputs

## Stop conditions

- the exact `2023-06` surface cannot be row-locked honestly
- required inputs are missing or non-evaluable
- the work begins to overlap Agent B or Agent C ownership tuples
- the slice requires March, July `2024`, late-2024, or annual-wide search to remain meaningful
- the output would imply runtime/default/promotion authority

## Escalation conditions

- the slice needs a wider corroborative control before any honest verdict exists
- the worker believes `2017-06` or `2023-04` should replace the current primary lane
- any governance conflict or `base_sha` mismatch appears

## What this packet does not authorize

This precode packet makes Agent A implementation-prepared, but not merge-independent.
It does not authorize shared-truth writes, runtime proposals, or backlog promotion.

The correct honest category after this slice remains:
- exact-bank supported (from prior synthesis)
- externally tested (pass or fail or source-unavailable)
- observational only
- non-authoritative
