# Decision gate finite numeric hardening packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `packet-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, strategy, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, config, or API behavior changes.

> Current implementation-status note:
>
> - The candidate framed by this packet has since been landed in a separate bounded runtime slice limited to `src/core/strategy/decision_gates.py` and `tests/utils/test_decision.py`.
> - Verification on that later slice was green on touched-file `black --check` / `ruff check`, focused decision tests, decision/sizing smoke, and determinism/parity/pipeline/feature-cache checks.
> - Repo-wide `black --check .` remains red on unrelated pre-existing files outside that slice; this note is therefore a targeted-slice verification claim, not a whole-repo formatting-baseline claim.
> - This packet remains the historical pre-code framing artifact and does not retroactively authorize wider strategy work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice only defines the next bounded pre-code candidate near a high-sensitivity strategy surface; the main risk is wording drift that could be mistaken for approval to perform a broader decision refactor or to alter thresholds/defaults
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice selects and bounds the next candidate without entering runtime implementation
- **Objective:** define the narrowest next pre-code candidate inside strategy/decision surfaces that reduces numeric fragility without changing decision policy, defaults, or gate ordering
- **Candidate:** `finite-numeric hardening for decision gate parsing`
- **Base SHA:** `66f97acc`

### Scope

- **Scope IN:** one docs-only packet; explicit description of the observed finite-numeric fragility in `src/core/strategy/decision_gates.py`; explicit relation to the finite/clamp precedent already present in `src/core/strategy/confidence.py`; exact likely future source/test scope for one bounded implementation packet only; explicit done criteria and stop conditions for that future packet
- **Scope OUT:** all code/test edits in this slice; all changes to thresholds, defaults, tie-break policy, EV formula, HTF/LTF gating, policy-router behavior, sizing behavior, config/schema semantics, paper/live behavior, readiness/promotion claims, or any claim that implementation is already approved
- **Expected changed files:** `docs/decisions/governance/decision_gate_finite_numeric_hardening_packet_2026-05-15.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that this packet remains docs-only and non-authorizing
- manual wording audit that the candidate stays narrower than a general decision refactor
- manual wording audit that valid finite-input behavior is described as unchanged unless a later code packet proves otherwise

### Stop Conditions

- any wording that treats this packet as implementation approval
- any wording that broadens the candidate from numeric hardening into general decision-policy redesign
- any wording that implies thresholds, defaults, or gate ordering should change as part of this packet
- any wording that silently absorbs `decision_fib_gating`, `decision_sizing`, `ri_policy_router`, config/schema, or paper/live surfaces into the same future slice

## Purpose

This packet answers one narrow question only:

- what is the next smallest strategy/decision hardening slice worth opening now that the runtime-config documentation ambiguity has already been resolved?

## Governing basis

The current read of the repo suggests a small but real numeric-hardening seam in the decision gate layer:

1. `src/core/strategy/decision_gates.py` defines `safe_float(...)`, which is defensive against `None` and invalid types but currently passes through convertible non-finite numerics such as `NaN` / `±inf`
2. the same module later performs several `int(...)` conversions from config/state-derived values, including persistence, guard-bar, hysteresis, cooldown, and decision-step paths
3. those two facts together create a plausible failure mode where strange numeric inputs are no longer just "invalid data" but can become either:
   - a runtime cast failure, or
   - a silent gate distortion if a non-finite float reaches comparison logic
4. `tests/utils/test_decision.py` already covers `None`, numeric strings, and non-numeric strings, but it does not currently anchor `NaN` / `±inf` behavior for these gate-adjacent paths
5. `src/core/strategy/confidence.py` already contains a local finite/clamp precedent (`_clamp01`, `_clamp`) that treats `NaN`/`±inf` as bounded defensive values rather than trusted numeric inputs

## Why this candidate is narrower than the other phase-4 examples

Compared with other sensitive candidates, this seam is the cheapest next move because it:

- does **not** widen config-authority or live-update policy
- does **not** require a broad strategy-family or policy-router redesign
- is likely containable to one gate-parsing module plus focused tests
- addresses a real failure mechanism without opening paper/live, promotion, or schema-authority questions

## Boundary decision

### Current standing conclusion

The next bounded high-sensitivity candidate should be framed as:

- **finite-numeric hardening for decision gate parsing in `decision_gates.py`**

This is a candidate-selection conclusion only. It is **not** approval to edit the strategy runtime yet.

### Likely future implementation scope

If this candidate is reopened as a real pre-code implementation packet, the smallest honest starting scope is likely:

- `src/core/strategy/decision_gates.py`
- `tests/utils/test_decision.py`

`src/core/strategy/decision.py` remains **OUT** for the initial slice. If later inspection shows that file must change, the work must stop, amend the packet/contract, and obtain fresh pre-code review before editing it.

### Likely future implementation scope OUT

A future packet for this candidate should keep the following out of scope unless separately reopened:

- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/ri_policy_router.py`
- confidence scaling semantics beyond reusing an existing finite-handling pattern as precedent
- config/schema files or runtime live-update surfaces
- paper/live, promotion, champion, or readiness implications

## What that future pre-code packet must define

A future implementation-bearing packet for this candidate must define at minimum:

- the exact numeric paths being hardened
- whether the change is limited to `safe_float(...)`, adjacent integer parsing, or both
- the exact fallback rule for non-finite numeric inputs
- what must remain unchanged for already-valid finite inputs
- the smallest focused test additions needed to prove no crash and no silent gate widening
- what code paths remain explicitly out of scope

## Future done criteria for the implementation slice

If the future implementation slice is opened, it should be considered done only if all of the following are true:

- non-finite numeric inputs in the named decision-gate parsing paths do not raise during gate evaluation
- non-finite values are handled only through the same invalid/missing-input path already used today; the slice must not create any path more permissive than current `None` / invalid handling
- those inputs do not widen entry permission relative to the current defensive/default path
- existing valid finite-input behavior remains unchanged across the targeted decision tests
- focused tests cover representative `NaN` / `+inf` / `-inf` cases for at least one float path and one int-cast-adjacent path
- finite-input parity is demonstrated with the existing focused decision tests plus those targeted `NaN` / `+inf` / `-inf` cases only; if broader fixtures, broader selectors, or cross-module edits are required, the slice must stop and reopen as a new packet

## Hard stop and reopen rule

If the future slice needs to change any of the following, it must stop and reopen as a separate bounded packet:

- threshold semantics or default values
- EV formulas or tie-break policy
- HTF/LTF fib gating behavior
- policy-router behavior
- sizing behavior
- config/schema authority or live-update semantics
- broad test rewrites outside the targeted decision-gate subset

## Bottom line

After the runtime-config clarification line, the next smallest risk-reducing move is not broader config policy and not a general strategy refactor. It is a separate bounded pre-code packet for **finite-numeric hardening in `src/core/strategy/decision_gates.py`**, with focused tests and explicit guarantees that valid finite-input behavior stays unchanged.
