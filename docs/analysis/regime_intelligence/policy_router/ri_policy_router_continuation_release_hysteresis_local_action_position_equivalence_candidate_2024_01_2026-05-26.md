# RI policy router continuation_release_hysteresis local action-position equivalence candidate 2024-01 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2024-01` exact local envelope slice.

Question:

> inside the exact `2024-01` continuation-release envelope, do the retained baseline-vs-`release_zero` differences actually reach execution surface, or are they still absorbed while both runs face the same pre-execution position context?

This slice is observational only.

It does **not** change runtime/config behavior, reinterpret the flat exact-envelope economics as hidden harm, or widen beyond the packet-imported exact envelope timestamps.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json`
- local envelope artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_20260526.py`

## Observed

### 1. `2024-01` still does not reach execution divergence on the exact local envelope

Packet summary:

- candidate execution divergence rows: `0`
- control execution divergence rows: `0`
- packet status: `candidate_and_control_asymmetry_absorbed_before_execution_surface`

So the widened 2024 candidate remains absorbed before execution surface, just like the fixed `2023-05` control.

### 2. The exact `2024-01` envelope stayed fixed at the same discrete `11` rows

Candidate envelope:

- start: `2024-01-17T15:00:00+00:00`
- end: `2024-01-19T06:00:00+00:00`
- row count: `11`
- span: `39h`

The wrapper reused the already-validated exact envelope timestamps from the landed `2024-01` envelope artifact rather than reintroducing a contiguous-range assumption.

### 3. Every `2024-01` diff row remained execution-equivalent

Candidate row summary:

- envelope row count: `11`
- diff rows: `11`
- execution-effect diff rows: `0`
- position-before diff rows: `0`
- all diff rows execution equivalent: `true`

Candidate classification counts:

- `execution_equivalent_other = 6`
- `router_internal_only = 4`
- `size_diff_absorbed_by_locked_position = 1`
- `execution_divergence = 0`

So even where baseline and `release_zero` still differ, they keep the same position context and the same effective execution class on every exact envelope row.

### 4. The single `2024-01` locked-size row is still pre-execution only

At `2024-01-18T09:00:00+00:00`:

- baseline action: `LONG`, size `0.0039`
- `release_zero` action: `LONG`, size `0.0078`
- both runs enter the row with the same existing long position:
  - side: `LONG`
  - current size: `0.00273`
  - entry time: `2024-01-17T06:00:00+00:00`
- both rows classify as `hold_existing`

So this is the same pattern seen in earlier candidates: size asymmetry is real on the router surface, but it is absorbed by an already locked position before execution can diverge.

### 5. The middle `2024-01` rows are router-internal only

Four candidate rows classify as `router_internal_only`:

- `2024-01-18T12:00:00+00:00`
- `2024-01-18T15:00:00+00:00`
- `2024-01-18T18:00:00+00:00`
- `2024-01-18T21:00:00+00:00`

Observed pattern on those rows:

- action stays `NONE`
- position context stays equivalent
- execution effect stays equivalent
- baseline stays on defensive/hysteresis labels while `release_zero` sits on continuation-supported labels

So the candidate retains real router-state asymmetry here, but still not execution-surface asymmetry.

### 6. The late `2024-01` rows already look like breadcrumb-only survivors

Three candidate rows classify as `execution_equivalent_other` at the end of the envelope:

- `2024-01-19T00:00:00+00:00`
- `2024-01-19T03:00:00+00:00`
- `2024-01-19T06:00:00+00:00`

On those rows:

- selected policy is already `RI_continuation_policy` on both paths
- switch reason is already `stable_continuation_state` on both paths
- action/effect remain aligned (`open_position` once, then `hold_existing` twice)
- the visible surviving difference is `switch_control_mode`:
  - baseline: `continuation_release`
  - `release_zero`: `default`

So the widened 2024 candidate is already showing the same kind of post-absorption breadcrumb tail that previously appeared in `2020-06`.

### 7. The fixed `2023-05` control remains absorbed too, but with a different mix

Control row summary:

- `router_internal_only = 6`
- `size_diff_absorbed_by_locked_position = 1`
- `execution_divergence = 0`

So both subjects stay absorbed before execution surface, but `2024-01` allocates more of its exact-envelope residual rows to the broader `execution_equivalent_other` bucket than the fixed control does.

## Inferred

### 1. `2024-01` now matches the same bounded local lifecycle as the earlier negative-like candidates

The bounded chain is now:

1. stronger packet asymmetry than the fixed control
2. exact local economic flatline
3. no execution divergence on the exact envelope

That keeps `2024-01` consistent with the earlier `2021-04` and `2020-06` local falsification path.

### 2. The best remaining local signal is now a residual breadcrumb inventory, not execution harm

Because the candidate is still absorbed before execution surface, the next honest question is no longer about local trade divergence.

It is narrower:

> after the last locked-size row, which exact `2024-01` differences remain, and do they collapse to a descriptive/debug-like breadcrumb only?

### 3. Keeping “2024 harm” in view remains legitimate, but not on the exact local path

This slice strengthens the same caution as the exact envelope slice:

> `2024-01` keeps the 2024 concern alive on frozen packet structure, but the exact local execution path still does not support a bounded local harm claim.

## Unverified

The following remain open:

1. whether the late `2024-01` residual collapses fully to `switch_control_mode`-style breadcrumb rows after the last locked-size row
2. whether the early `execution_equivalent_other` rows in `2024-01` reduce to another non-execution router-state difference when inventoried directly
3. whether any wider non-local surface can still separate 2024 candidates after packet, exact-envelope economics, and exact-envelope execution all remain locally absorbed

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_20260526.py` -> emitted artifact with packet status `candidate_and_control_asymmetry_absorbed_before_execution_surface`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_20260526.py` -> pass

## Bottom line

`2024-01` is now falsified on the exact local execution path too.

What is supported is:

> the widened 2024 candidate preserves more negative-like packet structure than the fixed `2023-05` control, but once the exact envelope is replayed it still produces zero local equity gap and zero execution divergence; the remaining differences live on router-internal, locked-size, or breadcrumb-like state surfaces only.

So the next honest continuation is:

> a candidate-only residual inventory after the last locked-size row in `2024-01`.
