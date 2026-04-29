# Regime Intelligence challenger family — experiment-map reselection candidate-surface packet

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `candidate-surface-selected / planning-only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows the already chosen `SIGNAL / segmentation` class to exactly one candidate surface, but must remain surface-selection-only and must not drift into pre-code, admissibility, launch, implementation, comparison, readiness, or promotion semantics.
- **Required Path:** `Quick`
- **Objective:** Select exactly one candidate surface inside the already chosen experiment-map reselection class after the current fixed-surface RI upstream diagnostic path was closed.
- **Candidate:** `future regime-definition candidate surface`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** one docs-only candidate-surface decision selecting exactly one seam inside the already chosen `SIGNAL / segmentation` class; explicit 3h-anchor preservation; explicit citation to one already implemented representative surface artifact; explicit not-chosen-now marking for the neighboring same-class seam and for DECISION; explicit non-authorization boundary.
- **Scope OUT:** no source-code changes; no config YAML creation; no validator/preflight/smoke/optimizer execution; no new slice; no pre-code packet; no launch subject; no admissibility packet; no implementation path; no changes under `src/**`, `config/**`, `scripts/**`, or `tests/**`; no fib reopening; no reopening of the closed slice8 upstream diagnostic path; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that turns the chosen surface into a runnable slice, launch subject, or implementation path
- any wording that treats the cited YAML artifact as already selected for execution rather than as a representative already implemented surface
- any wording that selects `signal-adaptation` as a second active seam
- any wording that reopens fib or the closed slice8 upstream diagnostic path
- any wording that changes timeframe, authority surface, or runtime contract by implication

## Purpose

This packet answers one narrow question only:

- inside the already chosen `SIGNAL / segmentation` class, what is the single next candidate surface for later separate governance?

This packet is **planning-only governance**.

It does **not**:

- choose a runnable slice
- create a launch subject
- define an admissibility path
- define an implementation path
- authorize validator/preflight/smoke/launch
- reopen comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence_upstream_diagnostic_path_closeout_2026-03-30.md`
- `docs/analysis/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/decisions/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- `docs/analysis/regime_intelligence_signal_regime_definition_roadmap_2026-03-27.md`

Carried-forward meaning:

1. the current fixed-surface RI upstream diagnostic path on the slice8 surface remains closed in current tracked state
2. Phase 1 already established that multiple already implemented, research-only `3h` seams exist
3. Phase 2 already selected `SIGNAL / segmentation` as the class orientation
4. this Phase 3 packet must therefore choose exactly one candidate surface inside that class and nothing more

## Non-reopen boundary

The closed slice8 upstream diagnostic path remains closed.

This packet does **not**:

- reopen that path
- extend that path
- derive a follow-on diagnostic slice from that path
- derive a follow-on implementation lane from that path

The present choice is therefore a **candidate-surface narrowing step**, not a continuation packet for the closed path.

## 3h anchor preserved

This candidate-surface choice preserves the `3h` anchor.

Meaning:

- it is bound to an already implemented `3h` seam
- it does not change timeframe
- it does not change authority surface
- it does not change runtime contract
- it does not promote an alternative discovery surface into a new target anchor

## Candidate surfaces under decision

### Option 1 — regime-definition seam

Exact seam:

- `multi_timeframe.regime_intelligence.regime_definition.*`

Representative already implemented artifact:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`

Current suitability:

- **CHOSEN NOW**

Why this seam is chosen:

- it is the most upstream segmentation-forming seam in the currently chosen class
- it varies regime-module ADX-band thresholds while keeping downstream decision, confidence, exit, and fib surfaces fixed
- it is the smallest viable seam most likely to alter information/regime segmentation rather than merely re-posture downstream thresholding
- it matches the earlier regime-definition planning line already documented in `docs/analysis/regime_intelligence_signal_regime_definition_roadmap_2026-03-27.md`

Important boundary:

- this packet selects the seam only
- the cited YAML serves only as the `3h`-anchored representative of an already implemented surface
- the cited YAML is **not** hereby made admissible, launchable, materialized, or promoted

### Option 2 — signal-adaptation seam

Exact seam:

- `thresholds.signal_adaptation.zones.{low,mid,high}.entry_conf_overall`

Representative already implemented artifact:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`

Current suitability:

- **NOT CHOSEN NOW**

Reason:

- it remains a valid in-class alternative
- it is more downstream than `regime-definition seam`
- after the closed threshold-only SIGNAL history, it is a weaker first candidate for experiment-map reselection than the more upstream segmentation-forming regime-definition seam

### Parked alternative outside class

- `NOT CHOSEN NOW — DECISION`

## Decision

### Chosen candidate surface

- `CHOSEN — regime-definition seam`

### Exact seam definition

- `multi_timeframe.regime_intelligence.regime_definition.*`

### Representative `3h` artifact citation

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`

### Not chosen now

- `signal-adaptation seam`
- `DECISION`

## Why this surface is chosen

This seam is chosen because it is the smallest viable surface that can still change **regime segmentation posture** without reopening:

- objective/scoring work
- EV work
- confidence work
- exit/management work
- fib work

Compared with `signal-adaptation`, `regime-definition` sits further upstream in the information-shaping path and is therefore more likely to produce binding change at the experiment-map level rather than another threshold-only retry.

That makes it the cleaner Phase 3 narrowing step after:

- the fixed slice8 upstream diagnostic path was closed, and
- `SIGNAL / segmentation` was already chosen as the class.

## Phase-separation boundary

Phase 2 resolved the **class choice**.

This Phase 3 packet resolves only the **candidate-surface choice inside that class**.

It does **not** resolve:

- a runnable slice design
- a pre-code packet
- an admissibility decision
- a launch path
- an implementation path

Any such step remains a separate future governance action.

## Explicit non-authorization boundary

This packet selects only one candidate surface for continued research orientation.

It does **not** choose:

- a runnable slice
- a search range or trial budget
- a launch subject
- an admissibility packet
- a validator/preflight/smoke path
- an implementation-enablement plan
- a promotion or writeback path

## Fixed surfaces in this candidate choice

The following remain fixed for the purpose of this candidate-surface choice:

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

- exact future packet boundary for any pre-code step
- whether the chosen seam is next handled docs-only or via research-level admissibility framing
- any future search ranges, fixed backdrop details, or falsification signatures
- any future launch subject, smoke, or execution path

## Bottom line

The single chosen candidate surface for the current experiment-map reselection track is now:

- **`multi_timeframe.regime_intelligence.regime_definition.*`**

With all of the following boundaries preserved:

- `3h` anchor preserved
- representative artifact cited but **not** authorized for launch
- `signal-adaptation` remains in-class but **not chosen now**
- `DECISION` remains **not chosen now**
- the closed slice8 upstream diagnostic path remains closed
- no runnable slice, pre-code packet, admissibility path, launch path, or implementation path is chosen here
