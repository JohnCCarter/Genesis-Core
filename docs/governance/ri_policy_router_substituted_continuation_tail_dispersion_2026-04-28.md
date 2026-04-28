# RI policy router substituted continuation tail dispersion

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only tail-localization / year-heterogeneous result`

This slice is a read-only follow-up to the shared-pocket outcome proxy comparison.
It narrows the question to the already-defined `substituted_continuation_longs` cohort and localizes its `fwd_16` tail dispersion by year.
It does not reopen runtime work, default semantics, or any authority surface.

All returns and dispersion metrics in this slice are timestamp-close observational proxies on existing evidence rows. They are descriptive only and do not represent realized trade PnL, exact row-to-trade truth, exact one-to-one pocket pairing, runtime authority, or promotion readiness.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice reads existing evidence inputs only and writes one bounded research artifact plus one governance note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the prior shared-pocket proxy already showed that the substituted continuation cohort did not separate cleanly at group level, so the next honest question is year-level tail localization rather than any new tuning.
- **Objective:** explain the substituted continuation cohort's positive-group `fwd_16` mean/median split by localizing year-level tail dispersion and worst rows.
- **Candidate:** `substituted continuation tail-dispersion localization`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `tmp/policy_router_evidence/analyze_substituted_continuation_tail_dispersion_20260428.py`
- `tmp/policy_router_evidence/analyze_shared_pocket_outcome_quality_20260428.py`
- `results/research/ri_policy_router_shared_pocket_outcome_quality_20260428/shared_pocket_outcome_quality_summary.json`
- `results/research/ri_policy_router_substituted_continuation_tail_dispersion_20260428/substituted_continuation_tail_dispersion_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/*_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Exact cohort lineage

Inputs are limited to the already-defined `substituted_continuation_longs` cohort as materialized by the existing shared-pocket artifact, or the exact upstream annual diff rows already used to materialize that cohort. This slice must not re-derive pocket membership from raw candles, introduce fresh cohort logic, or add new pocket heuristics.

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_substituted_continuation_tail_dispersion_20260428.py --base-sha 989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Main result

The positive-group negative mean is **not** just a one-year left-tail illusion, and the substituted continuation cohort does **not** align cleanly with the annual positive-vs-negative split.

The stronger result is year heterogeneity.

## Year-level localization

### Negative full years

- `2019`: mean `-0.035260%`, median `-0.364016%`, `< -5%` tail share `10.14%`, `< -10%` tail share `3.38%`
- `2021`: mean `+0.950563%`, median `+1.148671%`, `< -5%` tail share `11.94%`, `< -10%` tail share `5.97%`
- `2024`: mean `+0.512109%`, median `+0.151565%`, `< -5%` tail share `4.51%`, `< -10%` tail share `0.00%`

### Positive full years

- `2018`: mean `-0.739613%`, median `+0.252926%`, `< -5%` tail share `21.15%`, `< -10%` tail share `8.65%`
- `2020`: mean `+1.327884%`, median `+1.239059%`, `< -5%` tail share `5.16%`, `< -10%` tail share `1.94%`
- `2022`: mean `-0.760365%`, median `-0.097944%`, `< -5%` tail share `18.14%`, `< -10%` tail share `3.92%`
- `2025`: mean `-0.851515%`, median `-0.425303%`, `< -5%` tail share `9.16%`, `< -10%` tail share `0.00%`

## What changed in the story

### 1. The positive-group mean/median split is only partly a tail-skew story

`2018` still fits the classic skew story:

- median stays slightly positive
- mean is pulled negative by a heavy left tail
- large tail mass appears below `-5%` and `-10%`

But the positive group is **not** just `2018`.

`2022` and `2025` both show:

- negative means, and
- negative medians

So in those two positive annual years, the substituted continuation cohort is not merely suffering from a few giant losers.
It looks broadly weak on this proxy surface.

### 2. The negative group is also mixed rather than uniformly continuation-hostile

`2021` and `2024` show positive mean and positive median continuation outcomes.
Only `2019` is clearly weak on both mean and median.

So the substituted continuation cohort does not sort neatly by annual router verdict:

- some negative years have healthy continuation proxies
- some positive years have weak continuation proxies

### 3. `2020` is the clean continuation-friendly counterexample

`2020` stands out as the strongest continuation-friendly year in the positive group:

- mean `+1.327884%`
- median `+1.239059%`
- relatively light tail shares below `-5%` and `-10%`

That makes `2020` a useful future counterexample against the weaker continuation years (`2018`, `2022`, `2025`).

## Worst-row reading

The worst rows across the weak continuation years are still dominated by `stable_continuation_state` and can be very large on the `fwd_16` proxy:

- `2018-02-04T12:00:00+00:00` -> `-16.81%`
- `2022-06-11T18:00:00+00:00` -> `-18.18%`
- `2025-03-08T15:00:00+00:00` -> `-8.70%`

This matters because it shows the continuation cohort's weakness is not one uniform low-grade drag.
Some years contain deep left-tail continuation pockets, while others do not.

## Interpretation

This slice weakens any simple year-group claim about substituted continuation quality.

What the evidence now supports:

- the substituted continuation cohort is **year-heterogeneous**
- the positive-group negative mean is **not** explained only by a single outlier year
- continuation quality does **not** align cleanly with the positive-vs-negative annual split
- the earlier blocked-baseline cohort remains the clearer annual divider on the current descriptive evidence surface

So the stronger bounded reading now is:

> annual sign differences are still better explained by what gets blocked than by a stable cross-year continuation-quality rule.

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- that continuation substitutions do not matter at all
- exact local pocket causality
- exact one-to-one blocked-versus-substituted pair quality
- runtime-authoritative row truth

It only says that continuation quality is mixed by year and does not map cleanly to the annual positive-vs-negative grouping.

## Next admissible step

If this lane is reopened again, the next honest read-only move should compare **continuation-friendly** and **continuation-hostile** years directly on smaller local windows instead of collapsing them into annual positive-vs-negative groups.

The cleanest current contrast is likely:

- continuation-friendly: `2020`
- continuation-hostile: `2018`, `2022`, `2025`

That comparison should remain descriptive and local unless a later higher-fidelity replay surface is explicitly proposed.

## What is not justified from this slice

- new router tuning
- runtime reopen on continuation semantics
- claiming that annual positivity automatically implies good continuation substitutions
- claiming exact contribution proof from timestamp-close proxy dispersion alone
