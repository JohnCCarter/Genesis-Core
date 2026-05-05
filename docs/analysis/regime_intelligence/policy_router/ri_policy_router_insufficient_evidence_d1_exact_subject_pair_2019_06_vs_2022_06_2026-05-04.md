# RI policy router insufficient-evidence D1 exact subject pair 2019-06 vs 2022-06

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only D1 subject pair / observational only`

This slice opens a **new** bounded D1 discriminator question after the July `2024` -> late-2024 -> `2022-06` translation chain was parked.
It reuses exact `2022-06` only as a fixed weak-control subject for that new question.
It does **not** reopen, validate, or extend the parked transport chain.
It does **not** authorize runtime/default/policy/config/promotion work.

The question is narrow:

> on one exact harmful-looking non-March negative-year `insufficient_evidence` pocket and one exact positive-year weak-control `insufficient_evidence` pocket, does any already-admissible decision-time field separate `router-was-wrong-to-suppress` from `router-was-right-to-suppress` on the chosen offline proxy surface?

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether any already-admissible decision-time field, or one bounded shallow split, separates the exact `2019-06` harmful `insufficient_evidence` pocket from the exact `2022-06` weak-control `insufficient_evidence` pocket.
- **Candidate:** `exact 2019-06 harmful pocket vs exact 2022-06 weak control`
- **Base SHA:** `164d5c97770d9f20cfd30bc28cf91f2d1d71f087`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_2022_06_weak_signal_holdout_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_translation_parking_synthesis_2026-05-04.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_20260504.py`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_20260504.py --base-sha 164d5c97770d9f20cfd30bc28cf91f2d1d71f087`

## Fixed subject pair

### Harmful target (`2019-06`) (`5` rows)

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Shared target context:

- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- zone = `low`
- candidate = `LONG`
- bars since regime change = `164`

### Harmful sibling context (`2019-06`) (`1` row)

- `2019-06-12T06:00:00+00:00`

Shared context:

- switch reason = `AGED_WEAK_CONTINUATION_GUARD`
- action pair = `LONG -> NONE`
- selected policy = `RI_no_trade_policy`
- zone = `low`
- candidate = `LONG`

### Weak control target (`2022-06`) (`5` rows)

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
- bars since regime change = `184`

### Weak control context (`2022-06`) (`4` rows)

- `2022-06-23T03:00:00+00:00`
- `2022-06-23T09:00:00+00:00`
- `2022-06-23T12:00:00+00:00`
- `2022-06-23T18:00:00+00:00`

Shared context:

- switch reason = `stable_continuation_state`
- displacement rows use `NONE -> LONG`
- blocked rows use `LONG -> NONE`
- selected policy = `RI_continuation_policy`
- zone = `low`
- candidate = `LONG`

## Main result

### 1. The exact row lock and harmful-vs-control polarity both held cleanly

The helper recovered the full locked pair exactly:

- harmful target: `5` rows
- harmful context: `1` row
- control target: `5` rows
- control context: `4` rows
- context rows excluded from separator fitting and selection: `true`

The offline truth polarity also held in the direction required by the packet:

- harmful target `fwd_16` mean: `+8.104614%`
- control target `fwd_16` mean: `-0.528871%`
- harmful minus control `fwd_16` mean gap: `+8.633485%`

So this pair remained admissible for the D1 question:

- `2019-06` still reads as a harmful-looking blocked pocket on the chosen offline proxy
- `2022-06` still reads as a weak / correct-suppression control on the same proxy

### 2. A non-age single-field discriminator did emerge on the exact target/control pair

The deterministic helper selected this accepted single-field rule:

- `action_edge >= 0.027801`

Exact target/control behavior:

- harmful target: `5 / 5` selected
- control target: `0 / 5` selected

That is a perfect target/control separation on the exact frozen pair.

The same result was **not unique** to `action_edge`.
Two additional direct decision-time fields also separated the exact target/control pair perfectly:

- `clarity_raw >= 0.361280`
- `confidence_gate >= 0.513901`

So the bounded D1 answer on this exact pair is:

> yes — the pair is not separable only by regime age; three direct non-age decision-time fields also separate the exact harmful target from the exact weak-control target without needing a two-field conjunction.

### 3. The non-age separator family is pair-clean but context-leaky

The important qualification is that the same accepted non-age rules also select the nearby context rows:

For `action_edge >= 0.027801`:

- harmful context: `1 / 1` selected
- control context: `4 / 4` selected

The exact same context placement holds for the tied `clarity_raw` and `confidence_gate` separators.

So this does **not** read as:

- a clean harmful-vs-safe local neighborhood classifier, or
- a generic `block these, pass those` rule across the entire small local envelope.

It reads more narrowly as:

- a clean separator between the exact `2019-06` harmful `insufficient_evidence` target rows and the exact `2022-06` weak-control `insufficient_evidence` target rows,
- while failing to exclude the locally positive `2022-06` continuation-context quartet.

That matters.
The bounded D1 answer is real, but it is still pair-local rather than globally persuasive.

### 4. The age-only split exists too, but it is not the accepted answer

As expected, the pure age split also separates the pair cleanly:

- `bars_since_regime_change <= 164`

Exact behavior:

- harmful target: `5 / 5` selected
- control target: `0 / 5` selected

But the packet explicitly demoted pure cross-envelope age-only separation to descriptive status only.
So the helper recorded it as:

- `descriptive_only_reason = pure_cross_envelope_age_split_not_accepted`

That means the accepted D1 answer did **not** collapse back to “it was just age.”

### 5. Not every admitted field works

The other admitted fields did **not** cleanly separate the pair:

- `clarity_score >= 36` selected `5 / 5` harmful target rows but also `4 / 5` control target rows
- `dwell_duration >= 11` selected `5 / 5` harmful target rows but also `2 / 5` control target rows

Because a valid non-age single-field separator already existed, the helper did **not** need to test a two-field conjunction.

## Exact separating ranges

### Harmful target ranges (`2019-06`)

- `action_edge = 0.027801 .. 0.033803`
- `clarity_raw = 0.361280 .. 0.364914`
- `confidence_gate = 0.513901 .. 0.516902`

### Weak control target ranges (`2022-06`)

- `action_edge = 0.012063 .. 0.025468`
- `clarity_raw = 0.351749 .. 0.359867`
- `confidence_gate = 0.506031 .. 0.512734`

These three fields show a full non-overlapping gap across the exact harmful-vs-control target pair.

## Interpretation

This slice answers the next honest D1 question more strongly than the packet minimum required.

The bounded read is now:

1. the exact `2019-06` harmful target and exact `2022-06` weak-control target do remain directionally opposite on the offline proxy,
2. the pair is separable by more than age alone,
3. three direct non-age decision-time fields (`action_edge`, `clarity_raw`, `confidence_gate`) each yield a perfect exact target/control split,
4. but that split is still context-leaky because it also selects the full `2022-06` continuation-context quartet and the `2019-06` sibling row.

So the honest conclusion is **not** “D1 is solved globally.”
It is narrower:

> on this exact pair, a real non-age discriminator family exists, but it currently distinguishes the harmful `2019-06` IE target from the weak `2022-06` IE target more cleanly than it distinguishes either target from nearby locally positive context rows.

That is useful research-evidence.
It is still not runtime authority.

## What this slice supports

- the exact pair remained admissible and polarity-consistent on the chosen offline proxy
- the fixed target/control pair is separable by at least three direct non-age decision-time fields
- the accepted deterministic rule is `action_edge >= 0.027801`
- `clarity_raw >= 0.361280` and `confidence_gate >= 0.513901` reproduce the same exact target/control split
- the age-only explanation is no longer the only clean bounded read on this pair
- the result is strong enough to justify one more bounded follow-up that tests whether this non-age separator family survives on a second fresh harmful/control subject pair

## What this slice does **not** support

- runtime threshold changes
- router-policy changes
- default-behavior changes
- any claim that the pair-local separator is already a clean broader local-context classifier
- promotion/readiness claims
- reopening the parked July `2024` -> late-2024 -> `2022-06` translation chain as if this slice had restored transport authority
- any claim that this exact pair exhausts the D1 question globally

## Consequence

The next honest bounded move is no longer “does anything non-age separate at all?”
This slice answered that in the affirmative on the exact fixed pair.

The next honest bounded move is now closer to:

- does the same non-age separator family survive on one second fresh harmful/control pair, or
- does it collapse outside this specific `2019-06` versus `2022-06` pairing?

That is the right next question if we want to know whether the current D1 answer is pair-local or starting to generalize.

## Validation notes

- exact row lock held: `5 + 1 + 5 + 4` fixed rows
- candidate field set used for selection:
  - `bars_since_regime_change`
  - `action_edge`
  - `confidence_gate`
  - `clarity_score`
  - `clarity_raw`
  - `dwell_duration`
- both optional direct fields were present on every locked target row:
  - `clarity_raw`
  - `dwell_duration`
- context rows were explicitly excluded from separator fitting and selection
- helper diagnostics were clean on creation
- deterministic double-run proof held with identical SHA256 on the emitted JSON artifact:
  - `20468D1127FFB7F13A7FCDF969048D65058A090FB8C96F02730A558A5DA17A92`
- all claims in this note remain observational, bounded, pair-local, and non-authoritative
