# RI policy router continuation_release_hysteresis top-line subject triad synthesis — 2026-05-04

## Scope

Bounded RI-only research-evidence synthesis over the **complete full-calendar-month top-line-divergent exact-subject set** on the frozen `continuation_release_hysteresis` inventory surface.

This note does **not** add new runtime behavior, run a new candidate, or reopen subject selection by guesswork. It only synthesizes the already-closed exact subjects `2021-08`, `2025-10`, and `2018-03` against the frozen monthly inventory that produced them.

This note is **bounded observational evidence only**. It does **not** establish runtime readiness, promotion value, or a general rule beyond this exact triad.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: docs-only synthesis over already-verified read-only evidence; no runtime/config/schema/test edits and no new backtest execution
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the frozen monthly inventory and all three exact subjects are already closed, and the only unresolved task on this surface is to state what the complete exact-subject triad does and does not support
- **Objective:** synthesize the shared mechanism and bounded divergence pattern across the full exact-subject triad for the frozen full-calendar-month inventory
- **Candidate:** `continuation_release_hysteresis exact-subject triad synthesis`
- **Base SHA:** `52b43e82b1c1e1aaceab3a078c62c736b6eea371`

## Evidence surface used

This note is built only from already-closed evidence surfaces:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_monthly_inventory_2026-05-04.md`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_2026-05-04.md`

No new backtests were run for this synthesis. The only new read is the frozen monthly windows artifact, which confirms that the current full-calendar-month grid contains exactly three rows with `topline_changed = true`.

## Why this synthesis is now the smallest honest move

The March 2018 note left two bounded options:

1. one more exact negative subject, or
2. one short synthesis note.

A direct reread of the frozen monthly windows artifact resolves that fork.

On the exact frozen monthly grid (`2016-07 -> 2026-03`), the full top-line-divergent set is:

1. `2021-08` — positive
2. `2025-10` — positive
3. `2018-03` — negative

There is **no fourth full-calendar-month exact subject** with `topline_changed = true` on this inventory surface, and there is therefore no second negative month to close without widening beyond the frozen grid.

So the next honest step is synthesis, not a fabricated extra subject.

## Shared invariants across the full triad

All three exact subjects share the same bounded surface:

- symbol: `tBTCUSD`
- timeframe: `3h`
- warmup: `120`
- data source policy: `curated_only`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- variant: enabled carrier baseline vs the same carrier with `multi_timeframe.research_policy_router.continuation_release_hysteresis = 0`
- canonical env: seed `42`, fast-window `1`, precompute-features `1`, cache-write `0`, mode-explicit `1`, fast-hash `0`, score-version `v2`

All three also preserve the same bounded action-layer invariants:

- `action_diff_count = 0`
- `num_trades_diff = 0`
- visible policy/reason/size-path changes inside the continuation-release seam

So the exact triad already proves that, on this frozen full-month surface, the seam can move top-line outcome **without** moving action count.

## Side-by-side comparison

| Subject   | Inventory rank | Top-line sign |   Final capital delta |               Return delta | Continuation-release rows (baseline -> release_zero) | Size / policy / reason / behavioral diffs | First decisive local split  |
| --------- | -------------: | ------------- | --------------------: | -------------------------: | ---------------------------------------------------- | ----------------------------------------- | --------------------------- |
| `2021-08` |            `1` | positive      | `+18.890086341649294` |  `+0.18890086341649295 pp` | `6 -> 6`                                             | `2 / 9 / 9 / 13`                          | `2021-08-19T03:00:00+00:00` |
| `2025-10` |            `2` | positive      | `+17.134840124999755` |  `+0.17134840124999756 pp` | `13 -> 10`                                           | `2 / 6 / 9 / 19`                          | `2025-10-17T21:00:00+00:00` |
| `2018-03` |            `3` | negative      | `-0.9371672999986913` | `-0.009371672999986924 pp` | `12 -> 6`                                            | `2 / 6 / 6 / 35`                          | `2018-03-17T03:00:00+00:00` |

## Shared mechanism

Across the triad, the local mechanism is recognizably the same seam:

- baseline keeps `effective_hysteresis = 1`
- baseline remains longer in `RI_defensive_transition_policy`
- baseline carries `switch_blocked_by_hysteresis`
- baseline therefore holds defensive half-size longer

while

- `release_zero` lowers `effective_hysteresis` to `0`
- `release_zero` reaches `RI_continuation_policy` earlier
- `release_zero` carries `continuation_state_supported`
- `release_zero` restores full size earlier

That common mechanism is present in all three exact subjects.

So the bounded question is **not** whether the seam is real.
The seam is real and exercised.

The bounded question is what outcome sign that same mechanism produces on different exact subjects.

## What the triad changes in the interpretation

The full triad sharpens the current read in two important ways.

### 1. Stable mechanism does not imply stable sign

Two exact subjects are positive:

- `2021-08`
- `2025-10`

But the same seam shape is negative on:

- `2018-03`

So the honest current read is:

> on the frozen full-calendar-month inventory, `continuation_release_hysteresis = 0` has a stable local policy/size-path mechanism but **not** a stable top-line sign.

### 2. More behavioral drift does not map cleanly to better top-line

The negative March 2018 subject has the **largest** behavioral row-diff count in the triad:

- `2018-03`: `35`
- `2025-10`: `19`
- `2021-08`: `13`

But it has the **smallest absolute** top-line magnitude:

- `2018-03`: `0.9371672999986913` USD against `release_zero`
- `2025-10`: `17.134840124999755` USD in favor of `release_zero`
- `2021-08`: `18.890086341649294` USD in favor of `release_zero`

That means the current frozen surface does **not** support any simple rule like:

- more router-state drift = better outcome, or
- more router-state drift = worse outcome

Diff-count magnitude and top-line magnitude/sign must remain separate on this surface.

## Honest current read

The strongest bounded statement now available is:

> on the frozen full-calendar-month continuation-release inventory, the complete top-line-divergent exact-subject set is a three-subject triad (`2021-08`, `2025-10`, `2018-03`). All three preserve `action_diff_count = 0` and unchanged trade count, all three show the same release-from-defensive policy/size-path mechanism, but the resulting top-line sign is mixed (`+`, `+`, `-`).

This is stronger than any one note alone, but it is still **research-evidence only**.

## Do-not-overclaim guardrails

This triad does **not** justify:

- runtime widening
- default-path changes
- promotion or readiness claims
- a general statement that `continuation_release_hysteresis = 0` is broadly better
- a general statement that `continuation_release_hysteresis = 0` is broadly worse
- a claim that the seam changes actions or trade counts on this carrier
- a claim that behavioral-row-diff count is a monotonic proxy for top-line benefit or harm
- a claim that there is already a proven broader negative subgroup beyond `2018-03`

## Next admissible move

On the current frozen **full-calendar-month** inventory surface, the exact-subject triad is now exhausted.

That means there is no further same-grid exact-subject closeout left to do.

If this chain continues beyond this synthesis, the next honest move requires a **fresh packet** that explicitly widens at least one axis beyond the frozen monthly grid.

Without such a widening packet, the correct bounded state is to keep the triad parked as the complete current top-line-divergent exact-subject bench for this carrier.
