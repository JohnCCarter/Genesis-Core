# Genesis-Core Edge Topology — monthly general control surface feasibility

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `8d8e972b`
Status: `completed / docs+artifact follow-up / observational only`

## Purpose

This bounded post-Phase-6 follow-up asks a concrete reopen-gate question:

> can a true monthly `enabled vs absent` control surface be honestly derived from the current retained repo-visible artifacts, or is the current `monthly_general_control_surface` still blocked by a material artifact gap?

This slice does **not** generate a new monthly control surface.
It does **not** reopen helper-backed artifact generation.
It does **not** edit the currently locally modified canonical Phase 5 / Phase 6 docs.

## Scope

### Scope IN

- audit the current retained monthly artifact surfaces already referenced by the Edge Topology lane
- determine whether a general monthly `enabled vs absent` control surface is already repo-visible on current retained artifacts
- distinguish a real artifact-gap blocker from a mere interpretive caution
- emit one docs note and one machine-readable feasibility verdict

### Scope OUT

- new backtests or helper-backed surface generation
- reconstructing a monthly control surface from non-retained intermediates
- editing the currently locally modified Phase 5 / Phase 6 docs
- runtime, tuning, or promotion claims

## Evidence inputs

- `results/research/edge_topology/phase_1_period_rankings/month_rankings_2016_07_to_2026_03.json`
- `results/research/edge_topology/phase_2_period_comparisons/phase_2_period_comparison_bundle_annual_primary_with_monthly_sidecar_2019_2025.json`
- `results/research/edge_topology/phase_3_attribution_maps/phase_3_attribution_map_annual_primary_with_monthly_sidecar_2019_2025.json`
- `results/research/edge_topology/phase_5_zone_synthesis/phase_5_provisional_zone_registry_2016_06_to_2026_04.json`
- `docs/analysis/edge_topology/edge_topology_phase_1_period_rankings_2016_06_to_2026_04.md`
- `docs/analysis/edge_topology/edge_topology_phase_6_canonical_summary_2016_06_to_2026_04.md`
- `docs/analysis/edge_topology/edge_topology_monthly_overlay_translation_adjudication_2026-05-27.md`
- repo-visible results path scan for monthly `enabled vs absent` artifacts under `results/**`

## Emitted artifact

- `results/research/edge_topology/monthly_surface_followups/edge_topology_monthly_general_control_surface_feasibility_2026-05-27.json`

## Observed

### 1. The canonical month ranking surface is still not a general monthly `enabled vs absent` surface

Phase 1 already froze the current month rankings to one source artifact:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`

That ranking artifact explicitly records:

- `delta_surface = continuation_release_hysteresis baseline vs release_zero`
- `general_monthly_enabled_vs_absent_control = unknown_on_current_retained_surface`

So the main canonical month ranking surface itself does **not** claim a general monthly control map.

### 2. The canonical Phase 2 bundle also preserves a monthly sidecar, not a monthly control surface

Phase 2 explicitly routes monthly evidence through the frozen exact-subject triad only.
Its unsupported dimensions already include:

- `monthly_general_enabled_vs_absent_control_unknown_on_current_retained_surface`

So the monthly sidecar was frozen as a local comparator-family pack, not as the missing general control surface.

### 3. The canonical Phase 3 attribution map still marks the general monthly enabled-vs-absent layer as unsupported

The current Phase 3 attribution artifact explicitly records:

- `general_monthly_enabled_vs_absent_map = unknown_on_current_monthly_inventory_surface`

So even after attribution mapping, the branch still does not have a retained general monthly control map.

### 4. The canonical Phase 5 / Phase 6 lane already classifies this as a first-class gap

Phase 5 registers:

- `monthly_general_control_surface -> UNKNOWN`

with the explicit reason:

- the current retained month surface does not yet expose a general enabled-vs-absent control map

Phase 6 carries the same unknown forward unchanged.
So the current blocker is already canonical, not accidental.

### 5. The monthly overlay translation follow-up sharpened the reason for the unknown

The already landed monthly overlay translation slice makes the current month surface boundary even tighter:

- it measures only `continuation_release_hysteresis baseline vs release_zero`
- it is useful local evidence
- it is **not** the month-level analogue of the annual enabled-vs-absent surface

So the current unknown is now sharper than “not yet proven.”
It is a concrete surface mismatch.

### 6. Repo-visible retained artifact scan does not reveal a monthly `enabled vs absent` result surface

A repo-visible path scan for retained results matching monthly + `enabled` + `absent` naming under `results/**` returned no files.

At the same time, the explicit retained `enabled_vs_absent` references used by the Edge Topology lane point to:

- annual / all-years summaries
- annual action-diff files
- bounded annual evidence notes

not to a retained monthly `enabled vs absent` artifact family.

So on the current retained repo-visible artifact set, the missing monthly control surface is not just undocumented; it is not presently materialized as a retained surface the lane can cite.

## Inferred

### 1. A true monthly `enabled vs absent` control surface is **not currently feasible** from retained repo-visible artifacts alone

This is the core feasibility verdict.

The current branch has:

- annual `enabled vs absent` evidence
- a comparator-family-specific monthly seam inventory
- monthly local exact-subject evidence

It does **not** currently have:

- a retained repo-visible monthly `enabled vs absent` summary surface
- a retained repo-visible monthly action-diff family on that control pairing
- a canonical Edge Topology artifact that bridges the current seam inventory into a general monthly control map

So the monthly general control surface remains blocked by a material artifact gap.

### 2. `monthly_general_control_surface` should remain `UNKNOWN` for structural reasons, not for lack of nerve

The lane is not hesitating because it forgot to decide.
It is staying `UNKNOWN` because the currently retained surfaces do not expose the needed comparator family.

### 3. Reopening this gap now would require an explicit new materialization slice

The next admissible reopen is not more reinterpretation of the current seam bench.
It is an explicit bounded slice that authorizes one of:

- generating a true monthly `enabled vs absent` control surface
- materializing retained monthly control-relative artifacts
- proving an honest bridge from retained annual control evidence plus retained monthly surfaces without silently changing comparator semantics

### 4. No new monthly zone promotion is justified from this feasibility check

This slice closes a blocker question.
It does **not** justify:

- upgrading `monthly_general_control_surface`
- promoting a new monthly zone
- reclassifying the current seam inventory as a general monthly control map

## Unverified

- whether a newly generated monthly `enabled vs absent` control surface would confirm or refute the current annual-to-month translation read
- whether the narrowed flat-month read would survive on a true monthly control surface
- whether a later governed bridge slice could reuse existing annual action-diff artifacts to build an honest monthly control surface without regeneration

## Verdict

### Feasibility result

- **keep `monthly_general_control_surface` as `UNKNOWN` and treat it as currently blocked by a material retained-artifact gap**

### Current blocker read

The blocker is not merely interpretive caution.
It is that the repo currently exposes:

- annual `enabled vs absent`
- monthly seam-specific `baseline vs release_zero`

but **not**:

- a retained monthly `enabled vs absent` control surface

### Promotion result

- **no new Edge Topology zone is promoted from this follow-up**

## Consequence

This follow-up matters because it prevents a second subtle drift:

- pretending that enough careful wording can substitute for a missing comparator surface

The honest current answer is now explicit:

> `monthly_general_control_surface` is still `UNKNOWN` because the retained repo-visible lane does not currently contain the needed monthly `enabled vs absent` artifact family; closing that gap requires a new explicit materialization slice, not a reinterpretation of the current seam inventory.

## What changed and what did not

What changed:

- the monthly general control gap is now explicitly classified as a retained-artifact feasibility blocker
- the branch now has a sharper reopen condition for the monthly control unknown
- the current seam inventory is now explicitly separated from the missing general monthly control surface at the feasibility level, not just at the interpretation level

What did **not** change:

- no runtime behavior changed
- no new backtests were run
- no monthly control surface was generated
- no new topology zone was promoted
- the locally modified Phase 5 / Phase 6 docs, locally modified flat-period artifact JSON, and locally modified mixed-year JSON were left untouched by this slice
