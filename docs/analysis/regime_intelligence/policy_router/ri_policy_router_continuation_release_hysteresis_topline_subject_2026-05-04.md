# RI policy router continuation_release_hysteresis top-line subject validation — 2026-05-04

## Scope

Bounded RI-only research-evidence validation of the inventory-ranked August 2021 monthly winner for the already-implemented enabled-only `continuation_release_hysteresis` seam.

This slice turns the monthly rank-1 subject into one dedicated exact-subject note with a tracked script and reproducible artifacts.

This note is **bounded observational evidence only**. It does **not** establish runtime readiness, promotion value, or a general rule beyond this exact subject.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: deterministic read-only paired backtests on a high-sensitivity router carrier; no runtime/config/schema/test edits
- **Required Path:** `Lite research-evidence path` — non-trivial read-only analysis slice; not quick path and not runtime integration
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the seam is already implemented, the monthly inventory is already complete, and the next unresolved question is one exact interpretation of the first top-line-divergent subject rather than further runtime work
- **Objective:** validate the exact August 2021 subject that the monthly inventory ranked first for bounded top-line divergence under `continuation_release_hysteresis = 0`
- **Candidate:** `continuation_release_hysteresis August 2021 exact subject`
- **Base SHA:** `52b43e82b1c1e1aaceab3a078c62c736b6eea371`

## Skill usage

- primary: `genesis_backtest_verify`
- supporting: `python_engineering`

## Why this exact subject

The historical monthly inventory over the frozen full-calendar-month grid (`2016-07 -> 2026-03`) found:

- `54` seam-active months
- `0` months with action-level divergence
- multiple months with top-line divergence

Within that bounded map, `2021-08` ranked first.

The exact subject therefore is:

- symbol: `tBTCUSD`
- timeframe: `3h`
- backtest window: `2021-08-01 -> 2021-08-31`
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

## Subject fingerprint and reproducibility scope

- base SHA: `52b43e82b1c1e1aaceab3a078c62c736b6eea371`
- actual head SHA at execution: `52b43e82b1c1e1aaceab3a078c62c736b6eea371`
- local reproducibility scope: bounded local research environment with `curated_only` data present
- explicitly **not** a clean-checkout CI-hermetic claim

## Commands run

```text
python -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504.py
```

## Determinism proof

The exact-subject script was executed **twice** on the same SHA and same inputs.

Both runs emitted identical hashes:

- summary hash: `9762fe09044712e95b772c4c13e70717264b9688d211ea632765026feacad55e`
- row-diff hash: `caa9971edc2c53f7af7ca0bc7621f99c5ee330bd51b0167bc023f5007d16e346`

Both summaries also reported canonical execution mode:

- `fast_window = true`
- `env_precompute_features = "1"`
- `precompute_enabled = true`
- `precomputed_ready = true`
- `mode_explicit = "1"`

## Tracked script and artifacts

Tracked script:

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504.py`

Generated artifacts:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_20260504/continuation_release_hysteresis_topline_subject_row_diffs.json`

## Exact continuation-release cluster

The baseline run reproduced this exact six-row `continuation_release` cluster:

- `2021-08-18T03:00:00+00:00`
- `2021-08-18T06:00:00+00:00`
- `2021-08-18T09:00:00+00:00`
- `2021-08-19T03:00:00+00:00`
- `2021-08-19T06:00:00+00:00`
- `2021-08-19T09:00:00+00:00`

The `release_zero` run preserves the same six continuation-release timestamps on this exact subject.

## Outcome summary

### Baseline

- final capital: `9986.57745325635`
- total return: `-0.13422546743649946%`
- trades: `7`
- profit factor: `0.6052453866698398`
- max drawdown: `0.3990334201665078%`
- net position PnL: `-13.42254674365007`

### Release-zero

- final capital: `10005.467539598`
- total return: `0.054675395979993484%`
- trades: `7`
- profit factor: `1.1607993267668864`
- max drawdown: `0.398282905445889%`
- net position PnL: `5.467539598000419`

### Exact deltas

- final capital delta: `+18.890086341649294`
- total return delta: `+0.18890086341649295 percentage points`
- trade count delta: `0`

## Row-level summary

Observed diff counts on the exact subject:

- all row diffs: `118`
- action diffs: `0`
- size diffs: `2`
- selected-policy diffs: `9`
- switch-reason diffs: `9`
- behavioral row diffs: `13`
- parameter-only row diffs: `105`
- baseline continuation-release rows: `6`
- release-zero continuation-release rows: `6`
- continuation-release rows with behavioral difference: `6`

The key bounded correction is explicit:

> this subject shows **top-line divergence without action-level divergence**.

Trade count stays unchanged and `action_diff_count` remains `0`.

## Representative local effect

The decisive local shift begins on `2021-08-19T03:00:00+00:00`.

At that timestamp:

- **baseline** stays in `RI_defensive_transition_policy`
- reason: `switch_blocked_by_hysteresis`
- effective hysteresis: `1`
- position size remains defensive half-size: `0.0039`

while

- **release_zero** switches to `RI_continuation_policy`
- reason: `continuation_state_supported`
- effective hysteresis: `0`
- position size restores to full size: `0.0078`

The following `2021-08-19T06:00:00+00:00` and `2021-08-19T09:00:00+00:00` rows continue that same bounded policy/reason split.

The earlier `2021-08-18T03/06/09` rows are still part of the continuation-release cluster, but there the difference remains control-level (`effective_hysteresis` `1 -> 0`) without a policy or size change.

## Interpretation

This subject is the first bounded exact subject on this carrier that combines all three of the following:

- the seam is genuinely exercised
- the row-level control/policy/size changes are visible
- the top-line result changes materially

But the evidence is still bounded and observational:

- the subject remains one exact August 2021 window only
- trade count does not change
- action-level divergence remains `0`
- no general runtime rule is established from this note alone

So the honest read is:

> on the exact `2021-08` subject, lowering `continuation_release_hysteresis` to `0` improves top-line outcome through policy/size-path changes while leaving action count unchanged.

## Do-not-overclaim guardrails

This note does **not** justify:

- runtime widening
- default-path changes
- promotion or readiness claims
- a general statement that `continuation_release_hysteresis = 0` is broadly better
- a claim that the seam changes actions/trade counts on this carrier

## Next admissible move

If this chain continues, the next smallest honest step is one more bounded RI-only exact-subject follow-up on the next inventory-ranked monthly candidate.

The cleanest options are now:

1. `2025-10` as the second positive top-line-divergent subject, or
2. `2018-03` as the first bounded opposite-sign top-line-divergent subject

That would let the next slice test whether August 2021 is a one-off winner or part of a broader sign-consistent subgroup on the same carrier.
