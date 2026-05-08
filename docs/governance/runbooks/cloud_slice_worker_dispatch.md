# Cloud Slice Worker Dispatch

Operational runbook for starting and receiving one bounded cloud-worker slice.

This runbook is subordinate to the repository's higher-order governance documents.
It does not change mode resolution, freeze rules, or shared-truth authority.

This is a retained target-model surface for explicitly activated slice workers.
It does not create standing worker identities or implicit worker-to-worker chaining authority.

## Purpose

Use this runbook when control / integration lane wants to dispatch one real cloud worker
on one bounded slice.

The default Genesis model is:

- one cloud worker = one **autonomous slice worker**
- most workers share the same ground role
- workers differ mainly by slice contract, not by permanent personality
- one worker may live a long time, but may own only one **active** slice at a time

## What this runbook is for

This runbook helps control plane answer:

1. Is the slice admissible for cloud execution now?
2. What must be pinned before the worker starts?
3. What may the worker do autonomously inside the slice?
4. What must happen before the worker may continue to a next slice?

## Activation rule

A worker is active only after **explicit dispatch**.

Important consequences:

- a workflow existing on `master` does not activate a worker
- a branch existing on `origin` does not activate a worker
- starting Worker A does **not** start Worker B
- same-role workers may run in parallel only when each receives its own bounded slice contract
- no worker may self-activate a next slice

## Preconditions before dispatch

Before starting a cloud worker, control / integration lane should confirm all of the following:

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

## Cloud-visible input rule

Default rule:

- workers may rely on repo-visible tracked inputs on the dispatched branch remote

Non-repo inputs are admissible only if the slice contract explicitly defines how they become
cloud-visible, for example:

- bounded artifact bundle
- approved remote fetch recipe
- deterministic regenerate-on-demand recipe

Local-only, `gitignored`, unstaged, or operator-mounted files are not admissible by default.

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
- required runtime inputs are admissible in cloud
- output namespace is explicit
- local-only data is not being smuggled in as if it were repo-visible

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

Each cloud worker should return at least:

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

A good steady-state cloud batch should usually look like this:

- same ground-role worker type
- different bounded slices
- one active slice per worker
- explicit activation per worker
- explicit return classification before any continuation

That keeps the workers useful, fast, and governable without turning them into self-authorizing chaos engines.
