# Workforce v1 wave 1 — Agent C — D1 2023-04 cloud dispatch

Date: 2026-05-07
Branch target: `feature/cloud/deepdive/d1-2023-04-fallback`
Mode: `RESEARCH`
Worker class: `deep-dive`
Activation state: `dormant until activated`
Status: `dispatch-ready / packet-only / fallback / non-authoritative`

## Authority fence

Agent C är en fallback-lane.
Den får inte starta utan explicit aktivering från control plane och får inte producera code, artifacts eller truth claims.

## Ownership tuple

- **Window:** `2023-04`
- **Question class:** `fallback packet framing`
- **Output class:** `packet-only`
- **Activation state:** `dormant until activated`

## Dispatch pins

- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Question fingerprint:** `qfp_d1_2023_04_fallback_packet_v1`
- **Change class:** `docs-only fallback prep`

## Exact question

If the primary `2023-06` lane stalls, returns null, or loses integration priority, can `2023-04` serve as the smallest same-year fallback subject for a later bounded external packet without reopening wider annual search?

## Source anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`

## Activation rule

Agent C ska förbli dormant tills minst en av följande inträffar:

- Agent A returnerar `blocked`, `null` eller `fail-closed`
- integration plane begär en same-year fallback explicit
- Agent B inte längre är den bästa corroborative uppföljningen

## Scope IN

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_04_fallback_packet_2026-05-07.md`

## Scope OUT

- all `2023-06` files owned by Agent A
- all `2017-06` files owned by Agent B
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

Raw JSON- eller backtest-artefakter som bara nämns inuti source anchors är inte required cloud inputs om de inte finns på base branch.

## Allowed outputs

- one packet only
- one recommended activation note embedded in that packet

## Forbidden surfaces

- helper creation
- test creation
- analysis-note creation
- result JSON creation
- any attempt to activate itself automatically
- shared truth writes
- backlog or roadmap promotion

## Done criteria

- one dormant fallback packet exists
- the packet states exact activation conditions
- the packet states exact off-limits and what it does not prove
- the packet stays bounded to `2023-04`

## Stop conditions

- the packet needs another month or broader annual search to remain interesting
- the lane begins to overlap Agent A or Agent B ownership tuples
- the packet would imply runtime/default/promotion authority
- control plane has not explicitly activated the lane

## Escalation conditions

- the worker believes the fallback should replace an active lane immediately
- the packet cannot stay bounded to `2023-04`
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

Det här dispatch-kontraktet autoriserar inte implementation, codeproduktion eller självaktivering.
Det är en packet-only fallback-lane tills control plane uttryckligen säger annat.
