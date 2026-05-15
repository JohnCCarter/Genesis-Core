# Next phase verkstad queue

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `active queue / docs-only / non-authorizing`

This document records the next post-premortem execution queue after the completed premortem closeout and evidence-manifest boundary work. It is a sequencing artifact in `RESEARCH`; it grants no runtime, config-authority, paper/live, promotion, or champion authority by itself.

## Mode and lane

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Research-evidence` for queue framing; future slices may open in `tooling`, `docs`, or `runtime-integration` lanes depending on the exact candidate
- **Base SHA:** `59c010c104903e49552608c15815aba1b9fa8fc3`

## Purpose

This queue answers one narrow question only:

- what is the next practical workshop loop now that the premortem plan and the evidence-manifest generalization decision are complete?

## Working loop

The operating loop for this phase is intentionally simple:

1. **Välj nästa enskilda risk/fynd att ta ned**
2. **Öppna en bounded slice**
3. **Implementera + verifiera**
4. **Repetera**

Interpretation boundary:

- one risk at a time
- one bounded slice at a time
- no framework jumps by convenience
- no pause between slices for ceremony when the next admissible step is already clear

## Current phase status

Already completed before this queue:

- premortem closeout
- runtime-config clarification line and bounded API/error-semantics follow-up
- decision-gate finite-numeric hardening
- EV-gate non-finite hardening
- execution-proxy manifest closeout
- edge-origin manifest closeout
- evidence-manifest candidate audit
- evidence-manifest generalization boundary (`defer generalization`)

That means this queue starts **after** the earlier premortem candidate set is closed.

## Current prioritized queue

### Slice 1 — editor-worker customization drift inventory

- **Status:** `selected and completed in this slice`
- **Why it comes first:** the premortem ranked agent/governance sprawl and stale instruction interpretation as a real operational risk, and this is the smallest low-risk way to reduce future orchestration mistakes
- **Artifact:** `docs/analysis/diagnostics/editor_worker_customization_drift_inventory_2026-05-15.md`
- **Outcome target:** clarify which customization surfaces are repo-local vs Claude-local support surfaces, confirm that `QUICK_REF` belongs in `.claude/`, and record what must be explicit in future worker dispatch

### Slice 2 — decision-influencing artifact replay smoke candidate selection

- **Status:** `queued`
- **Why it is next:** the premortem still ranks determinism illusion from artifact/cache/env drift as a top failure mode, and the next useful move is to pick one decision-influencing artifact chain for a clean-checkout replay smoke candidate
- **Expected shape:** bounded tooling/evidence slice, likely script/test/docs only
- **Must not widen into:** repo-wide replay framework or multi-chain rollout in one step

### Slice 3 — transport/falsifier gate for RI/policy-router candidate promotion

- **Status:** `queued`
- **Why it remains important:** the premortem explicitly warns against local-pocket overfitting and implied runtime-candidate promotion from exact-window research
- **Expected shape:** bounded docs/research-governance slice unless a later narrower implementation seam becomes obvious
- **Must not widen into:** runtime family/policy changes or broad strategy redesign

### Slice 4 — paper-shadow / live-paper isolation seam check

- **Status:** `queued`
- **Why it stays in queue:** paper/live boundary regression remains low-frequency but very high impact in the premortem ranking
- **Expected shape:** bounded docs/test seam check before any operational feature work touches that edge again
- **Must not widen into:** live-paper feature additions or observability-driven contract expansion

## Selection rule for the next slice

When this queue advances, the next admissible slice should be the smallest candidate that satisfies all of the following:

- directly reduces one ranked premortem failure mode
- has an explicit Scope IN/OUT
- has a clear verification stack
- does not require a framework-first abstraction
- does not silently cross into stricter authority zones without reopening governance path

## What changed now

- the next phase is now framed as a workshop queue rather than as unfinished premortem work
- the first post-closeout slice was selected and completed in the same bounded docs-only step
- future work is ordered by risk-reduction payoff, not by nearby file proximity

## What did not change

- no runtime behavior
- no config-authority semantics
- no strategy/backtest behavior
- no paper/live semantics
- no promotion or readiness stance

## Bottom line

The next phase is now explicit: reduce one real risk at a time through bounded slices, starting with orchestration/customization drift, then moving to reproducibility smoke selection, transport/falsifier gating, and paper/live isolation only as separately bounded follow-ups.
