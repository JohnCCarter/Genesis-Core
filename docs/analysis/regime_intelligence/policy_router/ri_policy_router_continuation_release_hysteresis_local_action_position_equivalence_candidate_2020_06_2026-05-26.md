# RI policy router continuation_release_hysteresis local action-position equivalence candidate 2020-06 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2020-06` local envelope slice.

Question:

> inside the exact local envelopes already recovered for the `2020-06` candidate and the fixed `2023-05` control, do the retained `baseline` vs `release_zero` differences ever reach execution surface, or are they absorbed while both runs still face the same pre-execution position context?

This slice is observational only.

It does **not** widen beyond the exact local envelopes, reopen the retired `2021-04` candidate, or claim that `2020-06` now proves local economic harm.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_2026-05-26.json`
- local envelope artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_20260526.py`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

## What changed and what did not

- **Changed:** one thin wrapper reused the landed local action-position equivalence machinery, but substituted the exact `2020-06` local envelope specs instead of the older `2021-04` candidate.
- **Did not change:** no runtime/config surface changed, no envelope bounds were widened by hand, and the earlier local-envelope conclusion was not rewritten as if it had already become execution or economic divergence.

## Observed

### 1. Both subjects reproduced the exact local envelopes without drift

For both `2020-06` and `2023-05`:

- baseline continuation-release timestamps matched the landed local packet
- `release_zero` continuation-release timestamps matched the landed local packet
- monthly reruns stayed flat:
  - `rerun_total_return_diff = 0.0`
  - `rerun_final_capital_diff = 0.0`

So the slice stayed bounded to the already-landed local envelopes rather than introducing a fresh comparison surface.

### 2. `2020-06` still does **not** reach execution-surface divergence

Candidate envelope:

- `2020-06-17T18:00:00+00:00 -> 2020-06-18T18:00:00+00:00`
- `9` rows, `24h`

Candidate row summary:

- `execution_divergence_rows = 0`
- `execution_effect_diff_rows = 0`
- `position_before_diff_rows = 0`
- `action_diff_rows = 0`
- `size_diff_rows = 2`
- `selected_policy_diff_rows = 6`
- `switch_reason_diff_rows = 6`
- `all_diff_rows_execution_equivalent = true`

Candidate classifications:

- `router_internal_only = 4`
- `size_diff_absorbed_by_locked_position = 2`
- `execution_equivalent_other = 3`
- `action_diff_absorbed_by_locked_position = 0`

So the stronger `2020-06` candidate still preserves only pre-execution asymmetry on this surface.

No row changes the execution-effect class.

### 3. `2023-05` remains execution-equivalent as well

Control envelope:

- `2023-05-17T06:00:00+00:00 -> 2023-05-18T00:00:00+00:00`
- `7` rows, `18h`

Control row summary:

- `execution_divergence_rows = 0`
- `execution_effect_diff_rows = 0`
- `position_before_diff_rows = 0`
- `action_diff_rows = 0`
- `size_diff_rows = 1`
- `selected_policy_diff_rows = 7`
- `switch_reason_diff_rows = 7`
- `all_diff_rows_execution_equivalent = true`

Control classifications:

- `router_internal_only = 6`
- `size_diff_absorbed_by_locked_position = 1`
- `action_diff_absorbed_by_locked_position = 0`

So the control is also fully absorbed before execution surface.

### 4. The candidate still looks more negative-like than the control, but only before execution

Compared with `2023-05`, the `2020-06` candidate keeps more non-trivial pre-execution structure:

- candidate locked-position size-absorption rows: `2`
- control locked-position size-absorption rows: `1`
- candidate `execution_equivalent_other` rows: `3`
- control `execution_equivalent_other` rows: `0`

At the same time, both subjects share the same hard boundary:

- no action divergence
- no pre-position-context divergence
- no execution-effect divergence

So the retained `2020-06` asymmetry still stops before action or trade-path separation.

### 5. The candidate decay path is partly familiar and partly not identical to the control

Inside the first part of the `2020-06` envelope:

- the candidate shows two `size_diff_absorbed_by_locked_position` rows while a long position is already open
- several subsequent rows reduce to `router_internal_only`

Later in the envelope, `2020-06` still shows three `execution_equivalent_other` rows where `switch_control_mode` differs but action, size effect, and pre-position context remain unchanged.

So the candidate does not merely copy the control row-for-row.

It keeps extra state variation, but that variation still fails to reach execution surface.

## Inferred

### 1. `2020-06` extends the falsification from local economics into local execution effects

The smallest honest inference is:

> `2020-06` remains more negative-like than `2023-05` on bounded local packet structure, but its retained asymmetry is still fully absorbed before execution surface inside the exact local envelope.

So the candidate swap did not rescue the local execution path after the local economic path already stayed flat.

### 2. The surviving `2020-06` signal still lives in non-economic state surfaces

Because there are:

- zero action divergence rows
- zero position-context divergence rows
- zero execution-effect divergence rows

the surviving separator is still not action or trade behavior.

What remains is mainly:

- policy/switch-reason drift
- locked-position size asymmetry
- later control-mode-only state differences that do not change execution effect

### 3. The next honest slice is narrower again, not broader

This slice rules out another tempting but weak story, namely that `2020-06` might still be hiding a local execution difference even after local equity stayed flat.

What remains admissible is narrower:

> candidate-only replay or state-decay inspection around the two `2020-06` locked-position size-absorption rows and the later control-mode-only residual rows.

## Unverified

The following remain open:

1. whether the two `2020-06` locked-position size-absorption rows decay into the same dormant breadcrumb structure previously seen in `2021-04`
2. whether the later `execution_equivalent_other` rows in `2020-06` are purely `switch_control_mode` residuals or also preserve another harmless state delta
3. whether a narrower candidate-only replay around the `2020-06` local envelope reveals a different state-decay sequence than the retired `2021-04` path

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_20260526.py` -> emitted artifact with packet status `candidate_and_control_asymmetry_absorbed_before_execution_surface`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_20260526.py` -> pass

## Bottom line

This slice keeps the widening chain alive only on non-execution state surfaces.

What is now supported is:

> `2020-06` retains more local negative-like structure than the fixed `2023-05` control, but that structure is still absorbed before execution surface inside the exact local envelope: zero action divergence, zero position-context divergence, and zero execution-effect divergence for both subjects.

So the next honest continuation is narrower again:

> candidate-only replay or state-decay around the `2020-06` locked-position rows and later control-mode residuals, not another attempt to sell local execution harm.
