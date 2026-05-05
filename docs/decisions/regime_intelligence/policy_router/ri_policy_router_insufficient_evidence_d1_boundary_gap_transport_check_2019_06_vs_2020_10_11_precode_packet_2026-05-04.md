# RI policy router insufficient-evidence D1 boundary-gap transport check 2019-06 vs 2020-10/11 precode packet

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / source-backed / non-authoritative / no behavior change`

This packet opens the smallest policy-facing follow-up after the completed D1 exact-pair, second-pair survival, and exact-tri-surface boundary-gap reread.
It does **not** reopen the parked July `2024` -> late-2024 -> `2022-06` transport chain as authority.
It does **not** reopen March as the primary loop.
It does **not** recycle late-2024.
It does **not** reopen the closed `2024` versus `2020` branch as a fresh age-envelope claim.
It does **not** search for a new threshold, new field family, or new conjunction.

It asks only this narrower question:

> if the exact `2019-06` harmful D1 anchor is held fixed, does the already-admitted non-age D1 boundary-gap family survive on one third exact weak-control surface, namely the exact `2020-10-31` -> `2020-11-02` `insufficient_evidence` cluster?

This slice is intentionally lean.
The only new surface is the exact `2020-10/11` weak-control side.
The harmful side, method, and claim family are all inherited.

Because the `2020` control was previously materialized on an older bounded truth-surface-correction path rather than on the new D1 artifact shape, this slice must be **source-backed** and **fail closed** on field admission.
In particular, it may not silently downgrade the current D1 family if `clarity_raw` is not directly available on the locked `2020` rows.

Any pass or fail is exact-surface only, descriptive only, and carries zero runtime, policy, promotion, readiness, or transport authority.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this packet keeps the already-proven harmful anchor fixed, introduces only one already-materialized exact weak-control surface, and proposes one bounded source-backed recurrence check with explicit fail-closed field-admission rules.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the exact-tri-surface boundary-gap slice already answered the residual/context-leak question, so the next honest move is one fresh exact control-side transport check rather than more rereads on the same surfaces or any runtime integration.
- **Objective:** test whether the current D1 non-age boundary-gap family survives on a third exact weak-control surface while keeping the exact `2019-06` harmful anchor fixed.
- **Candidate:** `fixed 2019-06 harmful anchor vs exact 2020-10/11 weak control`
- **Base SHA:** `6ac59ef0c08cb3328348d5e64ad40d83ccd4f9f9`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Why this packet exists

Three bounded answers are already locked on repo-visible evidence:

1. exact `2019-06 harmful` versus exact `2022-06 weak control`
2. exact `2019-06 harmful` versus exact `2025-03 weak control`
3. exact-tri-surface reread showing that the harmful target is materially closer to its local context floor than both weak-control targets on `action_edge`, `confidence_gate`, and `clarity_raw`

That means the current D1 line is no longer asking whether the boundary-gap read exists.
It is asking whether that read is worth one more transport/recurrence test before the line is either parked or allowed to approach a very narrow candidate discussion.

The exact `2020-10/11` weak-control cluster is the cheapest repo-visible next control surface because:

- it is already row-locked in the completed truth-surface-correction slice,
- it is positive-year and locally weak on the same offline proxy,
- and it allows one new answer without changing the harmful side, selector family, or boundary-gap method.

This packet is the only admissible way to reuse that `2020` surface.
It does **not** revive the closed July `2024` versus `2020` age-envelope argument.
It reuses `2020` only as one exact weak-control subject for the D1 line.

## Exact research question

The future execution slice must answer only this bounded question:

### D1 third-control boundary-gap question

On the fixed exact `2019-06` harmful target and the fixed exact `2020-10/11` weak-control target below, using the same all-context-floor boundary-gap framing as the completed D1 boundary-gap slice, do the current admitted non-age D1 fields still produce a harmful-versus-control ordering?

For each fixed surface $S$ and admitted field $f$, define:

$$
\text{context\_floor}(S, f) = \min\{f(x) : x \in \text{fixed context rows on } S\}
$$

and for each claim-eligible target row $t$ on that same surface:

$$
\text{boundary\_gap}(t, S, f) = \text{context\_floor}(S, f) - f(t)
$$

PASS is descriptive only and means:

1. the fixed harmful and control row locks hold exactly,
2. the current D1 non-age family is directly available on the locked source-backed row surface with no substitution,
3. at least one admitted non-age field produces a harmful-target boundary-gap range that is strictly smaller than and non-overlapping with the `2020` control-target boundary-gap range,
4. only `harmful_target` and `control_target` rows participate in PASS/FAIL adjudication,
5. context rows remain descriptive only and may not rescue or widen the claim.

FAIL is descriptive only and means one or more of the following happens:

- row-lock drift,
- truth-polarity collapse,
- required field admission failure,
- harmful/control gap overlap on every admitted non-age field,
- or a need to search, substitute, or widen.

Allowed final statuses for the later execution slice are:

- `bounded_boundary_gap_signal_present`
- `bounded_boundary_gap_null`
- `fail_closed_required_field_unavailable`

This slice may **not**:

- mine a new threshold,
- mine a new field family,
- treat a partial family downgrade as “close enough”,
- reopen July `2024` as transport logic,
- or restore runtime, policy, promotion, or transport authority.

## Exact allowed input surface

The future helper may read only the minimum repo-visible surfaces needed to materialize the fixed pair honestly:

- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`

Supporting descriptive anchors allowed for packet/note wording only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.md`
- `GENESIS_WORKING_CONTRACT.md`

No March subject, no late-2024 holdout, no July target extraction, and no new year mining is in scope.

## Fixed subject lock

### Claim-eligibility roles

The helper and emitted JSON artifact must preserve the following roles:

- exact `2019-06` harmful target rows: `row_role = harmful_target`, `claim_eligible = true`
- exact `2020-10/11` weak-control target rows: `row_role = control_target`, `claim_eligible = true`
- exact `2019-06` sibling row: `row_role = context`, `claim_eligible = false`
- exact `2020-10/11` nearby context rows: `row_role = context`, `claim_eligible = false`

Only target rows may participate in PASS/FAIL adjudication.
Context rows are descriptive only.

### Exact harmful target (`2019-06`) (`5` rows)

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Shared target context to re-assert:

- year = `2019`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`

### Exact harmful sibling context (`2019-06`) (`1` row)

- `2019-06-12T06:00:00+00:00`

Retained as descriptive context only.

### Exact weak-control target (`2020-10/11`) (`4` rows)

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Shared target context to re-assert source-backed:

- year = `2020`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`

This control side is admissible here only as a fixed weak-control D1 subject.
It may not be reframed as a reopened July `2024` comparison branch.

### Exact weak-control nearby context (`2020-10/11`) (`4` rows)

Displacement rows (`2`):

- `2020-11-02T03:00:00+00:00`
- `2020-11-02T21:00:00+00:00`

Stable blocked context rows (`2`):

- `2020-11-02T09:00:00+00:00`
- `2020-11-03T03:00:00+00:00`

These rows remain context only.
They may contribute only to descriptive floor placement and leakage description.

## Fixed field family under test

Primary admitted non-age fields remain exactly the current D1 family:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

Descriptive-only side reads allowed:

- `clarity_score`
- `bars_since_regime_change`

Critical admission rule:

- because this slice is explicitly a transport/recurrence check of the **same** D1 family, `clarity_raw` must be directly present on every locked harmful/control target row and every locked context row needed for floor construction;
- if `clarity_raw` is not directly available on that locked source-backed surface, the later execution slice must stop with `fail_closed_required_field_unavailable`;
- no substitute field, no backfill, no reconstruction, and no silent downgrade to a reduced family is allowed.

Not allowed:

- any new threshold discovery
- any fresh field search
- any two-field conjunction search
- any substitute for `clarity_raw`
- any payoff-state or future-leakage field (`fwd_*`, `mfe_*`, `mae_*`) as a rule input

## Allowed operations

The future helper is allowed to:

1. assert the fixed `2019` and `2020` row locks,
2. verify the existing harmful-side field ranges against the committed D1 artifacts,
3. source-check direct field availability on the locked `2020` surface,
4. compute one all-context floor per admitted field on each surface,
5. compute per-target boundary-gap ranges,
6. report non-overlap or overlap only,
7. emit one deterministic JSON artifact and one human-readable note.

The future helper is not allowed to:

- widen the year surface,
- search for a better `2020` pocket,
- switch to July `2024`, March, or late-2024,
- fit a new threshold,
- rephrase a descriptive age split as success,
- or touch runtime/config/default/policy surfaces.

## Success / fail-closed rule

A later execution slice may report a bounded non-null result only if all of the following remain true:

1. the exact `2019-06` harmful lock holds,
2. the exact `2020-10/11` weak-control lock holds,
3. the harmful side remains favorable / harmful-looking on the chosen offline proxy while the `2020` control side remains weak / correct-suppression-looking,
4. `action_edge`, `confidence_gate`, and `clarity_raw` are all directly evaluable on the locked source-backed row surface,
5. at least one admitted non-age field yields a harmful-target gap range that is strictly smaller than and non-overlapping with the control-target gap range,
6. only target rows determine PASS/FAIL,
7. the note explicitly keeps the result exact-surface only and non-authoritative.

If any of the following happens, the later execution slice must fail closed:

- row-lock drift,
- target/control truth-polarity collapse,
- missing `clarity_raw` on the locked source-backed row surface,
- a need to substitute or reconstruct any admitted field,
- overlap on every admitted non-age field,
- any attempt to widen or reinterpret the closed July/2020 branch.

## Required row-lock and assertion discipline

Before any later helper may compute boundary gaps, it must assert all of the following:

- exact `2019-06` harmful target timestamps are the five listed above,
- exact `2019-06` sibling context timestamp is `2019-06-12T06:00:00+00:00`,
- exact `2020-10/11` control target timestamps are the four listed above,
- exact `2020-10/11` context timestamps are the four listed above,
- the `2020` target rows remain low-zone `LONG -> NONE` `insufficient_evidence` rows under `RI_no_trade_policy`,
- context rows remain excluded from selection logic,
- `clarity_raw` availability is proven directly row-by-row rather than inferred.

If any row-lock, count, or field-admission check fails, the helper must fail closed rather than widen or infer.
The JSON artifact must include `context_rows_excluded_from_selection = true` and per-row `row_role` / `claim_eligible` metadata for every locked row.

## Planned future output paths

If this packet is approved and executed, the exact output paths should be:

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_20260504.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.md`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the completed slice changes the truthful next admissible step

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_precode_packet_2026-05-04.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_20260504.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.md`
  - `GENESIS_WORKING_CONTRACT.md` only if the completed slice becomes the truthful next-step anchor
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/backtests/**` outside the single fixed `2020` row source already named above
  - March `2021` / March `2025` as a primary loop
  - July `2024` as a reopened primary subject
  - late-2024 as a recycled holdout
  - the closed `2024` versus `2020` branch as an age-envelope argument
  - runtime/default/policy/family/champion/promotion/readiness surfaces
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Validation requirements for a later execution slice

- `get_errors` on the packet/helper/note and any touched working-contract file
- exact row-lock proof for the fixed `2019` and `2020` target/context rows
- source-backed proof of direct field availability on every locked row, including `clarity_raw`
- successful helper execution against the fixed pair only
- deterministic JSON artifact emission
- deterministic metadata covering locked timestamps, per-row roles, admitted fields, field-admission outcomes, all-context floors, per-target boundary gaps, and final status
- `ruff check` on the helper
- `pre-commit run --files` on the touched files
- manual diff review confirming that the slice stays exact-surface only and non-authoritative

## Stop conditions

- the helper needs to widen beyond the fixed `2020` cluster
- `clarity_raw` is unavailable and the slice tries to proceed anyway
- the work starts to relabel the old July `2024` versus `2020` branch as policy evidence
- any runtime/config/default surface gets touched
- any new threshold or conjunction temptation appears

## Output required from a later execution slice

- one deterministic JSON artifact stating whether the current D1 family survives on the fixed `2019` versus `2020` surface or fails closed on field admission
- one human-readable analysis note stating clearly:
  - whether the fixed non-age family remained admissible,
  - whether any admitted field produced a non-overlapping harmful-versus-control boundary-gap read,
  - and what the result does **not** justify
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- runtime threshold changes
- router-policy changes
- default changes
- reopening July `2024` transport logic
- treating a reduced family as equivalent to the current D1 family
- promotion of any resulting signal into runtime or concept authority

Bottom line for this packet only:

> the cheapest next policy-facing D1 test is one source-backed third-control boundary-gap check: keep the exact `2019-06` harmful anchor fixed, lock the exact `2020-10/11` weak-control cluster, require honest `clarity_raw` admission, and either get one real recurrence answer or fail closed quickly.
