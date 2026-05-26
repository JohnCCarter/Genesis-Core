# RI policy router continuation_release_hysteresis local envelope cancellation check — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed local-packet slice.

Question:

> when the exact continuation-release envelopes recovered from the `2021-04` candidate and the `2023-05` control are rerun on the same carrier, does either month open a local release_zero-minus-baseline economic gap on the total-equity path that later closes back to flat by month end?

This slice is observational only.

It does **not** reopen the frozen triad, override the local-packet result, claim hidden local harm has been proven, or change any runtime/config surface.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_20260526.py`

## What changed and what did not

- **Changed:** one new read-only helper imported the exact local envelope windows from the landed local packet, reran `baseline` and `release_zero`, and measured only the local `release_zero_total_equity - baseline_total_equity` path plus trade-signature equivalence.
- **Did not change:** no runtime/config files changed, no new widening target was introduced, and the earlier local-packet conclusion about decision-surface asymmetry was not rewritten as if it had already become an economic harm claim.

## Observed

### 1. Both months reproduced the local-packet envelope boundaries exactly

For both subjects:

- baseline continuation-release timestamps matched the landed local packet
- `release_zero` continuation-release timestamps matched the landed local packet
- monthly reruns stayed flat:
  - `rerun_total_return_diff = 0.0`
  - `rerun_final_capital_diff = 0.0`

So this slice stayed strictly inside the envelope-economics question.

### 2. `2021-04` does **not** open a local total-equity gap anywhere inside its envelope

Envelope:

- `2021-04-16T09:00:00+00:00 -> 2021-04-18T06:00:00+00:00`
- `16` rows, `45h`

At every envelope row:

- `capital_diff = 0.0`
- `unrealized_pnl_diff = 0.0`
- `total_equity_diff = 0.0`

Key checkpoints all remain exactly flat:

- pre-envelope anchor: `0.0`
- envelope start: `0.0`
- envelope end: `0.0`
- month end: `0.0`

So the candidate does **not** open a hidden local economic pocket on this surface.

### 3. `2023-05` is also economically flat on the same local surface

Envelope:

- `2023-05-17T06:00:00+00:00 -> 2023-05-18T00:00:00+00:00`
- `7` rows, `18h`

Again, every envelope row stays exactly flat on the same basis:

- `capital_diff = 0.0`
- `unrealized_pnl_diff = 0.0`
- `total_equity_diff = 0.0`

Key checkpoints remain:

- pre-envelope anchor: `0.0`
- envelope start: `0.0`
- envelope end: `0.0`
- month end: `0.0`

So the control is not merely “smaller” on this economic surface.

It is equally invariant.

### 4. The executed trade path also matches exactly in both comparisons

#### `2021-04`

- baseline trade events: `7`
- `release_zero` trade events: `7`
- overlapping trade events inside the envelope: `2` vs `2`
- exit events inside the envelope: `2` vs `2`
- full-month trade signature match: `true`
- overlap trade signature match: `true`

#### `2023-05`

- baseline trade events: `5`
- `release_zero` trade events: `5`
- overlapping trade events inside the envelope: `1` vs `1`
- exit events inside the envelope: `0` vs `0`
- full-month trade signature match: `true`
- overlap trade signature match: `true`

So the economic invariance is not just a drawdown/equity artifact.

On this slice, the executed trade ledger is also unchanged.

### 5. This slice does **not** support the local outcome-cancellation hypothesis on the total-equity surface

The helper was designed to test whether a local gap opens and then closes back to flat.

What actually happened is smaller and stricter:

> there is no local total-equity gap to cancel in either subject.

That means the observed local asymmetry from the prior packet is still real on the decision surface, but it does **not** become a local economic divergence on this particular surface.

## Inferred

### 1. The candidate/control separation is still a decision-surface result, not an economic-path result

The smallest honest inference is:

> `2021-04` remains more negative-like than `2023-05` on the frozen triad's local rule surface, but that separation does not materialize as a local total-equity or trade-ledger divergence on the exact envelope rerun.

So this slice narrows the claim.

It does not enlarge it.

### 2. The current envelope economics surface is effectively falsified as the next separator

Because both months are identically flat on:

- local total-equity diff
- local capital diff
- local unrealized-pnl diff
- full-month and overlap trade signatures

the next useful separator should **not** be another version of the same envelope-level equity-gap test.

### 3. The next admissible slice is now action-or-position equivalence, not local harm quantification

The sharper next question is:

> if the policy/size asymmetry remains visible in `2021-04`, but the executed economic path is unchanged, which action-state or position-state surface is absorbing that difference before it becomes a trade-path difference?

## Unverified

The following remain open:

1. whether the retained `selected_policy` / `switch_reason` / `size_changed` asymmetry is economically inert because executed actions stay the same
2. whether a finer local surface (for example action-state replay, position-state carry, or pending-size equivalence) can still separate `2021-04` from `2023-05`
3. whether any other negative-like widening candidate produces a non-zero local economic gap where `2021-04` does not

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_20260526.py` -> emitted artifact with status `candidate_and_control_remain_economically_invariant_on_local_envelope_path`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_20260526.py` -> pass

## Bottom line

The local-packet slice still mattered.

But this new envelope slice sharply limits what we may claim from it.

What is now supported is:

> `2021-04` and `2023-05` differ on the local policy-router decision surface, yet remain economically invariant on the exact bounded local envelope when measured by `release_zero - baseline` total equity and by executed trade signatures.

So the next honest continuation is narrower again:

> a local action-or-position equivalence slice, not another attempt to sell this envelope as hidden local harm.
