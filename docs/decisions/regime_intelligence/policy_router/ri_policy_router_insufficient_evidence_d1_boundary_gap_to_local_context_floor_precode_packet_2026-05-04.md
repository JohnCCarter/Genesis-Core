# RI policy router insufficient-evidence D1 boundary-gap to local context floor precode packet

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / runtime-read-only / source-read-closed / artifact-only / non-authoritative / no behavior change`

This packet opens the next smallest honest question after the completed D1 pair-local family-survival slice.
It does **not** reopen the parked July `2024` -> late-2024 -> `2022-06` transport chain.
It does **not** reopen March as a primary loop, recycle late-2024, or reopen the closed `2024` versus `2020` harmful-vs-correct branch.
It does **not** search for a new threshold, a new field family, or a new conjunction.

It asks only this narrower post-survival question:

> when the recurring non-age D1 family is reread on the already-materialized exact surfaces as a **local boundary-gap to the fixed context floor**, does anything become more selective than the current absolute-threshold read, or does the family still collapse to a broad context-envelope marker?

This slice is exact-surface only, artifact-only, and descriptive only.
Any pass or fail is bounded to the fixed D1 tri-surface below and carries zero runtime, policy, promotion, readiness, or transport authority.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads only the two already-emitted D1 evaluation artifacts, computes one pre-registered local boundary-gap reread on the fixed locked rows, and emits one helper, one JSON artifact, and one analysis note without touching runtime/config/default/authority surfaces.
- **Required Path:** `Lite` — low-risk, non-trivial `RESEARCH` evidence path closed to the explicitly listed validation steps in this packet; no heavier runtime gate stack is implied or authorized.
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the first D1 pair established pair-local non-age separation and the second D1 slice showed the same family survives on a fresh exact control pair, so the next honest move is a bounded artifact-only reread of the context leak rather than new source mining or runtime integration.
- **Objective:** determine whether the recurring D1 non-age family becomes honestly more selective when reread as a target-to-local-context-floor boundary gap on the fixed `2019-06`, `2022-06`, and `2025-03` surfaces.
- **Candidate:** `fixed D1 local-context-floor boundary-gap reread`
- **Base SHA:** `ea888a4b5d6b2ed2bbbacc2c93d5181d73260723`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Why this packet exists

Two bounded D1 answers are now already locked on repo-visible evidence:

1. exact `2019-06 harmful` versus exact `2022-06 weak control`
2. fixed `2019-06 harmful` versus exact `2025-03 weak control`

Across those two slices, the same non-age family survived:

- `action_edge >= 0.027801`
- `confidence_gate >= 0.513901`
- `clarity_raw >= 0.361280`

But that family remained context-leaky on every current D1 surface:

- the fixed `2019-06` sibling context row is selected
- the fixed `2022-06` context quartet is selected
- the fixed `2025-03` displacement, blocked, and aged-weak context rows are all selected

That means the next honest question is no longer:

> can a non-age D1 family survive at all?

It is now:

> does the missing structure sit in the **distance from each target row to its local selected-context boundary**, rather than in another absolute threshold or another subject search?

This packet therefore forbids fresh mining and allows only an artifact-only reread of the already-locked D1 surfaces.

## Exact research question

The future execution slice must answer only this bounded question:

### D1 boundary-gap question

On the already-materialized exact D1 surfaces below, and using only the fixed recurring non-age field family,
does at least one admitted field show a harmful-versus-control distinction when reread as a **gap to the local context floor**?

For each fixed surface $S$ and admitted field $f$, define:

$$
\text{context\_floor}(S, f) = \min\{f(x) : x \in \text{fixed context rows on } S\}
$$

and for each claim-eligible target row $t$ on that same surface:

$$
\text{boundary\_gap}(t, S, f) = \text{context\_floor}(S, f) - f(t)
$$

PASS is descriptive only and means at least one admitted non-age field satisfies all of the following on the fixed tri-surface:

1. the fixed context floor is directly evaluable from the existing D1 artifacts on all three surfaces
2. the harmful-target boundary-gap range is strictly smaller than and non-overlapping with the `2022-06` control-target boundary-gap range
3. the harmful-target boundary-gap range is strictly smaller than and non-overlapping with the `2025-03` control-target boundary-gap range
4. only `harmful_target` and `control_target` rows participate in PASS/FAIL adjudication
5. context rows remain descriptive only and may not rescue, widen, or create the claim

FAIL is descriptive only and means every admitted field either overlaps, loses the harmful-versus-control ordering, becomes unevaluable, or requires forbidden widening to say anything stronger.

This slice may conclude only one of the following:

- **bounded boundary-gap signal present** — at least one admitted non-age field shows the required harmful-versus-control non-overlap across both control surfaces
- **bounded boundary-gap null** — the family still behaves like a broad local-envelope marker on the current exact tri-surface

This slice may **not**:

- search for a new threshold
- search for a new conjunction
- switch baselines after seeing the data
- widen to new rows, new subjects, or new years
- reopen transport logic or runtime integration

## Exact allowed input surface

The future helper is fail-closed to the following already-emitted D1 artifacts only:

- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`

Supporting descriptive anchors allowed for the packet/note only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_2026-04-30.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_packet_2026-04-30.md`
- `GENESIS_WORKING_CONTRACT.md`

No new reads from annual enabled-vs-absent JSON files, curated candle parquet, fresh local windows, or new evaluation artifacts are in scope for this slice.

## Frozen tri-surface lock

### Claim-eligibility roles

The helper and JSON artifact must preserve the following adjudication roles:

- exact `2019-06` harmful target rows: `row_role = harmful_target`, `claim_eligible = true`
- exact `2022-06` weak-control target rows: `row_role = control_target`, `claim_eligible = true`
- exact `2025-03` weak-control target rows: `row_role = control_target`, `claim_eligible = true`
- all sibling/context rows on every surface: `row_role = context`, `claim_eligible = false`

Only `harmful_target` and `control_target` rows may participate in PASS/FAIL adjudication.
Context rows may explain local geometry only; they may not rescue, widen, rank, or create success.

### Exact harmful surface (`2019-06`)

Claim-bearing harmful target rows (`5`):

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Fixed harmful sibling context row (`1`):

- `2019-06-12T06:00:00+00:00`

This harmful surface appears in both allowed D1 artifacts.
The future helper must assert that the shared `2019-06` rows match exactly across those artifacts on timestamps, cohort identity, and admitted field values before computing any boundary gaps.

### Exact weak-control surface (`2022-06`)

Claim-bearing control target rows (`5`):

- `2022-06-24T03:00:00+00:00`
- `2022-06-24T21:00:00+00:00`
- `2022-06-25T06:00:00+00:00`
- `2022-06-25T15:00:00+00:00`
- `2022-06-26T00:00:00+00:00`

Fixed control context rows (`4`):

- `2022-06-23T03:00:00+00:00`
- `2022-06-23T09:00:00+00:00`
- `2022-06-23T12:00:00+00:00`
- `2022-06-23T18:00:00+00:00`

### Exact weak-control surface (`2025-03`)

Claim-bearing control target rows (`5`):

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Fixed control context rows (`5`):

Displacement context (`2`):

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Blocked context (`2`):

- `2025-03-13T21:00:00+00:00`
- `2025-03-14T06:00:00+00:00`

Aged-weak context (`1`):

- `2025-03-16T12:00:00+00:00`

These context-role splits remain descriptive only.
They may not be rebucketed, dropped, or reweighted after seeing the boundary-gap result.

## Fixed field family and baseline definition

Primary admitted non-age fields for the boundary-gap claim:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

Optional descriptive-only side read:

- `clarity_score`

Boundary-gap claims must use one and only one pre-registered baseline:

- the **all-context floor** on each fixed surface for the same field

That means:

- `2019-06` floor = the single sibling context value
- `2022-06` floor = the minimum across the fixed four context rows
- `2025-03` floor = the minimum across the fixed five context rows

Not allowed:

- switching to mean, median, max, or midpoint baselines after seeing the result
- switching to displacement-only, blocked-only, or aged-weak-only baselines
- recomputing or smoothing the floor from raw upstream rows
- using `bars_since_regime_change`, `dwell_duration`, `fwd_*`, `mfe_*`, or `mae_*` as claim fields
- treating age-only as a rescue path for a non-null result

`clarity_raw` may participate only if present directly on every fixed target and context row required by this slice within the existing artifacts.
If any required `clarity_raw` value is missing, it must be recorded as `not_evaluable` and excluded from PASS/FAIL with no backfill, substitute field, or reconstruction.

## Allowed operations

The future helper is allowed to:

1. read only the two allowed D1 evaluation artifacts
2. assert the fixed row locks, context counts, and claim-eligibility roles
3. assert the repeated `2019-06` harmful surface matches across artifacts on the admitted field family
4. compute one all-context floor per surface and admitted field
5. compute per-target boundary gaps for each claim-eligible row on each surface
6. summarize harmful-target gap range versus `2022-06` control-target gap range versus `2025-03` control-target gap range
7. report overlap or non-overlap only
8. emit one deterministic JSON artifact and one human-readable analysis note

The future helper may also report `clarity_score` boundary gaps descriptively, but `clarity_score` may not participate in PASS/FAIL adjudication or rescue a null.

Not allowed:

- any threshold fitting or threshold ranking
- any conjunction search
- any raw-source reread
- any new subject selection
- any widening beyond the frozen tri-surface
- any subgroup-baseline retry after the result is known
- any runtime/config/policy/default/promotion/readiness claim

## Success / fail-closed rule

A future execution slice may report a bounded non-null boundary-gap read only if all of the following remain true:

1. both input artifacts load cleanly and expose the fixed surfaces documented here
2. the shared `2019-06` harmful surface matches exactly across the two artifacts
3. the helper can compute the pre-registered all-context floor for the admitted field on every surface without widening
4. the harmful-target gap range is strictly smaller than and non-overlapping with both control-target gap ranges
5. only claim-eligible target rows determine PASS/FAIL
6. the note explicitly keeps the result exact-surface only, research-evidence only, and non-authoritative

If any of the following happens, the slice must fail closed:

- row-lock drift
- shared `2019-06` artifact disagreement
- missing required field values
- overlap between harmful and either control gap range
- a need to change the baseline definition
- a need to widen the context set or add a new field

## Required row-lock and assertion discipline

Before the later helper may compute any boundary gap, it must assert all of the following:

- exact `2019-06` harmful target timestamps are the five listed above
- exact `2019-06` harmful context timestamp is `2019-06-12T06:00:00+00:00` only
- exact `2022-06` control target timestamps are the five listed above
- exact `2022-06` control context timestamps are the four listed above
- exact `2025-03` control target timestamps are the five listed above
- exact `2025-03` control context timestamps are the five listed above
- the source artifacts still report `context_rows_excluded_from_selection = true`
- the admitted field family is directly available on the required rows
- no context row is promoted into the claim set

The first D1 artifact does not carry per-row `row_role` / `claim_eligible` metadata on every row.
For that artifact, the future helper may derive roles deterministically from the fixed cohort names documented in this packet.
If any cohort name, count, or row set drifts, the slice must fail closed rather than infer.

## Planned future output paths

If this packet is approved and executed, the exact output paths should be:

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_20260504.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.md`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the completed slice materially changes the truthful next admissible step, and then only as next-step drift-anchor wording with no governance, process, or authority edits

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_precode_packet_2026-05-04.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_20260504.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.md`
  - `GENESIS_WORKING_CONTRACT.md` only if the completed slice changes the next-step truthfully, and then only for next-step drift-anchor wording with no governance/process/authority edits
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/backtests/**`
  - annual enabled-vs-absent JSON source rereads
  - curated candle rereads
  - March `2021` / March `2025` as a reopened primary loop
  - July `2024` as a reopened transport subject
  - late-2024 as recycled holdout
  - the closed `2024` versus `2020` control branch
  - runtime/default/policy/family/champion/promotion/readiness surfaces
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Validation requirements for a later execution slice

- `get_errors` on the packet/helper/note and any touched working-contract file
- successful helper execution against the two allowed D1 artifacts only
- deterministic JSON artifact emission
- deterministic double-run hash replay on the JSON artifact
- deterministic metadata covering fixed row locks, admitted fields, all-context floors, per-target boundary gaps, overlap verdicts, observational-only tags, and claim-eligibility roles
- execution report or note trail explicitly recording invocation of `decision_gate_debug` and `python_engineering`
- `ruff check` on the helper
- `pre-commit run --files` on the touched files
- manual diff review confirming the slice remains artifact-only, exact-surface only, and non-authoritative

## Stop conditions

- any need to reopen raw-source reads
- any need to change the baseline from all-context floor
- any need to exclude inconvenient context rows after the result is known
- any new threshold or conjunction temptation
- any row-lock drift between packet and artifacts
- any implication of runtime tuning, router-policy change, default change, or promotion authority

## Output required from a later execution slice

- one deterministic JSON artifact stating whether a bounded boundary-gap signal exists on the fixed tri-surface
- one human-readable analysis note stating clearly:
  - whether any admitted non-age field produced a non-overlapping harmful-versus-control boundary-gap range across both controls,
  - whether the result was a bounded non-null or a bounded null,
  - and what the result does **not** justify
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- execution by itself
- runtime threshold changes
- router-policy changes
- default-behavior changes
- transport reopening
- promotion of any boundary-gap result into runtime authority
- a claim that the D1 family is now globally selective beyond the fixed exact tri-surface

Bottom line for this packet only:

> the next smallest honest D1 move is an artifact-only reread of the fixed `2019-06`, `2022-06`, and `2025-03` surfaces as **boundary gaps to the local context floor**, with no new threshold search, no source widening, and no authority inflation.
