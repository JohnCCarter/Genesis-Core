# Runtime config live-update policy boundary packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `packet-boundary-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin code, config, test, or API behavior changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice only defines the boundary for any future runtime-config live-update policy work; the main risk is wording drift that could be mistaken for approval to widen the live-write surface or to treat the current B1 reading as a permanent design lock
- **Required Path:** `Quick`
- **Objective:** define what packet type must come next, if work continues, before any runtime-config live-update whitelist or API-semantics change is considered on the current repository surface
- **Candidate:** `future runtime-config live-update policy clarification / expansion line`
- **Base SHA:** `66f97acc`

### Scope

- **Scope IN:** one docs-only boundary packet; explicit relation to the current-state live-update matrix, current docs clarifications, and existing audit note; explicit statement of what the current docs-only line already resolved; explicit stop/reopen rules for any future code/config/API change; explicit definition of the next admissible packet type only
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all whitelist expansion; all API behavior changes; all runtime/default changes; all readiness/promotion/paper/live claims; all claims that future implementation is already approved
- **Expected changed files:** `docs/decisions/governance/runtime_config_live_update_policy_boundary_packet_2026-05-15.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that this packet remains docs-only and non-authorizing
- manual wording audit that current behavior description is kept separate from future policy choice
- manual wording audit that no source-change authority is implied

### Stop Conditions

- any wording that treats this packet as approval to widen the live-write whitelist
- any wording that treats current docs clarification as a code-change authorization
- any wording that makes `validate` success equivalent to live-write authority
- any wording that treats the current B1 reading as a permanently chosen implementation policy rather than the current observed repo state
- any wording that mixes future docs-only clarification and source changes into one implicitly approved packet

## Purpose

This packet answers one narrow question only:

- what packet type must come next, if work continues, before any runtime-config live-update behavior or whitelist change can be considered?

## Governing basis

This packet is downstream of the following already visible current-state surfaces:

- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
- `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`
- `README.md`
- `config/README.md`
- `docs/architecture/ARCHITECTURE.md`
- `src/core/api/config.py`
- `src/core/config/authority.py`
- `src/core/config/schema.py`

Carried-forward meaning:

1. the repository currently documents that `validate` is broader than live-write authority
2. the current guarded live-write surface is the `propose` path backed by `ConfigAuthority.propose_update(...)`
3. the current observed repo reading is closest to a **B1 safety-model interpretation**: narrower live-write surface, now documented more explicitly
4. none of the above by itself decides whether a future broader live-update surface should or should not exist

## What the current docs-only line already resolved

The current docs-only follow-up has already made the following materially clearer:

- `validate` should be read as schema/config-object validation, not as live-write approval
- `propose` is the actual guarded live-write path
- the live-write surface is intentionally narrower than the declared runtime schema on the current repo surface
- user-facing docs now point at the current-state matrix instead of implying all schema-valid fields are live-updatable

That means the current line has already resolved the **documentation ambiguity** that motivated the premortem follow-up.

This packet therefore does **not** reopen that ambiguity as if it were still unresolved.

## What is not required next

Because the current docs-only line already clarified the present behavior, the next step does **not** need to be:

- an immediate whitelist-expansion implementation slice
- a broad config-authority refactor
- a combined docs-plus-code "small fix" slice
- a runtime-default change
- an API behavior change folded into a docs clarification task

Why:

- the current observed behavior is now documented clearly enough to avoid the earlier false implication that schema-valid means live-writable
- the remaining question is no longer "what does the repo do now?"
- the remaining question, if work continues, is whether the repo should keep the current guarded live-write surface or deliberately widen it for a small explicit field set

## Boundary decision

### Current standing conclusion

The docs-only follow-up line is sufficient for the current B1-style reading:

- current behavior is documented
- current live-write scope is clearer
- no source change is required merely to make the present contract legible

This is a **current-state documentation conclusion**, not a future implementation lock.

### What the next admissible packet may be

If work continues beyond the current docs-only line, the next admissible step may only be:

- a **separate pre-code packet for one exact bounded live-update policy change candidate**

That future packet must choose one explicit objective, such as:

- widening the live-write surface for one small explicit field set, or
- tightening/reshaping user-facing error semantics for the guarded live-write path

It must **not** combine multiple policy moves by convenience.

### What that future pre-code packet must define

A future bounded packet must define at minimum:

- the exact field set under consideration
- whether the slice is docs-only or implementation-bearing
- whether `src/core/config/authority.py`, `src/core/api/config.py`, or `src/core/config/schema.py` must change
- what tests/gates become necessary if code changes are required
- what must remain unchanged on the default path
- what live-write surfaces remain explicitly out of scope
- what rollback / stop rules apply if the change spreads beyond the named field set

## Hard stop and reopen rule

From this boundary onward, if any future work needs to modify:

- `src/core/config/authority.py`
- `src/core/api/config.py`
- `src/core/config/schema.py`
- tests that define current config API or authority semantics
- user-facing docs in order to describe newly changed semantics rather than current behavior

then that work must stop and reopen as a **separate bounded packet**.

No future slice may silently absorb a source change under the cover of the already completed docs-only clarification line.

## What remains out of scope now

Still out of scope beyond this packet:

- whitelist expansion
- config-authority refactor
- actor-specific write-permission model
- runtime-default changes
- schema changes
- API error-contract changes
- readiness, promotion, paper/live, or champion implications

## Bottom line

The current docs-only line is sufficient to document the present runtime-config live-update boundary. The next honest question, if work continues, is no longer "what does the repo do now?" but "do we want to change the live-update policy for one exact bounded surface?". If that question is reopened, it must start with a separate pre-code packet rather than by smuggling code or config-authority changes into the already completed docs clarification work.
