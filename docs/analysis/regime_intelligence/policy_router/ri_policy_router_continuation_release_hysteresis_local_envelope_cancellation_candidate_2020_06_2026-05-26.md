# RI policy router continuation_release_hysteresis local envelope cancellation candidate 2020-06 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2020-06` local-packet widening slice.

Question:

> when the exact continuation-release envelopes recovered from the `2020-06` candidate and the fixed `2023-05` control are rerun on the same carrier, does either month open a local release_zero-minus-baseline economic gap on the total-equity path that later closes back to flat by month end?

This slice is observational only.

It does **not** reopen the retired `2021-04` candidate, claim hidden local harm has now been proven for `2020-06`, or change any runtime/config surface.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_20260526.py`

## What changed and what did not

- **Changed:** one thin wrapper reused the landed local envelope cancellation machinery, but imported exact envelope bounds from the new `2020-06` packet instead of the older `2021-04` packet.
- **Did not change:** no runtime/config files changed, no new widening month was introduced, and the earlier local-packet conclusion about `2020-06` being more negative-like than `2023-05` was not rewritten as if it had already become an economic harm claim.

## Observed

### 1. Both months reproduced the new local-packet envelope boundaries exactly

For both `2020-06` and `2023-05`:

- baseline continuation-release timestamps matched the landed local packet
- `release_zero` continuation-release timestamps matched the landed local packet
- monthly reruns stayed flat:
  - `rerun_total_return_diff = 0.0`
  - `rerun_final_capital_diff = 0.0`

So this slice stayed strictly inside the bounded envelope-economics question.

### 2. `2020-06` does **not** open a local total-equity gap anywhere inside its envelope

Envelope:

- `2020-06-17T18:00:00+00:00 -> 2020-06-18T18:00:00+00:00`
- `9` rows, `24h`

At every envelope row:

- `capital_diff = 0.0`
- `unrealized_pnl_diff = 0.0`
- `total_equity_diff = 0.0`

Key checkpoints all remain exactly flat:

- pre-envelope anchor: `0.0`
- envelope start: `0.0`
- envelope end: `0.0`
- month end: `0.0`

So the stronger `2020-06` packet still does **not** produce a hidden local economic pocket on this surface.

### 3. `2023-05` remains equally flat on the same local economic basis

Control envelope:

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

It is equally invariant again.

### 4. The executed trade path still matches exactly in both comparisons

#### `2020-06`

- baseline trade events: `7`
- `release_zero` trade events: `7`
- overlapping trade events inside the envelope: `1` vs `1`
- exit events inside the envelope: `1` vs `1`
- full-month trade signature match: `true`
- overlap trade signature match: `true`

#### `2023-05`

- baseline trade events: `5`
- `release_zero` trade events: `5`
- overlapping trade events inside the envelope: `1` vs `1`
- exit events inside the envelope: `0` vs `0`
- full-month trade signature match: `true`
- overlap trade signature match: `true`

So the economic invariance is not just a total-equity artifact.

On this slice, the executed trade ledger is also unchanged.

### 5. This slice again falsifies local envelope economics as the next separator

The helper was designed to test whether a local gap opens and later cancels.

What actually happened is stricter:

> there is no local total-equity gap to cancel in either subject.

So the new `2020-06` candidate still looks more negative-like than the control on the local packet surface, but not on the bounded local economic path.

## Inferred

### 1. `2020-06` extends the same pattern seen in `2021-04`

The smallest honest inference is:

> `2020-06` preserves more frozen negative local asymmetry than `2023-05` on the packet surface, yet still remains economically invariant on the exact local envelope when measured by `release_zero - baseline` total equity and executed trade signatures.

So the chain survives the candidate swap, but it still does not reach local economics.

### 2. The local economic surface is now a repeated dead end, not a one-off dead end

This matters because `2021-04` could have been a single exhausted candidate.

Now `2020-06` shows the same bounded outcome:

- stronger packet
- zero local equity gap
- zero trade-ledger divergence

So the local economic surface is no longer just falsified for one month.

It is now falsified across two negative-like candidates on this path.

### 3. The next honest slice is action-or-position equivalence again

Because the stronger `2020-06` packet still does not produce an economic gap, the next admissible question is:

> which action-state or position-state surface is absorbing the retained policy/size asymmetry before it can become a trade-path difference?

## Unverified

The following remain open:

1. whether `2020-06` reaches execution-surface divergence where both `2021-04` and the current envelope economics surface remain flat
2. whether the retained `2020-06` policy/size asymmetry is absorbed by the same locked-position mechanism as `2021-04`
3. whether `2020-06` collapses to the same post-reentry breadcrumb pattern or follows a different dormant-state decay path

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_20260526.py` -> emitted artifact with status `candidate_and_control_remain_economically_invariant_on_local_envelope_path`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2020_06_20260526.py` -> pass

## Bottom line

This slice keeps the widening chain alive, but only on the non-economic surfaces.

What is now supported is:

> `2020-06` is more negative-like than the fixed `2023-05` control on the frozen local packet surface, yet both months remain economically invariant on the exact bounded local envelope when measured by `release_zero - baseline` total equity and by executed trade signatures.

So the next honest continuation is narrow again:

> local action-or-position equivalence for `2020-06`, not another attempt to sell the bounded envelope as hidden local harm.
