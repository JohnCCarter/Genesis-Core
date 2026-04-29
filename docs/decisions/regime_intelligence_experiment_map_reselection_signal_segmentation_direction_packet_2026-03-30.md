# Regime Intelligence challenger family — experiment-map reselection direction packet

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `direction-selected / planning-only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet chooses exactly one orthogonal next hypothesis class after the fixed-surface slice8 upstream diagnostic path was closed, but must remain class-only and must not drift into surface selection, pre-code, admissibility, launch, implementation, comparison, readiness, or promotion semantics.
- **Required Path:** `Quick`
- **Objective:** Select exactly one next hypothesis class for experiment-map reselection after the current fixed-surface RI upstream diagnostic path was closed in current tracked state.
- **Candidate:** `future experiment-map reselection class choice`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** one docs-only direction decision selecting exactly one next hypothesis class; explicit closure respect; explicit 3h-anchor preservation; explicit not-chosen-now marking for neighboring same-class seam and for DECISION; explicit non-authorization boundary.
- **Scope OUT:** no source-code changes; no config YAML creation; no validator/preflight/smoke/optimizer execution; no new slice; no candidate-surface selection; no launch subject; no admissibility packet; no implementation path; no changes under `src/**`, `config/**`, `scripts/**`, or `tests/**`; no fib reopening; no reopening of the closed slice8 upstream diagnostic path; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that implies a runnable slice, concrete candidate surface, launch subject, admissibility path, or implementation path is already chosen
- any wording that reopens or extends the closed slice8 upstream diagnostic path
- any wording that makes `signal-adaptation` a second simultaneously chosen path
- any wording that changes timeframe, authority surface, or runtime contract by implication

## Purpose

This packet answers one narrow question only:

- what is the next chosen **hypothesis class** for experiment-map reselection after the current fixed-surface RI upstream diagnostic path was closed?

This packet is **planning-only governance**.

It does **not**:

- choose a runnable slice
- choose a concrete candidate surface
- create a launch subject
- define an admissibility path
- define an implementation path
- authorize validator/preflight/smoke/launch
- reopen comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence_upstream_diagnostic_path_closeout_2026-03-30.md`
- `docs/analysis/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/decisions/regime_intelligence_optuna_signal_lane_launch_admissibility_packet_2026-03-27.md`

Carried-forward meaning:

1. the current fixed-surface RI upstream diagnostic path on the slice8 surface is closed in current tracked state
2. the next admissible move is experiment-map reselection under separate governance
3. Phase 1 inventory has already established that multiple already implemented, research-only `3h` seams exist
4. this packet must therefore choose a **class orientation only**, not a runnable next step

## Non-reopen boundary

The closed slice8 upstream diagnostic path remains closed.

This packet does **not**:

- reopen that path
- extend that path
- derive a follow-on implementation lane from that path
- derive a follow-on diagnostic sub-lane from that path

The present choice is therefore an **orthogonal hypothesis-class orientation step**, not a continuation packet for the closed path.

## 3h anchor preserved

This direction preserves the `3h` anchor.

Meaning:

- it is based only on already inventoried, already implemented `3h` seams
- it does not change timeframe
- it does not change authority surface
- it does not change runtime contract
- it does not promote any alternative surface into a new target anchor by implication

## Candidate classes under decision

### Option 1 — SIGNAL / segmentation class

Meaning:

- keep the next move inside the broader `SIGNAL` class
- move attention to upstream segmentation-forming seams rather than renewed same-surface explanation or downstream decision tuning
- keep objective, EV, confidence, exit, and fib surfaces fixed

Class anchor:

- `regime-definition seam`

Neighboring same-class seam:

- `signal-adaptation seam`

Current suitability:

- **CHOSEN NOW**

Rationale:

- among the inventoried `3h` candidates, the SIGNAL-class seams are the most experiment-map-like because they act upstream of later decision and management surfaces
- `regime-definition` is the cleanest class anchor because it is the most clearly segmentation-forming seam in the current inventory
- `signal-adaptation` remains a same-class neighboring seam, but is not chosen now at the class-anchor level in this packet
- this keeps the next step orthogonal to the closed slice8 upstream diagnostic continuation while staying closer to candidate formation than a jump to downstream decision seams

Important boundary:

- choosing this class does **not** choose a runnable seam, candidate surface, YAML shape, parameter cluster, or launch subject
- `regime-definition` is chosen here only as the **class anchor**, not as an already selected runnable surface

### Option 2 — DECISION

Meaning:

- move the next step to downstream decision seams such as EV/edge or transition-guard posture

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- DECISION remains a valid future governance alternative
- it is not permanently rejected
- it is simply not the next chosen hypothesis class while an upstream SIGNAL segmentation route still exists in the already implemented `3h` inventory

## Decision

### Chosen next hypothesis class

- `CHOSEN — SIGNAL / segmentation class`

### Class anchor

- `regime-definition seam`

### Same-class neighboring seam

- `NOT CHOSEN NOW — signal-adaptation seam`

### Parked alternative class

- `NOT CHOSEN NOW — DECISION`

## Why this class is chosen

The next chosen class is `SIGNAL / segmentation` because the current governance record has already closed:

- fib as a non-informative lane for the current question
- the fixed slice8 upstream diagnostic continuation as the next admissible move on that surface

That leaves experiment-map reselection as the next safe planning step.

Within the inventoried `3h` seams, the cleanest orthogonal class is the one that can change **candidate segmentation posture** without reopening:

- downstream decision seams,
- objective/scoring seams,
- confidence seams,
- exit seams, or
- fib work.

`SIGNAL / segmentation` is therefore chosen because it stays upstream, preserves the `3h` anchor, and remains more map-selective than another explanatory continuation of the closed path.

## Explicit non-authorization boundary

This document chooses only **one orthogonal hypothesis class** for continued research orientation.

It does **not** choose:

- a runnable slice
- a concrete candidate surface
- a launch subject
- an admissibility packet
- an implementation path
- a YAML surface
- a validator/preflight/smoke path

Any such step requires later separate governance.

## Fixed surfaces in this class choice

The following remain fixed for the purpose of this class choice:

- fib lane closed
- current slice8 upstream diagnostic path closed
- objective/scoring class fixed
- EV surface fixed
- confidence surface fixed
- exit/management surface fixed
- family-registry and family-admission rules fixed
- comparison closed
- readiness closed
- promotion closed
- champion/default writeback closed

## What remains for later phases

This packet intentionally leaves the following unresolved for later separate governance:

- exact candidate-surface choice inside the chosen class
- exact packet boundary for any future pre-code work
- whether a future step remains docs-only or seeks research-level admissibility
- any future launch subject, smoke, or execution path

## Bottom line

The next chosen experiment-map reselection class is now:

- **SIGNAL / segmentation class**

With all of the following boundaries preserved:

- `3h` anchor preserved
- `regime-definition` chosen only as class anchor
- `signal-adaptation` same-class but **not chosen now**
- `DECISION` **not chosen now**
- the closed slice8 upstream diagnostic path remains closed
- no runnable surface, pre-code packet, launch subject, admissibility path, or implementation path is chosen here
