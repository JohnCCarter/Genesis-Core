# RI policy router insufficient-evidence late 2024 recurrence falsifier

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only portability falsifier / observational only`

This slice is a bounded follow-up to the completed July `2024` within-envelope falsifier.
It keeps the exact late-2024 `5 + 6` local surface fixed and asks only whether the bounded July transport rules survive unchanged on that new non-March subject.

It does **not** reopen March `2021` / March `2025` as the primary subject.
It does **not** reopen July `2024` as the primary subject.
It does **not** reopen the closed `2024` versus `2020` harmful-vs-correct counterfactual screen as active control logic.
It does **not** authorize runtime/default/policy/config/promotion work.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** pressure-test whether the bounded July `2024` age-plus-weak-signal read transports unchanged to one exact late-2024 non-March subject while reporting weak-signal recurrence separately and descriptively only.
- **Candidate:** `exact late-2024 insufficient_evidence recurrence falsifier`
- **Base SHA:** `2c9522eaecee5392e294eb0c0a1a6aac9d0d51a5`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_july_2024_within_envelope_falsifier_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `scripts/analyze/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_20260504.py`
- `results/evaluation/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_2026-05-04.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_20260504.py --base-sha 2c9522eaecee5392e294eb0c0a1a6aac9d0d51a5`

## Fixed late-2024 surface

### Exact target rows (`5`)

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Shared target context:

- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- zone = `low`
- candidate = `LONG`

### Fixed anti-target rows (`6`)

`AGED_WEAK_CONTINUATION_GUARD` sibling rows (`4`):

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`

Nearby `stable_continuation_state` rows (`2`):

- true displacement row: `2024-12-01T00:00:00+00:00`
- stable blocked context row: `2024-12-01T06:00:00+00:00`

Exact local envelope lock:

- `2024-11-27T15:00:00+00:00` -> `2024-12-03T00:00:00+00:00`
- exact local membership: `5` target + `6` anti-target rows
- additional unlabeled local rows: `0`

## Main result

### 1. Exact July transport is fully falsified on the late-2024 subject

All three transported July rule variants failed completely:

- `bars_since_regime_change <= 166` AND `action_edge <= 0.034334`
- `bars_since_regime_change <= 166` AND `confidence_gate <= 0.517167`
- `bars_since_regime_change <= 166` AND `clarity_score <= 37`

Exact behavior for every transported variant:

- late-2024 target: `0 / 5` selected
- late-2024 anti-target: `0 / 6` selected

So the bounded July conjunction does **not** transport unchanged to this late-2024 subject.
The transport verdict is therefore:

- `status = transport_falsified`

### 2. The weak-signal half does recur descriptively on the late-2024 target rows

The weak-signal ceilings from the July slice do re-materialize locally, but only as descriptive recurrence:

- `clarity_score <= 37`:
  - target: `5 / 5`
  - anti-target: `1 / 6`
  - leakage row: `2024-11-29T00:00:00+00:00`
- `action_edge <= 0.034334`:
  - target: `4 / 5`
  - anti-target: `0 / 6`
- `confidence_gate <= 0.517167`:
  - target: `4 / 5`
  - anti-target: `0 / 6`
- three-way weak-signal intersection:
  - target: `4 / 5`
  - anti-target: `0 / 6`

The missed target row on the tighter edge/confidence screens is:

- `2024-11-30T03:00:00+00:00`

because it sits just above both corresponding July cutoffs while still matching the July clarity ceiling:

- `action_edge = 0.034684`
- `confidence_gate = 0.517342`
- `clarity_score = 37`

### 3. Only the weak-signal ceilings recur descriptively on this subject

The late-2024 target rows remain locally weak on the chosen offline proxy surface:

- `fwd_16` mean: `-0.855705%`
- `bars_since_regime_change` mean: `281.4`
- `action_edge` mean: `0.027769`
- `confidence_gate` mean: `0.513884`
- `clarity_score` mean: `36.2`

So the honest bounded read is now:

> on this exact late-2024 subject, only the weak-edge / weak-confidence / low-clarity ceilings recur descriptively; the full July conjunction does not transport.

This is slice-local observational evidence only.
It does **not** propose a portable threshold or screening rule.
The age clause carried the subject specificity, while the weak-signal half alone is not unique to the locally favorable July target.

## Interpretation

This slice narrows the portability story in a useful way.

Before this falsifier, the bounded July `2024` result could still be misread as a candidate conjunction that might generalize to another fixed subject.
After the exact late-2024 transport check, the more honest read is:

1. the July conjunction is **not** portable unchanged,
2. the weak-signal half is locally real but not uniquely favorable, and
3. the current evidence remains bounded, descriptive, and non-authoritative.

So this slice weakens portability while strengthening the case that the weak-signal family itself is broader than the single July subject.

## What this slice supports

- all three transported July rule variants fail on the exact late-2024 subject
- the weak-signal ceilings recur descriptively on the exact late-2024 target rows
- the bounded July conjunction remains exact-surface evidence rather than portable authority
- the late-2024 target pocket is locally weak even while matching much of the July weak-signal family

## What this slice does **not** support

- new threshold discovery
- runtime threshold changes
- router-policy changes
- default-behavior changes
- promotion/readiness claims
- any claim that the weak-signal recurrence read can rescue the failed transport result

## Consequence

The current honest state of this translation line is now tighter than before:

- the bounded July conjunction remains real on the exact July `2024` / frozen `2020` surface,
- but it does **not** transport unchanged to the exact late-2024 subject,
- and the weak-signal half is broader than one locally favorable pocket.

If this line is reopened again, the next honest move should be either:

1. one docs-only synthesis/parking note, or
2. one fresh packet for a second fixed non-March subject beyond this late-2024 pocket.

Both remain cheaper and more honest than runtime.

## Validation notes

- exact row lock held: `5` target + `6` anti-target = `11` rows with `0` unlabeled extras
- helper diagnostics were clean on creation
- deterministic double-run proof held with identical SHA256 on the emitted JSON artifact:
  - `25088B556A8004EB042C18AF6915BD1252BA8CA3A6990C13849585F4151B5D9C`
- the emitted JSON artifact currently remains ignored by git under the repo's `results/` ignore rule, so this slice's artifact is deterministic local evidence unless explicitly force-added
- all claims in this note remain observational, bounded, and non-authoritative
