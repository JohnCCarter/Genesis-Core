# RI policy router insufficient-evidence July 2024 within-envelope falsifier

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only within-envelope falsifier / observational only`

This slice is a bounded follow-up to the completed July `2024` truth-surface-correction note.
It keeps the exact July `2024` target rows, the four nearby July rows, and the frozen `2020` control rows fixed.
It does **not** reopen March `2021` / March `2025`, the closed `2024-11` null branch, or any runtime/default/policy surface.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the surviving `bars_since_regime_change <= 166` screen remains only a broad July `2024` envelope separator or whether one bounded within-envelope refinement survives on the same exact fixed surface.
- **Candidate:** `exact July 2024 within-envelope falsifier on surviving bars_since_regime_change <= 166 screen`
- **Base SHA:** `2c9522eaecee5392e294eb0c0a1a6aac9d0d51a5`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_20260504.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2024_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_20260504.py --base-sha 2c9522eaecee5392e294eb0c0a1a6aac9d0d51a5`

## Fixed surface

### Exact July `2024` target rows (`3`)

- `2024-07-13T09:00:00+00:00`
- `2024-07-14T09:00:00+00:00`
- `2024-07-14T18:00:00+00:00`

### Exact July `2024` anti-target rows (`4`)

True displacement rows (`2`):

- `2024-07-12T09:00:00+00:00`
- `2024-07-12T18:00:00+00:00`

Stable blocked context rows (`2`):

- `2024-07-12T15:00:00+00:00`
- `2024-07-13T00:00:00+00:00`

Exact July envelope lock:

- `2024-07-12T09:00:00+00:00` -> `2024-07-15T18:00:00+00:00`
- exact envelope membership: `3` target + `4` anti-target
- additional unlabeled local rows: `0`

### Frozen `2020` control rows (`4`)

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

### Frozen `2020` nearby descriptive rows (`4`)

True displacement rows (`2`):

- `2020-11-02T03:00:00+00:00`
- `2020-11-02T21:00:00+00:00`

Stable blocked context rows (`2`):

- `2020-11-02T09:00:00+00:00`
- `2020-11-03T03:00:00+00:00`

## Main result

### 1. The inherited single-field survivor is still envelope-only

The inherited screen from the truth-surface-correction slice remains:

- `bars_since_regime_change <= 166`

On this tighter within-envelope surface it behaves as:

- July `2024` target: `3 / 3` selected
- July `2024` anti-target: `4 / 4` selected
- frozen `2020` control: `0 / 4` selected

So the inherited single-field screen still collapses to a broad envelope separator inside the exact July `2024` window.
It does **not** isolate the target rows from the nearby July rows by itself.

### 2. No single-field within-envelope survivor exists

The helper evaluated `52` one-field inequality thresholds on the admitted allowlist:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`

No one-field candidate satisfied the strict within-envelope survival rule:

- `3 / 3` July target rows selected
- `<= 1 / 4` July anti-target rows selected
- `<= 1 / 4` frozen `2020` control rows selected

So the bounded within-envelope survivor, if any, had to be two-field only.

### 3. One bounded two-field within-envelope refinement does survive

The helper emitted:

- `status = bounded_within_envelope_two_field_survivor`

Top surviving candidate:

- `bars_since_regime_change <= 166`
- `action_edge <= 0.034334`

Its exact behavior on the locked surface:

- July `2024` target: `3 / 3` selected
- July `2024` anti-target: `0 / 4` selected
- frozen `2020` control: `0 / 4` selected
- frozen `2020` nearby descriptive rows: `0 / 4` selected

The same exact bounded outcome also appears on two tied alternative second clauses:

- `clarity_score <= 37`
- `confidence_gate <= 0.517167`

So the exact July `2024` surface is **not** purely envelope-only after all.
A bounded within-envelope refinement exists on the admitted decision-time surface.

### 4. The separating signature is “older and still weak,” not “older and stronger”

Cohort means on the locked surface:

#### July `2024` target

- `bars_since_regime_change`: `166.0`
- `action_edge`: `0.027348`
- `confidence_gate`: `0.513674`
- `clarity_score`: `36.333333`
- `fwd_16`: `+6.726739%`

#### July `2024` anti-target

- `bars_since_regime_change`: `164.5`
- `action_edge`: `0.122247`
- `confidence_gate`: `0.561123`
- `clarity_score`: `41.5`
- `fwd_16`: `+5.161748%`

#### Frozen `2020` control

- `bars_since_regime_change`: `302.0`
- `action_edge`: `0.027054`
- `confidence_gate`: `0.513527`
- `clarity_score`: `36.0`
- `fwd_16`: `-0.875411%`

So the exact target rows are:

- **older in regime age** than the nearby July rows,
- but also **weaker** than those nearby July rows on `action_edge`, `confidence_gate`, and `clarity_score`,
- while the frozen `2020` control shares the same weak edge/confidence/clarity family and is rejected only because it is much later in regime age.

That means the surviving refinement is not a generic “later and stronger” discriminator.
It is a narrower exact-surface conjunction that behaves more like:

> later-in-regime while still sitting inside a weak-edge / weak-confidence / lower-clarity band

on the current bounded July `2024` / frozen `2020` surface.

## Interpretation

This slice changes the bounded reading in one important way.

Before this falsifier, the surviving `bars_since_regime_change <= 166` rule looked like a coarse exact-subject envelope separator only.
After the tighter within-envelope test, the more honest read is:

> the inherited age ceiling is envelope-only by itself, but one bounded within-envelope refinement does survive on the exact July `2024` / frozen `2020` surface when that age ceiling is paired with a weak-edge / weak-confidence / lower-clarity ceiling.

That is still a **bounded research-evidence** result only.
It does **not** authorize runtime gating, default or policy changes, family changes, promotion/readiness claims, or concept authority.

## What this slice supports

- the inherited single-field survivor is still envelope-only on the exact July `2024` window
- the exact July `2024` surface nevertheless contains a bounded within-envelope survivor once a second weak-signal ceiling is added
- the surviving refinement is not unique to one second field; `action_edge`, `confidence_gate`, and `clarity_score` each produce an equivalent bounded two-field survivor when paired with the inherited age ceiling
- the bounded selectivity on this exact surface is carried by a conjunction of regime age plus weak edge/confidence/clarity, not by regime age alone

## What this slice does **not** support

- a runtime threshold change
- a router-policy change
- a claim that `bars_since_regime_change <= 166` alone is now sufficient
- a claim that the surviving two-field refinement is already portable beyond this exact July `2024` / frozen `2020` surface
- reopening March `2021` / March `2025` as the primary subject
- reopening the closed `2024-11` null branch
- promotion, readiness, or family/champion claims

## Consequence

The next honest step, if this line is reopened, is no longer another reread of the same July `2024` surface.
The next admissible move should be one additional **fixed non-March subject** falsifier that asks whether the composite bounded signature recurs outside this exact July `2024` / frozen `2020` pairing.

That is still cheaper and more honest than runtime.

## Validation notes

- exact July envelope lock held: `7` rows with `0` unlabeled extras
- exact cohort locks held for July `2024` target (`3`), July `2024` anti-target (`4`), frozen `2020` control (`4`), and frozen `2020` nearby descriptive rows (`4`)
- the helper executed successfully and wrote the bounded JSON artifact
- the emitted JSON artifact currently remains ignored by git via `.gitignore` rule `results/`, so this slice's artifact is deterministic local evidence unless explicitly force-added
- targeted `ruff check` passed on `scripts/analyze/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_20260504.py`
- all claims in this note remain observational, exact-surface, bounded, and non-authoritative
