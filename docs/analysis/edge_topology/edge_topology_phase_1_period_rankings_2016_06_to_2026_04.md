# Genesis-Core Edge Topology — Phase 1 period rankings

Date: 2026-05-26
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `cdcfc5a632dab6afff9649933188b38474e0535b`
Status: `completed / observational ranking surface / no runtime authority`

## Purpose

This slice converts the initial Phase 0 anchor set into canonical machine-readable period ranking tables.

It does **not** explain why the periods differ yet.
It only freezes which periods belong to the current:

- strongest buckets
- weakest buckets
- flattest buckets
- positive-vs-control buckets where the comparator is valid
- negative-vs-control buckets where the comparator is valid
- unknown / insufficient-evidence buckets where the comparator is not yet valid

## Scope

### Scope IN

- canonical full-year ranking table on the current annual enabled-vs-absent surface
- canonical full-month ranking table on the current retained monthly inventory surface
- first stable bucket definitions for Phase 2 period comparison work
- docs summary of ranking semantics and the most important observed divergences

### Scope OUT

- runtime behavior changes
- tuning, optimization, or parameter search
- feature-causality claims
- unified monthly `enabled vs absent` claims that the current retained month surface does not support
- topology-zone promotion beyond ranking and bucket selection

## Evidence inputs

- `results/research/edge_topology/phase_0_period_inventory/period_inventory_summary_2016_06_to_2026_04.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`

## Emitted artifacts

- `results/research/edge_topology/phase_1_period_rankings/year_rankings_2017_to_2025.json`
- `results/research/edge_topology/phase_1_period_rankings/month_rankings_2016_07_to_2026_03.json`

## Observed

### 1. The year surface now has one canonical ranking table and one canonical bucket registry

The annual surface now has fixed ordered rankings for:

- `absolute_desc`
- `absolute_asc`
- `absolute_abs_asc`
- `delta_desc`
- `delta_asc`

And fixed first-pass year buckets:

- `top_absolute = [2024, 2025, 2020]`
- `worst_absolute = [2021, 2022, 2018]`
- `flat_absolute = [2019, 2018, 2017]`
- `positive_vs_control = [2022, 2025, 2018, 2020]`
- `negative_vs_control = [2021, 2024, 2023, 2019, 2017]`

These bucket labels are now stable enough for later comparison slices.

### 2. Absolute year strength and control-relative year strength clearly diverge

The strongest absolute years are currently:

1. `2024`
2. `2025`
3. `2020`

But the strongest control-relative years are:

1. `2022`
2. `2025`
3. `2018`
4. `2020`

That means the branch now has an explicit machine-readable split between:

- years where Genesis was strong in absolute terms
- years where Genesis most improved versus control

This is the first hard ranking proof that Edge Topology cannot be modeled as one axis only.

### 3. The month surface now also has one canonical ranking table, but with narrower comparator meaning

The month surface now has fixed ordered rankings for:

- `absolute_desc`
- `absolute_asc`
- `absolute_abs_asc`
- `delta_desc`
- `delta_asc`

And fixed first-pass month buckets:

- `top_absolute` = first `12` months on `absolute_desc`
- `worst_absolute` = first `12` months on `absolute_asc`
- `flat_absolute` = first `12` months on `absolute_abs_asc`
- `positive_toggle_delta = [2021-08, 2025-10]`
- `negative_toggle_delta = [2018-03]`
- `unknown_general_control = all_full_calendar_months_on_current_monthly_surface`

The strongest full months on the current retained month surface remain:

1. `2025-04`
2. `2021-01`
3. `2024-09`
4. `2025-12`
5. `2023-03`

The weakest full months remain:

1. `2024-12`
2. `2021-05`
3. `2021-04`
4. `2025-02`
5. `2021-06`

The flattest months begin with:

1. `2016-08`
2. `2017-01`
3. `2016-09`
4. `2016-11`
5. `2017-07`

### 4. Monthly delta remains useful but non-general

The current month-delta surface is still only:

- `continuation_release_hysteresis baseline vs release_zero`

So the month ranking file explicitly preserves:

- the current delta surface name
- the fact that a general monthly `enabled vs absent` control status is still `unknown_on_current_retained_surface`

This prevents later slices from mistakenly treating the current month-delta ordering as a universal Genesis-wide monthly edge ranking.

### 5. The new bucket registry is sufficient to start Phase 2 without ad hoc reselection

The branch can now choose comparison subjects from stable, already-written buckets instead of recomputing period orderings each time.

That means Phase 2 can ask better questions, such as:

- why `2024` is absolute-top but control-negative
- why `2022` is absolute-weak but control-positive
- what separates top absolute months like `2025-04` from worst months like `2024-12`
- whether flat periods are mostly noise, transition, or structurally distinct low-information states

## Inferred

### 1. Phase 2 should compare both aligned and misaligned period types

The best Phase 2 comparison set should not only use obvious winners and losers.
It should include at least one example of each:

- absolute-positive and control-positive
- absolute-positive but control-negative
- absolute-negative but control-positive
- absolute-negative and control-negative
- flat / near-flat

That will make the topology work far more informative than a simple best-vs-worst comparison.

### 2. The year surface is stronger than the month surface for control-relative claims at the moment

Because the annual comparator is already a true enabled-vs-absent surface, while the monthly delta surface is comparator-specific, the branch should expect:

- stronger control-relative claims at year level first
- weaker / more local control-relative claims at month level until a broader monthly control surface exists

### 3. Flat periods should be treated as their own topology class

The new ranking tables make it cheap to isolate near-zero periods.
Those are likely important for later distinguishing:

- low-signal environments
- cancellation / mixed-pressure environments
- states where policy motion is active but realized impact stays close to zero

## Unverified

- This slice does **not** prove that the selected top/worst/flat buckets form cleanly separable causal structures.
- This slice does **not** prove that month-level positive or negative toggle deltas generalize beyond the continuation-release hysteresis comparator.
- This slice does **not** prove that flat periods are a coherent market/system class rather than a mixed remainder bucket.
- This slice does **not** yet classify any edge domain as `ACTIVE`, `WEAK`, `REJECTED`, `SUPERSEDED`, or `UNKNOWN`; it only prepares the evidence ordering needed to do that later.

## Consequence

The next admissible step is now **Phase 2 — top / worst / flat period comparison packs**.

That phase should compare the content and system state of selected period buckets using the now-frozen Phase 1 ranking tables rather than re-mining periods ad hoc.

## What changed and what did not

What changed:

- the branch now has canonical year and month ranking tables for the first Edge Topology lane
- the branch now has fixed first-pass top / worst / flat bucket registries
- the year surface and month surface now carry explicit comparator semantics instead of implicit assumptions
- Phase 2 can now select periods from stable ranking files rather than from remembered snippets

What did **not** change:

- no runtime behavior changed
- no strategy behavior changed
- no tuning or optimization occurred
- no causal mechanism claim was made
- no topology zone was promoted beyond observational ranking status
