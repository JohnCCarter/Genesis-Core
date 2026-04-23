# GENESIS_WORKING_CONTRACT.md

> Working anchor for day-start and resumed sessions.
> This file is **not SSOT** and must not override repo governance documents.

## Purpose

This file exists to prevent session drift.
Before starting new work, the agent should re-anchor against the latest validated lane, known blockers, and next admissible step.

## Non-purpose

This file does **not**:

- authorize new implementation work by itself
- grant execution authority by itself
- override `.github/copilot-instructions.md`, `docs/governance_mode.md`, `AGENTS.md`, or explicit user instructions
- replace packets, reports, or verified evidence artifacts

## Authority order

1. Explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`
5. `AGENTS.md`
6. This file (`GENESIS_WORKING_CONTRACT.md`)

## Current branch and mode anchor

- Branch: `feature/ri-role-map-implementation-2026-03-24`
- Expected mode on this branch: `RESEARCH`
- RESEARCH allows the smallest reproducible, traceable step
- RESEARCH does **not** authorize drift into strict-only surfaces, runtime-default authority, promotion, or champion claims without the required lane/packet

## Core conceptual lock

Genesis must be treated as a **deterministic policy-selection system**.
It is **not** an adaptive system.
It selects among predefined policies based on observable state, and any switching must remain exact, traceable, and reproducible.

## Current validated lane

Active focus right now:

- operationalize the three-lane workflow model so concept and research-evidence work stay cheaper than runtime-integration
- keep this slice on docs/workflow surfaces only unless a separate packet opens broader integration work
- avoid accidental drift from hypothesis/evidence shaping into family/runtime/authority structure

## Explicitly not active by default

Unless the user reopens them explicitly with the needed authority, do **not** treat these as active:

- the earlier `3h` historical validation lane from the prior working anchor
- inherited runtime/integration authority from RI research docs
- runtime-default changes
- paper-shadow follow-up fixes
- promotion/champion claims from isolated research evidence

## Key anchors already verified

- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` is the canonical practical definition of concept / research-evidence / runtime-integration lanes
- `.github/copilot-instructions.md` already says to prefer the cheapest admissible lane before proposing durable runtime structure
- `docs/OPUS_46_GOVERNANCE.md` treats lane classification as workflow framing, not new authority
- the next operational gap is workflow tooling/templates that make concept/research cheaper in practice, not more runtime structure

## Last verified facts relevant to today

- the lane model is already documented in the practical SSOT and governance references
- the command-packet workflow still needed explicit lane-framing prompts to reduce accidental over-scoping
- explicit user request for this task supersedes the prior `3h` historical-validation anchor

## Next admissible steps

Choose the smallest valid next step that matches the user request:

1. make the workflow template explicitly ask which lane applies and why a cheaper non-runtime form is sufficient
2. keep the working anchor aligned to the lane-model operationalization until the user explicitly reopens another lane
3. only after that, open any further concept- or research-evidence slice on bounded non-runtime surfaces

## Hard stops

Stop and re-anchor before proceeding if any of the following happens:

- the next step starts relying on memory instead of cited anchors
- concept or research language starts implying runtime/family/authority status
- runtime/paper work starts to creep in without explicit authority
- a task touches strict-only surfaces or champion/promotion semantics
- the lane is no longer obvious from the latest user request

## Required day-start / resume ritual

At the start of a new day or resumed session, do this before reasoning forward:

1. read this file
2. read persistent user memory relevant to workflow
3. read current repo memory items relevant to the active lane
4. identify the latest validated lane and the latest non-active lanes
5. state the next smallest admissible step before making claims

## Update rule

Update this file only when one of these changes:

- active lane
- blocked/not-active lane status
- known verified blocker
- next admissible action

Keep it short. If detail is needed, point to the authoritative doc instead of copying it here.
