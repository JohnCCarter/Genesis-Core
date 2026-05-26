# RI policy router continuation_release_hysteresis local packet — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed widening-candidate inventory.

Question:

> when the first negative-like widening candidate (`2021-04`) and the first positive control (`2023-05`) are rerun as exact full-month subjects on the same carrier, does the candidate preserve more of the frozen negative triad's local asymmetry than the control?

This slice is observational only.

It does **not** widen the exact divergent triad, claim hidden local top-line divergence has already been proven, change runtime/config surfaces, or grant any promotion authority.

## Inputs

- monthly inventory windows: `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`
- triad-local sign-candidate artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json`
- widening shortlist artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json`

## What changed and what did not

- **Changed:** one new read-only helper reran the first negative-like widening candidate and the first positive control, rebuilt their continuation-release clusters, and scored them against the frozen triad's perfect negative local rules.
- **Did not change:** no runtime/config files changed, no policy was promoted, no new stack-wide validation matrix was introduced, and the frozen exact triad was not reopened as if a new divergent month had already been discovered.

## Observed

### 1. Both reruns reproduced the monthly inventory exactly — and both months stayed flat at the monthly ledger level

For both `2021-04` and `2023-05`:

- `rerun_total_return_diff = 0.0`
- `rerun_final_capital_diff = 0.0`
- exact baseline and `release_zero` continuation-release timestamps matched the frozen monthly inventory

So this slice did **not** discover a hidden fourth divergent month.

It stayed inside the smaller local-structure question only.

### 2. `2021-04` keeps the asymmetric seam packaging that motivated the widening shortlist

`2021-04` reproduces one long continuation-release cluster in baseline and a shorter cluster under `release_zero`:

- baseline: `16` rows, `2021-04-16T09:00:00+00:00 -> 2021-04-18T06:00:00+00:00`, span `45h`
- `release_zero`: `9` rows, `2021-04-16T09:00:00+00:00 -> 2021-04-17T09:00:00+00:00`, span `24h`
- retention ratio: `0.5625`
- span compression: `21h`

The first decisive local split occurs at `2021-04-17T03:00:00+00:00`, `18h` into the cluster, with:

- `action_edge = 0.077282`
- `confidence_gate = 0.538641`
- `clarity_score = 39`
- `zone = low`

This is not a perfect replica of `2018-03`, but it is clearly not the same local shape as the symmetric control.

### 3. `2023-05` behaves like a cleaner control than a negative-like near-miss

`2023-05` reproduces one symmetric cluster on both sides of the comparison:

- baseline: `7` rows, span `18h`
- `release_zero`: `7` rows, span `18h`
- retention ratio: `1.0`
- span compression: `0h`

Its first decisive split is immediate at the first cluster row (`2023-05-17T06:00:00+00:00`) with:

- `action_edge = 0.094719`
- `confidence_gate = 0.54736`
- `clarity_score = 40`

So the control preserves the seam, but not the same truncated packaging as `2021-04`.

### 4. The candidate is stronger than the control on the frozen negative-rule surface, but only narrowly

The helper scored both reruns against the frozen triad's `9` perfect negative local separators.

#### `2021-04` — candidate

- hits `5 / 9`
- satisfied features:
  - `decisive_hours_from_cluster_start`
  - `decisive_clarity_score`
  - `cluster_policy_diff_rows`
  - `cluster_switch_diff_rows`
  - `cluster_size_diff_rows`
- misses:
  - `release_retention_ratio`
  - `decisive_rank_pct`
  - `decisive_action_edge`
  - `decisive_confidence_gate`

#### `2023-05` — control

- hits `4 / 9`
- satisfied features:
  - `decisive_rank_pct`
  - `decisive_hours_from_cluster_start`
  - `cluster_policy_diff_rows`
  - `cluster_switch_diff_rows`
- misses:
  - `release_retention_ratio`
  - `decisive_action_edge`
  - `decisive_confidence_gate`
  - `decisive_clarity_score`
  - `cluster_size_diff_rows`

So `2021-04` does come out more negative-like than `2023-05`, but only by one rule hit.

That is real signal, not overwhelming separation.

### 5. The decisive support difference is real but still partial

`2021-04` gets closer to the frozen negative decisive row than the control does:

- candidate clarity reaches the negative threshold exactly (`39`)
- candidate action-edge and confidence-gate are only slightly above the negative thresholds
  - `action_edge 0.077282` vs negative threshold `0.075402`
  - `confidence_gate 0.538641` vs negative threshold `0.537701`

So the candidate is not failing the triad-local read broadly.

It is failing it narrowly on the decisive support fields while matching it more strongly on size/path divergence and cluster truncation.

## Inferred

### 1. `2021-04` remains the least arbitrary next local-window target

The smallest honest inference is:

> `2021-04` still deserves to be the first localized widening target because it reproduces more negative triad-local asymmetry than the `2023-05` control while keeping the full-month ledger flat.

That means the widening shortlist was not random noise.

### 2. The next useful question is now local outcome cancellation, not more monthly ranking

Because both months remain monthly-flat even after the rerun, the next honest move is not another full-month ranking pass.

The more informative next question is:

> inside the candidate's truncated `45h -> 24h` seam cluster, are there offsetting local paths that cancel at the month level and hide what would otherwise look like a negative local pocket?

## Unverified

The following remain open:

1. whether a strictly local envelope around the `2021-04` cluster reveals hidden harmful sub-window structure that the monthly ledger averages away
2. whether `2023-05` stays cleaner than `2021-04` once local outcome proxies or local replay evidence are added
3. whether the one-hit advantage for `2021-04` survives once the widening packet moves beyond this first candidate/control pair

## Verification

- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_20260526.py` -> emitted artifact with status `negative_like_candidate_preserves_more_triad_local_asymmetry_than_control`

## Bottom line

Staying with the current bounded path was the right call.

The new packet does **not** prove hidden divergence in `2021-04`.

But it does prove something smaller and useful:

> when rerun on the same carrier, `2021-04` preserves more of the frozen negative triad's local asymmetry than `2023-05`, mainly through cluster truncation, lower clarity, and heavier size/path divergence — even though both months still net to flat at the full-month ledger level.

So the next honest step is now tighter, not broader:

> a strictly local `2021-04` vs `2023-05` envelope slice focused on local outcome cancellation inside the seam cluster.
