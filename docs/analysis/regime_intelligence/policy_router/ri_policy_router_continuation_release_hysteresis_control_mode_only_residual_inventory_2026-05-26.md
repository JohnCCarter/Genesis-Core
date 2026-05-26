# RI policy router continuation_release_hysteresis control-mode-only residual inventory — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed candidate dormant field-decay slice.

Question:

> inside the exact local envelopes, are rows where `switch_control_mode` is the **only** surviving diff field unique to the `2021-04` candidate, or do they also appear in the `2023-05` control?

This slice is observational only.

It does **not** rerun the carrier, reopen the local equity/execution question, or reinterpret a control-mode breadcrumb as if it had already become a trade or policy-selection separator.

## Inputs

- action-position equivalence artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json`
- candidate dormant field-decay artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_20260526.py`

## What changed and what did not

- **Changed:** one new artifact-only inventory helper scanned both exact local envelopes and isolated rows where `switch_control_mode` was the sole remaining diff field.
- **Did not change:** no runtime/config files changed, no new widening month was introduced, and the earlier findings on execution equivalence and dormant field decay were not revised.

## Observed

### 1. The candidate has four control-mode-only residual rows, the control has zero

The inventory found:

- `2021-04` candidate: `4` rows where `switch_control_mode` is the only remaining diff field
- `2023-05` control: `0` such rows

So this breadcrumb is **not** shared across both exact local envelopes.

Within this bounded comparison, it is candidate-specific.

### 2. All candidate-only residual rows occur at or after the first shared re-entry

The candidate timestamps are:

- `2021-04-17T21:00:00+00:00`
- `2021-04-18T00:00:00+00:00`
- `2021-04-18T03:00:00+00:00`
- `2021-04-18T06:00:00+00:00`

The inventory marks all four as:

> at or after candidate re-entry = `true`

So the candidate does **not** carry any control-mode-only residuals before the first shared `LONG` re-entry.

The breadcrumb begins exactly when the broader dormant field set has already collapsed.

### 3. All four candidate rows remain execution-equivalent

All four candidate-only residual rows are classified as:

> `execution_equivalent_other`

Across those rows, the following still match between baseline and `release_zero`:

- `action`
- `execution_effect`
- `selected_policy`
- `switch_reason`
- `size`

The only surviving difference is:

- baseline `switch_control_mode = continuation_release`
- `release_zero` `switch_control_mode = default`

So even where the breadcrumb persists, it still does **not** reopen the already closed execution question.

### 4. The residual survives across more than one local post-re-entry state

The four candidate rows span multiple local states:

- shared `LONG` open-position row (`2021-04-17T21:00:00+00:00`)
- shared hold-existing row (`2021-04-18T00:00:00+00:00`)
- shared hold-flat rows (`2021-04-18T03:00:00+00:00`, `2021-04-18T06:00:00+00:00`)

So the candidate-specific breadcrumb is not just a one-row re-entry blip.

It persists through the rest of the exact local envelope.

### 5. The emitted verdict is candidate-only residual persistence after re-entry

The artifact status is:

> `candidate_only_control_mode_residual_rows_persist_after_reentry`

That verdict is supported by three observed facts:

1. candidate count `4`
2. control count `0`
3. all candidate rows occur after re-entry and remain execution-equivalent

So the final surviving breadcrumb is candidate-specific in this bounded pair, but it is still isolated to one internal routing field.

## Inferred

### 1. The candidate is not fully exhausted at the artifact surface, but the remainder is extremely narrow

The smallest honest inference is:

> `2021-04` still retains a candidate-specific residual after re-entry, but that residual is now only `switch_control_mode`.

That is narrower than a policy-selection signal.

It is narrower than the earlier dormant size disagreement.

### 2. The surviving breadcrumb is persistent, but still non-execution-bearing on this evidence surface

Because the four rows span open-position, hold-existing, and hold-flat states while staying execution-equivalent, the current artifact surface supports:

> persistence of a router breadcrumb, not persistence of a realized divergence.

So the candidate's local edge has not disappeared completely, but it has been compressed into one internal label.

### 3. The next honest move is now close to a branch decision

The remaining question is no longer “does the candidate still differ?”

That is now answered: yes, but only via `switch_control_mode`.

The next real choice is closer to:

> inspect the semantics of `switch_control_mode` directly, or retire `2021-04` as an exhausted candidate and widen to the next negative-like month.

## Unverified

The following remain open:

1. whether `switch_control_mode` is purely descriptive router state or still carries a reusable explanatory role
2. whether another negative-like widening candidate shows the same post-re-entry control-mode-only persistence pattern
3. whether the candidate-specific control-mode breadcrumb corresponds to any deeper router path distinction not already visible in the artifact-only surface

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_20260526.py` -> emitted artifact with status `candidate_only_control_mode_residual_rows_persist_after_reentry`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_20260526.py` -> pass

## Bottom line

This slice keeps the candidate alive only by a thread.

What is now supported is:

> within the exact local envelopes, `2021-04` — but not `2023-05` — retains four post-re-entry rows where `switch_control_mode` is the only surviving diff field, and all four rows remain execution-equivalent.

So the remaining candidate-specific signal is real on the artifact surface, but it is now just one persistent internal routing breadcrumb.
