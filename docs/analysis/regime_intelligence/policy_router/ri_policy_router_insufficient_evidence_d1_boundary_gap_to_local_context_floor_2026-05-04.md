# RI policy router insufficient-evidence D1 boundary-gap to local context floor

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / artifact-only boundary-gap reread / fixed tri-surface`

This slice is the bounded follow-up to the completed D1 exact-pair and second-pair family-survival work.
It does not search for a new threshold.
It does not reopen the parked July `2024` transport chain.
It does not reopen March as a primary loop, recycle late-2024, or reopen the closed `2024` versus `2020` branch.
It does not authorize runtime, default, policy, config, or promotion work.

It asks only whether the already-recurring non-age D1 family becomes more honest and selective when reread on the fixed `2019-06`, `2022-06`, and `2025-03` surfaces as a **target gap to the local context floor** rather than as a plain absolute threshold.

All returns and excursion values in this slice remain timestamp-close observational proxies already embedded in the source artifacts.
They are descriptive only and do not establish realized trade PnL, fill-aware row truth, causal authority, runtime readiness, or transport authorization.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: the helper reads only the two already-emitted D1 evaluation artifacts and computes one pre-registered all-context-floor boundary-gap reread on a locked tri-surface.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** determine whether the recurring D1 non-age family becomes more selective when reread as a local boundary gap on the fixed `2019-06`, `2022-06`, and `2025-03` surfaces.
- **Candidate:** `fixed D1 local-context-floor boundary-gap reread`
- **Base SHA:** `ea888a4b5d6b2ed2bbbacc2c93d5181d73260723`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_2026-04-30.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.json`

## Exact commands run

- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_20260504.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_20260504.py --base-sha ea888a4b5d6b2ed2bbbacc2c93d5181d73260723`
- identical second helper run on the same two source artifacts with SHA256 hash check before/after

Determinism check on the emitted artifact:

- SHA256 before rerun: `E726FEE746F77276B8E0B5B17BABDD9C7227AF33940115463DFB3838AE35CCF1`
- SHA256 after rerun: `E726FEE746F77276B8E0B5B17BABDD9C7227AF33940115463DFB3838AE35CCF1`

## Fixed tri-surface that actually materialized

### Exact harmful surface (`2019-06`)

Claim-bearing harmful target rows (`5`):

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Fixed context row (`1`):

- `2019-06-12T06:00:00+00:00`

Re-asserted local shape:

- `row_role = harmful_target` for the five target rows
- `row_role = context`, `claim_eligible = false` for the sibling row
- offline proxy still reads as harmful-looking: target `fwd_16` mean = `+8.104614%`

### Exact weak-control surface (`2022-06`)

Claim-bearing control target rows (`5`):

- `2022-06-24T03:00:00+00:00`
- `2022-06-24T21:00:00+00:00`
- `2022-06-25T06:00:00+00:00`
- `2022-06-25T15:00:00+00:00`
- `2022-06-26T00:00:00+00:00`

Fixed context rows (`4`):

- `2022-06-23T03:00:00+00:00`
- `2022-06-23T09:00:00+00:00`
- `2022-06-23T12:00:00+00:00`
- `2022-06-23T18:00:00+00:00`

Offline proxy still reads as weak/correct-suppression-looking:

- target `fwd_16` mean = `-0.528871%`

### Exact weak-control surface (`2025-03`)

Claim-bearing control target rows (`5`):

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Fixed context rows (`5`):

- `2025-03-13T15:00:00+00:00`
- `2025-03-13T21:00:00+00:00`
- `2025-03-14T00:00:00+00:00`
- `2025-03-14T06:00:00+00:00`
- `2025-03-16T12:00:00+00:00`

Offline proxy still reads as weak/correct-suppression-looking:

- target `fwd_16` mean = `-1.017927%`

## Main result

### 1. The residual/context-leak question closes with a bounded **yes** on the fixed tri-surface

All three admitted non-age fields produced a non-overlapping harmful-versus-control boundary-gap read across **both** control surfaces:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

So the old bounded question — whether any still-admissible read could distinguish harmful-versus-correct target rows without treating the whole sibling/context envelope as the claim set — now has a fixed-surface answer:

> yes, on the current exact tri-surface, the harmful blocked target sits materially closer to its local context floor than either weak-control target set does.

This is still research evidence only.
It is not a new threshold family and not a runtime rule.

### 2. `action_edge` shows the same ordered gap shape on all three surfaces

All-context floors:

- `2019-06` floor = `0.042122`
- `2022-06` floor = `0.073824`
- `2025-03` floor = `0.047301`

Target boundary-gap ranges:

- harmful `2019-06`: `0.008319 .. 0.014321`
- control `2025-03`: `0.025155 .. 0.035355`
- control `2022-06`: `0.048356 .. 0.061761`

Required pairwise ordering holds in both comparisons:

- harmful vs `2025-03` separation margin = `0.010834`
- harmful vs `2022-06` separation margin = `0.034035`

So `action_edge` no longer reads merely as an absolute survivor threshold here.
On this exact tri-surface it reads as a **local boundary-distance field**.

### 3. `confidence_gate` shows the same smaller-harmful-gap ordering

All-context floors:

- `2019-06` floor = `0.521061`
- `2022-06` floor = `0.536912`
- `2025-03` floor = `0.523651`

Target boundary-gap ranges:

- harmful `2019-06`: `0.004159 .. 0.007160`
- control `2025-03`: `0.012578 .. 0.017678`
- control `2022-06`: `0.024178 .. 0.030881`

Required pairwise ordering holds in both comparisons:

- harmful vs `2025-03` separation margin = `0.005418`
- harmful vs `2022-06` separation margin = `0.017018`

So the same exact ordering recurs on `confidence_gate`: the harmful target is nearer to its local context floor than both control target surfaces are to theirs.

### 4. `clarity_raw` remains fully evaluable and shows the same shape again

`clarity_raw` stayed directly present on every required target and context row, so it did not fail closed.

All-context floors:

- `2019-06` floor = `0.369952`
- `2022-06` floor = `0.389149`
- `2025-03` floor = `0.373088`

Target boundary-gap ranges:

- harmful `2019-06`: `0.005038 .. 0.008672`
- control `2025-03`: `0.015233 .. 0.021410`
- control `2022-06`: `0.029282 .. 0.037400`

Required pairwise ordering holds in both comparisons:

- harmful vs `2025-03` separation margin = `0.006561`
- harmful vs `2022-06` separation margin = `0.020610`

So the third admitted non-age field confirms the same exact envelope-relative read.

### 5. `clarity_score` stays descriptive only and does **not** carry the claim

The packet allowed `clarity_score` only as a descriptive side read.
That was the right fence.

Its gap ranges were:

- harmful `2019-06`: `1.0 .. 1.0`
- control `2025-03`: `1.0 .. 2.0`
- control `2022-06`: `3.0 .. 4.0`

So `clarity_score` cleanly separated harmful from `2022-06`, but it **did not** separate harmful from `2025-03` because the ranges touch at `1.0`.

That means the bounded non-null result belongs to the admitted non-age family only:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

not to the descriptive side field.

## What changed relative to the previous D1 reads

The first D1 exact pair answered:

> the non-age family can separate one harmful/control pair, but it leaks across sibling/context rows.

The second D1 pair answered:

> the same non-age family survives on a fresh control pair, but it still leaks across every fixed context row.

This boundary-gap slice sharpens the interpretation one step further:

> the recurring family is better read on the current fixed tri-surface as a **distance-to-local-context-floor** structure than as an arbitrary absolute threshold winner.

That is new, but bounded.
It does **not** mean the family is suddenly transport-ready or globally classifier-clean.

## Interpretation

The smallest honest read from this slice is:

> on the exact already-materialized `2019-06`, `2022-06`, and `2025-03` surfaces, the harmful blocked target pocket sits materially closer to its local context floor than either weak-control target pocket does on all three admitted non-age decision-time fields.

This means the earlier D1 recurrence is no longer best described as “some absolute threshold happened to win twice.”
On the current tri-surface, the better description is:

- the non-age D1 family survives as an **envelope-relative boundary-gap structure**
- the claim remains target-only and exact-surface only
- the local context rows remain descriptive inputs to the floor, not promoted success rows

## What this slice does **not** prove

This slice does **not** prove:

- that a portable runtime threshold or runtime gap rule exists
- that the same boundary-gap ordering survives on any new pair or any wider year surface
- that context-role structure no longer matters
- that the parked July chain should be reopened
- that the recurring D1 family is globally classifier-clean or promotion-ready
- that any runtime/config/default/policy change is warranted

## Next admissible step

The next honest bounded move is no longer another residual/context-leak reread on the same three surfaces.
This slice answered that question with a bounded **yes**.

If the user wants to continue this exact insufficient-evidence D1 line, the next smallest honest move is now a **fresh governed transport check** on one additional exact harmful/control surface using the same all-context-floor boundary-gap framing.

That next step must still:

- keep the July `2024` translation chain parked
- avoid reopening March as a primary loop
- avoid late-2024 recycling
- avoid the closed `2024` versus `2020` branch
- keep any result exact-surface only until a later governed slice proves otherwise
