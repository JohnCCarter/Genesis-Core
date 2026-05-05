# RI policy router insufficient-evidence July 2024 within-envelope falsifier precode packet

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / read-only / non-authoritative / no behavior change`

This packet opens one bounded follow-up to the completed July `2024` truth-surface-correction slice.
It chooses the cheaper of the two still-admissible pressure tests:

- one tighter **within-envelope falsifier** on the exact July `2024` surface

This packet does **not** open the alternative path of a new fixed non-March subject.
It does **not** reopen March `2021` / March `2025`, the closed `2024-11` null branch, or any runtime/default/policy surface.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this packet defines one future read-only evidence slice on already-fixed rows and already-admitted decision-time fields only.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the corrected July `2024` versus frozen `2020` truth surface is already fixed, so the next honest question is a tighter falsifier on that exact surface rather than fresh annual mining or runtime speculation.
- **Objective:** define one future read-only slice that tests whether the surviving `bars_since_regime_change <= 166` screen is only a broad July `2024` envelope separator or whether one bounded within-envelope refinement survives on the same exact fixed surface.
- **Candidate:** `exact July 2024 within-envelope falsifier on surviving bars_since_regime_change <= 166 screen`
- **Base SHA:** `2c9522eaecee5392e294eb0c0a1a6aac9d0d51a5`
- **Skill Usage:** `none suitable / no skill coverage claimed for this docs-only packet; if the future execution slice is later approved separately, skill usage is limited to .github/skills/python_engineering.json and no broader skill coverage is claimed`

## Why this packet exists

The completed truth-surface-correction slice already established three bounded facts on the chosen offline `fwd_16` proxy surface:

1. the exact July `2024` target rows are locally favorable,
2. the frozen `2020` control rows remain locally weak, and
3. `bars_since_regime_change <= 166` survives on the fixed July-target-versus-2020-control surface.

But the same surviving field also selects the full fixed July `2024` envelope, including the nearby displacement and stable blocked context rows.
So the next honest question is narrower than a new subject search:

> does the current survivor remain envelope-only when the four nearby July rows are promoted from descriptive context to explicit anti-target rows on the same exact bounded surface?

This packet defines that question only.
It does **not** authorize execution, runtime interpretation, or policy promotion.
Any surviving screen from a later execution slice remains a bounded July `2024` / frozen `2020` research-evidence observation only. It does **not** authorize runtime gating, default/policy/family changes, promotion/readiness claims, or fresh subject discovery.

## Exact research question

On the exact July `2024` corrected envelope, does the currently surviving screen `bars_since_regime_change <= 166` collapse fully to a broad envelope separator, or can one bounded within-envelope refinement using only the same decision-time allowlist preserve the exact July target rows while excluding most nearby July anti-target rows and still leaving the frozen `2020` control suppressed?

If answering that question would require widening to fresh annual discovery, reopening March `2021` / March `2025`, revisiting the closed `2024-11` null branch, or interpreting runtime/policy consequences, stop and open a new governed packet.

## Fixed subject lock

### Exact July `2024` target rows (`3`)

- `2024-07-13T09:00:00+00:00`
- `2024-07-14T09:00:00+00:00`
- `2024-07-14T18:00:00+00:00`

Shared target context:

- year = `2024`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `166`

Observed offline truth carried forward from the completed slice:

- `fwd_16` mean: `+6.726739%`
- `fwd_16 > 0` share: `100%`

### Exact July `2024` anti-target rows (`4`)

These rows are already fixed by the completed truth-surface-correction slice, but this future falsifier promotes them from descriptive context to explicit anti-target rows.

True displacement rows (`2`):

- `2024-07-12T09:00:00+00:00`
- `2024-07-12T18:00:00+00:00`

Stable blocked context rows (`2`):

- `2024-07-12T15:00:00+00:00`
- `2024-07-13T00:00:00+00:00`

Exact July envelope lock:

- `2024-07-12T09:00:00+00:00` -> `2024-07-15T18:00:00+00:00`
- exact envelope membership = `3` target + `4` anti-target rows
- additional unlabeled local rows inside the envelope = `0`

### Frozen `2020` control rows (`4`)

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Shared control context:

- year = `2020`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`

Frozen offline truth carried forward from the completed slice:

- `fwd_16` mean: `-0.875411%`
- `fwd_16 > 0` share: `25%`

### Frozen `2020` nearby rows remain descriptive only

True displacement rows (`2`):

- `2020-11-02T03:00:00+00:00`
- `2020-11-02T21:00:00+00:00`

Stable blocked context rows (`2`):

- `2020-11-02T09:00:00+00:00`
- `2020-11-03T03:00:00+00:00`

These `2020` nearby rows may be reported descriptively in a future execution slice, but they are not promoted into active anti-target logic under this packet.

## Allowed candidate surface

Only the already-admitted decision-time descriptive fields may be screened:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`

Allowed candidate forms for the future helper are closed to:

1. the inherited single-field threshold `bars_since_regime_change <= 166`
2. one-field **inequality** thresholds on the same allowlist
3. ordered two-field **inequality** conjunctions only if all single-field thresholds fail to produce within-envelope selectivity

Not allowed:

- equality matching such as exact `== 166` style predicates
- new fields
- payoff or post-entry fields as rule inputs
- fresh annual mining
- fresh subject discovery
- runtime-authoritative interpretation

## Survival rule for the future falsifier

For the future execution slice, a bounded within-envelope survivor may exist **only** if all of the following remain true:

1. fixed July `2024` target truth remains locally favorable on the chosen offline `fwd_16` proxy surface
   - target `fwd_16` mean must remain `> 0`
2. frozen `2020` control truth remains locally weak on the same chosen offline `fwd_16` proxy surface
   - control `fwd_16` mean must remain `< 0`
3. truth ordering remains directionally correct
   - target `fwd_16` mean must remain `> control fwd_16 mean`
4. the candidate selects all exact July target rows
   - selection rate on July target rows must be `3 / 3`
5. the candidate rejects most July anti-target rows inside the same exact envelope
   - selection rate on July anti-target rows must be `<= 1 / 4`
6. the candidate keeps the frozen `2020` control largely suppressed
   - selection rate on frozen `2020` control rows must be `<= 1 / 4`

If no candidate satisfies all six conditions, the future helper must fail closed to `envelope_only_no_survivor`.

If one candidate does satisfy all six conditions, the verdict remains bounded, observational, and non-authoritative.
It would justify at most a later docs-only interpretation packet rather than runtime, policy, default, promotion, or concept authority.

## Required row-lock and assertion discipline

Before any future candidate may be evaluated, the helper must assert all of the following:

- the July `2024` envelope is exactly `7` rows
- the July `2024` envelope contains exactly `3` target rows and `4` anti-target rows
- the July `2024` envelope contains no unlabeled extras
- the frozen `2020` control rows match the exact timestamp list above
- the frozen `2020` nearby rows match the exact descriptive timestamp lists above
- the truth-surface prerequisite remains directionally opposed on the chosen offline `fwd_16` proxy surface

If any row-lock or truth assertion fails, the future helper must fail closed rather than widen, infer, or substitute.
Selector/count drift, equality matching, or widening beyond ordered one-field and two-field inequality screens is `FAIL`, and the nearby descriptive `2020` rows cannot rescue acceptance.

## Planned future output paths

If a later execution slice is separately approved, its exact output paths should be:

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_20260504.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_precode_packet_2026-05-04.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_20260504.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.md`
  - `GENESIS_WORKING_CONTRACT.md` only if the packet becomes the pointer-only next admissible-step anchor
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/backtests/**`
  - any reopening of March `2021` / March `2025` as primary subject
  - any reopening of the closed `2024-11` null branch as primary subject
  - any fresh annual discovery or new exact subject search
  - runtime/default/policy/family/champion/promotion/readiness surfaces
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Validation requirements for a later execution slice

- `get_errors` on the packet/helper/note and any touched working-contract file
- exact row-lock proof for July `2024` target rows, July `2024` anti-target rows, frozen `2020` control rows, and frozen `2020` nearby descriptive rows
- successful helper execution against the fixed locked surface only
- emitted artifact schema check proving exact cohort membership and deterministic ordering
- `ruff check` on the new helper and any touched Python file
- `pre-commit run --files` on the touched files
- manual diff review confirming that payoff remains offline and no runtime/policy/default authority leaks into the note

## Stop conditions

- the future slice needs equality matching or another brittle exact-match rule to isolate the July target rows
- the future slice needs fresh annual mining, new subjects, or reopened March `2021` / March `2025` discovery
- the future slice needs to reinterpret the closed `2024-11` branch instead of keeping it closed
- the future slice starts implying runtime tuning, policy changes, default changes, promotion, or readiness
- the future slice needs fields outside the already-admitted allowlist

## Output required from a later execution slice

- one deterministic JSON summary artifact on the exact locked surface
- one human-readable analysis note stating clearly whether the current survivor remains envelope-only or whether one bounded within-envelope refinement survived
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- execution by itself
- runtime threshold changes
- router-policy changes
- default-behavior changes
- concept promotion of `bars_since_regime_change <= 166`
- any claim that the July `2024` truth-surface-correction survivor is already more than a bounded offline separator

Bottom line for this packet only:

> the next smallest honest pressure test is a within-envelope falsifier on the already-fixed July `2024` surface, not a new subject search and not a runtime move.
