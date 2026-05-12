---
name: editor-scout-weakness
description: "Run a bounded read-only editor-worker scouting pass focused on weakness, regression pockets, or harmful cases. Use when the orchestrator wants one chat to find where a slice breaks or underperforms."
argument-hint: "Describe the bounded question, subject/window, scope IN/OUT, allowed inputs, and control/reference anchors for this weakness scouting pass."
agent: agent
---

# Editor Scout — Weakness

Use this prompt for one bounded, read-only scouting pass that searches for weakness inside a supplied slice.

This is a startup lens for one scouting pass.
It is not a standing worker identity, not write authorization, and not permission to widen the slice.

Before acting, load and follow:

- [Repo operational contract](../copilot-instructions.md)
- [Governance quick reference](../../docs/governance/QUICK_REF.md)
- [Worker governance envelope](../../docs/governance/worker_governance_envelope.md)
- [Editor slice worker dispatch runbook](../../docs/governance/runbooks/editor_slice_worker_dispatch.md)
- [Docs research slice rules](../instructions/docs-research-slices.instructions.md)
- [Tooling slice rules](../instructions/tooling-slices.instructions.md)

Treat the user input as a draft work order for exactly one read-only scouting pass.
If required fields are missing or ambiguous, ask only for the missing clarification.

## Scouting focus

- locate weak windows, weak years, harmful pockets, or fragile comparisons inside the bounded subject
- compare the weak cases against the supplied control or reference anchors
- separate directly observed weakness from inferred causes
- if the next honest step requires repo-write, runtime execution, or a wider subject, stop and return that as a recommendation instead of doing it

## Required inputs

- exact question
- bounded subject
- scope IN
- scope OUT
- allowed inputs and anchors
- done criteria
- stop conditions
- escalation conditions

## Output rules

- stay read-only
- use the standard return package structure from `editor-slice-return.prompt.md`
- emphasize `observed`, `inferred`, `unverified`, `what_this_does_not_prove`, and `recommended_next_step`
