# RI policy router blocked vs substituted same windows

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only same-window comparison / local phase-sensitive result`

This slice is a read-only follow-up to the local continuation-window note.
It keeps the existing curated annual diff cohort definitions unchanged and compares them inside two pre-fixed local windows where blocked baseline rows and substituted continuation rows co-occur.
It does not reopen runtime work, default semantics, family authority, or promotion claims.

This slice is limited to two pre-fixed local windows on the curated observational surface:

- `2020-03-14T09:00:00+00:00 -> 2020-03-19T06:00:00+00:00`
- `2018-03-20T06:00:00+00:00 -> 2018-03-26T12:00:00+00:00`

These windows were retained from prior probe work because blocked baseline rows and substituted continuation rows co-occur within the same bounded interval.
The slice does not widen annual scope or reclassify year-level findings.

Reported forward-return and excursion values are timestamp-close observational proxies on fixed-window rows only.
The comparison is descriptive and does not establish causality, trade authority, realized trade PnL, row-to-trade truth, or promotion guidance.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice reads existing evidence inputs only and writes one bounded research artifact plus one governance note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** compare blocked baseline longs and substituted continuation longs inside the same fixed local windows on a continuation-friendly `2020` subject and a continuation-weaker `2018` subject.
- **Candidate:** `blocked vs substituted same-window comparison`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `tmp/policy_router_evidence/analyze_blocked_vs_substituted_same_windows_20260428.py`
- `tmp/policy_router_evidence/analyze_shared_pocket_outcome_quality_20260428.py`
- `results/research/ri_policy_router_blocked_vs_substituted_same_windows_20260428/blocked_vs_substituted_same_windows_summary.json`
- `docs/governance/ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2018_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Selection basis and containment

Blocked baseline and substituted continuation cohort definitions are reused unchanged from `tmp/policy_router_evidence/analyze_shared_pocket_outcome_quality_20260428.py`.
No thresholds, matchers, year groups, or upstream semantics were changed in this slice.

### Why these two windows

#### `2020-03-14 -> 2020-03-19`

The more severe `2020` continuation-tail subwindows on `2020-03-11` and `2020-03-14` had zero blocked-row overlap.
This widened local union window was therefore retained as the smallest mixed March 2020 interval where blocked baseline rows and substituted continuation rows co-occur on the curated observational surface.

#### `2018-03-20 -> 2018-03-26`

This March 2018 window was retained because it is a recurrent hostile local interval with substantial mixed-cohort overlap on the same curated observational surface.
It provides a bounded contrast against the mixed March 2020 subject without widening the year set.

#### Why not `2022`

`2022` was not retained in this slice because the ugliest continuation-tail windows in the prior local-window probe were largely pure continuation clusters without blocked-row overlap, making them poor same-window blocked-versus-substituted subjects.

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_blocked_vs_substituted_same_windows_20260428.py --base-sha 989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Determinism check

The helper was rerun twice consecutively and produced the same artifact hash both times:

- SHA256: `0113ECB68F747D208E771CEF9F6210A6AF85473179D91FCA565238AFF2C90C59`

## Main result

The same-window surface does **not** produce one universal blocked-versus-substituted winner.
Instead, the local result flips across the two fixed windows, and the decisive difference is **phase ordering inside the interval**, not a row-for-row cohort dominance rule.

## Window 1 — mixed March 2020 union window

Window:

- `2020-03-14T09:00:00+00:00 -> 2020-03-19T06:00:00+00:00`

Observed counts:

- blocked baseline longs: `5`
- substituted continuation longs: `7`
- total rows: `12`

### Descriptive cohort contrast

Blocked baseline rows:

- `fwd_16` mean: `8.730945%`
- `fwd_16` median: `10.683272%`
- `fwd_16` min: `1.102507%`
- `mae_16` mean: `-6.200573%`

Substituted continuation rows:

- `fwd_16` mean: `4.351859%`
- `fwd_16` median: `0.591890%`
- `fwd_16` min: `-16.016916%`
- `mae_16` mean: `-11.486966%`

### What the ordered timeline shows

Inside this fixed March 2020 window, the continuation cohort occupies the earliest and most left-tail-exposed part of the interval:

- the worst early rows are substituted continuation rows on `2020-03-14` with `fwd_16` of `-16.02%` and `-8.17%`
- blocked rows start later, from `2020-03-15 15:00` onward
- later in the same interval both cohorts participate in the rebound, but blocked rows remain materially less downside-exposed on the current proxy surface

### Bounded reading

Within this fixed mixed March 2020 window, blocked baseline rows look locally stronger than substituted continuation rows on the current proxy surface.
But that local contrast is inseparable from the fact that the two cohorts do **not** fire on the same timestamps.
The continuation cohort carries the earlier drawdown segment of the interval, while blocked rows appear later in the local sequence.

## Window 2 — recurrent hostile March 2018 window

Window:

- `2018-03-20T06:00:00+00:00 -> 2018-03-26T12:00:00+00:00`

Observed counts:

- blocked baseline longs: `9`
- substituted continuation longs: `8`
- total rows: `17`

### Descriptive cohort contrast

Blocked baseline rows:

- `fwd_16` mean: `-3.912314%`
- `fwd_16` median: `-5.289905%`
- `fwd_16` min: `-11.695500%`
- `mae_16` mean: `-6.807876%`

Substituted continuation rows:

- `fwd_16` mean: `-2.077926%`
- `fwd_16` median: `-1.272574%`
- `fwd_16` min: `-7.222945%`
- `mae_16` mean: `-5.526740%`

### What the ordered timeline shows

Inside this March 2018 window, the temporal arrangement is different:

- blocked rows dominate the early part of the interval from `2018-03-20` into early `2018-03-22`
- substituted continuation rows take over the middle and later part from `2018-03-22 09:00` onward
- blocked rows then reappear during the later relapse on `2018-03-24`

### Bounded reading

Within this fixed March 2018 hostile window, blocked baseline rows look locally weaker than substituted continuation rows on the current proxy surface.
So the local same-window balance points in the opposite direction from the March 2020 mixed window.

## Interpretation

This slice sharpens the constraint on local RI-router reading.

What it now supports:

- even when blocked baseline rows and substituted continuation rows coexist in the same bounded local interval, they do **not** form a row-for-row matched comparison surface
- the local outcome picture depends heavily on **where inside the interval** each cohort appears
- the mixed `2020` March window is continuation-left-tail-loaded early and blocked-later afterward
- the recurrent hostile `2018` March window shows a different sequencing pattern and a different local blocked-versus-substituted balance

So the strongest bounded reading now is:

> same-window evidence is useful for local chronology and phase structure, but it still does not collapse into one universal blocked-versus-substituted dominance rule.

## Consequence for the broader evidence chain

This slice does **not** overturn the earlier annual evidence.
It also does **not** replace the earlier blocked-baseline cohort conclusion with a new local dominance rule.

Instead, it shows something more specific:

- local same-window comparison remains highly phase-sensitive
- mixed windows can point in opposite directions even inside the positive-year side of the annual surface
- therefore local same-window comparison is best read as a bounded timing-structure tool, not as a universal policy-ranking mechanism

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- causal superiority of one cohort over the other
- row-to-trade truth
- annual reclassification
- promotion or tuning guidance
- that these two windows are representative of all `2020` or all `2018` behavior

## Next admissible step

If this line is reopened again, the cheapest honest move is a **phase-ordering** follow-up on these same two windows only, for example quantifying whether blocked rows tend to appear earlier, later, or in a relapse segment relative to substituted continuation rows.
That would stay on the same bounded subjects instead of widening to new years or returning to runtime tuning.

## What is not justified from this slice

- widening to more same-window subjects without a new packet
- claiming a universal blocked-versus-substituted winner
- runtime tuning based on these two local windows
- promotion or family-readiness claims
