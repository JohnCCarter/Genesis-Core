# RI policy router continuation_release_hysteresis top-line subject validation — 2018-03 — 2026-05-04

## Scope

Bounded RI-only research-evidence validation of the first opposite-sign exact subject from the frozen continuation-release monthly inventory.

This slice turns the monthly `2018-03` candidate into one dedicated exact-subject note with a tracked script and reproducible local artifacts.

This note is **bounded observational evidence only**. It does **not** establish runtime readiness, promotion value, or a general rule beyond this exact subject.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: deterministic read-only paired backtests on a high-sensitivity router carrier; no runtime/config/schema/test edits
- **Required Path:** `Lite research-evidence path` — non-trivial read-only analysis slice; not quick path and not runtime integration
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the seam is already implemented, two exact positive subjects are already closed, and the next unresolved question is whether the first opposite-sign monthly candidate remains negative on a dedicated exact-subject rerun without widening scope
- **Objective:** validate the exact March 2018 subject that the frozen monthly inventory fixed as the first opposite-sign exact subject under `continuation_release_hysteresis = 0`
- **Candidate:** `continuation_release_hysteresis March 2018 exact subject`
- **Base SHA:** `52b43e82b1c1e1aaceab3a078c62c736b6eea371`

## Skill usage

- primary: `genesis_backtest_verify`
- supporting: `python_engineering`

## Why this exact subject

The historical monthly inventory over the frozen full-calendar-month grid (`2016-07 -> 2026-03`) found:

- `54` seam-active months
- `0` months with action-level divergence
- multiple months with top-line divergence in both signs

Within that bounded map:

- `2021-08` closed as the first exact positive subject
- `2025-10` closed as the second exact positive subject
- `2018-03` remained the first opposite-sign exact subject to close from that frozen monthly inventory

The exact subject therefore is:

- symbol: `tBTCUSD`
- timeframe: `3h`
- backtest window: `2018-03-01 -> 2018-03-31`
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

The emitted summary records:

- runtime base SHA: `52b43e82b1c1e1aaceab3a078c62c736b6eea371`
- evidence commit SHA: `52b43e82b1c1e1aaceab3a078c62c736b6eea371`
- evidence checkout clean: `false`
- local reproducibility scope: bounded local research environment with `curated_only` data present
- carrier SHA256: `d6bfd4e18ea27f5cfd59f4ac1c6cff1f8762a1d35f6b5a369f5ccd004934913e`

`runtime_base_sha` and `evidence_commit_sha` are distinct provenance fields that happened to be equal on this checkout.

That means this slice proves **same-local-checkout double-run reproducibility**, not a clean-checkout CI-hermetic claim.

## Commands run

```text
python -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504.py
```

## Determinism proof

The exact-subject script was executed **twice** on the same local evidence checkout.

Both runs emitted identical hashes:

- summary hash: `e0b4dd04ae6bffc7f554f45eb5eebbb9739c84ebf6fcbdbfd9f0f81d03ab026a`
- row-diff hash: `70cd626fc8edf8469fbd00b982a0c82a02cebff291bb07f6916d39510ee35838`

Both summaries also reported canonical execution mode:

- `fast_window = true`
- `env_precompute_features = "1"`
- `precompute_enabled = true`
- `precomputed_ready = true`
- `mode_explicit = "1"`

## Tracked script and artifacts

Tracked script:

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504.py`

Generated local artifacts:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2018_03_20260504/continuation_release_hysteresis_topline_subject_2018_03_row_diffs.json`

These `results/backtests/**` outputs are local evidence artifacts for this slice and are **not** part of the tracked-file scope unless scope is explicitly widened later.

## Exact continuation-release cluster

The baseline run reproduced this exact twelve-row `continuation_release` cluster:

- `2018-03-16T09:00:00+00:00`
- `2018-03-16T12:00:00+00:00`
- `2018-03-16T15:00:00+00:00`
- `2018-03-17T03:00:00+00:00`
- `2018-03-17T06:00:00+00:00`
- `2018-03-17T09:00:00+00:00`
- `2018-03-17T12:00:00+00:00`
- `2018-03-17T15:00:00+00:00`
- `2018-03-17T18:00:00+00:00`
- `2018-03-17T21:00:00+00:00`
- `2018-03-18T00:00:00+00:00`
- `2018-03-18T03:00:00+00:00`

The `release_zero` run preserves only the first six continuation-release timestamps:

- `2018-03-16T09:00:00+00:00`
- `2018-03-16T12:00:00+00:00`
- `2018-03-16T15:00:00+00:00`
- `2018-03-17T03:00:00+00:00`
- `2018-03-17T06:00:00+00:00`
- `2018-03-17T09:00:00+00:00`

## Outcome summary

### Baseline

- final capital: `9986.751527150065`
- total return: `-0.13248472849934842%`
- trades: `13`
- profit factor: `0.7094389933209679`
- max drawdown: `0.2767040530368071%`
- net position PnL: `-13.248472849936935`

### Release-zero

- final capital: `9985.814359850066`
- total return: `-0.14185640149933534%`
- trades: `13`
- profit factor: `0.6900617700620761`
- max drawdown: `0.2767299537799832%`
- net position PnL: `-14.18564014993693`

### Exact deltas

- final capital delta: `-0.9371672999986913`
- total return delta: `-0.009371672999986924 percentage points`
- trade count delta: `0`

## Row-level summary

Observed diff counts on the exact subject:

- all row diffs: `121`
- action diffs: `0`
- size diffs: `2`
- selected-policy diffs: `6`
- switch-reason diffs: `6`
- behavioral row diffs: `35`
- parameter-only row diffs: `86`
- baseline continuation-release rows: `12`
- release-zero continuation-release rows: `6`
- continuation-release rows with behavioral difference: `12`

The key bounded correction remains explicit:

> this subject shows **negative top-line divergence without action-level divergence**.

Trade count stays unchanged and `action_diff_count` remains `0`.

## Representative local effect

The first decisive local split begins on `2018-03-17T03:00:00+00:00`.

At that timestamp:

- **baseline** stays in `RI_defensive_transition_policy`
- reason: `switch_blocked_by_hysteresis`
- effective hysteresis: `1`
- position size remains defensive half-size: `0.006`

while

- **release_zero** switches to `RI_continuation_policy`
- reason: `continuation_state_supported`
- effective hysteresis: `0`
- position size restores to full size: `0.012`

The same bounded policy/reason split continues at `2018-03-17T06:00:00+00:00` and `2018-03-17T09:00:00+00:00`.

After that point, `release_zero` has already normalized out of continuation-release mode, while the baseline branch continues recording continuation-release on `2018-03-17T12:00:00+00:00` through `2018-03-18T03:00:00+00:00`.

The earlier `2018-03-16T09:00:00+00:00` through `2018-03-16T15:00:00+00:00` rows are still inside the continuation-release cluster, but the difference there remains control-level (`effective_hysteresis` `1 -> 0`) without a policy or size change.

## Interpretation

This subject is the first exact bounded opposite-sign reread on this carrier.

It shows that:

- the same continuation-release seam is genuinely exercised
- the same control/policy/size-path changes are visible
- the action count still does **not** change
- but the top-line outcome moves in the **opposite** direction from the two positive exact subjects

So the honest read is:

> on the bounded exact subject `tBTCUSD / 3h / 2018-03-01..2018-03-31`, setting `multi_timeframe.research_policy_router.continuation_release_hysteresis = 0` underperformed the baseline enabled carrier by `0.9371672999986913` USD (`0.009371672999986924` return points), while `num_trades` remained `13 -> 13` and `action_diff_count` remained `0`.

This is observational exact-subject evidence only. It does **not** authorize runtime or generalization claims.

## Do-not-overclaim guardrails

This note does **not** justify:

- runtime widening
- default-path changes
- promotion or readiness claims
- a general statement that `continuation_release_hysteresis = 0` is broadly worse
- a generalized asymmetry claim from one opposite-sign subject alone
- a claim that the seam changes actions/trade counts on this carrier

## Next admissible move

At this point, the bounded exact-subject picture now includes two positive subjects and one opposite-sign subject on the same carrier.

The next smallest honest move is no longer automatic runtime work.

If this chain continues, the cleanest bounded options are now either:

1. one more exact negative subject to test whether March 2018 is representative of a broader opposite-sign subgroup, or
2. one short synthesis note that explicitly compares the shared policy/size-path mechanism across `2021-08`, `2025-10`, and `2018-03` without widening into runtime claims.
