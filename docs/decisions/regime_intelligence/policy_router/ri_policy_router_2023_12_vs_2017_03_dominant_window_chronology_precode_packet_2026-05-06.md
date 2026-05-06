# RI policy router 2023-12 vs 2017-03 dominant-window chronology precode packet

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `föreslagen / docs-only chronology reread / no behavior change`

Relevant skills claimed for this slice: `none`

This slice does **not** claim repository skill coverage.
It is a docs-only reread over already-materialized evidence.

## COMMAND PACKET

- **Category:** `docs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: this slice reads two existing sources only, writes two docs, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the mixed-year annual line is already closed through annual comparison plus local-window concentration, so the next honest step is one docs-only chronology reread on the fixed top windows rather than any new packaging, helper, artifact, or runtime work.
- **Objective:** reread the already-fixed dominant continuation windows for `2023-12` and `2017-03` as chronology and wave ordering rather than as a replacement concentration metric.
- **Candidate:** `2023-12 vs 2017-03 dominant-window chronology`
- **Base SHA:** `9005f5b11d7d261a763a96e8611652b9d82552e9`
- **Skill Usage:** `none claimed` — docs-only reread of frozen evidence
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`
- **Constraints:** `NO BEHAVIOR CHANGE`

## Exact question

The completed local-window concentration slice already established two authoritative concentration facts:

- `2023-12` top-two continuation share = `13 / 22 = 0.590909`
- `2017-03` top-two continuation share = `7 / 17 = 0.411765`

This reread does **not** revise those landed concentration results.

Instead, it asks one new chronology-only question on the already-fixed windows:

> when the already-named dominant windows are read as an ordered timeline rather than as a top-two concentration table, does `2023-12` resolve into one compact late-month dual-wave burst while `2017-03` resolves into one early anchor plus two later revisit waves?

## Why the tie-aware March framing is allowed here

The prior concentration slice was correct to report `top-two` shares.
But for chronology only, `2017-03` contains a real second-place tie between two already-named `3`-row late-March revisit windows.

So this chronology reread keeps:

- `2023-12`: the two already-named dominant late-December windows (`6`, `7` rows)
- `2017-03`: the largest already-named early-March window plus both already-named tied `3`-row revisit windows (`4`, `3`, `3` rows)

This tie-aware March set is **chronology coverage only**.
It must **not** be presented as a replacement for the landed concentration comparison.

Required wording guardrail for the analysis note:

> This reread does not revise the landed dominant-window concentration result. The authoritative concentration comparison remains the previously reported top-two shares (`2023-12 = 13/22`, `2017-03 = 7/17`). For chronology only, `2017-03` retains both already-named tied second-place revisit windows so the month is not forced into an arbitrary top-two ordering; the resulting `10/17` figure is descriptive chronology coverage, and the chronology delta is carried by wave ordering and gap structure rather than a replacement concentration metric.

## Exact admissible sources

Only these two already-materialized sources are allowed as evidence inputs:

1. `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md`
2. `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`

Not allowed:

- regenerating or modifying the JSON artifact
- reopening annual action-diff extraction
- any new `scripts/**` or `tests/**`
- any new `results/**` or `artifacts/**`
- widening to any window not already named in the landed note and artifact

## Fixed chronology surface

### `2023-12`

- `2023-12-15T21:00:00+00:00 -> 2023-12-17T18:00:00+00:00` (`6` rows)
- `2023-12-22T15:00:00+00:00 -> 2023-12-26T00:00:00+00:00` (`7` rows)
- inter-window gap: `117h`
- chronology coverage retained for this reread: `13 / 22 = 0.590909`

### `2017-03`

- `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00` (`4` rows)
- `2017-03-23T18:00:00+00:00 -> 2017-03-24T12:00:00+00:00` (`3` rows)
- `2017-03-29T21:00:00+00:00 -> 2017-03-30T15:00:00+00:00` (`3` rows)
- inter-window gaps: `429h`, `129h`
- chronology coverage retained for this reread: `10 / 17 = 0.588235`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_precode_packet_2026-05-06.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md`
- **Scope OUT:**
  - `GENESIS_WORKING_CONTRACT.md`
  - all `src/**`
  - all `config/**`
  - all `scripts/**`
  - all `tests/**`
  - all `results/**` generation or retention changes
  - widening beyond the already named fixed windows
  - reopening annual shape, month packaging, suppression, combined counts, candle/proxy surfaces, or runtime/default/authority/promotion/family semantics

## Exact method

1. reread the landed concentration note
2. reread the frozen local-window concentration JSON artifact
3. restate the already-named retained windows as an ordered timeline table with:
   - start
   - end
   - row count
   - gap to next retained window
4. describe the chronology difference as wave ordering and spacing only
5. restate explicitly that concentration authority remains with the prior landed top-two comparison

## Output required

- one bounded analysis note
- one ordered timeline table for each month
- one explicit concentration-versus-chronology separation paragraph
- one validation note covering touched-doc checks only

## Stop conditions

- the new note starts describing `10 / 17` as a revised concentration result
- any source outside the two fixed admissible inputs becomes necessary
- the slice begins to imply runtime, default, promotion, or family authority
- the reread starts widening to additional windows, months, or years
