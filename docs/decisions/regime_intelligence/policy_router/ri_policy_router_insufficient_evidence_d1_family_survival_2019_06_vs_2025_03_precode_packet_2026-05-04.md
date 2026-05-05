# RI policy router insufficient-evidence D1 family survival 2019-06 vs 2025-03 precode packet

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / read-only / non-authoritative / no behavior change`

This packet opens the next bounded post-D1 question after the completed exact subject-pair slice `2019-06 harmful` vs `2022-06 weak control`.
It does **not** reopen the parked July `2024` -> late-2024 -> `2022-06` translation chain.
It does **not** ask whether a new discriminator can be mined.
It asks only whether the already-observed D1 non-age separator family survives on one second fresh harmful/control pair.
This slice does not search for a new separator and does not reopen transport.
It tests only whether the already-observed D1 threshold family survives when the harmful side remains fixed at exact `2019-06` and the control side is swapped to exact `2025-03`.
Any pass or fail is bounded to this fixed-family survival question only.

The question is therefore narrower than the first D1 packet:

- on the fixed exact `2019-06` harmful `insufficient_evidence` target and one fresh exact `2025-03` positive-year weak-control `insufficient_evidence` target, do the current non-age D1 separators still separate harmful versus correct-suppression targets, or does the read collapse back to age-only / pair-local behavior?

This packet does **not** reopen March `2021` / March `2025` as the primary loop.
It does **not** reopen July `2024` as the primary subject.
It does **not** reuse late-2024 as a recycled holdout.
It does **not** reopen the closed `2024` versus `2020` harmful-vs-correct control branch.
It does **not** restore authority to the falsified July transport rule.
It does **not** authorize runtime/default/policy/config/promotion work.
It reuses exact `2019-06` only as the already-validated harmful anchor for one second bounded family-survival question.
It reuses exact `2025-03` only as a fixed positive-year weak-control subject already materialized on repo-visible evidence.
`2025-03` is in scope only as the locked target/supporting row set listed in this packet, not as a month-wide March loop, search, or widened selector family.
Any surviving separator remains observational with zero runtime, policy, promotion, or readiness authority.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this packet fixes one already-validated harmful anchor, one already-materialized positive-year weak-control target, and evaluates only the existing D1 family thresholds plus a descriptive age-only comparator on existing decision-time fields.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the first exact D1 pair already answered the existence question on a pair-local basis, so the next honest move is one bounded survival test on a fresh control surface rather than broader mining or runtime integration.
- **Objective:** test whether the existing D1 non-age separator family survives outside the exact `2019-06` vs `2022-06` pair by holding the harmful side fixed and swapping to the exact `2025-03` weak-control target.
- **Candidate:** `fixed 2019-06 harmful anchor vs exact 2025-03 weak control`
- **Base SHA:** `cbd03a763a22f8ab0902e2b7a8db73e8d581e7d5`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Why this packet exists

The completed exact D1 slice already fixed the first honest answer on one pair:

- `action_edge >= 0.027801`
- `confidence_gate >= 0.513901`
- `clarity_raw >= 0.361280`

all separated the exact `2019-06` harmful target from the exact `2022-06` weak-control target.
But the same rules also selected the fixed sibling/context rows, so the result remained pair-local and context-leaky rather than broadly classifier-clean.

That means the next honest question is no longer:

> can any non-age field separate anything at all?

It is now:

> does the current D1 non-age family survive when the exact `2019-06` harmful anchor is kept fixed and the control side is replaced with one fresh repo-visible positive-year weak-control target?

This packet chooses `2025-03` because it is already materialized as an exact positive-year weak-control surface and is cleaner under current guardrails than recycling `2020` or reopening March as a loop.

## Exact research question

The future execution slice must answer only this bounded question:

### D1 family-survival question

On the fixed exact `2019-06` harmful target and the fixed exact `2025-03` weak-control target below, do the current D1 non-age separators:

- `action_edge >= 0.027801`
- `confidence_gate >= 0.513901`
- `clarity_raw >= 0.361280` when present directly on all locked target rows

still separate harmful versus correct-suppression targets with context rows excluded from fitting and selection?

PASS means the already-observed D1 thresholds are evaluated unchanged on the locked `2019-06` harmful target rows versus the locked `2025-03` weak-control target rows, with no threshold edits, no field search, no field substitution, and no control-family substitution.
FAIL means the family does not survive on this exact locked pair without widening, mining, substituting fields, or promoting an age-only read.

The helper may also report the descriptive age-only comparator:

- `bars_since_regime_change <= 164`

but that comparator may **not** be treated as the accepted answer on its own.

The helper may report both:

1. exact harmful-target versus control-target separation, and
2. descriptive placement of the fixed harmful/control context rows.

But the slice may **not**:

- mine new thresholds,
- invent a new field family,
- treat a descriptive age-only split as accepted survival,
- or reopen transport logic, threshold promotion, or runtime integration.

If the current non-age family does not survive on this exact pair, the slice must fail closed and stop at research evidence.
July `2024` remains parked and descriptive only.
The age-only comparator `bars_since_regime_change <= 164` is descriptive only, excluded from PASS/FAIL logic, excluded from ranking or separator claims, and may not be used to reopen the parked July `2024` transport chain or any new two-field conjunction search.

## Fixed subject lock

### Claim-eligibility roles

The helper and JSON artifact must preserve the following fixed adjudication roles:

- exact `2019-06` harmful target rows: `row_role = harmful_target`, `claim_eligible = true`
- exact `2025-03` weak-control target rows: `row_role = control_target`, `claim_eligible = true`
- exact `2019-06` sibling context row: `row_role = context`, `claim_eligible = false`
- exact `2025-03` supporting rows: `row_role = context`, `claim_eligible = false`

Only the `harmful_target` and `control_target` rows may participate in PASS/FAIL adjudication or any family-survival claim.
Context rows may explain local shape only; they may not rescue, create, widen, or rank survival.

### Exact harmful target (`2019-06`) (`5` rows)

These exact low-zone `insufficient_evidence` rows remain the fixed harmful anchor:

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Shared target context to be re-asserted by the helper:

- year = `2019`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `164`

Previously verified decision-time ranges on this exact target:

- `action_edge = 0.027801 .. 0.033803`
- `confidence_gate = 0.513901 .. 0.516902`
- `clarity_raw = 0.361280 .. 0.364914` when present
- `clarity_score = 36`

### Exact harmful sibling context (`2019-06`) (`1` row)

Retained as bounded context only:

- `2019-06-12T06:00:00+00:00`

Current visible shape:

- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `LONG -> NONE`
- `selected_policy = RI_no_trade_policy`
- same low-zone candidate-LONG family

### Exact weak-control target (`2025-03`) (`5` rows)

These are the exact low-zone `insufficient_evidence` rows to freeze as the fresh positive-year weak control:

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Shared target context:

- year = `2025`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `65`

Previously verified decision-time ranges on this exact target:

- `action_edge = 0.011946 .. 0.022146`
- `confidence_gate = 0.505973 .. 0.511073`
- `clarity_score = 35 .. 36`
- target `fwd_16` mean currently reads as weak / negative on the chosen offline proxy

### Exact weak-control supporting rows (`2025-03`) (`5` rows)

True displacement rows (`2`):

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Stable blocked context rows (`2`):

- `2025-03-13T21:00:00+00:00`
- `2025-03-14T06:00:00+00:00`

Additional aged-weak context row (`1`):

- `2025-03-16T12:00:00+00:00`

These rows remain context only.
They may be used for descriptive placement / leakage checks but may not change the primary target-vs-control definition.
They are excluded from separator fitting, separator selection, and any success claim.
They are also excluded from failure rescue, success counts, and any family-survival adjudication.

## Fixed field family under test

The future helper may evaluate only the already-observed D1 family and the descriptive age comparator.

Accepted family members to test exactly as inherited from the completed exact D1 pair:

- `action_edge >= 0.027801`
- `confidence_gate >= 0.513901`
- `clarity_raw >= 0.361280` only if `clarity_raw` is present directly on every locked harmful/control target row; otherwise `clarity_raw = not_evaluable` for this slice and is excluded from success/failure with no backfill, reconstruction, or substitute field

Descriptive-only comparator:

- `bars_since_regime_change <= 164`

Not allowed:

- any new threshold discovery
- any fresh field search
- any two-field conjunction search
- any backfilled or reconstructed field
- payoff-state inputs
- future leakage fields (`fwd_*`, `mfe_*`, `mae_*`) as rule inputs
- runtime-only derived state not emitted on the fixed row surface

## Allowed operations

The future helper is allowed to:

1. assert the exact harmful and control row locks
2. re-check the offline truth polarity for the fixed harmful/control targets
3. evaluate only the fixed current D1 family thresholds above
4. evaluate the descriptive age-only comparator separately
5. report descriptive placement of the fixed harmful/control context rows
6. emit one deterministic JSON artifact and one human-readable note

Not allowed:

- runtime changes
- config changes
- src/\*\* edits outside the helper script path
- broad annual mining after the exact pair is fixed
- optimizer, grid search, cross-window tuning, backfilled features, reconstructed fields, or new threshold fitting
- implicit reopening of parked transport logic
- promotion of any found survival into runtime or concept authority

## Success / fail-closed rule

A future slice may report bounded family survival only if all of the following remain true:

1. the exact `2019-06` harmful target lock holds
2. the exact `2025-03` control target lock holds
3. the helper can describe the chosen offline truth polarity honestly:
   - harmful target remains favorable / harmful-looking on the chosen offline proxy
   - control target remains weak / correct-suppression-looking on the chosen offline proxy
4. at least one fixed non-age family member survives on the exact harmful/control target pair
5. only `harmful_target` and `control_target` rows participate in PASS/FAIL adjudication
6. the note explicitly keeps the result pair-local and descriptive only

If the harmful/control truth polarity collapses, if the row lock drifts, if only the age-only comparator survives, or if the helper needs to mine a fresh threshold to recover separation, the slice must fail closed and stop at research evidence.

## Required row-lock and assertion discipline

Before any later helper may evaluate this pair, it must assert all of the following:

- exact `2019-06` harmful target rows are the five timestamps listed above
- exact harmful sibling context row is `2019-06-12T06:00:00+00:00` only
- exact `2025-03` control target rows are the five timestamps listed above
- exact `2025-03` supporting rows are the five timestamps listed above
- blocker reasons and action-pair signatures remain exactly as documented
- `clarity_raw` may only be tested if present directly on all locked harmful/control target rows; otherwise it must be recorded as `not_evaluable` and excluded from success/failure with no backfill, reconstruction, or substitute field
- context rows remain excluded from selection logic

If any row-lock, count, signature, or field-admission check fails, the helper must fail closed rather than widen or infer.
The helper must also record `context_rows_excluded_from_selection = true` in the JSON artifact and in any row-lock proof it emits.
The JSON artifact must include per-row `row_role` and `claim_eligible` metadata for all locked target and context rows.

## Planned future output paths

If this packet is approved and executed, the exact output paths should be:

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_20260504.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the slice is completed and changes the next admissible step truthfully

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_precode_packet_2026-05-04.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_20260504.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
  - `GENESIS_WORKING_CONTRACT.md` only if the completed slice becomes the truthful next-step anchor
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/backtests/**`
  - March `2021` / March `2025` as the primary subject loop
  - July `2024` as a reopened primary subject
  - late-2024 as a recycled holdout
  - the closed `2024` versus `2020` harmful-vs-correct control logic
  - runtime/default/policy/family/champion/promotion/readiness surfaces
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Validation requirements for a later execution slice

- `get_errors` on the packet/helper/note and any touched working-contract file
- exact row-lock proof for the `2019-06` harmful target, the harmful sibling row, the `2025-03` control target, and the `2025-03` supporting rows
- successful helper execution against the fixed pair only
- deterministic JSON artifact emission
- deterministic metadata covering locked timestamps, fixed family thresholds tested, age-only comparator status, surviving family members or `null`, `clarity_raw` availability, observational-only authority tag, and `context_rows_excluded_from_selection = true`
- deterministic metadata covering locked timestamps, fixed family thresholds tested, age-only comparator status, surviving family members or `null`, `clarity_raw` evaluability (`evaluable` or `not_evaluable`), observational-only authority tag, `context_rows_excluded_from_selection = true`, and per-row `row_role` / `claim_eligible`
- `ruff check` on the helper
- `pre-commit run --files` on the touched files
- manual diff review confirming the slice remains descriptive only and does not restore transport authority or runtime implications

## Stop conditions

- the pair loses its harmful-vs-correct polarity on the chosen offline proxy
- the helper needs new threshold discovery or new fields to recover separation
- the helper widens beyond the fixed `2019-06` and `2025-03` row surfaces
- the helper reopens March, July, late-2024, or the closed `2024` vs `2020` loop implicitly
- the write-up starts implying runtime tuning, policy changes, default changes, or promotion

## Output required from a later execution slice

- one deterministic JSON summary artifact on the exact fixed pair
- one human-readable analysis note stating clearly:
  - whether the inherited non-age D1 family survived on the second pair,
  - whether the answer collapsed to age-only / pair-local behavior,
  - and how the fixed context rows were placed descriptively
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- execution by itself
- runtime threshold changes
- router-policy changes
- default-behavior changes
- promotion of any surviving family member into runtime or concept authority
- reopening the parked July transport question
- treating a successful `2019-06` vs `2025-03` survival read as broad generalization beyond this second fixed pair

Bottom line for this packet only:

> the next smallest honest D1 step is one family-survival pair — fixed `2019-06` harmful pocket versus exact `2025-03` weak control — that tests whether the already-observed non-age separator family survives outside the first exact D1 pair while staying fully descriptive, pair-local, and read-only.
