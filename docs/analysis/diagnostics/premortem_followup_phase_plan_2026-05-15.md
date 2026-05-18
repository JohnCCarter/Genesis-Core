# Premortem follow-up phase plan

Date: 2026-05-15
Originating branch: `feature/editor-worker-orchestrator`
Status: `historical planning artifact / non-executable / no runtime authority`

> 2026-05-18 note (`feature/evidence-closeout-pilot`): This document is retained as the original docs-first framing artifact from the earlier `feature/editor-worker-orchestrator` context. The bounded candidate set selected by this plan has now been completed, and this file should not be read as a branch-current work selector or new authority surface.

> Current status note:
>
> - This plan translates `artifacts/diagnostics/genesis_core_premortem_2026-05-15.md` into a small sequence of bounded follow-up slices.
> - It does **not** authorize `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, `artifacts/**`, paper/live, promotion, champion, or runtime-default changes.
> - Later sensitive phases still require their own commit contract, packet, and stricter review where applicable.

> Later progress note:
>
> - Phases 1-3 in this plan have since been landed as docs/governance surfaces.
> - The phase-4 `decision_gates.py` finite-numeric candidate has since been implemented in a separate bounded runtime slice limited to `src/core/strategy/decision_gates.py` and `tests/utils/test_decision.py`.
> - The phase-4 EVGate non-finite hardening candidate has since been implemented in a separate bounded runtime slice limited to `src/core/strategy/components/ev_gate.py` and `tests/core/strategy/components/test_ev_gate_integration.py`.
> - The phase-4 config-authority API-alignment candidate has since been implemented in a separate bounded slice limited to `src/core/api/config.py`, `tests/integration/test_config_endpoints.py`, and `tests/integration/test_config_api_e2e.py`.
> - The phase-4 reproducibility closeout candidate has since been implemented in a separate bounded evidence slice limited to `scripts/analyze/execution_proxy_evidence.py` and `tests/backtest/test_execution_proxy_evidence.py`.
> - The bounded candidate set selected by this plan has now been completed; any further premortem follow-up should be opened as new slices rather than treated as unfinished work from this phase plan.
> - That later implementation slice was separately reviewed and verified; this planning note remains the original docs-first framing artifact and does not retroactively become runtime authority.

## COMMAND PACKET (planning-only)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice adds planning and governance-reference docs only; the main risk is wording drift that could be mistaken for new authority or unnecessary STRICT friction
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the task is to sequence follow-up work and start the smallest low-friction documentation surfaces before any runtime-adjacent or config-adjacent slice is opened
- **Objective:** convert the premortem into a phased implementation plan that reduces evidence drift and reproducibility gaps without imposing STRICT-style process on ordinary `RESEARCH` slices
- **Base SHA:** `66f97acc`

### Scope

- **Scope IN:** one docs-only phase plan; one current-state active-lane index; one claim-bearing evidence header template; one governance README refresh pointing to the new files
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all runnable commands/selectors; all runtime/config-authority/default changes; all paper/live, readiness, promotion, or champion claims; all claims that any later phase is already approved for implementation
- **Expected changed files:**
  - `docs/analysis/diagnostics/premortem_followup_phase_plan_2026-05-15.md`
  - `docs/governance/active_lane_index.md`
  - `docs/governance/templates/evidence_claim_header.md`
  - `docs/governance/README.md`
- **Max files touched:** `4`

### Stop Conditions

- any wording that treats this plan as implementation authority
- any wording that makes the active-lane index or claim-header template a new SSOT
- any wording that implies all `RESEARCH` work should now carry STRICT-style packets or gates
- any widening into `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**`
- any wording that treats future phases as already approved rather than separately admissible questions

## Purpose

This plan answers one narrow question only:

- what is the cheapest phased follow-up that operationalizes the premortem without making routine research work slow?

## Operating principle

The premortem should be implemented as **mis-sized-governance prevention**, not as a universal process tax.

That means:

- high-risk boundaries should become easier to see and harder to cross by accident
- claim-bearing evidence should become easier to reproduce and harder to overstate
- ordinary `RESEARCH` slices should remain light unless they actually approach high-sensitivity surfaces

## Phase 1 — Boundary visibility surfaces

Goal:

- reduce evidence-to-authority drift and reproducibility slippage with the smallest docs-only surfaces first

Deliverables:

- `docs/governance/active_lane_index.md`
- `docs/governance/templates/evidence_claim_header.md`
- `docs/governance/README.md` refresh so the new surfaces are discoverable

Why this phase comes first:

- it attacks the two highest-leverage premortem risks (`evidence-to-authority drift` and weak claim provenance)
- it creates almost no runtime or research friction
- it improves later packets, notes, and evidence summaries without changing behavior

Started in this slice:

- yes

Success criteria:

- a worker can identify the current active lane and parked lanes without rereading the entire working contract
- a claim-bearing note has a copyable provenance/authority header
- neither surface claims new authority or adds mandatory gates to ordinary scratch research

## Phase 2 — Runtime-config live-update matrix

Goal:

- make the boundary between schema-valid, propose-allowed, and intentionally blocked runtime fields explicit

Planned output:

- one docs-only matrix or reference note that maps runtime-config fields across:
  - schema support
  - propose/update allowance
  - intended live-updatability stance
  - explicit blocked surfaces

Current phase-2 reference created in this slice:

- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`

Current phase-2 clarification surfaces created in this slice:

- `README.md`
- `config/README.md`
- `docs/architecture/ARCHITECTURE.md`

Why this is phase 2 instead of phase 1:

- it needs a closer read of `schema.py`, `authority.py`, and API/runtime docs
- it is still docs-first, but it is nearer a real behavior/ops boundary and should not be rushed into the first kickoff slice

Started in this slice:

- yes

## Phase 3 — Claim-bearing evidence adoption boundary

Goal:

- define how the claim-header template is adopted for actual evidence notes without turning every exploratory note into a heavyweight ritual

Planned output:

- one bounded adoption note or runbook that says when the header is expected and when a lighter scratch note is still acceptable
- optional clean-checkout replay expectation for artifacts that influence decisions, packets, or candidate promotion arguments

Current phase-3 runbook created in this slice:

- `docs/governance/runbooks/evidence_claim_adoption.md`

Important boundary:

- this phase should stay trigger-based (`claim-bearing`, `decision-influencing`, `promotion-adjacent`) rather than universal for all docs

Started in this slice:

- yes

## Phase 4 — Sensitive hardening candidates

Goal:

- address the premortem items that are real but live near high-sensitivity code and config surfaces

Examples for later separate packets:

- strategy numeric coercion hardening around probabilities / thresholds
- config-authority alignment where schema support and live proposal surfaces disagree
- bounded reproducibility automation where claim-bearing evidence depends on a clean-checkout proof

Current phase-4 boundary packets created in this slice:

- `docs/decisions/governance/runtime_config_live_update_policy_boundary_packet_2026-05-15.md`
- `docs/decisions/governance/decision_gate_finite_numeric_hardening_packet_2026-05-15.md`
- `docs/decisions/governance/ev_gate_non_finite_expected_value_hardening_packet_2026-05-15.md`
- `docs/decisions/governance/runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md`
- `docs/decisions/governance/execution_proxy_evidence_manifest_closeout_packet_2026-05-15.md`

Important boundary:

- these are **not** phase-1 or phase-2 tasks
- each one requires its own narrower contract and may need stricter review because it gets closer to runtime, config-authority, or high-sensitivity zones
- the new boundary packet explicitly says the current docs-only clarification line is sufficient for the present behavior description and that any future source-level whitelist/API change must reopen as a separate bounded pre-code packet
- the decision-gate packet selects one narrower high-sensitivity candidate for later work: finite-numeric hardening in `src/core/strategy/decision_gates.py`, while explicitly keeping `src/core/strategy/decision.py`, fib-gating, sizing, policy-router, and config-authority surfaces out of scope unless separately reopened
- the EV-gate packet selects a separate component-level candidate: fail-closed handling for non-finite `expected_value` in `src/core/strategy/components/ev_gate.py`, while explicitly keeping upstream context-builder emission and broader component-pipeline semantics out of scope unless separately reopened
- the config-authority packet selects the narrowest remaining API-edge alignment candidate: expose a coarse public `non_whitelisted_field` detail for guarded propose rejections, while explicitly keeping whitelist scope and live-write policy unchanged unless separately reopened
- the reproducibility packet selects the narrowest remaining evidence-closeout candidate: add one deterministic non-self manifest artifact to `execution_proxy_evidence`, while explicitly keeping runtime semantics, shared utility extraction, and broader governance redesign out of scope unless separately reopened

## What changed now

- created a phased follow-up plan anchored to the premortem
- started the first low-friction governance-reference surfaces in the same slice
- added a docs-only runtime-config live-update matrix that separates schema support, validate acceptance, and live propose authority
- added a trigger-based adoption boundary for the evidence claim header so claim-bearing notes become stricter without making scratch research heavy
- clarified user-facing config docs so `validate` is not misread as live-write authority and the narrower propose whitelist is discoverable from everyday docs
- added a docs-only boundary packet that stops the current clarification line from bleeding into implicit config-authority implementation work
- added a second docs-only phase-4 packet that identifies `decision_gates.py` finite-numeric hardening as the next smallest strategy/decision candidate instead of treating phase 4 as an open-ended hardening bucket

## What did not change

- no runtime behavior
- no config-authority semantics
- no tests or selectors
- no paper/live behavior
- no promotion/champion readiness stance
- no new SSOT

## Bottom line

The premortem follow-up should begin by making the current lane easier to see and evidence claims easier to frame correctly. That is the smallest step that reduces future rework without punishing ordinary research with unnecessary STRICT-style friction.
