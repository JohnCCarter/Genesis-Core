# Workforce v1 wave 1 — Agent B — D1 2017-06 cloud dispatch

Date: 2026-05-07
Branch target: `feature/cloud/deepdive/d1-2017-06-corroborative`
Mode: `RESEARCH`
Worker class: `deep-dive`
Activation state: `secondary`
Status: `dispatch-ready / packet-first / bounded-prep only / non-authoritative`

## Authority fence

Agent B är en corroborative lane.
Den får inte imitera Agent A:s output class och får inte själv promotera findings till truth, readiness eller runtime-authority.

## Ownership tuple

- **Window:** `2017-06`
- **Question class:** `corroborative packet framing`
- **Output class:** `packet-first bounded prep`
- **Activation state:** `secondary`

## Dispatch pins

- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Question fingerprint:** `qfp_d1_2017_06_corroborative_packet_v1`
- **Change class:** `docs-only corroborative prep`

## Exact question

Should one exact `2017-06` low-zone suppression surface be opened later as a corroborative external subject, without duplicating Agent A's `2023-06` falsifier lane or widening into a second implementation lane prematurely?

## Source anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`

## Scope IN

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2017_06_corroborative_packet_2026-05-07.md`
- optional bounded planning appendix inside the same packet file

## Scope OUT

- all `2023-06` files owned by Agent A
- all `2023-04` files owned by Agent C
- `scripts/**`
- `tests/**`
- `results/evaluation/**`
- `docs/analysis/**`
- `src/**`
- `config/**`
- `GENESIS_WORKING_CONTRACT.md`
- March, July `2024`, late-2024, and annual-wide rescans

## Allowed inputs

- all source anchors listed above
- `workforce_roadmap.md`
- `docs/governance/worker_governance_envelope.md`

## Allowed outputs

- one packet only
- one bounded research plan embedded in that packet
- one recommended next step for control / integration lane

## Forbidden surfaces

- helper creation
- test creation
- analysis-note creation
- result JSON creation
- any reuse of Agent A's exact selector set as if it were this lane's output class
- shared truth writes
- backlog or roadmap promotion

## Done criteria

- one `2017-06` corroborative packet exists
- the packet makes its non-overlap with Agent A explicit
- the packet defines a later exact subject without widening beyond `2017-06`
- the packet states clearly what it does not prove

## Stop conditions

- the proposed packet begins to duplicate Agent A's implementation-ready lane
- the `2017-06` subject requires March or annual-wide search to stay meaningful
- the lane needs code, tests or artifacts to justify itself immediately
- the packet would imply runtime/default/promotion authority

## Escalation conditions

- the worker concludes that Agent A should be paused, superseded or replaced
- the packet cannot be made non-overlapping with Agent A
- the worker believes `2017-06` should become a primary implementation lane now
- any governance conflict or `base_sha` mismatch appears

## Required return format

- `status`
- `packet_path`
- `summary`
- `observed`
- `inferred`
- `unverified`
- `what_this_does_not_prove`
- `recommended_next_step`
- `recommended_integration_class`
- `base_sha_confirmed`
- `scope_adherence_report`

## What this brief does not authorize

Det här dispatch-kontraktet autoriserar inte implementation, helper/test-skrivning eller parallell deep-dive-exekvering på samma output class som Agent A.
