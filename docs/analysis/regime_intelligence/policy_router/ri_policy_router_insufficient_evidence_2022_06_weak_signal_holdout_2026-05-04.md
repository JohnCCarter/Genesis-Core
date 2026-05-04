# RI policy router insufficient-evidence 2022-06 weak-signal holdout

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only second holdout / observational only`

This slice is a bounded follow-up to the completed July `2024` within-envelope falsifier and the completed late-2024 recurrence falsifier.
It keeps one exact `2022-06` `5 + 4` low-zone surface fixed and asks two separate questions only:

1. whether the exact July transport variants survive unchanged on this second non-March subject, and
2. whether the July weak-signal ceilings recur descriptively on the fixed `2022-06` target rows even if transport fails again.

It does **not** reopen March `2021` / March `2025` as the primary subject.
It does **not** reopen July `2024` as the primary subject.
It does **not** reuse the completed late-2024 `5 + 6` subject as the new holdout.
It does **not** reopen the closed `2024` versus `2020` harmful-vs-correct counterfactual screen as active control logic.
It does **not** authorize runtime/default/policy/config/promotion work.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the fixed July transport variants fail or survive on one second exact non-March subject while reporting weak-signal recurrence separately and descriptively only.
- **Candidate:** `exact 2022-06 weak-signal holdout`
- **Base SHA:** `b1fc5cfb5d938b5bd3b95d133d0f769248241a48`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_2026-05-04.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_20260504.py`
- `results/evaluation/ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_2026-05-04.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_20260504.py --base-sha b1fc5cfb5d938b5bd3b95d133d0f769248241a48`

## Fixed 2022-06 surface

### Exact target rows (`5`)

- `2022-06-24T03:00:00+00:00`
- `2022-06-24T21:00:00+00:00`
- `2022-06-25T06:00:00+00:00`
- `2022-06-25T15:00:00+00:00`
- `2022-06-26T00:00:00+00:00`

Shared target context:

- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- zone = `low`
- candidate = `LONG`

### Fixed anti-target rows (`4`)

True displacement rows (`2`):

- `2022-06-23T03:00:00+00:00`
- `2022-06-23T12:00:00+00:00`

Stable blocked context rows (`2`):

- `2022-06-23T09:00:00+00:00`
- `2022-06-23T18:00:00+00:00`

Shared anti-target context:

- switch reason = `stable_continuation_state`
- displacement rows use `NONE -> LONG`
- blocked context rows use `LONG -> NONE`
- selected policy = `RI_continuation_policy`
- zone = `low`
- candidate = `LONG`

### Exact local envelope lock

- `2022-06-23T03:00:00+00:00` -> `2022-06-26T00:00:00+00:00`
- exact local membership: `5` target + `4` anti-target rows
- additional unlabeled local rows: `0`

## Main result

### 1. Exact July transport is fully falsified again on the 2022-06 subject

All three transported July rule variants failed completely:

- `bars_since_regime_change <= 166` AND `action_edge <= 0.034334`
- `bars_since_regime_change <= 166` AND `confidence_gate <= 0.517167`
- `bars_since_regime_change <= 166` AND `clarity_score <= 37`

Exact behavior for every transported variant:

- `2022-06` target: `0 / 5` selected
- `2022-06` anti-target: `0 / 4` selected

The reason is simple and fail-closed rather than magical:

- every target row sits at `bars_since_regime_change = 184`
- every anti-target row sits at `bars_since_regime_change = 182..183`
- so the transported July age clause `bars_since_regime_change <= 166` fails for the entire fixed `2022-06` surface before the weak-signal half can matter

The transport verdict is therefore:

- `status = transport_falsified`

### 2. The weak-signal family recurs perfectly on this fixed holdout surface, but only descriptively

All four weak-signal variants select the entire exact target cluster while rejecting the full fixed anti-target set:

- `action_edge <= 0.034334`:
  - target: `5 / 5`
  - anti-target: `0 / 4`
- `confidence_gate <= 0.517167`:
  - target: `5 / 5`
  - anti-target: `0 / 4`
- `clarity_score <= 37`:
  - target: `5 / 5`
  - anti-target: `0 / 4`
- three-way weak-signal intersection:
  - target: `5 / 5`
  - anti-target: `0 / 4`

This is cleaner than the late-2024 holdout because the full weak-signal field family separates the cohorts on every row of the fixed surface.

Target ranges:

- `action_edge = 0.012063 .. 0.025468`
- `confidence_gate = 0.506031 .. 0.512734`
- `clarity_score = 35 .. 36`

Anti-target ranges:

- `action_edge = 0.073824 .. 0.112293`
- `confidence_gate = 0.536912 .. 0.556147`
- `clarity_score = 39 .. 41`

So on this exact holdout, each weak-signal field stays entirely below the July ceiling on all target rows and entirely above it on all anti-target rows.

### 3. The local outcome polarity also remains coherent on this exact surface

The fixed `2022-06` target cluster is locally weak on the chosen offline proxy surface, while the fixed anti-target set is locally positive:

- target `fwd_16` mean: `-0.528871%`
- anti-target `fwd_16` mean: `+3.165801%`
- target `action_edge` mean: `0.018855`
- anti-target `action_edge` mean: `0.093059`
- target `confidence_gate` mean: `0.509427`
- anti-target `confidence_gate` mean: `0.546529`
- target `clarity_score` mean: `35.8`
- anti-target `clarity_score` mean: `40.0`

So the bounded `2022-06` read is internally coherent:

- the exact July transport fails again,
- the weak-signal family re-materializes descriptively on the exact target rows,
- and the anti-target surface remains materially stronger on the same offline proxy.

## Interpretation

This second non-March holdout tightens the line in a very specific way.

After the July `2024` exact-surface survivor and the late-2024 portability falsifier, the `2022-06` holdout now shows:

1. the exact July conjunction still does **not** transport unchanged,
2. the weak-signal family can recur even more cleanly on another fixed holdout than it did on late-2024, and
3. that descriptive recurrence still does **not** restore transport authority because the transported age clause keeps failing outside the original July surface.

So the honest bounded read is now:

> the July conjunction remains exact-surface evidence only, while the weak-signal family itself appears broader and descriptively recurrent across fixed holdouts.

That is useful research-evidence.
It is still not runtime authority.

## What this slice supports

- all three transported July rule variants fail again on the exact `2022-06` subject
- the July weak-signal ceilings recur descriptively on the exact `2022-06` target rows
- the exact `2022-06` holdout shows full `5 / 5` target and `0 / 4` anti-target weak-signal separation across all three admitted fields and their intersection
- the local offline proxy polarity is directionally coherent with the target/anti-target split on this exact surface
- the current line is ready for a docs-only synthesis/parking closeout rather than runtime escalation

## What this slice does **not** support

- new threshold discovery
- runtime threshold changes
- router-policy changes
- default-behavior changes
- promotion/readiness claims
- any claim that descriptive weak-signal recurrence rescues the falsified July transport result
- any claim that this bounded chain is globally exhaustive

## Consequence

The bounded translation line is now narrower and cleaner than before:

- July `2024` still holds one exact-surface conjunction on its frozen original surface,
- late-2024 already falsified unchanged transport once,
- and `2022-06` now falsifies unchanged transport a second time while producing an even cleaner descriptive weak-signal holdout.

That makes a docs-only parking synthesis the next honest closeout for this chain.

## Validation notes

- exact row lock held: `5` target + `4` anti-target = `9` rows with `0` unlabeled extras
- helper diagnostics were clean on creation
- deterministic double-run proof held with identical SHA256 on the emitted JSON artifact:
  - `6E8E6000FE959F8D9FE8738B1649F2BA8FB377BBE724C5C12BFF70D0E51A7424`
- all claims in this note remain observational, bounded, and non-authoritative
