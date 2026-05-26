# Genesis-Core Edge Topology — Phase 3 attribution maps

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `fe591061`
Status: `completed / attribution map / supported annual-primary plus monthly-sidecar only`

## Purpose

This slice maps which state clusters recur inside stronger, weaker, and anti-edge periods on the current retained surfaces.

It does **not** widen into raw feature mining.
It maps only what can be read honestly from the retained annual pocket summaries, the shared-pocket proxy comparison, and the frozen monthly exact-subject triad.

## Scope

### Scope IN

- policy attribution map where retained annual summaries support it
- regime/state attribution map where retained annual summaries support it
- month-level local seam attribution on the frozen exact-subject triad
- explicit documentation of unsupported layers that remain unknown

### Scope OUT

- raw feature/indicator mining
- fabricated exit-family attribution on period surfaces that do not expose it
- unified monthly control claims that the retained monthly surface still cannot support
- runtime or tuning implications

## Evidence inputs

- `results/research/edge_topology/phase_2_period_comparisons/phase_2_period_comparison_bundle_annual_primary_with_monthly_sidecar_2019_2025.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.md`

## Emitted artifact

- `results/research/edge_topology/phase_3_attribution_maps/phase_3_attribution_map_annual_primary_with_monthly_sidecar_2019_2025.json`

## Observed

### 1. One annual shared pocket recurs across all selected topology classes

The annual primary cohort continues to show the same recurrent structural pocket:

- low-zone dominance
- bars-`8+` dominance
- `LONG -> NONE` as the largest action-diff flow
- `NONE -> LONG` as the second flow
- a policy split dominated by `RI_continuation_policy` and `RI_no_trade_policy`

So the first attribution result is deliberately negative in spirit:

- **the pocket itself is not the classifier**

It is background topology, not enough by itself to separate edge from anti-edge.

### 2. The annual control-positive cluster is continuation-dominant rather than suppressor-dominant

The annual control-positive subjects in the primary cohort are `2025` and `2022`.
They share:

- stronger `RI_continuation_policy` share (`63.78%` to `70.41%`)
- lighter `RI_no_trade_policy` share (`29.59%` to `36.22%`)
- lighter `AGED_WEAK_CONTINUATION_GUARD` share (`16.97%` to `19.86%`)
- enabled drawdown better than absent drawdown on both years

So the second attribution map result is:

- relative-beneficial annual periods currently map more cleanly to **continuation-dominant** local structure than to raw return sign alone

### 3. The annual control-negative cluster is suppressor-heavier

The annual control-negative subjects in the primary cohort are `2024` and `2019`.
They share:

- heavier `RI_no_trade_policy` mass (`35.59%` to `41.04%`)
- heavier `AGED_WEAK_CONTINUATION_GUARD` share (`20.47%` to `25.76%`)
- enabled drawdown worse than absent drawdown on both years

That remains true even though `2024` is still the strongest absolute year on the annual return ranking.

So the third attribution map result is:

- relative-harmful annual periods currently map to **suppressor-heavier** local structure rather than to “the pocket exists more”

### 4. The strongest annual attribution boundary is blocked-entry quality, not substituted-entry presence

The shared-pocket proxy comparison still provides the strongest separation on the blocked cohort:

- negative-year blocked median `fwd_16` = `+0.076866%`
- positive-year blocked median `fwd_16` = `-0.261849%`

The substituted continuation cohort does not separate as cleanly.

So the clearest annual attribution boundary is:

- whether the router is suppressing a cohort that still looks weak,
- or suppressing a cohort that has become flat / mildly positive on the same proxy surface.

### 5. The monthly attribution sidecar is local and comparator-family-specific

The frozen month triad does support one real local attribution map:

- all three exact subjects exercise the same continuation-release seam
- the sign split is not explained by broad phase placement alone
- the negative exact subject (`2018-03`) is distinguished by:
  - earlier release inside the cluster
  - weaker decisive-row support
  - longer path divergence from baseline

So the month-level attribution map is real, but narrow:

- it is a **local seam attribution map**, not a universal month map

### 6. Two expected attribution layers remain honestly unknown on current retained surfaces

The current retained period surfaces do **not** yet support a full:

- feature/indicator behavior map, or
- trigger-pattern / exit-family map

without reopening wider raw feature or ledger-like surfaces.

Those layers remain `unknown`, not omitted by accident.

## Inferred

### 1. Annual topology currently separates more by qualitative mix than by raw pocket presence

The attribution map now supports a more precise reading than Phase 2 alone:

- continuation-heavy mix tends to align with better control-relative outcomes
- suppressor-heavier mix tends to align with worse control-relative outcomes
- blocked-entry quality is a stronger separator than substituted-entry counts alone

### 2. The monthly seam behaves like a local boundary map, not a global score map

The month triad can help explain **why** one seam-active month differs from another.
It still cannot support a general statement about all months on the requested horizon.

## Unverified

- This slice does **not** prove that continuation-heavy mix is itself the cause of better control-relative annual outcome.
- This slice does **not** prove that the same attribution clusters will survive if the period set is widened beyond the current primary cohort.
- This slice does **not** prove that feature-level or exit-family-level maps would reinforce the same clustering if reopened later.

## Consequence

Phase 3 is now complete.
The lane has a supported attribution map strong enough to open failure-mode and anti-edge synthesis without reopening raw-source mining.

## What changed and what did not

What changed:

- the lane now has one explicit annual attribution map for shared, beneficial-relative, and harmful-relative period clusters
- the month sidecar is now mapped as a local seam boundary rather than left as an isolated note chain
- unsupported attribution layers are now explicitly frozen as unknown instead of left implicit

What did **not** change:

- no runtime behavior changed
- no raw feature mining was opened
- no false exit-family or indicator attribution was invented
