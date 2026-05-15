# Deep premortem follow-up phase plan for `feature/evidence-closeout-pilot`

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `docs-only / planning-only / non-executable / no runtime authority`

> Current status note:
>
> - This plan translates `docs/analysis/diagnostics/genesis_core_deep_premortem_feature_evidence_closeout_pilot_2026-05-15.md` into a small sequence of bounded follow-up phases.
> - It does **not** reopen `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md` and it does **not** authorize execution by implication.
> - Any later slice selected from this plan must still be reopened explicitly as its own bounded docs, tooling, evidence, or stricter-governed packet.

> Later progress note:
>
> - Phase 1B local-only reference containment is now införd in the tracked docs that cited the local untracked note path.
> - This is a wording-boundary cleanup only; working-contract re-anchor remains a separate later bounded reopen, so Phase 1 is not otherwise re-scoped or closed here.

## COMMAND PACKET (planning-only)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice adds one branch-current planning note only; the main risk is wording drift that could be mistaken for queue reopen, implementation approval, or new authority
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the task is to phase the next checks from the deep premortem without widening into live execution surfaces
- **Objective:** convert the deep branch premortem into a phased follow-up map that reduces precision-loss risk after partial success without turning the plan itself into a new live queue
- **Base SHA:** `d1755ec51770adc22a486f1e9d636c6fdaaece59`

### Scope

- **Scope IN:** one docs-only phase plan derived from the tracked deep premortem; branch-current sequencing guidance for later bounded reopen decisions
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all edits to `GENESIS_WORKING_CONTRACT.md`; all edits to `docs/governance/active_lane_index.md`; all edits to `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`; all runtime/config-authority/default changes; all paper/live, readiness, promotion, or champion claims; all claims that any later phase is already approved for implementation
- **Expected changed files:** `docs/analysis/diagnostics/deep_premortem_followup_phase_plan_feature_evidence_closeout_pilot_2026-05-15.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that treats this plan as a live queue or automatic reopen
- any wording that treats later phases as already approved rather than separately admissible questions
- any widening into `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**`
- any wording that implies runtime readiness, promotion readiness, or paper/live authority from the deep premortem
- any wording that rewrites historical docs as current shared-truth instruction instead of preserving their bounded role

## Purpose

This plan answers one narrow question only:

- what is the cheapest phased follow-up after the deep branch premortem if the goal is to reduce **precision loss after partial success** without reopening execution scope by convenience?

## Observed planning inputs

The tracked deep premortem identifies a different residual risk posture than the earlier May 15 baseline:

- the branch now has stronger replay labels, carrier boundaries, claim-header discipline, dependency inventory, and queue freshness discipline
- the highest remaining risk is no longer “missing boundaries,” but **over-retelling bounded success as broader proof**
- the deep premortem's recommended next checks cluster around five concrete seams:
  1. stale branch-anchor truth in `GENESIS_WORKING_CONTRACT.md`
  2. tracked docs that still name the local untracked premortem path
  3. claim-envelope completeness and explicit portability labels in older frequently cited evidence notes
  4. the top-ranked SCPE / Phase C mixed replay dependency family
  5. same-local-checkout versus clean-checkout interpretation drift

The already-closed successor queue also now says that future work should be reopened explicitly from current branch state rather than inherited from stale “next” prose.

## Inferred sequencing rule

The next honest follow-up should stay **docs/control-plane first** until the repo can state current anchors, local-only boundaries, and portability labels more cleanly.

That implies:

- phase the next work around **interpretation hardening** before new portability or runtime-adjacent claims
- prefer one seam at a time instead of reopening another broad queue
- keep every future phase reopen bounded, explicit, and separately admissible

## Operating principle

The deep premortem should be operationalized as **precision-loss prevention**, not as a new process tax.

That means:

- current truths should become easier to identify than stale branch memory
- local-only references should become harder to mistake for tracked authority
- portability labels should become harder to collapse in later retelling
- runtime-adjacent language should remain downstream of explicit contradiction, transport, and authority checks

## Phase 1 — Control-plane re-anchor and local-only reference containment

Goal:

- reduce the two highest-leverage control-plane risks from the deep premortem: stale branch-anchor truth and local-only path inheritance

Planned outputs:

- one bounded docs slice that either refreshes or further demotes `GENESIS_WORKING_CONTRACT.md` for the current branch context
- one bounded docs slice that sharpens “local-only / historical reference only” wording wherever tracked docs currently name the unrelated untracked premortem path and that wording materially affects interpretation

Why this phase comes first:

- it directly attacks failure modes `#2` and `#3` from the deep premortem
- it reduces future session drift before any stronger portability or runtime-adjacent language is revisited
- it stays fully docs-only and does not require replay, fixture, or runtime changes

Success criteria:

- a future worker can identify current branch truth without stale working-contract inheritance
- touched tracked docs no longer let the local untracked premortem path read like tracked authority
- no queue is reopened and no new shared-truth authority is created

## Phase 2 — Claim-envelope and portability label hardening

Goal:

- reduce the chance that fixture-level or same-local-checkout evidence is later remembered as historical-trace or clean-checkout proof

Planned outputs:

- one bounded docs slice that samples a frequently cited older evidence note for claim-header completeness, especially `Input carrier`, dirty/clean state, env/cache posture, and explicit non-authority framing
- one bounded docs slice that sharpens same-local-checkout versus clean-checkout wording where a currently tracked note is likely to be reused more broadly than it proves

Why this phase comes second:

- the deep premortem says the current failure risk is precision loss after narrow success
- that risk is most likely to show up first in evidence wording, not in missing code
- tightening interpretation costs less than widening carriers or rerunning evidence

Success criteria:

- at least one frequently reused evidence note demonstrates the expected modern claim-envelope discipline
- the difference between `fixture-level`, `same-local-checkout`, and stronger portability claims is harder to collapse in casual reuse
- no runtime, fixture, test, or queue surface changes are required

## Phase 3 — Highest unresolved dependency-root containment

Goal:

- reopen the most dangerous still-mixed ignored/local-only dependency family only when its carrier or non-portability status can be stated honestly

Primary target:

- the SCPE / Phase C mixed replay family ranked first in `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`

Planned outputs:

- one bounded decision note that either chooses the next admissible carrier for the mixed Phase C dependency or classifies the broader family more explicitly as non-portable at current branch state

Why this phase comes third:

- the branch already narrowed the SCPE-derived line to the exact `defensive_probe` pocket, but the mixed-root dependency family still exists behind broader replay-root memories
- this is the highest unresolved dependency root left in the tracked inventory
- phase 1 and phase 2 should land first so that any later carrier decision inherits cleaner control-plane and claim-label discipline

Success criteria:

- the repo can state the current portability status of the SCPE / Phase C family more precisely than “partly tracked, partly remembered”
- no broader replay-root authority is implied beyond the chosen bounded conclusion
- the phase remains chain-local and does not widen into framework extraction or runtime semantics

## Phase 4 — Runtime-adjacent inheritance guards

Goal:

- keep the deep premortem's runtime-adjacent residuals behind explicit contradiction, transport, and authority gates instead of letting them re-enter by wording drift

Planned outputs:

- one bounded docs/governance slice, if needed, that sharpens same-local-checkout and non-portability language for execution-summary style evidence before clean-checkout portability is discussed
- one bounded docs/evidence slice, if needed, that restates the contradiction or falsifier prerequisite before any fresh RI/policy-router candidate or readiness language is admitted
- one bounded docs clarification, if needed, that keeps `validate` success distinct from live-write authority where future reuse pressure appears again

Why this phase comes last:

- it sits closest to runtime, paper/live, and promotion-adjacent interpretation even when it remains docs-only
- it should inherit the cleaner control-plane, claim-header, and dependency-root work from earlier phases instead of compensating for ambiguity all at once

Important boundary:

- this phase is still **not** approval for runtime, config-authority, paper/live, promotion, or champion work
- any actual entry into those surfaces must reopen under the appropriate stricter packet/review path

Success criteria:

- runtime-adjacent conversations are forced back through explicit contradiction, transport, or authority gates instead of inheriting from research evidence by convenience
- no docs-only note is allowed to read like readiness or promotion approval

## Selection rule if any phase is reopened later

If the user wants to continue from this plan, the next admissible phase should prefer the smallest move that:

- reduces one concrete deep-premortem failure mode
- tightens interpretation before widening portability
- keeps local-only versus tracked authority explicit
- does not reopen the closed successor queue by shorthand
- stays outside runtime/default/paper-live/promotion authority unless separately packeted

## What changed now

- created one branch-current phase plan derived from the deep premortem
- translated the deep premortem's recommended next checks into four bounded follow-up phases
- kept the plan explicitly separate from the already-closed successor queue

## What did not change

- no queue reopened
- no runtime, config-authority, paper/live, readiness, promotion, or champion semantics changed
- no code, tests, fixtures, results, or governance SSOT surfaces changed
- no later phase was approved for implementation by this file alone

## Bottom line

The deep branch premortem does not call for another broad workshop queue. It calls for a short phased follow-up that prevents **precision loss after partial success**.

That makes the next honest shape simple: re-anchor the control plane first, harden claim and portability wording second, contain the highest unresolved dependency root third, and only then revisit runtime-adjacent inheritance guards under explicit bounded reopen decisions.
