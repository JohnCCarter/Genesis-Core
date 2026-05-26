# RI policy router continuation_release_hysteresis candidate dormant field decay — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed candidate locked-size replay slice.

Question:

> after the `2021-04` candidate's dormant size gap has already been shown to expire before the next shared entry, which non-economic fields still differ on the trigger rows, the unlock row, and the first shared re-entry row?

This slice is observational only.

It does **not** reopen the control comparison, rerun the carrier, claim latent post-unlock harm, or reinterpret the candidate's remaining router/debug drift as if it had already become a decision or execution separator.

## Inputs

- action-position equivalence artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json`
- locked-size replay artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_20260526.py`

## What changed and what did not

- **Changed:** one new read-only post-processing helper built a 7-row field-decay matrix for the single `2021-04` locked-size episode, using only the already landed artifacts.
- **Did not change:** no runtime/config files changed, no new month was widened, no control month was reopened, and the earlier conclusion that the size gap expires before the next shared entry was not weakened.

## Observed

### 1. The field-decay slice stays inside one single candidate episode

The helper recovered exactly one candidate-only episode, matching the prior replay:

- episode row count: `7`
- trigger row count: `2`
- phase counts:
  - locked-size triggers: `2`
  - locked router-internal rows: `3`
  - unlock row: `1`
  - first shared re-entry row: `1`

So this slice does not widen the question.

It just resolves the remaining field-level drift inside the same bounded `2021-04` episode.

### 2. The trigger signature is still size + policy drift, not a broader execution surface

Across the two trigger rows, the common diff fields are:

- `selected_policy`
- `switch_reason`
- `size`

The union across both trigger rows is:

- `selected_policy`
- `switch_reason`
- `switch_control_mode`
- `size`

Everything else in the measured field set already matches on the trigger rows:

- `zone`
- `bars_since_regime_change`
- `clarity_score`
- `confidence_gate`
- `action_edge`
- `action`
- `execution_effect`

So even where the candidate still looks most negative-like, the retained difference is narrowly concentrated in size and router-policy labeling.

### 3. The size component disappears before unlock, leaving a policy trio

At the unlock row `2021-04-17T18:00:00+00:00`, the remaining diff fields are exactly:

- `selected_policy`
- `switch_reason`
- `switch_control_mode`

What is already gone by then:

- `size`
- `action`
- `execution_effect`

So the dormant size disagreement does not survive to the shared flat boundary.

By unlock, the residual has already collapsed to policy/debug labeling only.

### 4. Only one field survives to the first shared re-entry row

At the first shared re-entry row `2021-04-17T21:00:00+00:00`, the remaining diff field set is:

- `switch_control_mode`

All of the following have fully converged by re-entry:

- `selected_policy`
- `switch_reason`
- `size`
- `zone`
- `bars_since_regime_change`
- `clarity_score`
- `confidence_gate`
- `action_edge`
- `action`
- `execution_effect`

So the candidate does **not** carry a multi-field dormant signature into the next shared `LONG`.

It carries one residual internal routing label.

### 5. The emitted verdict is decay to a control-mode breadcrumb only

The artifact status is:

> `dormant_state_decays_to_control_mode_only`

That verdict is supported by a simple observed sequence:

1. trigger rows -> size + policy drift
2. unlock row -> policy/debug drift only
3. re-entry row -> only `switch_control_mode`

So the candidate's retained dormant state keeps shrinking as the episode advances.

## Inferred

### 1. The last surviving residual is router-internal, not decision-bearing

The smallest honest inference is:

> once the candidate's dormant size gap has expired, the only field still separating baseline from `release_zero` at the first shared re-entry is `switch_control_mode`.

That is weaker than a dormant decision signal.

It is best read as a router breadcrumb.

### 2. The candidate's local negative-like edge now looks exhausted on the measured surfaces

The chain is now:

1. local rule surface difference exists
2. local equity difference does not appear
3. execution difference does not appear
4. size gap expires before next shared entry
5. remaining field drift decays to one internal control-mode label

That is a strong sign that the current `2021-04` candidate has little remaining evidence value on this path.

### 3. The next honest move may be a branch decision, not another replay

Because the remaining re-entry residual is only `switch_control_mode`, the next admissible question is no longer “does the candidate still diverge?”

It is now closer to:

> is this breadcrumb interesting enough to merit one final micro-slice, or has the `2021-04` candidate been exhausted and should a new widening target take over?

## Unverified

The following remain open:

1. whether `switch_control_mode` alone has any reusable explanatory value beyond being a descriptive router breadcrumb
2. whether a different negative-like widening candidate retains a multi-field dormant signature at re-entry where `2021-04` does not
3. whether the remaining `execution_equivalent_other` rows in other candidate windows decay in the same way

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_20260526.py` -> emitted artifact with status `dormant_state_decays_to_control_mode_only`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_dormant_field_decay_20260526.py` -> pass

## Bottom line

This slice narrows the candidate story one notch further.

What is now supported is:

> inside the single `2021-04` locked-size episode, the dormant state decays from size-plus-policy drift on the trigger rows, to policy/debug drift at unlock, and then to `switch_control_mode` alone at the first shared re-entry.

So the surviving residual is no longer a size signal, no longer a policy-selection signal, and still not an execution signal.

It is just one internal control-mode breadcrumb.
