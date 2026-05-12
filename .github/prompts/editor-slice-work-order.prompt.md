---
name: editor-slice-work-order
description: "Run one bounded Genesis-Core editor-worker slice from a clear work order. Use when a task needs explicit scope, done criteria, comparisons, and stop rules."
argument-hint: "Describe the slice question, subject, scope IN/OUT, allowed inputs, done criteria, and any control/reference anchors."
agent: agent
---

# Editor Slice Work Order

Use this prompt to run one bounded Genesis-Core editor-worker slice.

Before acting, load and follow:

- [Repo operational contract](../copilot-instructions.md)
- [Governance quick reference](../../docs/governance/QUICK_REF.md)
- [Worker governance envelope](../../docs/governance/worker_governance_envelope.md)
- [Editor slice worker dispatch runbook](../../docs/governance/runbooks/editor_slice_worker_dispatch.md)
- [Docs research slice rules](../instructions/docs-research-slices.instructions.md)
- [Tooling slice rules](../instructions/tooling-slices.instructions.md)

Treat the user input as a draft work order for exactly one bounded slice.
If any required field is missing or ambiguous, ask only for the missing clarification.
If a referenced governance document is unavailable, stop and ask for clarification or an alternate reference.

## Required work-order fields

- exact question or objective
- bounded subject (year, month, window, seam, or file surface)
- scope IN
- scope OUT
- allowed inputs and baseline anchors
- done criteria
- stop conditions
- escalation conditions
- required comparisons, if relevant

## Execution rules

- Resolve mode and choose the smallest admissible, least-permissive governance path that still satisfies the repo rules for the current slice. If that path is unclear, fail closed and escalate rather than widen scope.
- Default local editor-worker operation uses the shared `Genesis-Core` checkout. Request dedicated branch/worktree isolation only when overlapping repo-write, destructive git/index operations, or PR preparation requires it.
- Treat the current slice as fail-closed: within this slice, do not widen subject, lane, or mission.
- Reuse the supplied baseline, artifacts, and anchor years. If any are missing or unclear, ask for clarification or return blocked instead of inventing a new baseline.
- If the slice is non-trivial, create a todo plan and obtain the required governance review before editing.
- Continue working only until one of these is true:
  1. the done criteria are satisfied
  2. a stop condition is reached
  3. an escalation condition is triggered; in that case, stop the current slice and return it for explicit redispatch or review instead of widening scope yourself

## Annual-slice rule

When the subject is a year bucket, the worker owns an explanatory question, not a sentiment filter.
For example: "explain why 2018 was classified as weak" does not mean "ignore everything positive in 2018."
The worker may inspect positive and negative subperiods inside the year, but must compare them against the supplied control and reference anchors.

## Required return package

Return the slice with these sections:

- scope summary (IN / OUT)
- files or artifacts changed or consulted
- validation run and outcomes
- observed
- inferred
- unverified
- what_this_does_not_prove
- recommended_next_step
- scope_adherence_report

Do not claim shared truth, runtime readiness, or autonomous continuation unless the work order explicitly authorizes it.
