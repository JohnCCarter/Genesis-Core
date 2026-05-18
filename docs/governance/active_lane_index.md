# Active lane index

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `current-state reference index / complementary / no new authority`

> Use this page as a short pointer only.
>
> - `GENESIS_WORKING_CONTRACT.md` remains the current drift anchor.
> - The cited packets, synthesis notes, and closeouts remain the actual lane anchors.
> - This index is meant to reduce reread overhead and evidence-to-authority drift, not to replace the underlying documents.

## What this file does not do

This file does **not**:

- override `docs/governance_mode.md`
- replace `.github/copilot-instructions.md`, `docs/OPUS_46_GOVERNANCE.md`, `AGENTS.md`, or `GENESIS_WORKING_CONTRACT.md`
- authorize code/config/test/runtime/paper/promote/champion work
- turn historical notes into live instructions by convenience

## Current mode

- `RESEARCH` — source: branch mapping for `feature/editor-worker-orchestrator`

## Current active lane

Treat the live repo-wide lane as the bounded **RI policy-router** line summarized in `GENESIS_WORKING_CONTRACT.md`.

Current direction lock and active carrier anchors:

- direction lock: `docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
- bounded runtime carrier anchor: `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md`

Current evidence-reading anchors to cite before making claims:

- exact top-line triad synthesis: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`
- D1 bank-state synthesis: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md`
- mixed-year annual comparison line: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`

Operational shorthand:

- the current lane is still research/evidence-first
- some bounded runtime slices already exist historically on this branch context, but new work does **not** inherit runtime/default/promotion authority from them by implication
- exact-surface findings remain bounded unless a fresh packet explicitly opens a new question

## Parked or closed lanes

Treat the following as non-active unless a fresh task reopens them explicitly:

- earlier `3h` historical validation lane from prior working-anchor state
- aged-weak second-hit and aged-weak-plus-stability lines (`closed negative / reverted`)
- July-2024 transport line after late-2024 and `2022-06` falsification (`parked` rather than portable authority)
- SCPE RI runtime/integration roadmap and seam-inventory docs (`historical future-only`, not active execution guidance)

Key parked/closed references:

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_active_carrier_truth_parked_handoff_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_translation_parking_synthesis_2026-05-04.md`
- `docs/analysis/scpe_ri_v1/archive/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`

## Not active by default

Unless the user explicitly reopens them with the required authority, do **not** treat these as active:

- inherited runtime/integration authority from RI research docs
- runtime-default changes
- paper-shadow follow-up fixes
- promotion/champion claims from isolated research evidence

## Forbidden inheritance boundaries

Do **not** infer any of the following from the existence of an analysis note, synthesis note, or historical packet alone:

- runtime authority
- default-path authority
- promotion or readiness authority
- champion authority
- paper/live execution authority
- Legacy identity from RI-labelled evidence surfaces

Practical reading rule:

- if a note says `observational only`, `historical`, `parked`, `planning-only`, or `non-authoritative`, keep it in that bucket until a later packet explicitly changes the status

## Quick use ritual

1. confirm branch and mode
2. read `GENESIS_WORKING_CONTRACT.md`
3. use this page to identify current versus parked anchors
4. cite the exact anchor docs in any new packet, note, or report
5. if the intended next step touches high-sensitivity, runtime-default, paper/live, or champion surfaces, stop and open the appropriate stricter path instead of relying on this index

## Update rule

Update this page only when one of these changes:

- active lane anchor
- parked/non-active lane status
- explicit forbidden-inheritance boundary wording
- the smallest pointer set needed to identify the live lane correctly
