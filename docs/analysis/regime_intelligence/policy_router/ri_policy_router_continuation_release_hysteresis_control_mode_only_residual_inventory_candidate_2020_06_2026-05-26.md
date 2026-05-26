# RI policy router continuation_release_hysteresis control-mode-only residual inventory candidate 2020-06 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2020-06` local action-position equivalence slice.

Question:

> after the last `2020-06` locked-size row has already disappeared inside the exact local envelope, do any later rows reduce to `switch_control_mode` as the sole surviving diff field, and if so are those rows unique to the candidate or also present in the fixed `2023-05` control?

This slice is artifact-only and observational.

It does **not** reopen local economics, claim execution divergence, or widen beyond the exact local envelopes already landed.

## Inputs

- action-position artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2020_06_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_20260526.py`

## What changed and what did not

- **Changed:** one artifact-only inventory scanned the landed `2020-06` action-position equivalence rows for cases where `switch_control_mode` is the sole remaining diff field after the candidate's last locked-size row.
- **Did not change:** no runtime/config surface changed, no new backtests were introduced, and the earlier execution-equivalence result was not reinterpreted as hidden trade-path harm.

## Observed

### 1. `2020-06` retains exactly three control-mode-only residual rows

Candidate summary:

- `candidate_control_mode_only_row_count = 3`
- first timestamp: `2020-06-18T12:00:00+00:00`
- last timestamp: `2020-06-18T18:00:00+00:00`
- `candidate_all_rows_after_last_locked_size_row = true`

All three candidate rows are classified as:

- `execution_equivalent_other`

So the late residual is real on the candidate, but it remains strictly non-execution.

### 2. The fixed `2023-05` control retains no such rows

Control summary:

- `control_control_mode_only_row_count = 0`

So the `switch_control_mode`-only residual is not shared by the control inside its exact local envelope.

### 3. On the candidate rows, everything except `switch_control_mode` already matches

For all three `2020-06` residual rows:

- action matches
- execution effect matches: `hold_existing`
- selected policy matches: `RI_continuation_policy`
- switch reason matches: `stable_continuation_state`
- size matches
- position context matches (`has_position = true` on both sides)

The only remaining difference is:

- baseline `switch_control_mode = continuation_release`
- `release_zero` `switch_control_mode = default`

So the late residual is a pure control-mode breadcrumb.

### 4. The residual appears only after the candidate's locked-size gap is gone

The inventory explicitly anchored itself after the candidate's last locked-size row.

All three candidate residual rows occur later than that boundary.

So the chain inside the `2020-06` envelope now looks like:

1. locked-position size asymmetry
2. non-execution router/policy drift
3. control-mode-only residual rows

without ever crossing into action or execution divergence.

## Inferred

### 1. `2020-06` now mirrors the same late breadcrumb shape that made `2021-04` unconvincing as local harm

The smallest honest inference is:

> the stronger `2020-06` candidate still decays to a candidate-only `switch_control_mode` breadcrumb after the locked-size gap disappears, while the fixed `2023-05` control does not show that exact late residual.

That keeps `2020-06` more negative-like than the control on state surfaces, but still not on execution surfaces.

### 2. The surviving separator is now even narrower than before

After the action-position slice, it was still possible that the late `execution_equivalent_other` rows hid some additional harmless state delta.

This inventory collapses that ambiguity.

On the late residual rows, only `switch_control_mode` survives.

So the candidate-specific separator has narrowed again to a pure control-mode breadcrumb.

### 3. The next honest continuation is semantics or candidate-only decay, not execution claims

Because the late residual is now isolated to `switch_control_mode` alone, the next admissible question is not whether `2020-06` still hides execution harm.

It is narrower:

> is this late `switch_control_mode` residual semantically meaningful enough to inspect directly, or has `2020-06` now reached the same effective retirement boundary that `2021-04` reached by a slightly different path?

## Unverified

The following remain open:

1. whether the `2020-06` late `switch_control_mode` residual is written-only/debug-like on exactly the same semantics path already inspected for `2021-04`
2. whether a tiny candidate-only decay helper from the last locked-size row to the first pure control-mode row adds anything beyond the inventory now already shown
3. whether the next honest move is direct code-semantics confirmation or a wider month swap to the next negative-like candidate

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_20260526.py` -> emitted artifact with packet status `candidate_only_control_mode_residual_rows_persist_after_locked_size_gap_candidate_2020_06`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_20260526.py` -> pass

## Bottom line

This slice narrows the surviving `2020-06` separator again.

What is now supported is:

> after the last locked-size row disappears, `2020-06` retains exactly three late candidate-only rows where `switch_control_mode` is the sole surviving diff field, while the fixed `2023-05` control retains none.

So the next honest continuation is not another attempt to sell hidden execution harm.

It is either direct `switch_control_mode` semantics confirmation or an explicit decision to retire `2020-06` on this local path and widen again.
