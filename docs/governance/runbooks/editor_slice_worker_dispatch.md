# Editor Slice Worker Dispatch

Operational runbook for starting and receiving one bounded editor-worker slice.

This runbook is subordinate to the repository's higher-order governance documents.
It does not change mode resolution, freeze rules, or shared-truth authority.

This is a retained target-model surface for explicitly activated slice workers.
It does not create standing worker identities or implicit worker-to-worker chaining authority.
This terminology refresh updates the retained worker model in live governance docs only.
It does not by itself change runtime capabilities, automation guarantees, or authority boundaries.

## Purpose

Use this runbook when control / integration lane wants to dispatch one real editor worker
on one bounded slice.

The default Genesis model is:

- one editor worker = one **autonomous slice worker**
- most workers share the same ground role
- workers differ mainly by slice contract, not by permanent personality
- one worker may live a long time, but may own only one **active** slice at a time

## What this runbook is for

This runbook helps control plane answer:

1. Is the slice admissible for editor-attached execution now?
2. What must be pinned before the worker starts?
3. What may the worker do autonomously inside the slice?
4. What must happen before the worker may continue to a next slice?

## Activation rule

A worker is active only after **explicit dispatch**.

Important consequences:

- an open editor window does not activate a worker
- an attached workspace or loaded checkout does not activate a worker
- starting Worker A does **not** start Worker B
- same-role workers may run in parallel only when each receives its own bounded slice contract
- no worker may self-activate a next slice

## Preconditions before dispatch

Before starting an editor worker, control / integration lane should confirm all of the following:

- `base_branch` and `base_sha` are pinned
- the slice question is exact and bounded
- `scope_in` and `scope_out` are explicit
- forbidden surfaces are explicit
- allowed inputs are explicit
- allowed outputs are explicit
- required gates / checks are explicit
- branch target or worker branch naming is decided
- repo-visible inputs are sufficient, or an explicit non-repo admission path is defined

If any one of these is unclear, the honest answer is: do not dispatch yet.

## Editor-visible input rule

Default rule:

- workers may rely on repo-visible tracked inputs in the active editor checkout
- workspace visibility does not by itself expand authority
- workspace-local or non-repo inputs are admissible only if the slice contract or direct user instruction explicitly allows them

Examples of explicit non-repo admission paths:

- bounded artifact bundle
- approved workspace path or fetch recipe
- deterministic regenerate-on-demand recipe

Local-only, `gitignored`, unstaged, or operator-mounted files outside declared scope are not admissible by default.

## Practical branch and worktree setup

For the current editor-worker model, the practical default topology is:

- `master` = stable shared baseline
- `feature/editor-worker-orchestrator` = long-lived control-plane branch for this wave
- one bounded slice = one worker branch = one PR
- one editor-attached worktree/checkout = one worker execution surface

Operationally:

- control / integration lane may stay on `feature/editor-worker-orchestrator`
- initial worker scouting may be read-only in the shared editor context
- any worker that will write, commit, or open a PR should move onto its own branch and preferably its own isolated worktree/checkout first
- the pinned `base_sha` for the slice still wins over whatever branch happens to be open in the editor

This means the branch/worktree is an execution surface, not a source of authority.
The worker is still governed by the bounded slice contract, global governance, and the pinned `base_sha`.

When in doubt, use the smaller honest rule:

- read-only comparison or inventory work may begin without a dedicated worker branch if the slice contract allows it
- repo-write work should not start until the worker has its own branch target and isolated editor-attached worktree/checkout

## Default startup bundle for new editor chats

For the current simplified model, new editor chats should normally all start from the
same generic worker surface:

- `.github/agents/editor-slice-worker.agent.md`

If control plane prefers prompt-first startup instead of agent-picker startup, the
prompt surfaces are:

- `.github/prompts/editor-slice-work-order.prompt.md`
- `.github/prompts/editor-slice-return.prompt.md`

The difference between `worker-01`, `worker-02`, `worker-03`, and `worker-04` belongs in:

- their branch/worktree
- their pinned `base_sha`
- their bounded slice contract

It does **not** belong in four different default worker personalities.

Historical weakness / control / contradiction / reference scout labels from an earlier
pilot should be treated as superseded startup surfaces rather than the retained default
model.

Important operator rule:

- a new editor chat does **not** auto-bind itself to the generic agent or prompts
- control plane must select the same generic worker agent in the picker, or invoke the same work-order prompt, for each new chat explicitly and then attach the correct bounded slice contract
- if a local pilot surface still carries an older scout label in its branch or worktree name, treat that label as a slot label only and not as standing role authority
- if a scouting chat needs repo-write, commit, or PR work, stop the scouting pass and move that slice onto its own branch target and preferably its own isolated editor-attached worktree/checkout before continuing

One concrete read-only specimen for the current startup setup lives at:

- `docs/contracts/editor_workers/editor_worker_startup_test_dispatch_2026-05-12.md`

## Dispatch steps

### 1. Choose one bounded slice

Define:

- exact question
- exact subject/window/year
- why this slice is the next admissible step
- why it does not overlap an already active worker

### 2. Compile the slice contract

The worker-facing dispatch should include at least:

- `task_id`
- `dispatch_id`
- `worker_class`
- `base_branch`
- `base_sha`
- `resolved_mode`
- `question`
- `scope_in`
- `scope_out`
- `allowed_inputs`
- `allowed_output_types`
- `done_criteria`
- `stop_conditions`
- `escalation_conditions`

### 3. Confirm runtime/data admission if execution is allowed

If the slice may run scripts, helpers, tests, or backtests, control plane must confirm that:

- runner entrypoint is declared
- required runtime inputs are admissible in the active editor/workspace context
- output namespace is explicit
- local-only data is not being smuggled in as if it were in scope automatically

### 4. Start the worker explicitly

Dispatch the worker on its branch target and slice contract.

Record at minimum:

- worker identifier
- branch target
- dispatch id
- base SHA
- activation time
- current integration backlog assumption

### 5. Let the worker execute autonomously inside the slice

Once started, the worker may do the work needed to complete the slice **inside the contract**.

That may include, if explicitly allowed:

- reading evidence anchors
- writing docs or packet updates
- writing helper/test files
- running scoped verification
- running bounded backtests or analysis helpers
- generating deterministic artifacts
- preparing a branch-local PR

## What the worker must not do

The worker must not:

- widen the subject on its own
- cross into forbidden surfaces
- update shared truth directly
- self-assign a new slice
- interpret advisory routing hints as self-authorization
- start another worker implicitly
- rely on undeclared local-only inputs

## Required return package

Each editor worker should return at least:

- `status`
- artifact or packet paths
- `summary`
- `observed`
- `inferred`
- `unverified`
- `what_this_does_not_prove`
- `recommended_next_step`
- `recommended_integration_class`
- `base_sha_confirmed`
- `scope_adherence_report`

Optional advisory handoff fields may include:

- `blocked_by`
- `handoff_state`
- `next_admissible_slice_candidate`
- `access_frame_delta`

These are routing hints only.
They do not authorize continuation by themselves.

## After the return

Control / integration lane must explicitly classify the result before the worker may continue.

Typical classifications:

- `ignore`
- `park`
- `blocked`
- `deep-dive`
- `duplicate`
- `contradicted`
- `integrate`

Only after explicit classification may control plane decide whether to:

- stop the worker
- redispatch the same worker on a new slice
- activate another worker
- escalate to integration or stricter governance path

## Stop / escalation reminders

Stop immediately if:

- the worker needs forbidden surfaces
- required inputs are missing
- base SHA is stale or mismatched
- the slice cannot stay bounded honestly

Escalate rather than improvising if:

- runtime/data admission is unclear
- two workers appear to converge on the same ownership tuple
- the result needs shared-truth write or larger synthesis
- a new slice is needed to make the result meaningful

## Practical default

A good steady-state editor-worker batch should usually look like this:

- same ground-role worker type
- different bounded slices
- one active slice per worker
- explicit activation per worker
- explicit return classification before any continuation

That keeps the workers useful, fast, and governable without turning them into self-authorizing chaos engines.
