# RI advisory environment-fit — Phase 3 partial baseline label-gap verdict

This memo is docs-only and fail-closed.
It records the outcome of the bounded partial-baseline preflight run on the Phase C capture-v2 evidence surface.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_partial_baseline_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `tmp/ri_advisory_environment_fit_partial_baseline_preflight_20260417.py`
- `results/research/ri_advisory_environment_fit/phase3_partial_baseline_preflight_2026-04-17/selector_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_partial_baseline_preflight_2026-04-17/label_surface_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_partial_baseline_preflight_2026-04-17/closeout.md`
- `results/research/ri_advisory_environment_fit/phase3_partial_baseline_preflight_2026-04-17/manifest.json`

## Decision question

Did the bounded partial-baseline slice open enough verified surface to compute and evaluate deterministic partial scores now?

## Short answer

**Not yet.**

The preflight confirms that the admitted pre-entry selector surface is present and non-degenerate enough for a bounded score definition.
But the exact Phase 2 supportive / hostile evaluation surface is still not materially joinable on the capture-v2 rows.

Overall preflight verdict: `BLOCKED_LABEL_GAP`.

That means the lane may not yet compute supportive/hostile evaluation buckets honestly on this surface.

## What the preflight proved

### 1. Selector surface is admissible

The preflight selector audit returned `PASS`.

The following consumed selector columns were all present on the capture-v2 rows and all stayed inside the packet allowlist:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- `proba_edge`
- `conf_overall`
- `decision_size`
- `htf_regime`
- `zone`
- `action`
- `side`

Important variation was present on this surface, including:

- `ri_clarity_score`: `12` unique values
- `ri_clarity_raw`: `146` unique values
- `bars_since_regime_change`: `138` unique values
- `proba_edge`: `146` unique values
- `decision_size`: `13` unique values

So the lane is no longer blocked on the narrow question of whether a bounded clarity/recency/reliability selector surface exists.
That part is now real.

### 2. Label surface is still blocked

The preflight label-surface audit returned `BLOCKED_LABEL_GAP`.

The missing exact Phase 2 fields were:

- `pnl_delta`
- `active_uplift_cohort_membership`

That is not cosmetic.
It is exactly the surface the Phase 2 taxonomy required for the supportive / hostile outcome labels.

The preflight also confirmed an important non-negotiable:

- raw `total_pnl` is present on the capture-v2 rows
- but raw `total_pnl` sign may **not** be substituted for the Phase 2 supportive / hostile contract

So the slice must stop before score evaluation rather than fake label coverage.

## Why this is still an honest improvement

This result does **not** mean capture-v2 was a dead end.
It means the lane has now cleanly separated two questions that were previously tangled:

1. **Do we have enough RI-native pre-entry selector surface to define a bounded partial score?**
   - **Yes**
2. **Do we already have the exact Phase 2 supportive / hostile evaluation surface materialized on those rows?**
   - **No**

That is a useful governance outcome.
It prevents the next slice from silently crossing the line between:

- bounded score definition, and
- unapproved label invention

## Consequence for Phase 3

Phase 3 should now be read more narrowly:

- a bounded partial score definition may be admissible in principle on the selector side
- but supportive / hostile evaluation remains blocked until the label-gap is resolved

So the lane is **not** ready for honest contradiction-year or supportive/hostile bucket evaluation yet.

## Exact next admissible step

Only one of the following may happen next:

### Option A — materialize the exact Phase 2 label surface

Create a bounded slice that materially joins the capture-v2 RI rows to the exact Phase 2 outcome-label contract, including:

- bounded baseline-comparison `pnl_delta`
- active-uplift cohort membership

### Option B — write a separate provisional-evaluation admissibility memo

If the lane wants to test a narrower provisional outcome-proxy surface instead, that needs a separate docs-only admissibility review first.

What may **not** happen next:

- no silent substitution of raw `total_pnl` sign
- no fabricated supportive/hostile labels
- no contradiction-year evaluation claims built on a weakened label contract

## Bottom line

The bounded partial-baseline preflight did exactly what a fail-closed slice should do:

- it confirmed that the RI selector surface is now real and usable
- it also confirmed that the exact Phase 2 supportive / hostile evaluation surface is still missing on the capture-v2 rows

So the honest verdict is:

- **selector surface: open**
- **label surface: still blocked**
- **partial baseline evaluation: not yet admissible without a label-materialization or separate provisional-review step**
