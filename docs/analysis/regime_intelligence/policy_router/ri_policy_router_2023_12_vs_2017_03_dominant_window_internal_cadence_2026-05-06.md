# RI policy router 2023-12 vs 2017-03 dominant-window internal cadence

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `completed / docs-only window-internal reread / frozen-evidence follow-up`

This slice is a docs-only follow-up to two already-landed mixed-year notes:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2017_03_dominant_window_chronology_2026-05-06.md`

It rereads one already-materialized evidence artifact only:

- `results/evaluation/ri_policy_router_2023_12_vs_2017_03_continuation_local_window_concentration_2026-05-06.json`

No new helper was created.
No new artifact was generated.
No extraction was rerun.

## COMMAND PACKET

- **Category:** `docs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the already-fixed dominant windows differ inside the window itself, not only in concentration or chronology across windows.
- **Candidate:** `2023-12 vs 2017-03 dominant-window internal cadence`
- **Base SHA:** `a3624233dfc49d764d9c6f3f917e80dbeea3af73`
- **Skill Usage:** `none claimed`

## Guardrail

This reread does **not** revise either prior landed result.

The authoritative higher-level reads remain:

- concentration: `2023-12` is more top-two concentrated than `2017-03`
- chronology: `2023-12` is a compact late dual-wave burst, while `2017-03` is an early anchor plus two later revisit waves

This note asks only what happens **inside** those already-fixed dominant waves.

## Fixed internal gap sequences

### `2023-12`

Retained wave 1:

- window: `2023-12-15T21:00:00+00:00 -> 2023-12-17T18:00:00+00:00`
- timestamps: `6`
- internal gaps: `[9h, 9h, 9h, 9h, 9h]`

Retained wave 2:

- window: `2023-12-22T15:00:00+00:00 -> 2023-12-26T00:00:00+00:00`
- timestamps: `7`
- internal gaps: `[9h, 9h, 18h, 9h, 18h, 18h]`

Aggregate retained internal cadence on the fixed December surface:

- total internal gaps = `11`
- `9h` gaps = `8`
- `18h` gaps = `3`

### `2017-03`

Retained wave 1:

- window: `2017-03-04T09:00:00+00:00 -> 2017-03-05T21:00:00+00:00`
- timestamps: `4`
- internal gaps: `[18h, 9h, 9h]`

Retained wave 2:

- window: `2017-03-23T18:00:00+00:00 -> 2017-03-24T12:00:00+00:00`
- timestamps: `3`
- internal gaps: `[9h, 9h]`

Retained wave 3:

- window: `2017-03-29T21:00:00+00:00 -> 2017-03-30T15:00:00+00:00`
- timestamps: `3`
- internal gaps: `[9h, 9h]`

Aggregate retained internal cadence on the fixed March surface:

- total internal gaps = `7`
- `9h` gaps = `6`
- `18h` gaps = `1`

## Main result

### 1. The two months share the same internal cadence alphabet

Inside the retained dominant windows, both months use only the same two gap sizes:

- `9h`
- `18h`

No retained dominant wave in either month introduces a wider internal gap than `18h`.

So the mixed-year divergence is **not** driven by a novel within-window cadence family.
Both subjects still operate on the same underlying bar-gap alphabet.

### 2. `2023-12` expresses its dominance through a more elastic large late wave

The smaller December wave is completely regular:

- `[9h, 9h, 9h, 9h, 9h]`

But the larger late wave is not a pure uninterrupted `9h` run.
It absorbs repeated skipped-bar pauses while still staying inside one retained wave:

- `[9h, 9h, 18h, 9h, 18h, 18h]`

That means the dominant December continuation mass is not only late and large.
It is also internally **elastic**: the wave can carry repeated `18h` pauses without breaking into separate revisit windows.

### 3. `2017-03` keeps its later revisit waves internally regular

March shows one `18h` gap only once, inside the early anchor wave:

- early anchor: `[18h, 9h, 9h]`

But both later revisit waves are internally regular:

- first revisit: `[9h, 9h]`
- second revisit: `[9h, 9h]`

So March's divergence is not a matter of increasingly elastic internal cadence.
Its later dominant mass is carried by **reopening new waves** that each remain internally regular.

### 4. The sharpened split is now clear: elastic late-wave persistence versus regular revisit recurrence

The bounded within-window comparison now sharpens the earlier chronology read like this:

- `2023-12`: same bar-gap alphabet, but more `18h` skipped-bar elasticity is absorbed inside one large late wave
- `2017-03`: same bar-gap alphabet, but the later mass reappears through separate revisit waves that keep regular `9h` internal cadence

So the difference is not “December has a different cadence system.”
The difference is where the interruptions live:

- December absorbs more interruption **inside** one dominant late wave
- March resolves more of the structure **between** separate revisit waves

## Honest synthesis

The smallest honest synthesis is now:

> the mixed-year continuation divergence survives at a third bounded level. The months already differed in concentration and chronology, and they now differ subtly inside the dominant windows too: both subjects share the same `9h/18h` internal cadence alphabet, but `2023-12` expresses more skipped-bar elasticity inside one large late wave, whereas `2017-03` keeps its later revisit waves internally regular and expresses dispersion mainly by reopening new waves.

This is a window-internal clarification only.
It does **not** revise the landed concentration result or the landed chronology result.

## What this slice supports

This slice now supports the following bounded statements:

1. both months share the same internal dominant-window cadence alphabet (`9h`, `18h`)
2. the mixed-year divergence is therefore not driven by a novel within-window cadence family
3. `2023-12` carries more skipped-bar elasticity inside its large late wave
4. `2017-03` keeps its later revisit waves internally regular and expresses divergence mainly between waves rather than inside them
5. the mixed-year line now differs at three bounded levels: concentration, chronology, and internal wave elasticity

## What this slice does not support

This slice does **not** support any of the following:

- revising the landed concentration comparison
- revising the landed chronology comparison
- widening to additional windows, months, or years
- any new helper, artifact, or regenerated extraction
- runtime/default/config/policy/promotion/family claims
- candle, proxy-return, or row-to-trade truth claims

## Exact command run

- none; this note was produced by rereading the landed notes and the frozen concentration artifact only

## Validation

Validation for this docs-only slice is limited to:

- manual cross-check that the timestamps and gap sequences match the frozen JSON artifact exactly
- touched-doc formatting / whitespace validation

## Re-anchor consequence

The mixed-year annual line is now sharper at one more tiny but honest layer:

- concentration divergence remains real
- chronology divergence remains real
- internal-wave cadence divergence is now also bounded and explicit

Still observational only.
Still non-authoritative.
Still nowhere near runtime crowning rights — just better cartography.
