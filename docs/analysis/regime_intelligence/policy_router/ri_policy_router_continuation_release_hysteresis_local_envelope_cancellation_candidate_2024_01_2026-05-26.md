# RI policy router continuation_release_hysteresis local envelope cancellation candidate 2024-01 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2024-01` local packet widening slice.

Question:

> when the exact continuation-release envelope recovered from the `2024-01` packet is rerun against the fixed `2023-05` control on the same carrier, does either month open a local `release_zero - baseline` economic gap on total equity, or do both remain locally invariant again?

This slice is observational only.

It does **not** change runtime/config surfaces, reinterpret the `2024-01` packet result as if it already proved local economic harm, or alter the fixed `2023-05` control.

## Inputs

- local packet artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_20260526.py`

## What changed and what did not

- **Changed:** one thin wrapper reused the landed local envelope-cancellation machinery for `2024-01`, but imported the candidate envelope via the exact packet `union_diff_surface` timestamps rather than assuming a contiguous time block.
- **Did not change:** no runtime/config file changed, no new carrier was introduced, and the `2024-01` packet asymmetry was not promoted into an economic claim.

## Observed

### 1. The exact `2024-01` envelope reproduced without drift only when using packet-exact timestamps

Candidate envelope:

- start: `2024-01-17T15:00:00+00:00`
- end: `2024-01-19T06:00:00+00:00`
- exact packet rows: `11`
- span: `39h`

Important detail:

- the `2024-01` union surface is not just a continuous every-candle interval
- it is a packet-defined exact timestamp surface with a gap between `2024-01-17T21:00:00+00:00` and `2024-01-18T09:00:00+00:00`

Once the wrapper respected those exact timestamps, the candidate rerun matched the landed packet timestamps cleanly.

### 2. `2024-01` still opens **no** local total-equity gap anywhere inside the exact envelope

Across all `11` exact candidate envelope rows:

- `capital_diff = 0.0`
- `unrealized_pnl_diff = 0.0`
- `total_equity_diff = 0.0`

Key candidate checkpoints:

- pre-envelope anchor: `0.0`
- envelope start: `0.0`
- envelope end: `0.0`
- month end: `0.0`
- peak absolute total-equity diff: `0.0`

So the stronger `2024-01` packet still does **not** produce a bounded local economic pocket on this surface.

### 3. The fixed `2023-05` control remains equally flat on the same basis

Control envelope:

- start: `2023-05-17T06:00:00+00:00`
- end: `2023-05-18T00:00:00+00:00`
- exact rows: `7`
- span: `18h`

Again, every control envelope row stays flat:

- `capital_diff = 0.0`
- `unrealized_pnl_diff = 0.0`
- `total_equity_diff = 0.0`

Control key checkpoints:

- pre-envelope anchor: `0.0`
- envelope start: `0.0`
- envelope end: `0.0`
- month end: `0.0`
- peak absolute total-equity diff: `0.0`

So the control remains fully economically invariant too.

### 4. The trade path still matches exactly for both subjects

#### `2024-01`

- baseline trade events: `6`
- `release_zero` trade events: `6`
- overlapping trade events inside the envelope: `2` vs `2`
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

So the economic flatline is not just an equity-curve artifact.

The executed trade ledger still matches exactly.

### 5. `2024-01` keeps 2024 alive on packet structure, but not on exact local economics

This is the key bounded contrast:

- packet slice: `2024-01` beat the fixed control on frozen negative local asymmetry (`6 / 9` vs `4 / 9`)
- envelope slice: `2024-01` remained economically invariant, exactly like the control

So the widened 2024 candidate survives only on the non-economic local surfaces so far.

## Inferred

### 1. The local economic surface is now falsified across three candidate months

The smallest honest inference is:

> `2021-04`, `2020-06`, and now `2024-01` can all preserve more negative-like local packet structure than the fixed `2023-05` control, yet still remain economically invariant on the exact local envelope when measured by `release_zero - baseline` total equity.

That makes the bounded local economic path look like a repeated dead end rather than a candidate-specific miss.

### 2. Keeping “2024 harm” in view still does not justify local economic claims

This slice matters because it explicitly tests a 2024 month after the earlier candidates were exhausted locally.

What it supports is narrow:

> `2024-01` is a real 2024 packet candidate on the frozen local asymmetry surface, but it still does **not** produce a bounded local economic gap.

So the 2024 concern remains legitimate as a research direction, but not yet on this exact local economic evidence surface.

### 3. The next honest slice is action-or-position equivalence for `2024-01`

Because packet asymmetry persists while exact local economics remain flat, the next admissible question is:

> which action-state or position-state surface is absorbing the retained `2024-01` policy/size asymmetry before it can become a trade-path difference?

## Unverified

The following remain open:

1. whether `2024-01` also stays fully absorbed before execution surface on a local action-or-position equivalence check
2. whether the late `2024-01` control-mode residual again collapses to a descriptive breadcrumb only
3. whether any wider non-local surface still separates 2024 candidates after the exact local packet and exact local envelope surfaces both remain flat economically

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_20260526.py` -> emitted artifact with packet status `candidate_and_control_remain_economically_invariant_on_local_envelope_path`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_20260526.py` -> pass

## Bottom line

This slice keeps the 2024 research path alive, but only on non-economic local surfaces.

What is now supported is:

> `2024-01` preserves more frozen negative local asymmetry than the fixed `2023-05` control on the packet surface, yet both months remain economically invariant on the exact local envelope when measured by `release_zero - baseline` total equity and by executed trade signatures.

So the next honest continuation is narrow again:

> local action-or-position equivalence for `2024-01`, not another attempt to sell the bounded envelope as hidden local harm.
