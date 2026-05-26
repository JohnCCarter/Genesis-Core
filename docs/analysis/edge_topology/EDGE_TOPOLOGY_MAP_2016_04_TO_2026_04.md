# Genesis-Core Edge Topology map — 2016-04 to 2026-04

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `cdcfc5a632dab6afff9649933188b38474e0535b`
Status: `phase-0 through phase-6 completed on current branch / observational only / no runtime authority`

## Purpose

This document opens the first canonical `Edge Topology` research lane for Genesis-Core.

The goal is to map, on bounded research-evidence surfaces, where Genesis-Core appears to:

- have edge
- have weak or unstable edge
- have no clear edge
- enter anti-edge states

across the requested long-horizon backtest window.

This document is intentionally a **living research-plan plus synthesis anchor**.
It does **not** claim that the topology is already known.
It only locks the phased route for discovering it without changing runtime behavior.

## Scope

### Scope IN

- docs-first Edge Topology research planning
- bounded research-evidence synthesis across already materialized backtest and replay-visible surfaces
- period ranking by year and month
- top / worst / flat period comparison framing
- policy / regime / decision / execution / trade / exit / failure-mode interpretation where supported by retained evidence
- support artifacts under `results/research/edge_topology/`

### Scope OUT

- runtime trading behavior changes
- parameter tuning or feature optimization
- new strategy behavior
- promotion, readiness, challenger, champion, or runtime-authority claims
- causal claims that exceed observational evidence
- pretending that all requested outputs can be landed honestly in one monolithic slice

## Global constraints

- Preserve determinism and governance rules.
- Treat this as research evidence, not promotion evidence.
- Separate `observed`, `inferred`, and `unverified`.
- Separate **absolute performance** from **marginal contribution versus control**.
- Treat full years, full calendar months, and partial edge periods separately.
- Do not claim causality from correlation.
- Do not silently unify incompatible comparator surfaces.

## Working Edge Topology definition

For this lane, `Edge Topology` means:

> the structured map of where Genesis-Core appears to have edge, weak edge, no clear edge, or anti-edge across combinations of market state, policy state, decision state, execution outcome, trade outcome, and control-relative comparison.

That map must include:

- edge domains
- edge boundaries
- anti-edge states
- unknown / insufficient-evidence zones
- the transitions where apparently similar periods diverge materially in outcome or control-relative contribution

## Requested horizon vs observed admissible coverage

The user-requested horizon is:

- `2016-04` to `2026-04`

The currently observed admissible curated coverage in repo-visible retained surfaces is narrower at the start boundary:

- common curated coverage start: `2016-06-07T00:00:00+00:00`
- common curated coverage end: `2026-04-15T00:00:00+00:00`
- full years currently visible on the annual surface: `2017` through `2025`
- full calendar months currently visible on the monthly inventory surface: `2016-07` through `2026-03`

So the topology target remains the user-requested long horizon, but the first admissible evidence map must honestly anchor itself to the current retained coverage rather than silently inventing April–May 2016 full-period truth.

## Phase structure

### Phase 0 — coverage lock and observed period inventory

**Goal**

Lock the current admissible evidence surfaces, record the real coverage boundary, and emit the first observed year/month ranking anchor set.

**Deliverables**

- this document
- `results/research/edge_topology/phase_0_period_inventory/period_inventory_summary_2016_06_to_2026_04.json`

**Status**

- `completed in this turn`

### Phase 1 — canonical year/month performance ranking tables

**Goal**

Produce the first canonical ranking tables for:

- strongest full years
- weakest full years
- flattest full years
- strongest full months
- weakest full months
- flattest full months
- strongest periods by control-relative delta where a valid comparator exists

**Required outputs**

- one docs note summarizing the ranking surfaces
- machine-readable year and month ranking tables under `results/research/edge_topology/phase_1_period_rankings/`
- explicit comparator-semantics labels so year-delta and month-delta surfaces are not conflated
- `docs/analysis/edge_topology/edge_topology_phase_1_period_rankings_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_1_period_rankings/year_rankings_2017_to_2025.json`
- `results/research/edge_topology/phase_1_period_rankings/month_rankings_2016_07_to_2026_03.json`

**Done means**

- the branch has one stable ranking surface for period selection
- top / worst / flat candidate buckets can be selected without ad hoc reranking in later slices

**Status**

- `completed on current branch`

### Phase 2 — top / worst / flat period comparison packs

**Goal**

Compare the content and system state of selected period buckets instead of only their return labels.

**Compare and inventory**

- decision behavior
- policy activation
- regime/state mix
- execution / non-execution patterns
- exit-family mix
- drawdown behavior
- failure-mode concentration

**Required outputs**

- one top-vs-worst-vs-flat comparison note
- one machine-readable period comparison artifact bundle

**Done means**

- the lane has one bounded annual primary comparison pack spanning distinct topology classes
- the lane has one explicit monthly sidecar instead of a fake general monthly control surface
- later attribution and failure-mode phases can reuse a frozen comparison bundle rather than reselect periods ad hoc

**Outputs landed on current branch**

- `docs/analysis/edge_topology/edge_topology_phase_2_period_comparison_packs_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_2_period_comparisons/phase_2_period_comparison_bundle_annual_primary_with_monthly_sidecar_2019_2025.json`

**Status**

- `completed on current branch`

### Phase 3 — attribution-layer period maps

**Goal**

Map which state clusters appear repeatedly inside strong, weak, and anti-edge periods.

**Sub-slices expected inside this phase**

1. policy attribution map
2. regime/state attribution map
3. feature/indicator behavior map where supported by replay-visible or retained evidence surfaces
4. trigger-pattern map for take-profit / stop-loss / trailing / manual-or-other exits

**Important boundary**

This phase must prefer currently observable or deterministically derivable surfaces.
It must not quietly widen into full raw-feature mining unless a later slice explicitly opens that question.

**Required outputs**

- one attribution-map note
- one machine-readable attribution-map artifact
- explicit unknown labels for unsupported attribution layers

**Done means**

- the lane can distinguish shared background structure from relative-beneficial and relative-harmful annual clusters
- the month-sidecar seam is mapped as a local attribution surface rather than a global month rule

**Outputs landed on current branch**

- `docs/analysis/edge_topology/edge_topology_phase_3_attribution_maps_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_3_attribution_maps/phase_3_attribution_map_annual_primary_with_monthly_sidecar_2019_2025.json`

**Status**

- `completed on current branch`

### Phase 4 — failure-mode and anti-edge topology

**Goal**

Identify repeated losing structures, anti-edge states, and the boundaries where seemingly similar periods separate into good versus harmful outcomes.

**Required outputs**

- failure-mode map
- anti-edge map
- first explicit boundary inventory between edge and anti-edge neighborhoods

**Outputs landed on current branch**

- `docs/analysis/edge_topology/edge_topology_phase_4_failure_and_anti_edge_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_4_failure_mode_maps/phase_4_failure_and_anti_edge_map_2016_06_to_2026_04.json`

**Status**

- `completed on current branch`

### Phase 5 — edge zones / anti-edge zones / unknown zones synthesis

**Goal**

Promote only the repeated and evidenced structures into provisional topology zones.

**Zone labels must use exactly one of**

- `ACTIVE`
- `WEAK`
- `REJECTED`
- `SUPERSEDED`
- `UNKNOWN`

**Important boundary**

No zone may be promoted to `ACTIVE` from one-off local period behavior alone.
Repeated support across admissible periods is required.

**Required outputs**

- one zone-synthesis note
- one machine-readable provisional zone registry

**Outputs landed on current branch**

- `docs/analysis/edge_topology/edge_topology_phase_5_zone_synthesis_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_5_zone_synthesis/phase_5_provisional_zone_registry_2016_06_to_2026_04.json`

**Status**

- `completed on current branch`

### Phase 6 — canonical Edge Topology summary

**Goal**

Close the lane with one bounded synthesis of:

- edge zones
- anti-edge zones
- weak / unstable zones
- unknown zones
- open contradictions and unresolved boundaries

**Done means**

- the branch can explain where Genesis-Core appears strong, weak, neutral, or harmful
- the synthesis still remains observational and non-authorizing
- future runtime/tuning ideas remain explicitly separate from this evidence layer

**Outputs landed on current branch**

- `docs/analysis/edge_topology/edge_topology_phase_6_canonical_summary_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_6_canonical_summary/edge_topology_summary_2016_06_to_2026_04.json`

**Status**

- `completed on current branch`

## Phase 0 — observed starting inventory

## Observed

### 1. Two distinct ranking axes already exist and must stay separate

Observed repo-visible retained surfaces already support two different kinds of ranking:

1. **absolute period performance**
2. **control-relative contribution**

That distinction is non-optional.
A period can be strong in absolute terms while still being a period where Genesis underperforms a control.

### 2. The current annual control-relative surface already supports full-year ranking on `2017` through `2025`

Observed annual evidence anchor:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`

Observed strongest full years by enabled absolute return:

1. `2024` -> `4.7456288772%`
2. `2025` -> `2.9268659989%`
3. `2020` -> `1.8645825546%`
4. `2023` -> `0.9902908235%`
5. `2017` -> `0.3488837885%`

Observed weakest full years by enabled absolute return:

1. `2021` -> `-1.9784226387%`
2. `2022` -> `-0.8766808546%`
3. `2018` -> `-0.3227125070%`
4. `2019` -> `-0.2487735097%`
5. `2017` -> `0.3488837885%` as the nearest still-positive weak edge of the visible full-year set

Observed flattest full years by absolute enabled return magnitude:

1. `2019` -> `-0.2487735097%`
2. `2018` -> `-0.3227125070%`
3. `2017` -> `0.3488837885%`
4. `2022` -> `-0.8766808546%`
5. `2023` -> `0.9902908235%`

Observed strongest full years by control-relative delta (`enabled - absent`):

1. `2022` -> `+1.8745614229 pp`
2. `2025` -> `+1.6954792056 pp`
3. `2018` -> `+0.3174597209 pp`
4. `2020` -> `+0.2500036580 pp`
5. `2017` -> `-0.0875312357 pp`

That already proves the first topology rule:

- **best absolute years are not the same thing as best edge-contribution years**

### 3. The current monthly inventory supports full-calendar-month absolute ranking on `2016-07` through `2026-03`

Observed monthly inventory anchor:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`

Observed strongest full months by baseline absolute return on that monthly surface:

1. `2025-04` -> `1.9593912600%`
2. `2021-01` -> `0.8295508292%`
3. `2024-09` -> `0.8138095250%`
4. `2025-12` -> `0.7761853779%`
5. `2023-03` -> `0.7013334757%`
6. `2022-03` -> `0.6831308460%`
7. `2025-05` -> `0.6614305200%`
8. `2021-07` -> `0.6135645042%`

Observed weakest full months by baseline absolute return on that monthly surface:

1. `2024-12` -> `-1.5325508637%`
2. `2021-05` -> `-1.4150030471%`
3. `2021-04` -> `-1.0926593500%`
4. `2025-02` -> `-1.0714201485%`
5. `2021-06` -> `-0.9652926440%`
6. `2025-08` -> `-0.9294220000%`
7. `2024-06` -> `-0.8776974960%`
8. `2026-01` -> `-0.7876839675%`

Observed flattest full months by absolute baseline return magnitude:

1. `2016-08` -> `-0.0000577840%`
2. `2017-01` -> `-0.0000772932%`
3. `2016-09` -> `-0.0003336073%`
4. `2016-11` -> `0.0004515451%`
5. `2017-07` -> `0.0022375269%`
6. `2018-09` -> `-0.0026391137%`
7. `2016-07` -> `-0.0026545859%`
8. `2019-03` -> `-0.0043712200%`

### 4. The currently visible month-delta surface is narrower in meaning than the annual enabled-vs-absent delta surface

Observed strongest months by visible monthly delta on the retained monthly inventory:

1. `2021-08` -> `+0.1889008634 pp`
2. `2025-10` -> `+0.1713484012 pp`

But the semantics of that monthly delta are currently:

- `continuation_release_hysteresis` baseline vs `release_zero`

not:

- general Genesis `enabled vs absent`
- general all-policy monthly contribution

So the month-delta surface is useful, but it cannot yet be treated as a universal monthly edge-contribution map.

### 5. Mixed-year month-shape notes already reveal non-trivial topology structure

Observed docs-visible mixed-year month-shape anchors already exist:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`

Observed locked month-shape findings from those notes:

- `2023` top combined month = `December`
- `2023` top continuation month = `December`
- `2023` top suppression month = `June`
- `2017` top combined month = `July`
- `2017` top continuation month = `March`
- `2017` top suppression month = `June`

So the repo already hints that:

- different mixed years can share one topology component (`June` suppression lead)
- while diverging sharply on others (`December` vs `July` / `March` leadership)

## Inferred

### 1. Edge Topology must be at least two-axis from the start

The current observed surfaces already imply that a one-axis “best periods” map would be too crude.
The lane must separate at minimum:

1. absolute performance quality
2. control-relative contribution quality

### 2. Month-level topology will likely need comparator-family separation before unification

The annual delta surface and the currently retained monthly delta surface do not yet measure the same thing.
So the branch should expect Phase 1 and Phase 2 to keep comparator families separate until a later slice can unify them honestly.

### 3. Anti-edge should be treated as a first-class topology object, not as a leftover bucket

The observed year and month rankings already show periods that are:

- strong in absolute terms
- weak versus control
- or flat enough that structural interpretation may be fragile

That means `anti-edge` and `unknown` cannot be afterthoughts.
They need their own first-class map surfaces.

## Unverified

- This branch has **not** yet verified that the same topology zones repeat robustly across multiple adjacent years and months.
- This branch has **not** yet verified that a single unified feature/indicator map can be derived honestly from the currently retained surfaces without reopening wider raw-source mining.
- This branch has **not** yet verified that the strongest and weakest periods form stable, cleanly separable edge neighborhoods rather than overlapping mixed structures.
- This branch has **not** yet verified that the current monthly delta surface can be generalized beyond the specific continuation-release hysteresis comparator.

## Lane completion status

The current bounded Edge Topology lane is complete through **Phase 6**.

If this lane is reopened later, the next admissible follow-up is **not** another pass over the same bounded pack.
It would need a fresh bounded slice that explicitly widens one currently frozen gap, for example:

1. a general monthly `enabled vs absent` control surface
2. flat-period structural-coherence testing beyond the current anchor set
3. feature / indicator behavior mapping from reopened raw-feature surfaces
4. trigger-pattern / exit-family mapping from a wider retained period surface

## What changed and what did not

What changed:

- the branch now has a branch-current Edge Topology research plan
- the lane is phased rather than left as one giant “analyze everything” request
- Phase 0 has already locked real coverage boundaries and initial period-ranking anchors
- Phase 1 has now materialized canonical year and month ranking tables plus first-pass bucket registries
- Phase 2 has now frozen one annual-primary comparison pack plus one explicit monthly-sidecar bundle
- Phase 3 has now materialized one bounded attribution map with explicit unsupported layers marked unknown
- Phase 4 has now materialized one failure-mode and anti-edge boundary map
- Phase 5 has now materialized one provisional zone registry using controlled labels
- Phase 6 has now materialized one canonical bounded summary artifact

What did **not** change:

- no runtime behavior changed
- no strategy behavior changed
- no tuning or optimization was performed
- no topology zone has been promoted as runtime or durable truth
- no causal claim was made
