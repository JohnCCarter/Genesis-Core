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

- **Status:** `selected and completed in this slice`
- **Why it is next:** the premortem still ranks determinism illusion from artifact/cache/env drift as a top failure mode, and the next useful move was to pick one decision-influencing artifact chain for a clean-checkout replay smoke candidate
- **Artifact(s):**
  - `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`
  - `docs/decisions/governance/execution_proxy_clean_checkout_replay_smoke_boundary_packet_2026-05-15.md`
- **Outcome target:** select `execution_proxy_evidence` as the first bounded replay-smoke candidate and lock the current fixture-containment gap as a separate follow-up boundary instead of jumping straight to implementation

### Slice 3 — execution-proxy fixture containment packet

- **Status:** `selected and completed in this slice`
- **Why it is next:** the candidate-selection slice showed that the current `execution_proxy_evidence` input trace is locally present but ignored/untracked, so a clean-checkout replay smoke could not yet be implemented honestly from the tracked repo surface
- **Artifact:** `docs/decisions/governance/execution_proxy_fixture_containment_packet_2026-05-15.md`
- **Outcome target:** choose one exact commit-safe carrier strategy and keep the next implementation slice bounded to a tracked minimal fixture rather than results-root tracking or bundle-first expansion

### Slice 4 — execution-proxy tracked-fixture smoke implementation

- **Status:** `selected and completed in this slice`
- **Why it is next:** the carrier strategy became explicit, so the next smallest implementation move was to add one tracked minimal fixture and focused smoke coverage for `execution_proxy_evidence`
- **Artifact(s):**
  - `registry/fixtures/execution_proxy_baseline_current_minimal.json`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Outcome target:** prove that `execution_proxy_evidence` can run and reproduce deterministic outputs from one tracked commit-safe fixture without relying on ignored `results/research/**` inputs

### Slice 5 — transport/falsifier gate for RI/policy-router candidate promotion

- **Status:** `queued`
- **Why it remains important:** the premortem explicitly warns against local-pocket overfitting and implied runtime-candidate promotion from exact-window research
- **Expected shape:** bounded docs/research-governance slice unless a later narrower implementation seam becomes obvious
- **Must not widen into:** runtime family/policy changes or broad strategy redesign

### Slice 6 — paper-shadow / live-paper isolation seam check

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
- the first three post-closeout slices were selected and completed as bounded docs-only steps
- the fourth post-closeout slice landed as a bounded fixture + focused-test implementation for `execution_proxy_evidence`
- the replay-smoke line is now narrowed to `execution_proxy_evidence`, and its carrier strategy is fixed to a tracked minimal fixture rather than ignored results inputs
- future work is ordered by risk-reduction payoff, not by nearby file proximity

## What did not change

- no runtime behavior
- no config-authority semantics
- no strategy/backtest behavior
- no paper/live semantics
- no promotion or readiness stance

## Bottom line

The next phase is now explicit: reduce one real risk at a time through bounded slices, starting with orchestration/customization drift, then replay-smoke candidate selection, then the `execution_proxy_evidence` fixture-containment decision, and now one landed tracked-fixture smoke implementation, with transport/falsifier gating plus paper/live isolation remaining queued behind that completed line.
