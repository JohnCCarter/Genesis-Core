# RI policy router insufficient-evidence D1 exact subject pair precode packet

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / read-only / non-authoritative / no behavior change`

This packet opens the next bounded D1 discriminator slice after the completed July `2024` -> late-2024 -> `2022-06` translation chain was parked.
It does **not** continue that parked transport question.
It opens a **new** read-only question instead:

- on one exact harmful-looking non-March negative-year `insufficient_evidence` pocket and one exact positive-year weak-control `insufficient_evidence` pocket, which admissible decision-time field, if any, separates `router-was-wrong-to-suppress` from `router-was-right-to-suppress` on the chosen offline proxy surface?

This packet does **not** reopen March `2021` / March `2025` as the primary loop.
It does **not** reopen July `2024` as the primary subject.
It does **not** reopen the closed `2024` versus `2020` harmful-vs-correct control branch.
It does **not** restore authority to the falsified July transport rule.
It does **not** authorize runtime/default/policy/config/promotion work.
This slice reuses `2022-06` only as a fixed weak-control subject for a new D1 discriminator question.
It does **not** reopen, validate, or extend the parked July `2024` -> late-2024 -> `2022-06` translation chain, and any observed separator remains observational with zero runtime, policy, promotion, or readiness authority.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this packet freezes one exact harmful-vs-control subject pair, allows one bounded descriptive single-field / shallow-split search on already-admissible decision-time fields only, and emits read-only evidence outputs only.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the prior translation chain is parked, runtime continuation-release work is already closed on its current monthly grid, and the next honest move is a fresh bounded discriminator read on repo-visible decision-time fields rather than runtime integration.
- **Objective:** test whether any admissible single decision-time field, or one bounded shallow split built from such fields, separates a harmful negative-year `insufficient_evidence` pocket from a positive-year weak-control `insufficient_evidence` pocket on the chosen offline proxy surface.
- **Candidate:** `exact 2019-06 harmful pocket vs exact 2022-06 weak control`
- **Base SHA:** `164d5c97770d9f20cfd30bc28cf91f2d1d71f087`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Why this packet exists

The current repo-aware structural roadmap says the next honest question is D1:

> on one genuinely new bounded `insufficient_evidence` surface, which admissible decision-time field, if any, distinguishes `should suppress` from `should not suppress`?

The completed July `2024` -> late-2024 -> `2022-06` line already answered a different question:

1. the July conjunction is exact-surface evidence only,
2. unchanged transport of that conjunction is falsified on both late-2024 and `2022-06`, and
3. the weak-signal family recurs descriptively only.

So the next slice must **not** be another transport reread.
It must be a fresh bounded discriminator question.

This packet chooses the smallest repo-visible subject pair that stays inside that question:

- one fresh harmful-looking non-March negative-year `insufficient_evidence` pocket in `2019-06`
- one already-fixed positive-year weak-control `insufficient_evidence` pocket in exact `2022-06`

That pair is admissible now because:

1. it avoids March `2021` / March `2025`,
2. it avoids July `2024` as the primary subject,
3. it avoids the closed `2024` vs `2020` control logic,
4. it reuses `2022-06` only as a fixed control pocket for a **new** D1 question,
5. it stays read-only on already-visible action-diff and curated-candle surfaces.

## Exact research question

The future execution slice must answer only this bounded question:

### D1 discriminator question

On the exact target/control pair below, does any already-admissible decision-time field — or one bounded shallow split composed from such fields — separate:

- the negative-year harmful pocket (`router-was-wrong-to-suppress` on the chosen offline proxy),
- from the positive-year weak control (`router-was-right-to-suppress` on the chosen offline proxy)?

The helper may report both:

1. exact target-vs-control target separation, and
2. descriptive placement of nearby context rows, where such rows already exist on the fixed surfaces.

But the slice may **not** treat a descriptive separator as runtime authority.
It may **not** treat a coarse cross-envelope age split as automatically meaningful just because it is numerically clean.
It may **not** reopen transport logic, threshold promotion, or runtime integration.

If no admissible single-field or shallow split achieves a meaningful bounded descriptive separation on this exact pair, the slice must fail closed and stop at research evidence.

## Fixed subject lock

### Exact harmful negative-year target (`2019-06`) (`5` rows)

These are the exact low-zone `insufficient_evidence` rows to be frozen as the harmful negative anchor:

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Shared target context to be asserted by the helper:

- year = `2019`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `164`

Observed local truth from the repo-visible surface to be revalidated by the helper:

- target `fwd_16` mean currently reads as strongly positive / harmful-looking on the chosen offline proxy
- the target rows currently show:
  - `action_edge` in the `0.027801 .. 0.033803` range
  - `confidence_gate` in the `0.513901 .. 0.516902` range
  - `clarity_score = 36`

### Exact harmful-anchor local context (`2019-06`) (`1` row)

This row is retained only as bounded sibling context and may not widen the target definition:

- `2019-06-12T06:00:00+00:00`

Current visible shape:

- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `LONG -> NONE`
- `selected_policy = RI_no_trade_policy`
- same low-zone candidate-LONG family

No additional rows may be inferred into the harmful target if the row lock drifts.

### Exact positive-year weak control target (`2022-06`) (`5` rows)

These are the exact low-zone `insufficient_evidence` rows to be frozen as the positive-year weak control:

- `2022-06-24T03:00:00+00:00`
- `2022-06-24T21:00:00+00:00`
- `2022-06-25T06:00:00+00:00`
- `2022-06-25T15:00:00+00:00`
- `2022-06-26T00:00:00+00:00`

Shared control-target context:

- year = `2022`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`

Observed local control truth from the committed `2022-06` holdout note to be revalidated by the helper:

- target `fwd_16` mean currently reads as weak / negative on the chosen offline proxy

### Exact positive-year weak control context (`2022-06`) (`4` rows)

True displacement rows (`2`):

- `2022-06-23T03:00:00+00:00`
- `2022-06-23T12:00:00+00:00`

Stable blocked context rows (`2`):

- `2022-06-23T09:00:00+00:00`
- `2022-06-23T18:00:00+00:00`

These rows remain context only.
They may be used for descriptive placement / leakage checks but may not change the primary target-vs-control definition.
They are excluded from separator fitting, separator selection, and any success claim.

## Allowed field surface

The future helper is closed to a bounded search over already-admissible decision-time fields visible on the action-diff JSON / RI snapshot surface.

Minimum allowed fields:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`

Optional additional fields are allowed **only** if already present directly on the same row surface and if the helper fails closed when absent:

- `clarity_raw`
- `dwell_duration`
- other scalar router-debug fields already emitted at decision time

Not allowed:

- payoff-state inputs
- future leakage fields (`fwd_*`, `mfe_*`, `mae_*`) as rule inputs
- runtime-only derived state not emitted on the fixed row surface
- raw-source widening beyond the exact annual action-diff JSONs and curated candles already used for observational metrics

## Allowed operations

The future helper is allowed to:

1. assert the exact harmful and control row locks
2. compute observational candle proxies for descriptive truth only
3. test at most one single-field threshold using cutpoints drawn only from the fixed target/control row values
4. if single-field screening is insufficient, test at most one shallow two-field conjunction composed only from already-admissible decision-time fields present directly on the locked target rows
5. report descriptive placement of the fixed `2019-06` sibling row and the fixed `2022-06` context rows
6. emit one deterministic JSON artifact and one human-readable note

Not allowed:

- runtime changes
- config changes
- src/\*\* edits outside the helper script path
- broad annual mining after the exact pair is fixed
- optimizer, grid search, cross-window tuning, backfilled features, or reconstructed fields
- implicit reopening of parked transport logic
- promotion of any found separator into runtime or concept authority

Any pure cross-envelope age split may be reported descriptively if it appears, but it may not be treated as the accepted D1 answer on its own.

## Success / fail-closed rule

A future slice may report a bounded descriptive discriminator only if all of the following remain true:

1. the exact `2019-06` harmful target lock holds
2. the exact `2022-06` control target lock holds
3. the helper can describe the chosen offline truth polarity honestly:
   - harmful target remains favorable / harmful-looking on the chosen offline proxy
   - control target remains weak / correct-suppression-looking on the chosen offline proxy
4. any candidate separator uses only admitted decision-time fields
5. the note explicitly keeps the result descriptive only

If the harmful/control truth polarity collapses, if the row lock drifts, or if the only surviving read is a trivial cross-envelope separator that cannot be described honestly as a bounded discriminator on this pair, the slice must fail closed and stop at research evidence.

## Required row-lock and assertion discipline

Before any later helper may evaluate this pair, it must assert all of the following:

- exact `2019-06` harmful target rows are the five timestamps listed above
- exact harmful local context row is `2019-06-12T06:00:00+00:00` only
- exact `2022-06` control target rows are the five timestamps listed above
- exact `2022-06` context rows are the four timestamps listed above
- blocker reasons and action-pair signatures remain exactly as documented
- any optional additional field is used only if present on all relevant rows, else it must be skipped or fail closed explicitly

If any row-lock, count, signature, or field-admission check fails, the helper must fail closed rather than widen or infer.
The helper must also record `context_rows_excluded_from_selection = true` in the JSON artifact and in any row-lock proof it emits.

## Planned future output paths

If this packet is approved and executed, the exact output paths should be:

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_20260504.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the slice is completed and changes the next admissible step truthfully

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_precode_packet_2026-05-04.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_20260504.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
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
- exact row-lock proof for the `2019-06` harmful target, the harmful local sibling row, and the `2022-06` target/control context rows
- successful helper execution against the fixed pair only
- deterministic JSON artifact emission
- deterministic metadata covering locked timestamps, candidate field set actually used, search shape (`single_threshold` or `two_field_conjunction`), selected rule or `null`, observational-only authority tag, and `context_rows_excluded_from_selection = true`
- `ruff check` on the helper
- `pre-commit run --files` on the touched files
- manual diff review confirming the slice remains descriptive only and does not restore transport authority or runtime implications

## Stop conditions

- the pair loses its harmful-vs-correct polarity on the chosen offline proxy
- the helper needs payoff-state or future leakage as rule input
- the helper widens beyond the fixed `2019-06` and `2022-06` row surfaces
- the helper reopens March, July, late-2024, or the closed `2024` vs `2020` loop implicitly
- the write-up starts implying runtime tuning, policy changes, default changes, or promotion

## Output required from a later execution slice

- one deterministic JSON summary artifact on the exact fixed pair
- one human-readable analysis note stating clearly:
  - whether any bounded single-field or shallow-split discriminator emerged,
  - whether it remained descriptive only,
  - and how it behaved on the fixed context rows
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- execution by itself
- runtime threshold changes
- router-policy changes
- default-behavior changes
- promotion of any found separator into runtime or concept authority
- reopening the parked July transport question

Bottom line for this packet only:

> the next smallest honest D1 step is one exact harmful-vs-control subject pair — `2019-06` harmful pocket versus exact `2022-06` weak control — that asks whether any already-admissible decision-time field can separate `router-was-wrong-to-suppress` from `router-was-right-to-suppress` on a fresh bounded surface, while staying fully descriptive and read-only.
