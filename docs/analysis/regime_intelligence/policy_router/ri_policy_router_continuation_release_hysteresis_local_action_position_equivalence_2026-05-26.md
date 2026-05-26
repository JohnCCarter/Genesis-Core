# RI policy router continuation_release_hysteresis local action-position equivalence — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed local envelope invariance slice.

Question:

> inside the exact `2021-04` candidate envelope and `2023-05` control envelope, do the retained baseline-vs-`release_zero` differences actually reach execution surface, or are they absorbed while both runs face the same pre-execution position context?

This slice is observational only.

It does **not** reopen the frozen triad, claim hidden local harm, change runtime/config surfaces, or reinterpret the earlier local-packet result as if it had already become an execution-path divergence.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json`
- local envelope artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_20260526.py`

## What changed and what did not

- **Changed:** one new read-only helper reran both exact local envelopes and compared `action`, `size`, router labels, and the pre-execution open-position snapshot on every envelope row.
- **Did not change:** no runtime/config files changed, no new widening target was introduced, and the earlier economic-invariance result was not rewritten as if it had already shown a deeper execution-path split.

## Observed

### 1. Neither subject reaches execution-surface divergence anywhere inside the exact local envelope

For both `2021-04` and `2023-05`:

- `action_diff_rows = 0`
- `position_before_diff_rows = 0`
- `execution_effect_diff_rows = 0`
- `execution_divergence_rows = 0`

So the retained asymmetry from the local packet remains strictly upstream of execution.

This slice found no bar where baseline and `release_zero` imply different execution effects once the current position context is taken into account.

### 2. `2021-04` keeps more dormant size asymmetry than the control, but still inside the same locked position

Candidate summary:

- envelope rows: `16`
- diff rows: `16`
- selected-policy diff rows: `6`
- switch-reason diff rows: `6`
- size diff rows: `2`
- size diff absorbed by locked position: `2`
- router-internal-only rows: `4`
- remaining execution-equivalent rows: `10`

The two size-diff rows are:

- `2021-04-17T03:00:00+00:00`
- `2021-04-17T12:00:00+00:00`

At both timestamps:

- both runs already hold the **same** open `LONG`
- baseline proposed size is smaller (`0.006`)
- `release_zero` proposed size is larger (`0.012`)
- selected policy differs (`RI_defensive_transition_policy` vs `RI_continuation_policy`)
- switch reason differs (`switch_blocked_by_hysteresis` vs `continuation_state_supported`)

But because the position is already open in both runs, the execution effect stays the same:

> hold the existing `LONG`, do not create a new trade event.

So the candidate's extra negative-like structure is still dormant on the execution surface.

### 3. `2023-05` shows the same absorption pattern, but in a smaller form

Control summary:

- envelope rows: `7`
- diff rows: `7`
- selected-policy diff rows: `7`
- switch-reason diff rows: `7`
- size diff rows: `1`
- size diff absorbed by locked position: `1`
- router-internal-only rows: `6`

The only size-diff row is:

- `2023-05-17T06:00:00+00:00`

At that timestamp:

- both runs already hold the same open `LONG`
- baseline proposed size is `0.0039`
- `release_zero` proposed size is `0.0078`
- selected policy and switch reason differ in the same defensive-vs-continuation direction

But again the actual execution effect is unchanged because the position is already open.

### 4. The candidate/control difference is now narrower than “policy diff” and narrower than “economic invariance”

The new slice sharpens the chain:

1. local packet: `2021-04` looked more negative-like than `2023-05` on the frozen triad's local rule surface
2. local envelope economics: neither subject opened a local total-equity gap
3. local action-position equivalence: neither subject opened an execution-surface gap either

So the current surviving difference is not:

- action divergence
- position-context divergence
- trade divergence
- equity divergence

It is smaller:

> candidate-local negative-likeness persists mainly as extra locked-position size/policy asymmetry before execution ever changes.

### 5. `2021-04` still has additional internal drift that the control does not need

Beyond the `2` explicit locked-size rows, the candidate also has `10` rows labeled `execution_equivalent_other`.

These are rows where the underlying per-bar payload still differs somewhere, but not on the surfaced fields that matter for:

- `action`
- effective execution class
- pre-execution position state

So even inside the candidate, part of the retained asymmetry is now best described as internal router/debug drift that still does not reach execution.

## Inferred

### 1. The candidate's negative-like edge is currently a dormant pre-execution signal, not an execution-path signal

The smallest honest inference is:

> `2021-04` still differs from the control locally, but the surviving difference is confined to pre-execution policy/size routing while the same position context keeps the execution effect unchanged.

That is weaker than a local harm claim.

But it is also more precise.

### 2. The same-position lock is the main absorber on the rows that still look most negative-like

The informative rows in the candidate are not action flips.

They are the two rows where:

- the candidate wants different size/policy treatment under `release_zero`
- yet both runs are already trapped in the same open `LONG`

So the best current explanation is:

> the candidate's retained asymmetry is being absorbed by locked position context before it can change execution.

### 3. The next admissible slice should be candidate-only and narrower again

Another broad pairwise envelope pass would likely just restate the same invariance.

The sharper next question is:

> on the two `2021-04` locked-size rows, what dormant state or replay surface still differs once execution and economic outputs are already known to match?

## Unverified

The following remain open:

1. whether the two candidate-only locked-size rows carry any meaningful dormant state beyond policy label and size multiplier disagreement
2. whether the `execution_equivalent_other` rows in `2021-04` are purely router-debug/internal-state drift or still reflect a reusable non-economic separator
3. whether another negative-like widening candidate produces execution-surface divergence where `2021-04` does not

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_20260526.py` -> emitted artifact with status `candidate_and_control_asymmetry_absorbed_before_execution_surface`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_20260526.py` -> pass

## Bottom line

This slice narrows the claim one more notch.

What is now supported is:

> `2021-04` differs from `2023-05` locally, but that difference still does not reach execution surface. The candidate's surviving edge currently appears as extra locked-position size/policy asymmetry, not as action, position, trade, or equity divergence.

So the next honest continuation is now very small:

> a candidate-only replay around the two `2021-04` locked-size rows, not another broad envelope comparison.
