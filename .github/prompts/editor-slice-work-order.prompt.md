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
If any required field is missing, ask only for the missing field or fields.

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

- Resolve mode and use the smallest admissible governance path.
- Treat the slice as fail-closed: do not widen subject, lane, or mission.
- Reuse the supplied baseline, artifacts, and anchor years; do not invent a new baseline.
- If the slice is non-trivial, create a todo plan and obtain the required governance review before editing.
- Continue working until one of these is true:
  1. the done criteria are satisfied
  2. a stop condition is reached
  3. an escalation condition requires explicit redispatch or review

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
