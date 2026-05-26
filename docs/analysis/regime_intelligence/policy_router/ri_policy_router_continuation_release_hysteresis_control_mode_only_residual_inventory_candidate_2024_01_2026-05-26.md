# RI policy router continuation_release_hysteresis control-mode-only residual inventory candidate 2024-01 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2024-01` local action-position equivalence slice.

Question:

> after the last `2024-01` locked-size row disappears, are there any rows left where `switch_control_mode` is the only surviving diff field, and if so are they candidate-specific or shared with the fixed `2023-05` control?

This slice is artifact-only and observational.

It does **not** rerun runtime code, reinterpret the already-flat local economic/execution path as hidden harm, or widen beyond the exact envelope rows already landed in the action-equivalence artifact.

## Inputs

- action-position equivalence artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_20260526.py`

## Observed

### 1. `2024-01` retains exactly three control-mode-only residual rows

Packet summary:

- candidate control-mode-only row count: `3`
- control control-mode-only row count: `0`
- candidate first timestamp: `2024-01-19T00:00:00+00:00`
- candidate last timestamp: `2024-01-19T06:00:00+00:00`
- candidate all rows after last locked-size row: `true`

Status:

- `candidate_only_control_mode_residual_rows_persist_after_locked_size_gap_candidate_2024_01`

So the widened 2024 candidate now has a clean late residual tail that the fixed control does not share.

### 2. All three candidate residual rows occur after the last locked-size row

The last `2024-01` locked-size row was the already-documented absorbed size asymmetry at `2024-01-18T09:00:00+00:00`.

Every control-mode-only row appears later:

- `2024-01-19T00:00:00+00:00`
- `2024-01-19T03:00:00+00:00`
- `2024-01-19T06:00:00+00:00`

So this residual inventory is downstream of the last candidate-specific size gap.

### 3. The surviving diff is exactly `switch_control_mode`

On all three candidate rows, the following match between baseline and `release_zero`:

- selected policy: `RI_continuation_policy`
- switch reason: `stable_continuation_state`
- size: identical
- action: identical
- execution effect: identical
- position context: identical

The sole surviving diff is:

- baseline `switch_control_mode = continuation_release`
- `release_zero` `switch_control_mode = default`

So the late candidate-specific tail is already reduced to a pure control-mode label difference.

### 4. The three residual rows are all execution-equivalent

Classification counts for the candidate residual rows:

- `execution_equivalent_other = 3`

Row-by-row:

#### `2024-01-19T00:00:00+00:00`

- action: `LONG` on both paths
- execution effect: `open_position` on both paths
- no prior position on either path
- only surviving diff: `switch_control_mode`

#### `2024-01-19T03:00:00+00:00`

- action: `NONE` on both paths
- execution effect: `hold_existing` on both paths
- both paths already hold the same position
- only surviving diff: `switch_control_mode`

#### `2024-01-19T06:00:00+00:00`

- action: `NONE` on both paths
- execution effect: `hold_existing` on both paths
- both paths still hold the same position
- only surviving diff: `switch_control_mode`

So even the candidate-only late tail remains fully execution-neutral.

### 5. The fixed `2023-05` control has no equivalent late breadcrumb tail

Control inventory:

- control-mode-only row count: `0`
- classification counts: `{}`

So this exact late breadcrumb pattern is candidate-specific inside the bounded `2024-01` local envelope.

## Inferred

### 1. `2024-01` now reaches the same late breadcrumb stage already seen in `2020-06`

The bounded local path is now:

1. stronger packet asymmetry than the fixed control
2. exact local economic flatline
3. no execution divergence on the exact envelope
4. three late candidate-only rows where only `switch_control_mode` remains different

That is very close to the same local end-state previously observed for `2020-06`.

### 2. The remaining `2024-01` candidate-specific signal is descriptive-sized, not execution-sized

The strongest narrow inference here is:

> by the time the last locked-size asymmetry disappears, the `2024-01` candidate-specific tail has already collapsed to a pure `switch_control_mode` label difference while action, policy, switch reason, size, position context, and execution effect all match.

That makes another local execution-harm interpretation weaker, not stronger.

### 3. The next honest step is semantics/state-decay closure, not more local envelope replay

Since the residual is now isolated to a control-mode label tail, the next admissible question is:

> does this late `2024-01` breadcrumb carry any independent runtime meaning beyond the already known descriptive/debug-like role of `switch_control_mode`, or does it close locally the same way as `2020-06`?

## Unverified

The following remain open:

1. whether the already-established global `switch_control_mode` semantics are sufficient to close `2024-01` without any new runtime inspection
2. whether the early `2024-01` `execution_equivalent_other` rows (before the late tail) reduce to another non-execution state-only difference if inventoried directly
3. whether any wider non-local surface still separates 2024 candidates once the exact local path has decayed to a candidate-only breadcrumb tail

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_20260526.py` -> emitted artifact with status `candidate_only_control_mode_residual_rows_persist_after_locked_size_gap_candidate_2024_01`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_20260526.py` -> pass

## Bottom line

`2024-01` now has the same kind of candidate-only late breadcrumb tail that previously showed up in `2020-06`.

What is supported is:

> after the last locked-size row disappears, the widened 2024 candidate retains exactly three late rows where only `switch_control_mode` differs; the fixed `2023-05` control retains none, and all three candidate rows remain fully execution-equivalent.

So the next honest continuation is no longer another local execution test.

It is semantics/state-decay closure for the late `2024-01` breadcrumb.
