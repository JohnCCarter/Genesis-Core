# RI policy router D1 transport/falsifier evidence boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records an evidence-boundary closeout only for the current D1 insufficient-evidence transport/falsifier chain. It does **not** authorize candidate-promotion discussion, runtime integration, champion comparison, writeback, family-rule changes, config-authority changes, or paper/live interpretation.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `MED` — why: this slice narrows promotion-adjacent interpretation for an existing RI/policy-router evidence chain, but it stays docs-only and non-authorizing
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet reduces interpretation drift without reopening runtime or candidate-promotion work
- **Objective:** record what the current D1 transport/falsifier chain does and does not justify before any RI/policy-router candidate-promotion discussion could be reopened
- **Base SHA:** `abaf6083`
- **Related queue item:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`

### Scope

- **Scope IN:** this boundary packet; the queue update that records Slice 5 as closed and keeps Slice 6 queued
- **Scope OUT:** all `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`, and `artifacts/**` changes; all runtime integration packets; all paper/live semantics; all champion, promotion, writeback, or family-rule changes; all edits to `src/core/strategy/ri_policy_router.py`, `src/core/strategy/decision.py`, `src/core/config/schema.py`, and `src/core/config/authority.py`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation on this packet and the queue file only
- manual wording audit that this packet stays evidence-boundary only
- manual wording audit that March 26 promotion-readiness documents remain historical context only rather than reopened decision surfaces
- manual wording audit that no readiness, approval, default, runtime, or writeback authority leaks into the final wording

## Purpose

This packet answers one narrow question only:

- after the current D1 insufficient-evidence transport/falsifier chain, what promotion-adjacent interpretation remains admissible now?

## Governing basis

### Observed

1. `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md` already frames Slice 5 as a bounded docs/research-governance slice and explicitly keeps runtime family/policy changes out of scope.
2. `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.md` records a bounded non-null exact-surface transport result, but also states that the result remains exact-surface only, observational only, non-authoritative, and unsuitable as runtime, policy, promotion, or transport authority by itself.
3. `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_2026-05-06.md` records `external_surface_falsified` on the first fresh late-2024 external surface, with no admitted claim field surviving unchanged transport there, and states that the current D1 line is insufficient for runtime, policy, or promotion authority.
4. The local-only, untracked historical note path `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` is retained only as historical reference context for how this slice was framed; it is not repository-tracked authority and is not required to interpret this packet.
5. The March 26 challenger-family promotion-readiness documents show a stricter, docs-only precedent in which discussion-opening and `not yet` readiness are recorded as separate bounded decisions below promotion approval.

### Inferred

- The current D1 chain has enough tracked evidence to support a boundary packet, but not enough to open candidate-promotion discussion.
- The May 4 transport success cannot be read in isolation because the May 6 first fresh external-surface falsifier remains open and unresolved.
- The honest current posture is that the evidence chain remains open as bounded observational work while candidate-promotion discussion remains closed.
- If this exact D1 line is ever reopened, the smallest admissible follow-up still matches the May 6 falsifier note: a docs-only synthesis or one second genuinely new external falsifier, not runtime or family-promotion work.

### Unverified in this packet

- whether a second fresh external-surface falsifier would pass or fail
- whether future D1 evidence could ever justify reopening candidate-promotion discussion
- whether broader RI family promotion-readiness work should ever inherit anything from this D1 transport/falsifier chain

## Boundary decision

### Decision label

- `EVIDENCE_BOUNDARY_OPEN_D1_TRANSPORT_AND_FALSIFIER_CHAIN`

### Meaning of that label

This label means only the following:

- the current D1 insufficient-evidence line remains a tracked observational evidence chain with one bounded exact-surface transport success and one first fresh external-surface falsifier
- candidate-promotion discussion remains closed on the current repository evidence
- runtime integration, family-rule, champion comparison, writeback, config-authority, and paper/live semantics remain out of scope
- any future reopening must begin from a new governed packet or an explicitly cited synthesis rather than from implied inheritance

This label does **not** mean:

- the D1 line is rejected overall
- a candidate is now ready, eligible, or promotable
- a promotion-readiness discussion is opened
- a runtime candidate exists
- any policy-router default, family behavior, or champion path change is justified

## Mandatory before any future candidate-promotion discussion

Before any later packet can reopen candidate-promotion discussion on this line, at least the following must be stated explicitly:

1. **External falsifier disposition**
   - the current `external_surface_falsified` result must be explicitly dispositioned rather than left as a remembered caveat
2. **Candidate identity declaration**
   - the later packet must say which exact candidate surface is under discussion; this packet does not name one
3. **Fresh governed evidence or blocker disposition**
   - a later packet must explain why promotion-adjacent discussion may reopen despite the current falsifier state, or what new governed evidence changed the boundary
4. **Lane separation**
   - runtime integration, family comparison, champion/writeback, and paper/live lanes must remain explicitly separate rather than being imported by implication
5. **Decision contract clarity**
   - any later promotion-adjacent packet must declare its exact acceptance/rejection rule up front

## What remains out of scope

This packet keeps the following out of scope unless separately reopened:

- `src/core/strategy/ri_policy_router.py`
- `src/core/strategy/decision.py`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- all policy-router analyzer/test changes
- all runtime integration packets or source-backed router changes
- all champion, promotion, writeback, or family-rule changes
- all paper-shadow or live-paper interpretation
- all claims that the current D1 chain has become a runtime-candidate or promotion-candidate authority surface

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen instead of leaning on this packet:

- runtime, test, or analyzer changes
- naming or ranking a specific candidate for promotion-adjacent use
- family comparison, champion/writeback, or promotion-decision semantics
- paper/live or operational-readiness interpretation
- any claim that this packet itself authorizes reopening candidate-promotion discussion

## Bottom line

The current D1 transport/falsifier chain is useful as a bounded observational evidence line, but it has not closed the external transport question. The correct present state is therefore boundary-only: keep the evidence line open, keep candidate-promotion discussion closed, and do not inherit runtime, promotion, or paper/live meaning from the existing D1 artifacts.
