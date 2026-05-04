# RI policy router continuation_release_hysteresis monthly inventory — 2026-05-04

## Scope

Bounded RI-only research-evidence inventory over historical **full calendar months** for the already-implemented enabled-only `continuation_release_hysteresis` seam.

This slice exists to stop one-off subject guessing and replace it with one reproducible monthly map.

It does **not** authorize runtime widening, config/schema changes, family/default changes, promotion claims, or clean-checkout CI-hermetic claims.

## Governance framing

- Mode: `RESEARCH`
- Lane: `Research-evidence`
- Path: `Lite`
- Risk: `MED` because the slice runs deterministic paired backtests on a high-sensitivity router carrier, but does not edit runtime/config/test surfaces
- Opus pre-code review verdict: `APPROVED_WITH_NOTES`

The required Opus notes were implemented by freezing:

- exact base SHA
- exact monthly grid
- exact ranking/tie-break order
- explicit skill usage
- explicit determinism proof via double execution hash match
- explicit local reproducibility scope

## Skill usage

- primary: `genesis_backtest_verify`
- supporting: `python_engineering`

## Why this inventory was needed

Two earlier continuation-release slices had already been closed:

1. December 2023 fail-B carrier: **null / non-exercising**
2. January 2024 exact exercising control: **exercising-but-topline-null**

A further read-only January 2024 extension (`2024-01-01 -> 2024-01-31`) still produced stronger semantics drift but **0 action diffs** and identical top-line metrics.

At that point, more guessed one-off windows were no longer the honest next move.
The next honest move was one bounded inventory over a fixed historical grid.

## Fixed inventory definition

### Base and reproducibility scope

- base SHA: `52b43e82b1c1e1aaceab3a078c62c736b6eea371`
- local reproducibility scope: bounded local research environment with `curated_only` data present
- explicitly **not** a clean-checkout CI-hermetic claim

### Shared subject definition

- symbol: `tBTCUSD`
- timeframe: `3h`
- warmup: `120`
- data source policy: `curated_only`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

### Compared surface

For every fixed window, two runs were compared:

1. **baseline** = enabled carrier as-is (implicit shared hysteresis)
2. **release_zero** = same enabled carrier with `continuation_release_hysteresis = 0`

### Canonical env

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_SCORE_VERSION=v2`

### Monthly grid

- family: `full_calendar_month`
- date bounds: `2016-07-01 -> 2026-03-31`
- stride: `1 month`
- max windows: `117`
- excluded edge partial months: `2016-06`, `2026-04`

The partial edge months were intentionally excluded to keep the grid on stable full-month windows and avoid clipped-edge ambiguity.

### Ranking order

Candidate windows were ranked by this frozen order:

1. `action_diff_count desc`
2. `topline_changed desc`
3. `abs(total_return_diff) desc`
4. `abs(final_capital_diff) desc`
5. `abs(num_trades_diff) desc`
6. `size_diff_count desc`
7. `selected_policy_diff_count desc`
8. `behavioral_row_diff_count desc`
9. `continuation_release_behavioral_diff_count desc`
10. `baseline_continuation_release_row_count desc`
11. `window_start asc`

## Tracked script and emitted artifacts

Tracked script:

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504.py`

Emitted artifacts:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`

## Commands run

```text
python -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504.py
```

## Determinism proof

The fixed monthly inventory was executed **twice** on the same grid.

Both runs emitted the same normalized summary hash:

- first hash: `f603422a891096a3e125f506a382d1cfe188168dd1c613412fca1fcc5021cf80`
- second hash: `f603422a891096a3e125f506a382d1cfe188168dd1c613412fca1fcc5021cf80`

That is the required bounded determinism proof for this inventory slice.

## Headline result

The inventory materially changes the search picture.

Across the fixed monthly grid:

- total windows scanned: `117`
- seam-active windows: `54`
- windows with any `action_diff_count > 0`: `0`
- windows with top-line divergence: present

So the monthly inventory says:

> no exact full-month subject in this bounded grid shows action-level divergence, but multiple full-month subjects do show real top-line divergence under `release_zero`.

That is enough to stop chasing action-flip windows as the leading hypothesis on this carrier and to prioritize the first true top-line-divergent subject instead.

## Rank 1 subject

The top-ranked monthly subject is:

- label: `2021-08`
- exact window: `2021-08-01 -> 2021-08-31`

### Why it ranks first

It has:

- `0` action diffs
- `2` size diffs
- `9` selected-policy diffs
- `9` switch-reason diffs
- `13` behavioral row diffs
- `6` baseline continuation-release rows
- `6` release-zero continuation-release rows
- **top-line divergence = true**

### Exact top-line difference

Baseline:

- final capital: `9986.57745325635`
- total return: `-0.13422546743649946%`
- trades: `7`
- profit factor: `0.6052453866698398`

Release-zero:

- final capital: `10005.467539598`
- total return: `0.054675395979993484%`
- trades: `7`
- profit factor: `1.1607993267668864`

Difference:

- final capital delta: `+18.890086341649294`
- total return delta: `+0.18890086341649295 percentage points`
- trade count delta: `0`

### Exact continuation-release timestamps

The monthly divergence clusters around these continuation-release rows:

- `2021-08-18T03:00:00+00:00`
- `2021-08-18T06:00:00+00:00`
- `2021-08-18T09:00:00+00:00`
- `2021-08-19T03:00:00+00:00`
- `2021-08-19T06:00:00+00:00`
- `2021-08-19T09:00:00+00:00`

## Other high-ranked months

The next strongest monthly subjects in this bounded inventory are:

- `2025-10`
  - top-line divergence true
  - final capital delta `+17.134840124999755`
  - total return delta `+0.17134840124999756 percentage points`

- `2018-03`
  - top-line divergence true
  - final capital delta `-0.9371672999986913`
  - total return delta `-0.009371672999986924 percentage points`

This means the inventory did **not** produce one isolated strange month; it produced a ranked candidate bench with August 2021 clearly on top.

## Negative result that still matters

No monthly window in the bounded grid produced any action-level divergence.

That matters because it narrows the honest next question.
The continuation-release seam on this carrier appears to matter first through:

- selected policy
- switch reason
- size
- downstream top-line performance

and **not** through direct action-count divergence on the bounded monthly surface.

## Do-not-repeat findings

- Do **not** reopen December 2023 fail-B as a continuation-release subject; it is already closed as non-exercising.
- Do **not** reopen January 2024 `2024-01-01 -> 2024-01-20` as unresolved; it is already closed as exercising-but-topline-null.
- Do **not** keep guessing arbitrary nearby January windows as the main search method; this monthly inventory supersedes that strategy for this carrier.
- Do **not** overclaim the inventory as runtime authority; it is only a bounded subject-ranking map.

## Honest interpretation

The monthly inventory provides the first bounded historical map of the seam on this exact carrier.

Its main contribution is not a code change but a **subject-selection correction**:

- the leading next subject is no longer January 2024
- the leading next subject is now **August 2021**
- the most promising follow-up target is now **top-line divergence**, not action-level divergence

## Next admissible move

If this chain continues, the next smallest honest step is one bounded RI-only exact-subject validation on:

- `tBTCUSD`
- `3h`
- `2021-08-01 -> 2021-08-31`
- `warmup=120`
- `curated_only`
- same weak-pre-aged release-guard carrier

The purpose of that next slice would be to turn the inventory-ranked monthly subject into one dedicated exact-subject note, verify the exact local seam cluster around `2021-08-18 -> 2021-08-19`, and keep the interpretation strictly at research-evidence level.
