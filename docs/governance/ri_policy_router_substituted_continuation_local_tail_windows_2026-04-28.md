# RI policy router substituted continuation local tail windows

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only local-window comparison / concentration-vs-recurrence result`

This slice is a read-only follow-up to the substituted continuation tail-dispersion note.
It keeps the same frozen `substituted_continuation_longs` cohort and adds one descriptive packaging step for already-qualifying tail rows.
It does not reopen runtime work, default semantics, or any authority surface.

All returns and dispersion metrics in this slice are timestamp-close observational proxies on existing evidence rows. They are descriptive only and do not represent realized trade PnL, exact row-to-trade truth, exact one-to-one pocket pairing, runtime authority, or promotion readiness.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice reads existing evidence inputs only and writes one bounded research artifact plus one governance note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: year-level continuation heterogeneity is already proven, so the next honest question is whether weak continuation years are dominated by a few local tail windows or by more recurrent local weakness.
- **Objective:** compare descriptive local substituted-continuation tail windows in continuation-friendly `2020` against continuation-weaker `2018`, `2022`, and `2025`.
- **Candidate:** `substituted continuation local tail-window comparison`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `tmp/policy_router_evidence/analyze_substituted_continuation_local_tail_windows_20260428.py`
- `docs/governance/ri_policy_router_substituted_continuation_tail_dispersion_2026-04-28.md`
- `results/research/ri_policy_router_substituted_continuation_tail_dispersion_20260428/substituted_continuation_tail_dispersion_summary.json`
- `results/research/ri_policy_router_substituted_continuation_local_tail_windows_20260428/substituted_continuation_local_tail_windows_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/*_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Exact lineage and packaging rule

`substituted_continuation_longs`, the `<= -5.0%` `fwd_16` tail filter, and the comparison year set were fixed from the prior tail-dispersion evidence surface. This slice adds only a descriptive `<=24h` packaging step for already-qualifying proxy rows.

This analysis groups already-qualifying substituted-continuation proxy rows into timestamp-close local windows using a fixed `<=24h` adjacency rule. These windows are descriptive packaging only and do not recover runtime pockets, causal seams, or realized trade-level authority.

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_substituted_continuation_local_tail_windows_20260428.py --base-sha 989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Fixed comparison set

- continuation-friendly reference: `2020`
- continuation-weaker years: `2018`, `2022`, `2025`
- fixed tail filter: `fwd_16_close_return_pct <= -5.0%`
- fixed local packaging rule: adjacent qualifying timestamps separated by `<=24h`

## Main result

`2020` is not continuation-friendly because it has no bad local windows.
It is continuation-friendly **despite** a few severe local windows.

The weak continuation years differ from `2020` mainly by **recurrence and spread**, not by the mere existence of bad windows.

## Year-by-year descriptive window picture

### 2020 — few windows, heavily concentrated

- qualifying tail rows: `8`
- window count: `5`
- multi-row window count: `3`
- rows inside multi-row windows: `75%`

The large negative continuation rows are concentrated around a small number of local windows, dominated by the March 2020 crash regime:

- `2020-03-11 03:00 -> 2020-03-11 12:00` (2 rows, mean `-33.17%`)
- `2020-03-14 09:00 -> 2020-03-14 18:00` (2 rows, mean `-12.09%`)
- `2020-03-26 12:00 -> 2020-03-27 09:00` (2 rows, mean `-6.26%`)

Then only two isolated rows remain.

So `2020` looks like a **small number of acute continuation tail events** rather than a broad recurrent continuation weakness.

### 2018 — many recurrent windows across the year

- qualifying tail rows: `44`
- window count: `19`
- multi-row window count: `12`
- rows inside multi-row windows: `84.09%`

`2018` shows many repeated multi-row windows across multiple calendar zones, including:

- late January / early February
- late March
- early June
- early August
- late November / early December

Representative recurring windows:

- `2018-11-22 21:00 -> 2018-11-24 18:00` (5 rows, mean `-10.81%`)
- `2018-06-08 06:00 -> 2018-06-09 18:00` (4 rows, mean `-10.07%`)
- `2018-08-02 12:00 -> 2018-08-04 09:00` (5 rows, mean `-6.30%`)

So `2018` looks like **recurrent continuation-hostile local windows**, not just one exceptional crash cluster.

### 2022 — recurrent clustered weakness again

- qualifying tail rows: `37`
- window count: `15`
- multi-row window count: `10`
- rows inside multi-row windows: `86.49%`

`2022` again shows repeated clustered windows, especially around major down legs:

- `2022-06-09 21:00 -> 2022-06-11 18:00` (5 rows, mean `-12.48%`)
- `2022-11-06 03:00 -> 2022-11-07 15:00` (4 rows, mean `-11.20%`)
- `2022-05-06 21:00 -> 2022-05-08 09:00` (4 rows, mean `-8.47%`)
- `2022-08-17 03:00 -> 2022-08-19 00:00` (5 rows, mean `-8.27%`)

Like `2018`, this is **repeated clustered continuation weakness**, not merely one or two isolated disasters.

### 2025 — weaker continuation year, but more fragmented

- qualifying tail rows: `12`
- window count: `8`
- multi-row window count: `3`
- rows inside multi-row windows: `58.33%`

`2025` is weaker than `2020`, but it does **not** look like `2018` or `2022`.
It shows:

- one clearer March cluster: `2025-03-08 06:00 -> 2025-03-09 00:00` (3 rows, mean `-7.31%`)
- a smaller February pair
- several isolated rows later in the year

So `2025` looks more like **fragmented continuation weakness** than broad recurrent multi-window clustering.

## Interpretation

This slice makes the continuation story more precise.

What it now supports:

- `2020` is continuation-friendly overall even though it still contains a few severe local tail windows
- `2018` and `2022` are not just skewed by one crash pocket; they show **recurrent multi-row continuation tail windows** across the year
- `2025` is weaker too, but its weakness is more fragmented and less broadly clustered than `2018` / `2022`

So the strongest bounded reading now is:

> continuation weakness itself has multiple shapes, but the cleanest contrast is that `2020` concentrates most of its bad continuation rows into a few acute windows, while `2018` and `2022` repeatedly revisit continuation-hostile local windows across the year.

## Consequence for the larger annual story

This still does **not** overturn the previous conclusion that blocked baseline longs are the clearer annual divider.

Instead, it sharpens the continuation side:

- continuation quality is heterogeneous by year,
- and even within the weaker continuation years there are different local shapes,
- so annual positive-vs-negative grouping remains too coarse for continuation interpretation.

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- exact local pocket causality
- exact one-to-one blocked-versus-substituted pairing
- that continuation windows alone determine annual router value
- runtime-authoritative row truth

It only describes how the already-qualifying continuation tail rows are locally distributed under one fixed packaging rule.

## Next admissible step

If this lane is reopened again, the next honest read-only move should compare **blocked baseline longs and substituted continuation longs inside the same local windows** on a smaller fixed subject, for example:

- `2020` March crash windows, versus
- one recurrent `2018` or `2022` continuation-hostile window

That would keep the comparison local and descriptive without reopening runtime tuning.

## What is not justified from this slice

- new router tuning
- runtime reopen on continuation semantics
- claiming that one universal continuation rule exists across all positive or all negative years
- claiming exact contribution proof from local proxy windows alone
