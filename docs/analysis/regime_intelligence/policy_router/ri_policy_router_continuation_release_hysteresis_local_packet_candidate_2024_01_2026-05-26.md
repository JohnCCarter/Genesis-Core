# RI policy router continuation_release_hysteresis local packet candidate 2024-01 — 2026-05-26

## Scope

Bounded RESEARCH widening follow-up after the local `2020-06` path was closed as a descriptive breadcrumb path rather than a local execution/economic separator.

Question:

> when the next negative-like widening candidate `2024-01` is rerun against the fixed `2023-05` control on the same carrier, does it preserve more of the frozen local negative asymmetry than the control?

This slice is observational only.

It does **not** claim local economic harm for `2024-01`, change the fixed control, or rewrite the already-closed `2020-06` local semantics conclusion.

## Inputs

- monthly inventory windows: `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`
- widening candidate inventory: `results/evaluation/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json`
- frozen negative rules: `results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526.py`

## What changed and what did not

- **Changed:** one thin wrapper widened the local packet comparison from the retired `2020-06` candidate to the next negative-like candidate `2024-01`, while keeping the fixed `2023-05` control unchanged.
- **Did not change:** no runtime/config surface changed, the carrier stayed frozen, and the packet result was not promoted into an execution or P&L claim.

## Observed

### 1. `2024-01` preserves more frozen negative local asymmetry than the fixed control

Packet summary:

- `2024-01` candidate negative-rule hits: `6 / 9`
- `2023-05` control negative-rule hits: `4 / 9`
- status: `negative_like_candidate_preserves_more_triad_local_asymmetry_than_control`

So widening beyond `2020-06` stays productive on the frozen local packet surface.

### 2. The `2024-01` candidate satisfies six of the nine frozen negative rules

Satisfied negative rules for `2024-01`:

- `decisive_hours_from_cluster_start = 18.0` (threshold `<= 18.0`)
- `decisive_action_edge = 0.073054` (threshold `<= 0.075402`)
- `decisive_confidence_gate = 0.536527` (threshold `<= 0.537701`)
- `decisive_clarity_score = 39.0` (threshold `<= 39.0`)
- `cluster_policy_diff_rows = 5.0` (threshold `>= 4.5`)
- `cluster_switch_diff_rows = 5.0` (threshold `>= 4.5`)

Unsatisfied rules:

- `release_retention_ratio = 0.727273` (threshold `<= 0.5`)
- `decisive_rank_pct = 0.3` (threshold `<= 0.272727`)
- `cluster_size_diff_rows = 1.0` (threshold `>= 1.5`)

So the new 2024 candidate is not “maximally negative-like,” but it clears more of the frozen separator stack than the control.

### 3. `2024-01` carries a longer and still asymmetrical local packet than the control

Candidate cluster:

- first decisive timestamp: `2024-01-18T09:00:00+00:00`
- baseline cluster: `11` rows, `39h`
- `release_zero` cluster: `8` rows, `30h`
- baseline-minus-release-zero span compression: `9h`
- release retention ratio: `0.727273`

Control cluster:

- first decisive timestamp: `2023-05-17T06:00:00+00:00`
- baseline cluster: `7` rows, `18h`
- `release_zero` cluster: `7` rows, `18h`
- span compression: `0h`
- release retention ratio: `1.0`

So the candidate again keeps a non-trivial local asymmetry that the fixed control does not.

### 4. The candidate keeps 2024 harm in view, but only on the packet surface so far

This matters because the wider research question explicitly kept “2024 harm” in scope.

`2024-01` now shows that a month inside the 2024 year still looks more negative-like than the fixed positive control on the frozen local packet surface.

But the same artifact also confirms:

- monthly total-return diff: `0.0`
- monthly final-capital diff: `0.0`

So what is supported here is local packet asymmetry, not local realized harm.

### 5. The row pattern mixes two local regimes inside the same widening candidate

Early candidate rows (`2024-01-17T15/18/21`) still show:

- `RI_defensive_transition_policy`
- `switch_control_mode = continuation_release`
- `switch_reason = switch_blocked_by_min_dwell`

The decisive middle cluster (`2024-01-18T09 -> 2024-01-18T21`) then flips to:

- baseline `RI_defensive_transition_policy`
- `release_zero` `RI_continuation_policy`
- `switch_reason` divergence from `switch_blocked_by_hysteresis` to `continuation_state_supported`

Late candidate rows (`2024-01-19T00/03/06`) already collapse to:

- same selected policy
- same switch reason
- same size behavior
- only `switch_control_mode` differs (`continuation_release` vs `default`)

So `2024-01` arrives with its own internal local decay chain already visible in the packet artifact.

## Inferred

### 1. Widening remains alive beyond `2020-06`, and now explicitly touches 2024

The smallest honest inference is:

> after `2020-06` was retired as a local breadcrumb path, the next widening candidate `2024-01` still preserves more frozen negative local asymmetry than the fixed `2023-05` control on the same carrier.

So the widening strategy has not exhausted itself yet.

### 2. The 2024 concern is now grounded in a reproducible packet, not just intuition

This slice does **not** prove that the policy harmed a good 2024 month economically.

But it does show that `2024-01` deserves the same exact local-envelope scrutiny already applied to `2021-04` and `2020-06`.

So “2024 harm” is no longer just a general caution.

It now has a bounded candidate month on the same local packet surface.

### 3. The next honest slice is the exact local envelope, not a top-line story jump

Because the packet stays local and the month-level economics remain flat, the admissible next step is:

> exact local envelope economics for `2024-01` vs the same fixed `2023-05` control.

## Unverified

The following remain open:

1. whether the exact `2024-01` local envelope is economically flat like `2021-04` and `2020-06`, or diverges differently
2. whether `2024-01` reaches a different action/position path than the earlier candidates once the exact envelope is isolated
3. whether the visible late `switch_control_mode` residual inside `2024-01` again decays to a descriptive breadcrumb only

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526.py` -> emitted artifact with packet status `negative_like_candidate_preserves_more_triad_local_asymmetry_than_control`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_20260526.py` -> pass

## Bottom line

This slice widens the local chain honestly after `2020-06` is retired.

What is now supported is:

> `2024-01` preserves more frozen negative local asymmetry than the fixed `2023-05` control on the same carrier (`6 / 9` vs `4 / 9`), while monthly economics still remain flat.

So the next honest continuation is clear:

> exact local envelope economics for `2024-01`, keeping `2023-05` fixed.
