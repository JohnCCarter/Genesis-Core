# Genesis-Core Edge Topology — flat period structural coherence

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `5c515718`
Status: `completed / docs+artifact follow-up / observational only`

## Purpose

This bounded post-Phase-6 follow-up narrows one remaining canonical unknown:

> on the current retained month surface, do the flattest full months behave like sparse / no-trade windows, or like low-amplitude periods with still-present trading and no realized continuation-release seam effect?

This slice does **not** claim that the global `flat_period_structural_coherence` question is now fully solved.
It only asks what the currently retained flat month bucket honestly supports.

## Scope

### Scope IN

- inspect the frozen `flat_absolute` month bucket from Phase 1
- compare flat-month trade presence and amplitude against the frozen `top_absolute` and `worst_absolute` month buckets
- test whether the current retained monthly seam contributes any realized sign or action separation inside the flat bucket
- decide whether the Phase 5 / Phase 6 `flat_period_structural_coherence` unknown can be narrowed on the current retained surfaces
- emit one docs note and one machine-readable verdict artifact

### Scope OUT

- new backtests or helper-backed surface generation
- a general monthly `enabled vs absent` control map
- rewriting the currently locally modified Phase 5 / Phase 6 docs
- annual flat-period generalization beyond the current retained annual primary cohort
- runtime, tuning, or promotion claims

## Evidence inputs

- `docs/analysis/edge_topology/edge_topology_phase_1_period_rankings_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_1_period_rankings/month_rankings_2016_07_to_2026_03.json`
- `docs/analysis/edge_topology/edge_topology_phase_2_period_comparison_packs_2016_06_to_2026_04.md`
- `results/research/edge_topology/phase_2_period_comparisons/phase_2_period_comparison_bundle_annual_primary_with_monthly_sidecar_2019_2025.json`
- `docs/analysis/edge_topology/edge_topology_phase_6_canonical_summary_2016_06_to_2026_04.md`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`

## Emitted artifact

- `results/research/edge_topology/flat_period_followups/edge_topology_flat_period_structural_coherence_2026-05-27.json`

## Observed

### 1. The current flat month bucket is already frozen and bounded

Phase 1 already froze the current `flat_absolute` full-month bucket to:

- `2016-08`
- `2017-01`
- `2016-09`
- `2016-11`
- `2017-07`
- `2018-09`
- `2016-07`
- `2019-03`
- `2017-04`
- `2019-10`
- `2019-02`
- `2016-10`

So this slice does **not** reselect or re-rank flat months.
It only inspects the already frozen bucket.

### 2. The flat bucket is not a pure no-trade or empty-window bucket

The flat bucket carries retained trading activity:

- trade count minimum = `2`
- trade count median = `4.5`
- trade count maximum = `10`

For comparison on the same retained month surface:

- `top_absolute` trade count median = `5.5`
- `worst_absolute` trade count median = `7.0`

So the flat months are quieter on average, but they are **not** empty windows and **not** a zero-trade class.

### 3. The flat bucket is uniformly seam-inert on the current monthly comparator

On the current retained monthly comparator surface
(`continuation_release_hysteresis baseline vs release_zero`), all `12/12` flat months have:

- `action_diff_count = 0`
- `total_return_diff = 0.0`

So the current retained monthly seam contributes **no realized action split** and **no realized top-line split** anywhere inside the current flat bucket.

### 4. A few flat months still show metadata-only policy-route drift without realized action or return separation

Three flat months are not perfectly metadata-identical even though they are top-line identical on the current comparator:

- `2016-08` -> `selected_policy_diff_count = 12`, `switch_reason_diff_count = 12`
- `2016-07` -> `selected_policy_diff_count = 9`, `switch_reason_diff_count = 9`
- `2018-09` -> `selected_policy_diff_count = 3`, `switch_reason_diff_count = 3`

But even in those cases:

- `action_diff_count` stays `0`
- `total_return_diff` stays `0.0`

So the retained seam can still leave metadata-only traces without creating a realized month-level sign or action split.

### 5. The flat bucket is genuinely low-amplitude, not merely seam-suppressed

The current flat bucket has very small absolute month-level outcome amplitude:

- median absolute total return = `0.00264685%`

That is dramatically smaller than the same retained month-surface comparison buckets:

- `top_absolute` median absolute total return = `0.672280683%`
- `worst_absolute` median absolute total return = `0.903559748%`

So the flat bucket is genuinely low-amplitude on outcome scale, not merely “topline hidden by the current seam.”

### 6. Seam-inertness alone does not define a unique flat topology class

The current monthly comparator is inactive in many non-flat months too.
On the same retained month surface:

- `top_absolute` months also show `0/12` nonzero action diffs and `0/12` nonzero total-return diffs
- `worst_absolute` months also show `0/12` nonzero action diffs and `0/12` nonzero total-return diffs

So the flat bucket is uniformly seam-inert, but seam-inertness itself is **not unique** to flat months.

### 7. The annual flat read is still too thin to generalize

The current retained annual primary comparison pack contains only one explicit flat annual subject:

- `2019` -> `flat_absolute_and_control_negative`

That subject is useful, but one annual flat subject is not enough to claim a general annual flat topology class.

## Inferred

### 1. The current flat month bucket is better read as low-amplitude with still-present trading

The strongest honest current read is:

- flat months are **not** empty windows
- flat months are **not** a pure no-trade bucket
- flat months are low-amplitude periods with still-present trading activity

### 2. The current monthly seam is not the thing explaining flatness inside the bucket

Because the full flat bucket is action-inert and top-line-inert on the current retained seam comparator, the current continuation-release seam is not the observed driver of flatness on this surface.

### 3. The global `flat_period_structural_coherence` unknown should be narrowed, but not closed

This slice supports a narrower current reading:

- the retained flat month bucket is coherent as a **low-amplitude, seam-inert, still-trading** bucket on the current comparator family

But it does **not** support a stronger global claim because:

- the current month surface is comparator-family specific, not a general monthly control surface
- seam-inertness is not unique to flat months on that surface
- the retained annual flat read is still only one primary subject (`2019`)

So the honest status is:

- **narrow the unknown**
- **do not promote a new flat topology zone yet**

### 4. Metadata-only policy-route differences should remain observational only for now

The few flat months with policy/switch diffs but zero action and zero top-line diffs are interesting, but they do not currently justify any stronger sign, mechanism, or zone claim.

## Unverified

- whether a true monthly `enabled vs absent` control surface would preserve this low-amplitude flat-bucket read
- whether additional annual flat years would share the current `2019` control-negative read
- whether flat months split into multiple subtypes (for example low-noise quietness versus balanced cancellation) on wider retained surfaces
- whether the metadata-only route differences in `2016-08`, `2016-07`, and `2018-09` matter on any wider monthly control-relative surface

## Verdict

### Flat-period follow-up result

- **keep `flat_period_structural_coherence` globally `UNKNOWN`, but narrow the current retained month-level read**

### Narrowed current read

The current retained flat month bucket is best described as:

- low-amplitude
- still-trading
- seam-inert on the current `continuation_release_hysteresis baseline vs release_zero` comparator

### Promotion result

- **no new Edge Topology zone is promoted from this follow-up**

## Consequence

This follow-up prevents two easy mistakes:

- reading flat months as if they were simply empty / inactive windows
- reading seam-inertness as if it uniquely explained the flat class

The honest current answer is narrower and cleaner:

> on the retained month surface, flat months look like low-amplitude periods with real trading but no realized continuation-release seam effect; that sharpens the unknown, but does not yet solve the global flat topology question.

## What changed and what did not

What changed:

- the canonical flat-period unknown is now narrower on the retained month surface
- the flat bucket is now explicitly characterized as still-trading and low-amplitude rather than implicitly treated as a leftover bucket
- the current continuation-release seam is now explicitly ruled out as the observed driver of flatness on the retained flat month bucket

What did **not** change:

- no runtime behavior changed
- no new backtests were run
- no general monthly `enabled vs absent` surface was created
- no new topology zone was promoted
- the locally modified Phase 5 / Phase 6 docs and locally modified mixed-year JSON were left untouched by this slice
