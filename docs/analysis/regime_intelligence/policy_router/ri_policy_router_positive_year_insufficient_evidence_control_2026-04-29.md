# RI policy router positive-year insufficient-evidence control

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only fixed-window control / positive-year selectivity check`

This slice is a read-only control follow-up to the completed March 2021 negative-year `insufficient_evidence` local-window note.
It freezes one exact positive-year `insufficient_evidence` cluster, keeps only true `stable_continuation_state` displacement rows in the comparison cohort, and leaves the remaining local rows as context only.
It does not reopen runtime work, default semantics, promotion surfaces, or the parked aged-weak chain.

All returns and excursion values in this slice are timestamp-close observational proxies on existing evidence rows only.
They are descriptive only and do not establish realized trade PnL, fill-aware row truth, causal superiority, runtime authority, or promotion readiness.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads one fixed annual action-diff file plus curated candles only and emits one bounded JSON artifact plus this note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the March 2021 negative-year slice is already frozen, so the next honest move is one positive-year local control using the same framing rather than any runtime speculation.
- **Objective:** materialize one exact positive-year `insufficient_evidence` local window with the same target-versus-displacement framing used in the March 2021 negative-year slice so local selectivity can be tested.
- **Candidate:** `2025-03-14 positive-year insufficient-evidence control window`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_packet_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_positive_year_insufficient_evidence_control_20260429.py --base-sha 1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Fixed subject that actually materialized

### Exact positive-year `insufficient_evidence` target cluster

The wrapper recovered the exact fixed `<=24h` adjacency group specified in the packet:

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Shared target context:

- year = `2025`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `65`

### Exact displacement comparison rows

Only true nearby `stable_continuation_state` displacement rows were kept in the comparison cohort:

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Shared comparison context:

- absent action = `NONE`
- enabled action = `LONG`
- switch reason = `stable_continuation_state`
- selected policy = `RI_continuation_policy`
- bars since regime change = `63..64`

### Context-only local rows

The local envelope `2025-03-13T15:00:00+00:00 -> 2025-03-17T03:00:00+00:00` also contains three context-only rows:

- two `stable_continuation_state` rows with action pair `LONG -> NONE`
- one `AGED_WEAK_CONTINUATION_GUARD` suppression at `2025-03-16T12:00:00+00:00`

The row lock is explicit in the artifact:

- target timestamps: `5`
- comparison timestamps: `2`
- context-only stable exclusions: `2`

## Main result

### 1. The positive-year `insufficient_evidence` target rows are locally weak on the first proxy surface

All five target rows are negative on `fwd_16`:

- row count: `5`
- `fwd_16` mean: `-1.017927%`
- `fwd_16` median: `-0.732922%`
- `fwd_16 > 0` share: `0%`
- `mfe_16` mean: `+0.846783%`
- `mae_16` mean: `-2.709338%`

So unlike the March 2021 negative-year slice, this positive-year target cluster does read like a local group of weak baseline longs.
On this first descriptive proxy surface, `RI_no_trade_policy` looks locally justified rather than over-binding.

### 2. The nearby displacement rows are positive and materially stronger

The two nearby `stable_continuation_state` displacement rows are both positive on the same proxy surface:

- row count: `2`
- `fwd_16` mean: `+3.826925%`
- `fwd_16` median: `+3.826925%`
- `fwd_16 > 0` share: `100%`
- `mfe_16` mean: `+5.178273%`
- `mae_16` mean: `-0.295090%`

Descriptive gap versus the target cohort:

- `fwd_16` mean gap (`insufficient_evidence` minus displacement): `-4.844852%`
- `mfe_16` mean gap: `-4.331490%`
- `mae_16` mean gap: `-2.414248%`

So this local control is a strong case where the target `insufficient_evidence` rows look materially worse than the nearby displacement rows.

### 3. The context-only rows do not overturn the control reading

The two context-only `stable_continuation_state` `LONG -> NONE` rows remain positive (`+3.994390%` and `+2.004758%` on `fwd_16`), while the one context-only `AGED_WEAK_CONTINUATION_GUARD` row is negative (`-1.790137%`).

That means the local envelope is not perfectly one-directional, but it still reads much more cleanly than March 2021:

- displacement rows are positive,
- target `insufficient_evidence` rows are uniformly negative,
- and the context does not erase that separation.

## Direct comparison against March 2021

The March 2021 negative-year slice and this March 2025 positive-year control now form a bounded local contrast.

### March 2021 negative-year window

- target `insufficient_evidence` rows: locally favorable (`fwd_16` mean `+3.692905%`)
- nearby true displacement rows: positive and somewhat stronger (`+5.141805%`)
- broader envelope: mixed positive suppression/displacement cluster

### March 2025 positive-year control

- target `insufficient_evidence` rows: locally weak (`fwd_16` mean `-1.017927%`)
- nearby true displacement rows: clearly positive (`+3.826925%`)
- broader envelope: still mixed, but the target-versus-displacement separation is directionally clean

So the strongest bounded cross-slice reading now is:

> `insufficient_evidence` is not a uniformly bad suppressor. In at least one negative-year local window it suppresses favorable baseline longs, while in this positive-year control it suppresses a locally weak cluster where nearby continuation displacement looks better.

## Interpretation

This is the first local evidence in the chain that supports a real **selectivity problem** rather than a one-sided condemn-or-keep verdict.

What this control now supports:

- the March 2021 negative-year slice was not enough to say whether `insufficient_evidence` was globally harmful,
- the March 2025 control now shows a positive-year local case where `insufficient_evidence` suppression looks locally justified,
- therefore the robust-policy problem is genuinely selective: a future proposal would need to preserve 2025-like justified suppression while avoiding 2021-like over-blocking.

What this control does **not** support:

- a rule that `insufficient_evidence` should simply be removed or weakened everywhere,
- a rule that `insufficient_evidence` is always beneficial,
- a runtime tuning proposal from two local windows alone.

## Consequence for the robust-policy question

This slice sharpens the question in the right direction.
The target is no longer “is `insufficient_evidence` bad?”
The target becomes:

> can a future bounded rule distinguish 2021-like favorable blocked clusters from 2025-like weak blocked clusters without damaging the positive-year control case?

That is a better formulation of the user’s robust-policy goal than the earlier annual aggregate framing.

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- exact one-to-one row pairing between blocked and displaced rows
- runtime-authoritative row truth
- that one scalar threshold can solve the selectivity problem
- that runtime/default/policy tuning is justified now
- that the parked aged-weak chain should be reopened

## Next admissible step

If this line is reopened, the cheapest honest next move should stay read-only and selective:

1. compare feature-level or gate-level differences between the March 2021 negative-year target rows and the March 2025 positive-year target rows, or
2. isolate one additional positive-year control or negative-year failure window only if needed to test whether the 2021/2025 contrast is stable rather than accidental.

That keeps the work inside research-evidence while moving one step closer to a genuinely robust policy criterion.

## What is not justified from this slice

- new router tuning
- default-policy changes
- global weakening of `insufficient_evidence`
- global strengthening of `insufficient_evidence`
- promotion or readiness claims from this local control window
