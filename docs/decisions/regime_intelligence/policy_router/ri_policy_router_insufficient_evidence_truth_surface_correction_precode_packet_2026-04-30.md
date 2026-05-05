# RI policy router insufficient-evidence truth-surface correction precode packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / precode bounded truth-surface correction / observational only`

This packet opens one bounded follow-up to the closed `2024`-vs-`2020` counterfactual-screen null.
It does **not** reopen March 2021 / March 2025 as the primary subject.
It does **not** authorize runtime tuning, config/default changes, or payoff-state admission into runtime.

The only purpose of this slice is to replace the closed weak `2024-11` target side with one exact **non-March** negative-year `insufficient_evidence` subset that actually materializes as locally favorable on the same chosen offline `fwd_16` proxy surface, while keeping the positive-year weak control side fixed.

This slice is an **asymmetric negative-side truth-surface correction**, not a fresh paired target/control search.
The fixed `2020` weak positive-year control cluster and its nearby displacement/context rows remain frozen from the closed `2024`-vs-`2020` slice and may not be reselected, re-ranked, or expanded.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice remains read-only against existing action-diff JSONs and curated candles, and would add only one bounded helper, one deterministic local artifact, and one analysis note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the prior exact `2024-11` branch is already closed as a bounded null, so the next honest move is one truth-surface correction on a fixed replacement target rather than any runtime speculation.
- **Objective:** rerun the bounded `insufficient_evidence` counterfactual-screen logic with a corrected exact negative-year target that is locally favorable on the same chosen offline `fwd_16` proxy surface.
- **Candidate:** `2024-07-13/14 exact insufficient_evidence target vs fixed 2020 positive-year weak control`
- **Base SHA:** `9e39b6db11637593941b0cbdb3e947dab5b2e47a`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

### Lane framing

#### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
- **Candidate / comparison surface:** exact `2024-07` low-zone `insufficient_evidence` target (`3` rows) versus the same fixed `2020` low-zone `insufficient_evidence` control cluster (`4` rows), with nearby `2024` and `2020` displacement/context rows retained descriptively only.
- **Vad ska förbättras:** recover a genuinely truth-opposed harmful-vs-correct bounded target/control surface on the chosen offline `fwd_16` proxy, without widening the slice or changing the candidate-field allowlist.
- **Vad får inte brytas / drifta:** the closed `2024-11` no-screen verdict remains untouched; payoff remains offline only; no runtime-authoritative claims may be made from the new slice alone.
- **Reproducerbar evidens som måste finnas:** one deterministic helper output JSON under `results/evaluation/`, one bounded human note under `docs/analysis/`, and a clear truth-surface check that fails closed if the corrected target/control polarity is not present.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_precode_packet_2026-04-30.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_truth_surface_correction_20260430.py`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md`
  - `results/evaluation/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json`
  - `GENESIS_WORKING_CONTRACT.md` only if and only if the bounded slice completes and the next admissible step changes materially
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**`
  - existing closed notes/results for the prior `2024-11` null slice
  - runtime/default/policy/family/champion/promotion surfaces
- **Expected changed files:** `4`
- **Max files touched:** `5`

### Gates required

- `black --check .`
- `ruff check .`
- execute `scripts/analyze/ri_policy_router_insufficient_evidence_truth_surface_correction_20260430.py` successfully against the fixed inputs
- relevant determinism replay selector
- relevant feature cache invariance selector
- relevant pipeline invariant selector
- confirm the emitted JSON artifact matches the fixed row lock and truth-surface check described below

### Stop Conditions

- Scope drift outside the fixed target/control rows and their explicitly named comparison/context rows
- Any move toward runtime/default/policy interpretation rather than bounded evidence
- The corrected target/control pair fails to remain truth-opposed on the chosen offline `fwd_16` proxy surface
- Any need to reopen March 2021 / March 2025 as the primary subject in order to complete this slice

### Output required

- **Implementation Report**
- **PR evidence template**

## Fixed subject lock

## `2024` corrected target side — exact non-March negative-year `insufficient_evidence` subset (`3` rows)

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

Observed bounded proxy surface on the current read-only scan:

- `fwd_16` mean: `+6.726739%`
- `fwd_16 > 0` share: `100%`

### Nearby `2024` descriptive rows retained for context only

True displacement rows (`2`):

- `2024-07-12T09:00:00+00:00`
- `2024-07-12T18:00:00+00:00`

Stable blocked context rows (`2`):

- `2024-07-12T15:00:00+00:00`
- `2024-07-13T00:00:00+00:00`

Exact local envelope:

- `2024-07-12T09:00:00+00:00` -> `2024-07-15T18:00:00+00:00`
- additional unlabeled local rows inside the envelope: `0`

## `2020` fixed control side — exact positive-year weak `insufficient_evidence` cluster (`4` rows)

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

Frozen proxy surface from the prior bounded screen:

- `fwd_16` mean: `-0.875411%`
- `fwd_16 > 0` share: `25%`

### Nearby `2020` descriptive rows retained for context only

True displacement rows (`2`):

- `2020-11-02T03:00:00+00:00`
- `2020-11-02T21:00:00+00:00`

Stable blocked context rows (`2`):

- `2020-11-02T09:00:00+00:00`
- `2020-11-03T03:00:00+00:00`

## Candidate-field allowlist

Only the same already-admitted descriptive fields may be screened:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`

No new fields, no runtime-only fields, and no payoff-state fields may enter this slice.

## Survival rule

A candidate screen may survive **only** if all of the following remain true:

1. fixed `2024` corrected target truth remains locally favorable on the chosen offline `fwd_16` proxy surface
   - target `fwd_16` mean must remain `> 0`
2. fixed `2020` control truth remains locally weak on the same chosen offline `fwd_16` proxy surface
   - control `fwd_16` mean must remain `< 0`
3. target/control truth ordering remains directionally correct
   - target `fwd_16` mean must remain `> control fwd_16 mean`
4. target/control selection rates satisfy the same bounded screen rule as the closed slice
   - selection rate on the fixed `2024` target rows must be `>= 0.80`
   - selection rate on the fixed `2020` control rows must be `<= 0.25`

If the truth surface is not opposed, or if no rule survives the bounded selection screen, the helper must fail closed to `no_surviving_screen`.

## Required row-lock/assert discipline

The helper must assert all of the following before any candidate may be evaluated:

- the `2024-07` local envelope is exactly `7` rows
- the `2024-07` local envelope membership is exactly `3` target + `2` nearby displacement + `2` nearby stable-blocked context rows
- the `2024-07` local envelope contains no unlabeled extras
- the frozen `2020` control, nearby displacement, and nearby stable-blocked sets match the exact timestamp lists in this packet
- the truth-surface prerequisite remains satisfied on the chosen offline `fwd_16` proxy surface

If any row-lock or truth-surface assertion fails, the helper must fail closed rather than widen, infer, or substitute.

## Non-goals

This slice does **not** justify:

- runtime threshold tuning
- default-policy changes
- global weakening or strengthening of `insufficient_evidence`
- promotion/readiness claims
- reopening March 2021 / March 2025 as the primary subject

## Planned implementation shape

If approved, implementation should:

1. add one new helper that mirrors the closed counterfactual-screen logic but locks the corrected `2024-07` target rows instead of the closed `2024-11` target rows
2. emit one bounded local artifact under `results/evaluation/`
3. record one bounded analysis note that states clearly whether the corrected pair yields a surviving screen or another fail-closed null

All claims must remain observational, exact-subject, and non-authoritative.
Any surviving field/rule combination is observational research evidence on the chosen offline `fwd_16` proxy surface only.
It does **not** reopen March 2021 / March 2025 as the primary closed subject and does **not** authorize runtime, policy-router, family, default, champion, or promotion changes.
