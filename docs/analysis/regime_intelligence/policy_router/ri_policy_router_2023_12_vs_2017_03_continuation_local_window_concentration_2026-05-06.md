# RI policy router 2023-12 vs 2017-03 continuation local-window concentration

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `completed / helper-backed / bounded local-window packaging comparison`

This slice is a read-only follow-up to the completed `2017` vs `2023` annual comparison.
It keeps the month set fixed to the two exact continuation-top months already named there:

- `2017-03`
- `2023-12`

It does **not** reopen the annual question.
It does **not** widen to suppression or combined-month framing.
It does **not** join candles, compute proxy returns, rerun backtests, or authorize runtime/default/config/policy/promotion work.

Its purpose is narrower:

> determine whether the continuation-top months share the same local continuation-window shape once rows are packaged by a fixed `<=24h` adjacency rule, or whether `2023-12` is materially more concentrated than `2017-03`.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW`
- **Required Path:** `approved non-trivial RESEARCH helper-backed evidence path`
- **Lane:** `Research-evidence`
- **Objective:** compare the fixed continuation local-window concentration shape of `2023-12` versus `2017-03` on the exact annual enabled-vs-absent action-diff surfaces.
- **Candidate:** `2023-12 vs 2017-03 continuation local-window concentration`
- **Base SHA:** `75a3cb6bf4d46e6cf04caa80551f0063e380619e`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES` on `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_precode_packet_2026-05-06.md`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_precode_packet_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md`
- `scripts/analyze/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_20260506.py`
- `tests/backtest/test_ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration.py`
- regenerate-on-demand artifact: `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_20260506.py --base-sha 75a3cb6bf4d46e6cf04caa80551f0063e380619e`

## Fixed family and packaging rule

Only continuation-displacement rows were counted:

- absent action = `NONE`
- enabled action = `LONG`
- zone = `low`
- switch reason = `stable_continuation_state`

Local windows were then packaged by one fixed descriptive rule:

- adjacent continuation timestamps separated by `<=24h` belong to the same local window

This is descriptive packaging only.
It does **not** recover runtime pockets, trade truth, or promotion authority.

## Main result

### 1. The two top continuation months do **not** share the same local-window shape

The helper returned:

- status = `continuation_local_window_shape_differs_between_2023_12_and_2017_03`
- `same_window_size_sequence_desc = false`
- `same_window_count = false`

So the bounded answer is already non-null on the exact packaging surface:

> `2023-12` and `2017-03` do **not** package into the same continuation local-window shape.

### 2. `2023-12` is dominated by two large late-month windows

Exact `2023-12` continuation packaging result:

- continuation rows: `22`
- window count: `7`
- window sizes descending: `[7, 6, 3, 2, 2, 1, 1]`
- largest-window share: `0.318182`
- top-two-window share: `0.590909`
- rows inside multi-row windows: `20 / 22 = 0.909091`

The two dominant windows are both late in the month:

1. `2023-12-22T15:00:00+00:00 -> 2023-12-26T00:00:00+00:00`
   - rows: `7`
2. `2023-12-15T21:00:00+00:00 -> 2023-12-17T18:00:00+00:00`
   - rows: `6`

That means nearly `59.1%` of the entire December continuation mass sits inside just those two late-December windows.

So the December-led continuation signal is **not** a single-pocket story, but it is still strongly concentrated into two dominant late-month windows.

### 3. `2017-03` is materially more fragmented across the month

Exact `2017-03` continuation packaging result:

- continuation rows: `17`
- window count: `9`
- window sizes descending: `[4, 3, 3, 2, 1, 1, 1, 1, 1]`
- largest-window share: `0.235294`
- top-two-window share: `0.411765`
- rows inside multi-row windows: `12 / 17 = 0.705882`

The largest window is:

- `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00`
  - rows: `4`

But March also carries additional windows across later parts of the month:

- `2017-03-23T18:00:00+00:00 -> 2017-03-24T12:00:00+00:00` (`3` rows)
- `2017-03-29T21:00:00+00:00 -> 2017-03-30T15:00:00+00:00` (`3` rows)
- plus five singleton windows spread through early/mid March

So the March-led continuation result is much less top-heavy.
Its strongest window is smaller, and the month reappears across more distinct windows and more singleton timestamps.

### 4. The sharpest difference is concentration-versus-fragmentation, not merely December-versus-March labeling

Cross-subject deltas from the helper:

- largest-window row delta (`2023-12` minus `2017-03`) = `+3`
- largest-window share delta = `+0.082888`
- top-two-window rows delta = `+6`
- top-two-window share delta = `+0.179144`

So the tightest bounded reading is:

> `2023-12` is more locally concentrated, while `2017-03` is more locally fragmented.

The annual continuation divergence therefore sharpens one level lower than the month ranking itself:

- `2023-12` is carried by two dominant late-December windows
- `2017-03` is carried by a more distributed March structure with smaller peaks and more spread

## Honest synthesis

The smallest honest synthesis is now:

> the annual comparison was not just month-label drift. On the fixed continuation-only packaging surface, `2023-12` and `2017-03` also differ locally: December 2023 is top-heavy and late-window concentrated, while March 2017 is more fragmented across multiple smaller windows.

That is stronger than saying only that the top month changed.
It is weaker than claiming that one exact December pocket is uniquely authoritative or runtime-relevant.

## What this slice now supports

This slice now supports all of the following bounded statements:

1. the top continuation months from the completed annual comparison do **not** share the same `<=24h` local-window shape
2. `2023-12` is materially more concentrated than `2017-03` on the continuation-only surface
3. the December 2023 continuation lead is carried mainly by two late-month windows rather than one single pocket
4. the March 2017 continuation lead is more fragmented across multiple smaller windows and more singleton timestamps
5. the annual continuation divergence sharpens into a concentration-versus-fragmentation difference on the fixed local-window packaging surface
6. the result remains observational only and non-authoritative

## What this slice does **not** support

This slice does **not** support any of the following:

- reopening suppression or combined-month interpretation
- candle/proxy-return claims
- runtime/default/config/policy/family/champion/promotion claims
- a claim that `2023-12` is one uniquely sufficient runtime pocket by itself
- widening beyond `2017-03` and `2023-12` without a fresh packet

## Validation and retention

Focused validation completed:

- `pytest tests/backtest/test_ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration.py` -> `3 passed`
- helper execution on the exact fixed month surface -> passed
- deterministic artifact replay -> passed

Deterministic rerun hash on the same input/base SHA:

- SHA256 before rerun: `1CAAEF922CC198B85C368A319D9B69AEE8775DCA11E1134D00167C9952B6C5CE`
- SHA256 after rerun: `1CAAEF922CC198B85C368A319D9B69AEE8775DCA11E1134D00167C9952B6C5CE`

Git visibility check on this exact artifact returned:

- `!! results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`
- ignore source: `.gitignore:232:results/`

So the correct retention posture remains:

> `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json` is regenerate-on-demand only unless a later governed step explicitly chooses to retain it.

Feature-cache invariance and pipeline invariant checks are **N/A by scope** for this slice because the helper imports no `src` runtime modules, reads only the two fixed annual action-diff JSON files, and does not touch feature-cache or pipeline component-order surfaces.

## Re-anchor verdict

The correct current continuation-shape read is therefore:

- the annual continuation-top divergence between `2017` and `2023` survives on the fixed local-window packaging surface
- `2023-12` is the more concentrated continuation month
- `2017-03` is the more fragmented continuation month
- the December 2023 signal is carried mainly by two late windows, not one lone exact pocket
- category unchanged: observational only, non-authoritative

That makes this a useful bounded local-window packaging slice, not a runtime opening and not a proof that one late-December continuation window should now be crowned emperor of the repo.
