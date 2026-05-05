# Regime Intelligence challenger family — experiment-map reselection roadmap

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical predecessor / archive-only / planning-only / research sequencing / no launch authorization`

> Current status note:
>
> - [ARCHIVED 2026-05-05] This roadmap is no longer the active sequencing surface on `feature/next-slice-2026-05-05`; the March 30 chain proceeded into later packet-boundary and post-binding docs.
> - Preserve it as archived historical reselection context only.
> - Do not treat its phase ordering as a current launch path on the present branch.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this roadmap sequences the next research work after closing the fixed-surface RI upstream diagnostic path, but must not drift into slice creation, launch authorization, implementation, comparison, readiness, or promotion semantics.
- **Required Path:** `Quick`
- **Objective:** Define a phased roadmap for experiment-map reselection / binding-surface discovery after the current fixed-surface RI upstream diagnostic path was closed in current tracked state.
- **Candidate:** `future experiment-map reselection / binding-surface discovery path`
- **Base SHA:** `c27add49`

### Scope

- **Scope IN:** one docs-only roadmap that sequences the next planning work after the slice8-surface upstream diagnostic closeout; explicit closure anchor; explicit 3h target-anchor guardrail; explicit phase order; explicit stop conditions; explicit phase-1 inventory start inside this document only.
- **Scope OUT:** no source-code changes; no config YAML creation; no validator/preflight/smoke/optimizer execution; no new slice; no changes under `src/**`, `config/**`, `scripts/**`, or `tests/**`; no C2; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that implies launch authorization or admissibility is already granted
- any wording that opens a runnable slice, new YAML, or implementation path
- any wording that reopens the fib lane or the closed slice8 upstream diagnostic path
- any wording that promotes an alternative surface into a new target anchor by implication

## Purpose

This roadmap answers one narrow question only:

- what phased planning path should govern the next move after the current fixed-surface RI upstream diagnostic path was closed and experiment-map reselection became the next admissible move?

This roadmap is **planning-only governance**.

It does **not**:

- authorize a new slice
- authorize config creation for a new lane
- authorize validator/preflight/smoke/launch
- authorize implementation
- reopen comparison, readiness, promotion, or writeback

## Closure anchor

The starting point for this roadmap is fixed by:

- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_diagnostic_path_closeout_2026-03-30.md`

Carried-forward meaning:

1. the current fixed-surface RI upstream diagnostic path on the slice8 surface is closed in current tracked state
2. the next admissible move is experiment-map reselection under separate governance
3. the fib lane remains closed
4. another RI upstream slice on the same fixed slice8 surface is not the next admissible move

## Roadmap boundary

This roadmap sequences work in two separate layers:

- `roadmap` = phase order, sequencing, stop conditions, and required downstream packets
- `future packets` = later direction-selection, candidate-surface selection, and pre-code artifacts if separately governed

This document is not a runnable specification.
It is not a launch artifact.

## 3h target-anchor guardrail

For this roadmap, `3h` remains the **target anchor**.

Any alternative surface that may later be cited must remain **discovery-only** unless a separate governed packet says otherwise.

That means:

- alternative surfaces may be used only for binding-surface discovery or comparison reasoning
- they must not, by mention or inventory, become the new target anchor
- they must not open a surface jump by implication

## Planning stance

The roadmap proceeds under the following planning stance:

- keep the next move in `experiment-map reselection / binding-surface discovery`
- do **not** continue the closed slice8 upstream diagnostic path
- do **not** return to fib
- do **not** open another local RI internal tuning loop
- keep `3h` as the strategic anchor while inventorying already implemented, potentially more binding surfaces

## Phases

### Phase 0 — Preserve the closure

Goal:

- preserve the already closed state of the fixed-surface slice8 upstream diagnostic path

Required outcome:

- all downstream planning must explicitly state that the closed path is the slice8-surface upstream diagnostic continuation, not RI research as a whole

Stop if:

- any text starts speaking as if the slice8 upstream diagnostic path is still open
- any text implies another RI upstream slice on that same surface

### Phase 1 — Inventory candidate binding surfaces

Goal:

- document which already implemented, 3h-anchored surfaces are plausible candidates for experiment-map reselection and are more likely to produce binding behavior than the now-closed fixed slice8 upstream diagnostic surface

Boundary:

- this is a documentation-only inventory step
- it does **not** select one next hypothesis class yet
- it does **not** authorize any slice, config creation, or execution

Phase status:

- **started now** in this document, only in the sense that the initial inventory note below is recorded here

Initial inventory note:

- the repository already contains multiple implemented, research-only `3h` surfaces that are plausible experiment-map reselection candidates because they vary a single seam while preserving the broader slice8-backed anchor geometry
- current documented inventory set:
  1. `regime-definition seam`
     - artifact: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`
     - varies only `multi_timeframe.regime_intelligence.regime_definition.*` ADX-band thresholds
     - keeps the broader `3h` candidate-formation backbone fixed
  2. `signal-adaptation seam`
     - artifact: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`
     - varies only `thresholds.signal_adaptation.zones.{low,mid,high}.entry_conf_overall`
     - keeps regime-definition, risk-state, fib, exit cadence, and the broader entry/gating backbone fixed
  3. `decision transition-guard seam`
     - artifact: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`
     - varies only `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
     - keeps signal, regime-definition, fib, exit, and the plateau anchor otherwise fixed
  4. `decision EV/edge seam`
     - artifact: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
     - varies only `ev.R_default` and `thresholds.min_edge`
     - keeps regime-definition, signal-adaptation, transition-guard posture, fib, and exit surfaces fixed
- among the currently inventoried candidates, the first two are more clearly experiment-map-like than a renewed same-surface RI explanatory continuation because they act upstream of later decision and management surfaces
- the repository also already documents the relevant admissibility boundary for a future `SIGNAL` research lane in:
  - `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_lane_launch_admissibility_packet_2026-03-27.md`
- this inventory note does **not** select any of these surfaces as the next lane; it only records that already implemented, 3h-anchored candidates exist and are therefore admissible for later experiment-map reselection discussion

Stop if:

- inventory wording starts to behave like an approved implementation spec or launch packet

### Phase 2 — Select exactly one orthogonal hypothesis class

Goal:

- choose exactly one next hypothesis class that is conceptually distinct from the closed slice8 upstream diagnostic path and from fib

Status:

- **föreslagen**, not selected by this roadmap itself

Rule:

- the chosen class must not be another continuation of the current RI formulation
- it must not be fib
- it must not be another local tuning loop

Stop if:

- more than one next class remains active at the same time
- the choice implicitly reopens the closed slice8 upstream diagnostic path

### Phase 3 — Choose exactly one candidate surface

Goal:

- choose one smallest viable candidate surface more likely to produce binding conditions, adjudicable divergence, and measurable impact on candidate formation

Status:

- **föreslagen**, not selected by this roadmap itself

Rule:

- prefer the most upstream or segmentation-relevant already implemented surface that can change binding behavior without reopening objective, EV, confidence, exit, or fib work

Stop if:

- more than one candidate surface remains active at the same time
- the surface choice implies implementation or launch authority

### Phase 4 — Define future packet boundary

Goal:

- define what governance packet boundary would be required before any future runnable slice could exist

Status:

- **föreslagen**, not opened by this roadmap

This future boundary must explicitly answer later:

- what remains fixed
- what remains out of scope
- whether the next move is still docs-only or is ready for a separate pre-code packet

Stop if:

- packet-boundary wording behaves like a launch approval

### Phase 5 — Future pre-code packet only if separately governed

Goal:

- if and only if the earlier phases resolve cleanly, define one exact future pre-code packet for a bounded next slice

Status:

- **föreslagen**, not opened by this roadmap

Boundary:

- this roadmap does **not** create that packet
- a future runnable slice can only be considered after a separate pre-code packet and separate governance review

## Fixed surfaces during reselection

For the purpose of this roadmap, the following remain fixed:

- fib lane closed
- current slice8 upstream diagnostic path closed
- objective/scoring class fixed
- EV surface fixed
- confidence surface fixed
- exit/management surface fixed
- comparison closed
- readiness closed
- promotion closed
- champion/default writeback closed

## Bottom line

The next move is not another RI upstream diagnostic continuation on the fixed slice8 surface.

The next move is a **phased experiment-map reselection roadmap** that:

- preserves the current closures
- keeps `3h` as the target anchor
- starts directly only by documenting a phase-1 inventory of already implemented, 3h-anchored candidate binding surfaces
- defers any exact hypothesis choice, candidate-surface choice, or pre-code slice to later separately governed steps
