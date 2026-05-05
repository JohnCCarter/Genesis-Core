# RI policy router blocked vs substituted same-window phase ordering

Date: 2026-04-29
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only phase-ordering interpretation / fixed-window chronology result`

This slice is a docs-only follow-up to `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_vs_substituted_same_windows_2026-04-28.md`.
It rereads the already-materialized `combined_timeline` on the same two fixed mixed windows and interprets the local result as **phase ordering and segment occupancy**, not as a new cohort-ranking or tuning surface.
It does not run new evidence helpers, create new artifacts, widen to new years/windows, or reopen runtime/default/promotion authority.

All returns and excursion values cited here remain timestamp-close observational proxies on existing evidence rows only.
They are descriptive only and do not establish causal superiority, realized trade PnL, row-to-trade truth, runtime authority, promotion guidance, or family readiness.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice rereads existing docs and result artifacts only and writes one bounded governance note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the same-window evidence surface is already frozen, and the missing step is a chronology read of the existing ordered timeline rather than new runtime or new artifact work.
- **Objective:** describe where blocked baseline rows and substituted continuation rows sit inside the same two fixed mixed windows, with explicit early/handoff/relapse/late segmentation.
- **Candidate:** `blocked vs substituted same-window phase ordering`
- **Base SHA:** `b52b5710cf55cbc186f6584080ebd6246c374546`
- **Skill Usage:** `none` — docs-only reread of existing evidence
- **Opus pre-code verdict:** `not required` — low-risk docs-only quick path

## Evidence inputs

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_vs_substituted_same_windows_2026-04-28.md`
- `results/research/ri_policy_router_blocked_vs_substituted_same_windows_20260428/blocked_vs_substituted_same_windows_summary.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md`
- `results/research/ri_policy_router_substituted_continuation_local_tail_windows_20260428/substituted_continuation_local_tail_windows_summary.json`
- `artifacts/bundles/findings/ri_policy_router/FIND-2026-0007_blocked_vs_substituted_same_windows_direction_lock.json`
- `artifacts/bundles/findings/ri_policy_router/FIND-2026-0006_substituted_continuation_local_tail_windows_direction_lock.json`

## Exact scope and containment

This slice is limited to the same two fixed windows already frozen by the prior same-window note:

- `2020-03-14T09:00:00+00:00 -> 2020-03-19T06:00:00+00:00`
- `2018-03-20T06:00:00+00:00 -> 2018-03-26T12:00:00+00:00`

It does **not**:

- widen to `2022`, `2025`, or any new local window
- create new `results/**` or `artifacts/**`
- reopen runtime/default/family/promotion surfaces
- claim a universal blocked-versus-substituted winner

## Exact command run

- none; this note was produced by rereading already-materialized evidence inputs only

## Fixed subject reminders

### Why the 2020 union window is still the right subject

The smaller acute `2020-03-11` and `2020-03-14` continuation-tail windows documented in the local-tail note had zero blocked-row overlap.
So the retained same-window subject remains the widened mixed union window beginning at `2020-03-14T09:00:00+00:00`, because that is the smallest bounded local interval where substituted continuation rows and blocked baseline rows both appear.

### Why the 2018 March hostile window is still the right subject

The retained `2018-03-20T06:00:00+00:00 -> 2018-03-26T12:00:00+00:00` window stays the correct contrast subject because it already carries mixed-cohort overlap and also sits inside the recurrent hostile March structure documented by the local-tail note.
So this slice keeps the broader mixed subject rather than switching to a different narrower `2018` tail pocket.

## Window 1 — mixed March 2020 union window

Window:

- `2020-03-14T09:00:00+00:00 -> 2020-03-19T06:00:00+00:00`

Observed counts reused from the prior summary artifact:

- blocked baseline longs: `5`
- substituted continuation longs: `7`
- total rows: `12`

### Phase ordering inside the interval

#### Early substituted left-tail segment

The interval opens with three substituted continuation rows before any blocked row appears:

- `2020-03-14T09:00:00+00:00` → `fwd_16 = -16.016916%`
- `2020-03-14T18:00:00+00:00` → `fwd_16 = -8.169770%`
- `2020-03-15T03:00:00+00:00` → `fwd_16 = 0.591890%`

So the continuation cohort clearly owns the earliest left-tail-exposed segment of this mixed window.

#### Delayed blocked handoff

The first blocked row does not appear until `2020-03-15T15:00:00+00:00`:

- `2020-03-15T15:00:00+00:00` → blocked `fwd_16 = 1.102507%`

That means blocked baseline participation begins only after the initial continuation-led drawdown sequence is already inside the window.

#### One last continuation relapse before the shared rebound

After the first blocked entry, the window still contains one more acute continuation relapse row:

- `2020-03-15T21:00:00+00:00` → substituted `fwd_4 = -14.521103%`, `fwd_16 = -0.819215%`

So even after blocked rows arrive, the continuation cohort still carries the last sharp early-window downside shock.

#### Mixed rebound segment

From `2020-03-16T06:00:00+00:00` through `2020-03-18T15:00:00+00:00`, both cohorts participate in the rebound segment:

Blocked rows in the rebound:

- `2020-03-17T03:00:00+00:00` → `fwd_16 = 1.334924%`
- `2020-03-17T12:00:00+00:00` → `fwd_16 = 10.683272%`
- `2020-03-18T03:00:00+00:00` → `fwd_16 = 17.644724%`

Substituted rows in the rebound:

- `2020-03-16T06:00:00+00:00` → `fwd_16 = 5.296323%`
- `2020-03-18T06:00:00+00:00` → `fwd_16 = 27.104620%`
- `2020-03-18T15:00:00+00:00` → `fwd_16 = 22.476079%`

This is therefore not a one-sided window after the handoff; it becomes a genuinely mixed rebound interval.

#### Blocked terminal timestamp

The final row in the retained 2020 window is blocked:

- `2020-03-19T06:00:00+00:00` → blocked `fwd_16 = 12.889299%`

So blocked baseline rows own the terminal timestamp even though substituted continuation rows owned the earliest left-tail segment.

### Bounded reading

The 2020 window reads best as:

> substituted early left tail -> delayed blocked handoff -> mixed rebound -> blocked terminal presence.

That means the earlier note's locally stronger blocked aggregate is still real on this proxy surface, but it is a **segment-occupancy result** inside the interval rather than a row-matched proof that blocked rows are universally stronger than substituted continuation rows.

## Window 2 — recurrent hostile March 2018 window

Window:

- `2018-03-20T06:00:00+00:00 -> 2018-03-26T12:00:00+00:00`

Observed counts reused from the prior summary artifact:

- blocked baseline longs: `9`
- substituted continuation longs: `8`
- total rows: `17`

### Phase ordering inside the interval

#### Early blocked segment

The window opens with six consecutive blocked rows before the first substituted continuation row appears:

- `2018-03-20T06:00:00+00:00` → blocked `fwd_16 = 7.496411%`
- `2018-03-20T15:00:00+00:00` → blocked `fwd_16 = -2.193636%`
- `2018-03-21T00:00:00+00:00` → blocked `fwd_16 = -5.739346%`
- `2018-03-21T09:00:00+00:00` → blocked `fwd_16 = -5.950605%`
- `2018-03-21T18:00:00+00:00` → blocked `fwd_16 = -2.967887%`
- `2018-03-22T03:00:00+00:00` → blocked `fwd_16 = -1.648346%`

So unlike the 2020 window, blocked baseline rows own the entire early segment here.

#### Substituted middle handoff

The first substituted row appears at `2018-03-22T09:00:00+00:00`, and the middle of the interval is then continuation-led:

- `2018-03-22T09:00:00+00:00` → substituted `fwd_16 = 0.962640%`
- `2018-03-22T18:00:00+00:00` → substituted `fwd_16 = 3.810543%`
- `2018-03-23T03:00:00+00:00` → substituted `fwd_16 = 1.432651%`
- `2018-03-23T12:00:00+00:00` → substituted `fwd_16 = -0.214760%`

So the 2018 window contains a true middle-window handoff where substituted continuation rows occupy the calmer recovery / less-hostile segment.

#### Blocked relapse re-entry

Blocked rows then re-enter on `2018-03-24` and own the relapse segment:

- `2018-03-24T00:00:00+00:00` → blocked `fwd_16 = -5.289905%`
- `2018-03-24T09:00:00+00:00` → blocked `fwd_16 = -7.222012%`
- `2018-03-24T18:00:00+00:00` → blocked `fwd_16 = -11.695500%`

So blocked baseline rows are not just early; they also reappear when the interval deteriorates again.

#### Substituted late tail

The interval then closes with four substituted continuation rows that form the late continuation-hostile tail:

- `2018-03-25T09:00:00+00:00` → substituted `fwd_16 = -5.950219%`
- `2018-03-25T18:00:00+00:00` → substituted `fwd_16 = -7.110930%`
- `2018-03-26T03:00:00+00:00` → substituted `fwd_16 = -7.222945%`
- `2018-03-26T12:00:00+00:00` → substituted `fwd_16 = -2.330388%`

This aligns with the local-tail note's broader statement that March 2018 belongs to a recurrent hostile continuation structure rather than a single acute continuation burst.

### Bounded reading

The 2018 window reads best as:

> blocked early deterioration -> substituted middle handoff -> blocked relapse re-entry -> substituted late tail.

That means the earlier same-window note's locally weaker blocked aggregate in this window is also a **timing/segment result**: substituted continuation rows sit inside the middle handoff and final late-tail parts of the interval rather than being compared row-for-row against blocked rows on identical timestamps.

## Cross-window synthesis

The two fixed windows now support a more explicit chronology reading:

- `2020` = substituted early left tail -> blocked delayed handoff -> mixed rebound -> blocked terminal timestamp
- `2018` = blocked early deterioration -> substituted middle handoff -> blocked relapse re-entry -> substituted late tail

So the sign flip between the two windows is best explained by **segment occupancy and handoff timing**, not by one universal blocked-versus-substituted quality rule.

This also reconciles the two upstream notes cleanly:

- the local-tail note already said `2020` is continuation-friendly despite a few acute concentrated windows
- the same-window note already said the mixed `2020` and `2018` windows flip in local blocked-versus-substituted balance
- this phase-ordering reread explains _why_ they flip: the cohorts occupy different parts of the local sequence in the two windows

## Consequence for the broader evidence chain

This slice does **not** change annual conclusions.
It also does **not** promote same-window comparison into a universal cohort-ranking tool.

What it adds is narrower and cleaner:

- same-window evidence is still useful, but mainly as a bounded chronology surface
- the key difference is who owns the early drawdown, the handoff, the relapse, and the terminal tail inside the interval
- therefore local same-window comparison is most honest when described as **phase ordering**, not as a universal winner declaration

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- row-to-trade truth
- causal superiority of one cohort
- annual reclassification
- runtime/default tuning guidance
- promotion or family-readiness claims
- that these two windows represent all `2018` or all `2020` behavior

## Next admissible step

If this exact line is reopened again, the cheapest honest move is either:

- to persist this fixed-window chronology result into the findings bank as another research-only duplicate-work guard, or
- to leave the local same-window chain parked here and move to a different read-only RI surface.

What is **not** justified from this note is widening to more years, opening new windows, or returning to runtime tuning.

## What is not justified from this slice

- widening to more same-window subjects without a new packet
- collapsing the two fixed windows into one universal blocked-versus-substituted ranking rule
- runtime tuning from local chronology alone
- promotion or readiness claims from these bounded proxy windows
