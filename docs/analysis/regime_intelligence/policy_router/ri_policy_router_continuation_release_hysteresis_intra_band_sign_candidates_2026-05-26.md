# RI policy router continuation_release_hysteresis intra-band sign candidates — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `continuation_release_hysteresis` phase-age transport slice.

Question:

> once the frozen exact-subject triad is already known to share one early subject-relative phase band, do any cluster-local features inside that same band separate the lone negative exact subject from the two positive exact subjects?

This slice is observational only.

It does **not** run new backtests, change runtime logic, modify config/schema authority, widen the frozen exact-subject triad, or claim any portable sign rule.

## Inputs

- prior phase-age transport artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_phase_age_transport_2026-05-25.json`
- frozen triad synthesis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`
- exact subject summaries:
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_summary.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_summary.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_summary.json`
- exact subject row-diff surfaces:
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_row_diffs.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_row_diffs.json`
  - `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_row_diffs.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json`

## What changed and what did not

- **Changed:** one new read-only helper reduced the frozen exact-subject triad into cluster-local subject features, searched simple threshold rules, and retained a new evaluation artifact.
- **Did not change:** no new backtests were run, no runtime/config surfaces changed, no subject selection changed, and no claim was made beyond the already-frozen triad.

## Observed

### 1. Raw cluster length alone does not separate sign

Two coarse candidates fail immediately on the frozen triad:

- `cluster_row_count`
  - `2021-08 = 6`
  - `2025-10 = 13`
  - `2018-03 = 12`
- `decisive_index_within_cluster`
  - `2021-08 = 3`
  - `2025-10 = 7`
  - `2018-03 = 3`

The retained artifact marks both as non-perfect features.

So the next bounded read is already narrower than “longer cluster = worse outcome.”

### 2. Retention and normalized decisive timing do separate the lone negative subject on the frozen triad

Three cluster-local timing/retention features cleanly isolate `2018-03` from the two positive exact subjects:

- `release_retention_ratio`
  - `2018-03 = 0.5`
  - `2025-10 = 0.769231`
  - `2021-08 = 1.0`
- `decisive_rank_pct`
  - `2018-03 = 0.272727`
  - `2025-10 = 0.583333`
  - `2021-08 = 0.6`
- `decisive_hours_from_cluster_start`
  - `2018-03 = 18`
  - `2025-10 = 21`
  - `2021-08 = 24`

The smallest honest statement is:

> inside the shared early phase band, the negative subject releases earlier inside its own cluster and retains less of the baseline continuation-release zone.

### 3. Decisive-row support also separates the frozen triad by sign

At the first decisive local split, the negative exact subject is weaker on all three checked support fields:

- `decisive_action_edge`
  - `2018-03 = 0.075402`
  - `2025-10 = 0.093725`
  - `2021-08 = 0.095446`
- `decisive_confidence_gate`
  - `2018-03 = 0.537701`
  - `2025-10 = 0.546862`
  - `2021-08 = 0.547723`
- `decisive_clarity_score`
  - `2018-03 = 39`
  - `2025-10 = 40`
  - `2021-08 = 40`

So phase-age was not the last word. Once the seam is held inside one early band, the first decisive row itself starts to carry sign-relevant structure on this triad.

### 4. The negative subject also carries heavier policy-path divergence inside the cluster

The negative exact subject differs from both positives on every checked path-divergence count:

- `cluster_policy_diff_rows`
  - `2018-03 = 6`
  - `2025-10 = 3`
  - `2021-08 = 3`
- `cluster_switch_diff_rows`
  - `2018-03 = 6`
  - `2025-10 = 3`
  - `2021-08 = 3`
- `cluster_size_diff_rows`
  - `2018-03 = 2`
  - `2025-10 = 1`
  - `2021-08 = 1`

So `2018-03` is not merely an early-band exception by top-line outcome; it is also the case where the release-zero path stays more structurally different from baseline inside the same band.

### 5. The weakness is concentrated at the decisive split, not across the whole cluster

One nuance matters.

Across the **full cluster**, `2018-03` is not globally weaker than the positive subjects:

- cluster mean `action_edge`
  - `2018-03 = 0.100715`
  - `2025-10 = 0.093265`
  - `2021-08 = 0.094982`
- cluster mean `confidence_gate`
  - `2018-03 = 0.550358`
  - `2025-10 = 0.546632`
  - `2021-08 = 0.547491`
- cluster mean `clarity_score`
  - `2018-03 = 40.75`
  - `2025-10 = 40`
  - `2021-08 = 40`

So the bounded fact is **not** “negative subjects have weaker clusters overall.”

The narrower observed fact is:

> `2018-03` is weaker at the **first decisive split**, releases earlier within the cluster, and diverges longer from baseline inside the same early band.

## Inferred

### 1. Intra-band structure looks more sign-informative than coarse phase placement on this triad

The prior slice showed that all three exact subjects share one early subject-relative phase band.

This follow-up now shows that several cluster-local features separate the lone negative exact subject while coarse cluster size does not.

So the smallest honest inference is:

> once phase-age has already localized the seam to one early band, sign differences on the frozen triad seem to live more in **when the decisive split happens**, **how strong that split is**, and **how long the released path diverges**, not in broad phase placement alone.

### 2. This is still a triad-local sign-candidate map, not a transport-ready rule

The bench still contains only one negative exact subject.

That means the perfect separators in this slice are useful as **candidates** and **ranking clues**, but not yet as a durable sign law.

## Unverified

The following remain open:

1. whether these same intra-band candidates survive a widened exact-subject bench with additional opposite-sign seam-active subjects
2. whether decisive support plus retention is genuinely causal, or only correlated with some still-hidden local structure
3. whether the strongest portable separator is a single feature or a small joint pattern across timing, support, and path divergence

## Verification

- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_20260526.py` -> emitted artifact with status `frozen_triad_intra_band_structure_yields_sign_candidates`

## Bottom line

The prior phase-age slice was right to stop at “early seam marker.”

But inside that shared early band, the frozen exact-subject triad is no longer sign-blind.

The new bounded evidence says:

> `2018-03` differs from `2021-08` and `2025-10` not because it sits in a different broad phase bucket, but because it releases earlier within its cluster, does so at a weaker decisive row, and stays more structurally different from baseline while the seam is active.

That is a better next anchor than broad phase-age alone.

It is still a triad-local candidate map, not a promoted rule.
