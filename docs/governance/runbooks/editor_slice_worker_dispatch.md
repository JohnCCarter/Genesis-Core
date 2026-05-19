# Editor Slice Worker Dispatch

Operational runbook for starting and receiving one bounded editor-worker slice.

This runbook is subordinate to the repository's higher-order governance documents.
It does not change mode resolution, freeze rules, or shared-truth authority.

> Status note (2026-05-18): This runbook is retained as a historical/paused reference for the earlier editor-worker orchestration model. It does not describe the current default governance workflow on `feature/evidence-closeout-pilot`, and it should not be read as standing instruction to open or coordinate multiple editor workers.
>
> - The operational guidance below is preserved for traceability and possible future reconsideration.
> - Unless that model is explicitly reopened, this document remains complementary reference material only.
>
> Later-branch truthfulness note (2026-05-19): This retained historical/paused status is not limited to `feature/evidence-closeout-pilot`; in the later-branch context covered here, including `feature/risk-hardening-wave2`, this runbook also remains non-current reference material unless explicitly reopened. This note records status only and does not designate a replacement or branch-current default workflow.

This is a retained historical target-model surface for explicitly activated slice workers.
It does not create standing worker identities or implicit worker-to-worker chaining authority.
This terminology refresh is preserved for traceability rather than presented as a live default in governance docs today.
It does not by itself change runtime capabilities, automation guarantees, or authority boundaries.

## Purpose

Use this runbook only if the paused editor-worker model is explicitly reopened for one real editor worker
on one bounded slice.

Within that retained model, the intended worker shape was:

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
- execution surface is decided (`shared local checkout` som default; dedicated branch/worktree bara när explicit isolering krävs)
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

## Practical execution-surface setup

For the retained editor-worker model captured here, the practical default topology was:

- `master` = stable shared baseline
- `feature/editor-worker-orchestrator` = long-lived shared local editor branch for this wave
- retained local editor setup = multiple bounded workers share the active `Genesis-Core` checkout on `feature/editor-worker-orchestrator`
- dedicated branch/worktree isolation is optional and used only when the slice explicitly needs isolation, destructive git work, or PR preparation

Operationally, that meant:

- control / integration lane may stay on `feature/editor-worker-orchestrator`
- most local worker slices may start in the shared active checkout
- any worker that needs overlapping repo-write, destructive git/index operations, or PR preparation should move onto its own branch and preferably its own isolated worktree/checkout first
- the pinned `base_sha` for the slice still wins over whatever branch happens to be open in the editor

This means the chosen execution surface is not a source of authority.
The worker is still governed by the bounded slice contract, global governance, and the pinned `base_sha`.

When in doubt, use the smaller honest rule:

- read-only comparison or inventory work may begin in the shared checkout if the slice contract allows it
- repo-write in the shared checkout is admissible only when scope, ownership, and touched files are explicitly bounded and non-overlapping
- if overlap, conflict-risk, destructive git work, or PR preparation appears, move the slice to a dedicated branch/worktree first

## Retained startup bundle for new editor chats

For the retained simplified model, new editor chats would normally all start from the
same generic worker surface:

- `.github/agents/editor-slice-worker.agent.md`

If control plane prefers prompt-first startup instead of agent-picker startup, the
prompt surfaces are:

- `.github/prompts/editor-slice-work-order.prompt.md`
- `.github/prompts/editor-slice-return.prompt.md`

The difference between `worker-01`, `worker-02`, `worker-03`, and `worker-04` belongs in:

- their bounded slice / ownership scope
- their pinned `base_sha`
- their optional execution-surface metadata when explicit isolation is assigned
- their bounded slice contract

It does **not** belong in four different default worker personalities.

Important operator rule:

- a new editor chat does **not** auto-bind itself to the generic agent or prompts
- control plane must select the same generic worker agent in the picker, or invoke the same work-order prompt, for each new chat explicitly and then attach the correct bounded slice contract
- if multiple local workers share the same checkout, their scopes, ownership, and repo-write permissions must stay explicit and non-overlapping
- if a slice needs overlapping repo-write, destructive git/index work, or PR preparation, stop the shared-checkout pass and move that slice onto its own branch target and preferably its own isolated editor-attached worktree/checkout before continuing

One concrete read-only specimen for that paused startup setup lives at:

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

Dispatch the worker on its chosen execution surface and slice contract.

Record at minimum:

- worker identifier
- execution surface
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

## Retained practical default

In that paused model, a good steady-state editor-worker batch would usually look like this:

- same ground-role worker type
- shared checkout by default or explicit isolated surface when needed
- different bounded slices
- one active slice per worker
- explicit activation per worker
- explicit return classification before any continuation

That keeps the workers useful, fast, and governable without turning them into self-authorizing chaos engines.
