# Regime Intelligence challenger family — SIGNAL regime-definition roadmap

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `planning-only / research sequencing / no launch authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this roadmap sequences the next RI research work after closing SIGNAL slice1 as plateau, but must not drift into admissibility, launch, runtime-validity, or promotion semantics
- **Required Path:** `Quick`
- **Objective:** Define a phased roadmap for the next RI research direction after closing the zone-entry-threshold SIGNAL surface as non-improving.
- **Candidate:** `future RI SIGNAL regime-definition research lane`
- **Base SHA:** `d227be7e`

### Scope

- **Scope IN:** one docs-only roadmap that sequences the next research work, preserves the slice1 closure, and identifies the next planning artifacts required before any future runnable lane may exist.
- **Scope OUT:** no source-code changes, no config YAML creation, no validator/preflight/smoke/optimizer execution for a new lane, no changes under `src/core/**`, no changes under `scripts/**`, no changes under `config/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no slice2, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/analysis/regime_intelligence_signal_regime_definition_roadmap_2026-03-27.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that implies launch authorization or admissibility is already granted
- any wording that implies runtime-valid RI conformity
- any wording that creates a runnable slice spec in this roadmap
- any wording that reopens slice2, comparison, readiness, promotion, or writeback

## Purpose

This roadmap answers one narrow question only:

- what phased planning path should govern the next RI research move after SIGNAL slice1 was closed as plateau?

This roadmap is **planning-only governance**.

It does **not**:

- authorize slice2
- authorize config creation for a new lane
- authorize validator/preflight/smoke/launch
- grant runtime-valid RI conformity
- reopen comparison, readiness, promotion, or writeback

## Closure anchor

The starting point for this roadmap is fixed by the already tracked slice1 outcome:

- `docs/decisions/regime_intelligence_optuna_signal_slice1_execution_outcome_signoff_summary_2026-03-27.md`

Carried-forward meaning:

1. `SIGNAL slice1` on **zone entry thresholds** is closed as `PLATEAU`
2. this closes that **specific surface only**
3. it does **not** close the broader `SIGNAL` research class
4. the next step is **not** slice2 on the same surface

## Roadmap boundary

This roadmap sequences work in two separate layers:

- `roadmap` = phase order, sequencing, stop conditions, and required downstream packets
- `direction packet` = exactly one next chosen research direction and why

Neither document is a runnable specification.
Neither document is a launch artifact.

## Chosen planning stance

The roadmap proceeds under the following planning stance:

- keep the next direction in the `SIGNAL` class
- move the next investigation **upstream** from zone entry thresholds to **regime-definition surface**
- keep `DECISION` parked as an available future alternative rather than rejecting it permanently
- keep objective, EV, confidence, and exit surfaces fixed in this next direction choice

## Phases

### Phase 0 — Anchor the closure

Goal:

- preserve the already closed state of `SIGNAL slice1`

Required outcome:

- all downstream work must explicitly state that the closed surface is `zone entry thresholds`, not the entire `SIGNAL` class

Stop if:

- any text starts speaking as if slice1 is still open
- any text implies slice2 on the same surface

### Phase 1 — Narrow the next direction

Goal:

- select exactly one next research direction inside the still-open `SIGNAL` class

Required outcome:

- one direction packet choosing `SIGNAL / regime-definition surface`
- `DECISION` marked as `not chosen now`

Stop if:

- more than one next direction is chosen
- `DECISION` is described as permanently rejected

### Phase 2 — Surface inventory

Goal:

- document which upstream regime-definition surfaces are already implemented and why they are more relevant than another threshold-only retry

Expected evidence basis:

- `src/core/strategy/regime.py`
- `src/core/strategy/regime_unified.py`
- `src/core/intelligence/regime/authority.py`

Boundary:

- these code surfaces may be cited as rationale only
- this phase does **not** authorize implementation or tuning of any one surface yet

Stop if:

- inventory wording starts to behave like an approved implementation spec

### Phase 3 — Narrow candidate selection

Goal:

- choose one smallest viable regime-definition candidate surface for later governance

Candidate selection rule:

- prefer the most upstream surface that can change information/regime segmentation without reopening objective, EV, confidence, or exit classes

Important note:

- if the chosen regime-definition surface is not yet externally tunable via existing config authority, the next step may need an **implementation-enablement packet** before any optimizer slice exists

Stop if:

- more than one candidate surface remains active at the same time
- the candidate spills into `DECISION` or `OBJECTIVE`

### Phase 4 — Authority/admissibility packet

Goal:

- define what governance boundary would be required before a new regime-definition lane could become launch-admissible at research authority

This phase must explicitly answer later:

- is the next lane config-only, or does it require implementation-enablement first?
- what fixed backdrop remains locked?
- what remains outside scope?

Boundary:

- this roadmap does **not** create that admissibility packet

### Phase 5 — First pre-code slice packet

Goal:

- if and only if Phase 4 resolves authority cleanly, define one exact first admissible regime-definition slice

This future packet must eventually define:

- exact candidate surface
- exact fixed backdrop
- exact expected improvement signature
- exact falsification condition
- exact future artifacts

Boundary:

- this roadmap does **not** create a runnable YAML
- this roadmap does **not** authorize smoke or launch

### Phase 6 — Later execution path (separately governed)

Only after the earlier packets exist may a later flow be considered:

1. validator
2. preflight
3. smoke
4. launch authorization
5. full execution
6. outcome signoff

Boundary:

- none of those steps are opened by this roadmap

### Phase 7 — Future decision gate

Only after a separately authorized future lane runs may a later decision gate classify the outcome as:

- improvement
- plateau
- degradation

Boundary:

- this roadmap creates no such decision now

## Parked alternative

`DECISION` remains a parked alternative for future governance review.

Meaning:

- it is **not chosen now** for the next lane
- it is **not permanently rejected**
- it may be revisited later if the regime-definition route also fails to produce uplift

## Fixed surfaces for the next direction choice

For the purpose of this roadmap, the following surfaces remain fixed:

- objective/scoring class
- EV surface
- confidence surface
- exit/management surface
- family-registry and family-admission rules
- comparison closed
- readiness closed
- promotion closed
- champion/default writeback closed

## Bottom line

The next RI move is planned as a **new SIGNAL direction on regime-definition surface**, not as slice2 and not as a jump to DECISION.

This roadmap sequences the work in phases, keeps the previous closure intact, and makes clear that launch/admissibility/runnable-slice work must come later through separate governance packets.
