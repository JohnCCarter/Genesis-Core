# Editor worker startup test dispatch

Date: 2026-05-12
Branch: `feature/editor-worker-orchestrator`
Mode: `RESEARCH`
Status: `ready for read-only trial`
Dispatch allowed: `true`
Execution authority: `read-only scouting only`
Shared truth effect: `none`

This document is a **single concrete test dispatch specimen** for the current editor-worker startup setup.

It is meant to answer one practical question:

> Can one newly opened editor worker run a bounded read-only scouting pass on the new startup bundle and return a usable package without widening scope?

It does **not** authorize repo-write, commits, PR creation, runtime execution, or shared-truth updates.

## How to use this test

1. Open the dedicated reference worker worktree prepared by control plane.
2. Open a new editor chat in that worktree.
3. Select the `Editor Scout Reference` agent.
4. Paste the specimen dispatch below into that chat.
5. Require a read-only return package only.

If the worker needs repo-write or a wider subject, the correct behavior is to stop and return blocked or recommended-next-step rather than improvising.

## Reusable minimal dispatch template

Use this skeleton for future scouting dispatches:

```yaml
task_id: <short-stable-task-id>
dispatch_id: <task-id-run-001>
worker_agent: <Editor Scout Weakness | Editor Scout Control | Editor Scout Contradiction | Editor Scout Reference>
worker_class: inventory
resolved_mode: RESEARCH
base_branch: feature/editor-worker-orchestrator
base_sha: <PINNED_SHA>
branch_target: <worker-branch>
question: <exact bounded question>
subject: <bounded file surface, year, window, or seam>
scope_in:
  - <allowed paths>
scope_out:
  - <forbidden paths>
allowed_inputs:
  - repo-visible tracked files only
allowed_output_types:
  - read-only scouting return
done_criteria:
  - <what counts as complete>
stop_conditions:
  - <when to stop immediately>
escalation_conditions:
  - <when to return to orchestrator>
reference_anchors:
  - <baseline or canonical files>
```

## Concrete specimen for the first test

```yaml
task_id: editor-worker-startup-reference-test
dispatch_id: editor-worker-startup-reference-test-001
worker_agent: Editor Scout Reference
worker_class: inventory
resolved_mode: RESEARCH
base_branch: feature/editor-worker-orchestrator
base_sha: d968a0f2
branch_target: research/editor-scout-reference
question: >
  Build the current reference picture for the editor-worker startup bundle:
  which tracked files define the startup surface, what branch/worktree model is
  documented, and what limits still remain operator-manual.
subject: editor-worker startup bundle file surface
scope_in:
  - .github/agents/editor-scout-*.agent.md
  - .github/prompts/editor-scout-*.prompt.md
  - docs/governance/runbooks/editor_slice_worker_dispatch.md
  - workforce_roadmap.md
scope_out:
  - src/**
  - tests/**
  - config/**
  - docs/analysis/**
  - docs/decisions/**
  - shared truth updates
  - repo-write actions
allowed_inputs:
  - repo-visible tracked files inside scope_in
  - current branch and worktree metadata already prepared by control plane
allowed_output_types:
  - read-only scouting return
done_criteria:
  - identify the canonical startup files
  - state the documented branch/worktree model
  - state what is still manual in the operator workflow
  - return observed / inferred / unverified cleanly separated
stop_conditions:
  - any need to edit files
  - any need to inspect forbidden paths
  - any need to widen the subject beyond the startup bundle
escalation_conditions:
  - startup truth appears internally contradictory
  - a docs repair is required to answer honestly
  - branch/worktree state appears stale versus base_sha
reference_anchors:
  - docs/governance/runbooks/editor_slice_worker_dispatch.md
  - workforce_roadmap.md
  - .github/agents/editor-scout-reference.agent.md
  - .github/prompts/editor-scout-reference.prompt.md
```

## Expected return contract for the test

The worker should return at least:

- `status`
- scope summary (`IN / OUT`)
- files consulted
- `observed`
- `inferred`
- `unverified`
- `what_this_does_not_prove`
- `recommended_next_step`
- `scope_adherence_report`

## Pass condition for this trial

The test counts as successful if the worker:

1. stays inside the declared scope
2. remains read-only
3. returns a coherent reference picture for the startup bundle
4. explicitly states the remaining manual operator steps instead of pretending they are automated

## What this test does not prove

This test does **not** prove:

- automatic agent selection on chat open
- automatic worktree or branch binding by VS Code
- repo-write dispatch correctness
- PR flow correctness
- runtime or backtest execution admission

It proves only that the current startup bundle can support one honest, bounded, read-only editor-worker dispatch.
