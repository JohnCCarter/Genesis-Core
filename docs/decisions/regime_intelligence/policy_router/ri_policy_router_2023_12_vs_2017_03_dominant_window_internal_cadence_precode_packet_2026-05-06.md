# RI policy router 2023-12 vs 2017-03 dominant-window internal cadence precode packet

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `föreslagen / docs-only window-internal reread / no behavior change`

Relevant skills claimed for this slice: `none`

This slice is a docs-only reread over frozen evidence.
It does **not** claim repository skill coverage.

## COMMAND PACKET

- **Category:** `docs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: this slice rereads already-materialized timestamps on fixed dominant windows only, writes two docs, and does not touch runtime/config/default/authority surfaces.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the mixed-year line has already closed annual shape, local-window concentration, and dominant-window chronology, so the next honest step is one bounded window-internal comparison question on the already-fixed windows rather than any new extraction, helper, artifact, or runtime work.
- **Objective:** compare the internal timestamp cadence of the already-fixed dominant windows for `2023-12` and `2017-03`.
- **Candidate:** `2023-12 vs 2017-03 dominant-window internal cadence`
- **Base SHA:** `a3624233dfc49d764d9c6f3f917e80dbeea3af73`
- **Skill Usage:** `none claimed` — docs-only reread of frozen evidence
- **Opus pre-code verdict:** `not required` — docs-only quick path inside RESEARCH

## Exact question

The completed concentration slice already fixed the top-two share difference.
The completed chronology slice already fixed the inter-wave ordering difference.

This slice therefore asks one narrower within-window question only:

> once the dominant windows are held fixed, do `2023-12` and `2017-03` also differ in their internal timestamp cadence, or do they still operate on the same bar-gap alphabet with the real difference being where skipped bars are absorbed?

This slice does **not** revise the landed concentration result.
It does **not** revise the landed chronology result.
It only compares the gap sequences inside the already-fixed windows.

## Exact admissible sources

Only these already-materialized sources are admissible inputs:

1. `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md`
2. `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md`
3. `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`

Not allowed:

- any new helper
- any new artifact
- any regeneration of the existing JSON artifact
- any new scan of annual action-diff files
- any touch under `src/**`, `config/**`, `scripts/**`, `tests/**`, or `GENESIS_WORKING_CONTRACT.md`
- any widening beyond the already-fixed dominant windows

## Fixed dominant-window surface

### `2023-12`

- retained wave 1:
  - `2023-12-15T21:00:00+00:00 -> 2023-12-17T18:00:00+00:00`
  - timestamps: `6`
  - internal gaps: `[9h, 9h, 9h, 9h, 9h]`
- retained wave 2:
  - `2023-12-22T15:00:00+00:00 -> 2023-12-26T00:00:00+00:00`
  - timestamps: `7`
  - internal gaps: `[9h, 9h, 18h, 9h, 18h, 18h]`

Aggregate retained internal gaps:

- total internal gaps = `11`
- `9h` gaps = `8`
- `18h` gaps = `3`

### `2017-03`

- retained wave 1:
  - `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00`
  - timestamps: `4`
  - internal gaps: `[18h, 9h, 9h]`
- retained wave 2:
  - `2017-03-23T18:00:00+00:00 -> 2017-03-24T12:00:00+00:00`
  - timestamps: `3`
  - internal gaps: `[9h, 9h]`
- retained wave 3:
  - `2017-03-29T21:00:00+00:00 -> 2017-03-30T15:00:00+00:00`
  - timestamps: `3`
  - internal gaps: `[9h, 9h]`

Aggregate retained internal gaps:

- total internal gaps = `7`
- `9h` gaps = `6`
- `18h` gaps = `1`

## Intended bounded result surface

This slice is expected to answer whether:

1. both months still share the same internal cadence alphabet (`9h` / `18h`) inside the fixed dominant windows
2. `2023-12` uses more skipped-bar elasticity inside one large late wave
3. `2017-03` keeps its later revisit waves internally regular and expresses divergence mainly by reopening new waves rather than stretching one wave

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_internal_cadence_precode_packet_2026-05-06.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_internal_cadence_2026-05-06.md`
- **Scope OUT:**
  - `GENESIS_WORKING_CONTRACT.md`
  - all `src/**`
  - all `config/**`
  - all `scripts/**`
  - all `tests/**`
  - all `results/**` generation or retention changes
  - any change to the landed concentration or chronology conclusions
  - annual-shape reopen
  - month-packaging reopen
  - runtime/default/authority/promotion/family claims

## Exact method

1. reread the landed concentration and chronology notes
2. reread the frozen JSON artifact timestamps for the already-fixed dominant windows
3. restate each retained wave with its internal gap sequence only
4. compare the internal gap alphabet and skipped-bar pattern across months
5. state explicitly that the result sharpens window-internal structure only and does not revise concentration or chronology authority

## Validation requirements

- touched-doc validation through `pre-commit run --files` on the two touched docs
- manual cross-check that all timestamps and gap sequences match the frozen JSON artifact exactly
- final self-review that the note does not imply new runtime/default/authority claims

## Stop conditions

- the note starts implying a replacement concentration or chronology verdict
- any new source outside the fixed frozen evidence becomes necessary
- the slice starts widening to additional windows, months, or years
- the slice starts implying runtime/default/promotion/family authority
