# RI policy router continuation_release_hysteresis exercising-subject validation — 2026-05-04

## Scope

Bounded RI-only research-evidence reread of the already-implemented enabled-only `continuation_release_hysteresis` seam on one exact subject that **does** exercise `switch_control_mode == continuation_release`.

This note does **not** authorize any new runtime widening, default change, family claim, or promotion claim.

## Why this exact subject

The earlier exact December fail-B validation note closed that carrier as a null seam-validation surface: the seam existed in code, but the subject never entered `switch_control_mode == continuation_release`.

To avoid reusing that null surface, the next honest move was to lock one exact subject that actually exercises the seam.

A quick read of the already-materialized annual enabled-vs-absent action-diff artifacts identified a promising fixed January 2024 cluster where the enabled carrier repeatedly showed:

- `previous_policy == RI_defensive_transition_policy`
- `raw_target_policy == RI_continuation_policy`

The tracked exercising subject chosen from that evidence is:

- symbol: `tBTCUSD`
- timeframe: `3h`
- backtest window: `2024-01-01 -> 2024-01-20`
- warmup: `120`
- data source policy: `curated_only`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

## Compared surface

Two runs were compared on the exact same subject:

1. **baseline**: enabled carrier as-is, with no explicit `continuation_release_hysteresis` override
2. **release_zero**: same enabled carrier with `multi_timeframe.research_policy_router.continuation_release_hysteresis = 0`

Shared execution envelope:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_SCORE_VERSION=v2`

## Commands run

```text
python -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_exercising_subject_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_exercising_subject_20260504.py
```

## Tracked script and artifacts

Tracked script:

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_exercising_subject_20260504.py`

Generated artifacts:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_exercising_subject_20260504/continuation_release_hysteresis_exercising_subject_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_exercising_subject_20260504/continuation_release_hysteresis_exercising_subject_row_diffs.json`

## Exact baseline continuation-release cluster

The baseline run reproduced one exact `continuation_release` cluster of **11** rows:

- `2024-01-17T15:00:00+00:00`
- `2024-01-17T18:00:00+00:00`
- `2024-01-17T21:00:00+00:00`
- `2024-01-18T09:00:00+00:00`
- `2024-01-18T12:00:00+00:00`
- `2024-01-18T15:00:00+00:00`
- `2024-01-18T18:00:00+00:00`
- `2024-01-18T21:00:00+00:00`
- `2024-01-19T00:00:00+00:00`
- `2024-01-19T03:00:00+00:00`
- `2024-01-19T06:00:00+00:00`

This closes the earlier subject-selection problem: the seam is genuinely exercised on this fixed surface.

## Outcome summary

Top-line summaries were identical across the pair:

- return: `+0.028202184149995445%`
- trades: `4`
- win rate: `75%`
- profit factor: `2.4831126657366176`
- max drawdown: `0.04865621571349886%`

But the row-level surface was **not** null:

- all row diffs: `33`
- behavioral row diffs: `17`
- parameter-only row diffs: `16`
- action diffs: `0`
- size diffs: `1`
- selected-policy diffs: `5`
- switch-reason diffs: `5`
- baseline continuation-release rows: `11`
- release-zero continuation-release rows: `8`
- continuation-release rows with behavioral difference: `11`

## Representative effect inside the seam

The decisive local shift appears on the low-zone `2024-01-18` subcluster.

At `2024-01-18T09:00:00+00:00`:

- **baseline** stays in `RI_defensive_transition_policy`
- reason: `switch_blocked_by_hysteresis`
- effective hysteresis: `1`
- position size remains defensive half-size: `0.0039`

while

- **release_zero** switches to `RI_continuation_policy`
- reason: `continuation_state_supported`
- effective hysteresis: `0`
- position size restores to full size: `0.0078`

The following `2024-01-18T12/15/18/21` rows also flip policy/reason state from defensive-blocked to continuation-supported, although they do not change action at the backtest layer on this exact subject.

By `2024-01-19T00/03/06`, baseline still records `switch_control_mode == continuation_release` because it is releasing from the defensive state on those rows, while the release-zero branch has already normalized into ordinary continuation state and therefore no longer counts those rows as continuation-release-mode rows.

## Interpretation

This exact subject gives the missing positive control for the seam:

- the seam is **real** and **exercised** here
- lowering `continuation_release_hysteresis` from implicit shared `1` to `0` causes visible policy-router-state changes on the intended `RI_defensive_transition_policy -> RI_continuation_policy` release path
- the change is strong enough to alter selected policy, switch reason, and one entry size decision inside the exact low-zone cluster
- on this bounded subject, those semantics-level changes still do **not** propagate into action-count or top-line P&L divergence

So the honest read is:

> this is an **exercising-but-topline-null** subject, not a null seam and not a proof of trading-performance impact.

## Next admissible move

If this chain is continued, the next smallest honest step is **not** more code.

The next admissible move is one more bounded RI-only evidence follow-up to locate either:

1. one exact continuation-release subject with **action-level** divergence, or
2. one exact continuation-release subject with **top-line** divergence,

while keeping the current 2024 January subject parked as the verified exercising control surface for the seam.
