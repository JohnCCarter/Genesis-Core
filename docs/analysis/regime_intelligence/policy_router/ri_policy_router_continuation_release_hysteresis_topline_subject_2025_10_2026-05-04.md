# RI policy router continuation_release_hysteresis top-line subject validation — 2025-10 — 2026-05-04

## Scope

Bounded RI-only research-evidence validation of the inventory-ranked October 2025 monthly follow-up for the already-implemented enabled-only `continuation_release_hysteresis` seam.

This slice turns the monthly rank-2 subject into one dedicated exact-subject note with a tracked script and reproducible local artifacts.

This note is **bounded observational evidence only**. It does **not** establish runtime readiness, promotion value, or a general rule beyond this exact subject.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: deterministic read-only paired backtests on a high-sensitivity router carrier; no runtime/config/schema/test edits
- **Required Path:** `Lite research-evidence path` — non-trivial read-only analysis slice; not quick path and not runtime integration
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the seam is already implemented, the monthly inventory is already complete, the first exact positive subject (`2021-08`) is already closed, and the next unresolved question is whether the next ranked positive subject repeats that bounded top-line pattern on a dedicated exact-subject surface
- **Objective:** validate the exact October 2025 subject that the monthly inventory ranked second for bounded top-line divergence under `continuation_release_hysteresis = 0`
- **Candidate:** `continuation_release_hysteresis October 2025 exact subject`
- **Base SHA:** `52b43e82b1c1e1aaceab3a078c62c736b6eea371`

## Skill usage

- primary: `genesis_backtest_verify`
- supporting: `python_engineering`

## Why this exact subject

The historical monthly inventory over the frozen full-calendar-month grid (`2016-07 -> 2026-03`) found:

- `54` seam-active months
- `0` months with action-level divergence
- multiple months with top-line divergence

Within that bounded map, `2025-10` ranked second behind `2021-08` and ahead of the first opposite-sign month `2018-03`.

The exact subject therefore is:

- symbol: `tBTCUSD`
- timeframe: `3h`
- backtest window: `2025-10-01 -> 2025-10-31`
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
python -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504.py
python scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504.py
```

## Determinism proof

The exact-subject script was executed **twice** on the same local evidence checkout.

Both runs emitted identical hashes:

- summary hash: `d34781f0420f9973656c4979eff458253a0d0b1a7f262b31274cd2f3a30b1760`
- row-diff hash: `0f4d348f38d5ca6966d65a6b35c5700ea3e444cf2b0210447f9bc96a83a692df`

Both summaries also reported canonical execution mode:

- `fast_window = true`
- `env_precompute_features = "1"`
- `precompute_enabled = true`
- `precomputed_ready = true`
- `mode_explicit = "1"`

## Tracked script and artifacts

Tracked script:

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504.py`

Generated local artifacts:

- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_topline_subject_2025_10_20260504/continuation_release_hysteresis_topline_subject_2025_10_row_diffs.json`

These `results/backtests/**` outputs are local evidence artifacts for this slice and are **not** part of the tracked-file scope unless scope is explicitly widened later.

## Exact continuation-release cluster

The baseline run reproduced this exact thirteen-row `continuation_release` cluster:

- `2025-10-17T00:00:00+00:00`
- `2025-10-17T03:00:00+00:00`
- `2025-10-17T06:00:00+00:00`
- `2025-10-17T09:00:00+00:00`
- `2025-10-17T12:00:00+00:00`
- `2025-10-17T15:00:00+00:00`
- `2025-10-17T18:00:00+00:00`
- `2025-10-17T21:00:00+00:00`
- `2025-10-18T00:00:00+00:00`
- `2025-10-18T03:00:00+00:00`
- `2025-10-18T15:00:00+00:00`
- `2025-10-18T18:00:00+00:00`
- `2025-10-18T21:00:00+00:00`

The `release_zero` run preserves the first ten of those continuation-release timestamps and exits continuation-release mode earlier:

- `2025-10-17T00:00:00+00:00`
- `2025-10-17T03:00:00+00:00`
- `2025-10-17T06:00:00+00:00`
- `2025-10-17T09:00:00+00:00`
- `2025-10-17T12:00:00+00:00`
- `2025-10-17T15:00:00+00:00`
- `2025-10-17T18:00:00+00:00`
- `2025-10-17T21:00:00+00:00`
- `2025-10-18T00:00:00+00:00`
- `2025-10-18T03:00:00+00:00`

## Outcome summary

### Baseline

- final capital: `9993.380796175`
- total return: `-0.06619203824999204%`
- trades: `5`
- profit factor: `1.3414558487208776`
- max drawdown: `0.237447527852395%`
- net position PnL: `-6.619203824999815`

### Release-zero

- final capital: `10010.5156363`
- total return: `0.10515636300000551%`
- trades: `5`
- profit factor: `2.6829116974417553`
- max drawdown: `0.28511722180659416%`
- net position PnL: `10.515636300000253`

### Exact deltas

- final capital delta: `+17.134840124999755`
- total return delta: `+0.17134840124999756 percentage points`
- trade count delta: `0`

## Row-level summary

Observed diff counts on the exact subject:

- all row diffs: `121`
- action diffs: `0`
- size diffs: `2`
- selected-policy diffs: `6`
- switch-reason diffs: `9`
- behavioral row diffs: `19`
- parameter-only row diffs: `102`
- baseline continuation-release rows: `13`
- release-zero continuation-release rows: `10`
- continuation-release rows with behavioral difference: `13`

The key bounded correction remains explicit:

> this subject also shows **top-line divergence without action-level divergence**.

Trade count stays unchanged and `action_diff_count` remains `0`.

## Representative local effect

The first decisive local split begins on `2025-10-17T21:00:00+00:00`.

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

The same bounded policy/reason split continues at `2025-10-18T00:00:00+00:00` and `2025-10-18T03:00:00+00:00`.

Earlier rows from `2025-10-17T00:00:00+00:00` through `2025-10-17T18:00:00+00:00` are still inside the continuation-release cluster, but the difference there remains control-level (`effective_hysteresis` `1 -> 0`) without a policy or size change.

After `2025-10-18T03:00:00+00:00`, the `release_zero` branch has already normalized out of continuation-release mode, while the baseline branch still records continuation-release on `2025-10-18T15:00:00+00:00`, `2025-10-18T18:00:00+00:00`, and `2025-10-18T21:00:00+00:00`.

## Interpretation

This subject strengthens the bounded exact-subject picture already opened by August 2021:

- the seam is genuinely exercised
- the row-level control/policy/size changes are visible
- the top-line result changes materially
- the action count still does **not** change

But the evidence is still bounded and observational:

- the subject remains one exact October 2025 window only
- trade count does not change
- action-level divergence remains `0`
- no general runtime rule is established from this note alone

So the honest read is:

> on the exact `2025-10` subject, lowering `continuation_release_hysteresis` to `0` again improves top-line outcome through policy/size-path changes while leaving action count unchanged.

This is observational evidence for this exact subject only. It does **not** widen runtime, promotion, or readiness claims.

## Do-not-overclaim guardrails

This note does **not** justify:

- runtime widening
- default-path changes
- promotion or readiness claims
- a general statement that `continuation_release_hysteresis = 0` is broadly better
- a claim that the seam changes actions/trade counts on this carrier

## Next admissible move

If this chain continues, the next smallest honest step is one more bounded RI-only exact-subject follow-up on the first opposite-sign top-line-divergent subject.

The cleanest next option is now:

1. `2018-03` as the first bounded opposite-sign exact subject

That would let the next slice test whether the current positive October/August pair is a sign-consistent subgroup rather than a universal rule on this carrier.
