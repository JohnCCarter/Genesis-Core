# RI policy router 2023-12 vs 2017-03 continuation local-window concentration precode packet

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `föreslagen / read-only evidence slice / no behavior change`

Relevant skills: `python_engineering`

Skill coverage for this slice is explicit and bounded:

- `python_engineering` governs the helper structure, hermetic pytest coverage, deterministic replay, and minimal-diff docs evidence landing.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: this slice reads only two fixed annual action-diff JSON files, emits one bounded summary artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the annual `2017` vs `2023` comparison is already closed, so the next honest step is one bounded local-window packaging question on the exact continuation-top months rather than any reopen of annual shape, candles, or runtime framing.
- **Objective:** compare the fixed continuation-displacement local-window concentration shape of `2023-12` versus `2017-03` on the exact annual enabled-vs-absent action-diff surfaces.
- **Candidate:** `2023-12 vs 2017-03 continuation local-window concentration`
- **Base SHA:** `75a3cb6bf4d46e6cf04caa80551f0063e380619e`
- **Skill Usage:** `python_engineering.json`

## Exact proposed question

The completed annual comparison already fixed these two facts:

- `2023` top continuation month = `December`
- `2017` top continuation month = `March`

The next bounded question is therefore:

> when only continuation-displacement rows are retained and then packaged by a fixed `<=24h` adjacency rule, do `2023-12` and `2017-03` show the same local continuation-window shape, or does `2023-12` concentrate into one or two dominant windows while `2017-03` remains more fragmented across smaller windows?

This slice does **not** reopen the annual comparison.
It does **not** reopen suppression or combined-month framing.
It does **not** join candles, compute proxy returns, rerun backtests, or claim runtime/default/promotion authority.

## Fixed subject and family definition

The helper is fail-closed to these two exact month subjects only:

- `2017-03`
- `2023-12`

The family definition is fixed to continuation displacement only:

- absent action = `NONE`
- enabled action = `LONG`
- zone = `low`
- switch reason = `stable_continuation_state`

The local packaging rule is fixed in advance:

- adjacent continuation timestamps separated by `<=24h` belong to the same local window

This is descriptive packaging only.
It does **not** recover runtime pockets, trade truth, or family authority.

## Preflight anchors already observed

Current raw-data preflight on the fixed annual surfaces already shows:

### `2017-03`

- continuation rows = `17`
- `<=24h` window sizes descending = `[4, 3, 3, 2, 1, 1, 1, 1, 1]`
- largest window = `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00`
- largest-window share = `0.235294`
- top-two-window share = `0.411765`

### `2023-12`

- continuation rows = `22`
- `<=24h` window sizes descending = `[7, 6, 3, 2, 2, 1, 1]`
- largest window = `2023-12-22T15:00:00+00:00 -> 2023-12-26T00:00:00+00:00`
- largest-window share = `0.318182`
- top-two-window share = `0.590909`

These preflight observations justify the bounded concentration-versus-fragmentation question, but they are not yet the landed result until the helper, test, and note are materialized under this packet.

## Exact allowed input surface

The helper may read only:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`

Supporting wording anchors allowed for note context only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_vs_substituted_same_windows_2026-04-28.md`
- `GENESIS_WORKING_CONTRACT.md`

Not allowed:

- candle joins
- forward-return or excursion proxies
- widening to any other year or month
- reopening suppression or combined-month counts
- `src/**` imports
- new backtests or regenerated upstream diff artifacts

## Allowed final statuses for the later execution slice

- `continuation_local_window_shape_differs_between_2023_12_and_2017_03`
- `continuation_local_window_shape_overlaps_between_2023_12_and_2017_03`
- `fail_closed_missing_fixed_continuation_surface`

These statuses are descriptive only.
They do **not** authorize runtime/default/config/policy/promotion claims.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_precode_packet_2026-05-06.md`
  - `scripts/analyze/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_20260506.py`
  - `tests/backtest/test_ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration.py`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md`
  - `GENESIS_WORKING_CONTRACT.md` only if the completed slice materially changes the next admissible step
- **Scope OUT:**
  - all `src/**`
  - all `config/**`
  - runtime/default/authority/promotion/family surfaces
  - widening beyond `2017-03` and `2023-12`
  - combined-month or suppression reopen
  - candle/proxy-return analysis
  - `docs/architecture/ARCHITECTURE_VISUAL.md`
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Expected output handling

The helper is expected to emit one regenerate-on-demand JSON artifact:

- `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`

This artifact is **not part of the landed scope by default**.
Treat it as regenerate-only unless a later governed step explicitly chooses to retain or force-stage it.

## Planned method

1. load only the two fixed annual action-diff files
2. select only continuation-displacement rows on the fixed month subjects
3. package the timestamps into local windows using the fixed `<=24h` adjacency rule
4. emit exact chronological windows plus concentration metrics:
   - total continuation row count
   - window count
   - window-size sequence descending
   - largest-window share
   - top-two-window share
   - multi-row-window share
5. summarize whether the fixed months share the same local continuation shape or differ on concentration-versus-fragmentation

## Validation requirements

- focused pytest on the new helper test file
- helper execution against the fixed two-month surface
- deterministic replay via two distinct temporary JSON outputs plus SHA256 comparison
- `pre-commit run --files` on the touched tracked files
- manual diff review confirming no runtime/config/default/authority drift

Feature-cache invariance and pipeline invariant are **N/A by scope** because the helper imports no `src` runtime modules, reads only the two fixed annual action-diff JSON files, and does not touch feature-cache or pipeline component-order surfaces. Any deviation blocks the slice and requires re-review.

Malformed-surface checks apply to missing fixed files, missing or invalid timestamps, and missing required family fields only. Optional descriptive fields must **not** be treated as required.

## Stop conditions

- either fixed month cannot be materialized from the existing annual action-diff evidence
- the helper starts requiring candle joins or `src/**` imports
- the slice starts implying runtime tuning or promotion authority
- scope drifts into broader annual re-analysis rather than this fixed concentration question

## Output required

- one deterministic read-only helper
- one hermetic pytest file
- one bounded analysis note stating what the concentration read does and does not justify
- exact command run and validation outcomes
