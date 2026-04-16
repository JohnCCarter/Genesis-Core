# current_atr 1435 default-off trial precode packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is a docs-only quick-path change that defines a future execution contract using already existing implementation/test surfaces; it authorizes no runtime, schema, config, or API behavior change.
- **Required Path:** `Quick`
- **Objective:** Define the bounded precode contract for a later execution-only default-off trial of `current_atr >= 1435.209570` using the already implemented research seam, without authorizing source-code changes, config changes, artifact generation, or execution in this slice.
- **Candidate:** `future current_atr 1435 default-off trial`
- **Base SHA:** `c9f35347fdb3c9019212478d2d7eac6939105c76`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; explicit citations to the already existing `current_atr` implementation surface; explicit citations to the already existing default-off parity tests; carried-forward references to the `900`, `900`-environment, `1435`, and `900-vs-1435` evidence chain; one future execution boundary for a later `1435`-only default-off trial; one hard stop/reopen rule if code/config/test changes become necessary.
- **Scope OUT:** no source-code changes; no tests; no config/runtime/result changes; no execution in this slice; no edits under `src/**`, `tests/**`, `config/**`, `tmp/**`, or `results/**`; no schema/API/config-authority/default changes; no widening beyond the already validated `1435` seam; no claim that `1435` is universally superior to `900`.
- **Expected changed files:** `docs/governance/current_atr_1435_default_off_trial_precode_packet_2026-04-16.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- `pre-commit run --files docs/governance/current_atr_1435_default_off_trial_precode_packet_2026-04-16.md`
- manual wording audit that this packet remains docs-only and non-authorizing
- manual wording audit that carried-forward implementation/test evidence is not misrepresented as re-verified in this slice
- manual wording audit that the tradeoff against `900` remains explicit
- manual wording audit that the rebased execution-basis caveat is preserved

### Stop Conditions

- any wording that authorizes `src/**`, `tests/**`, `config/**`, `tmp/**`, or `results/**` edits now
- any wording that implies runtime readiness, default promotion, or rollout activation now
- any wording that treats `1435` as universally superior to `900`
- any wording that flattens the mixed execution-basis caveat into a fake same-basis rerun
- any wording that allows a future execution-only trial to silently absorb code/config/test changes instead of reopening as a separate implementation packet

### Output required

- one reviewable docs-only precode packet for a later execution-only `1435` trial
- one explicit stop/reopen rule for any future need to modify code, tests, config, or tmp execution surfaces

### Skill Usage

- No repo-local skill is claimed for this docs-only slice.
- This packet uses only existing evidence surfaces and wording discipline.
- Any later execution-only trial packet must explicitly choose the relevant execution/verification skill set or document why no matching skill applies.

## What this packet is

This packet is documentation-only and research-only.
It does **not** execute anything.
It does **not** re-verify code in this slice.
It carries forward the already existing implementation and test surfaces as evidence anchors for a later, separate trial packet.

This packet does **not** authorize:

- implementation
- source-code changes
- test changes
- config changes
- runtime activation
- artifact generation
- replay regeneration
- default promotion

Any such work requires a separate later packet with explicit scope, gates, containment, rollback, and approval.

## Existing implementation surface carried forward

The implementation surface for this candidate already exists and is only being carried forward as a future execution surface:

- `src/core/strategy/decision_sizing.py`
  - `_apply_current_atr_selective_high_vol_multiplier`
  - application inside the existing high-vol sizing branch
- `src/core/config/schema.py`
  - `ResearchCurrentATRHighVolMultiplierOverrideConfig`
  - mounting under `multi_timeframe.research_current_atr_high_vol_multiplier_override`
- `src/core/config/authority.py`
  - whitelist support for `enabled`, `current_atr_threshold`, and `high_vol_multiplier_override`

This packet does **not** claim that those surfaces were re-verified here.
It cites them only as carried-forward implementation anchors for the later trial packet.

## Existing parity and enabled-path evidence carried forward

The following tests are carried forward as the current bounded evidence that the seam already behaves as a default-off research surface:

- `tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_absent_matches_explicit_disabled`
- `tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_replaces_high_vol_multiplier`
- `tests/governance/test_config_schema_backcompat.py::test_validate_current_atr_selective_override_absent_matches_explicit_false_leaf`

These tests are **not** re-run by this packet.
They remain carried-forward proof points that a later execution-only trial must cite and preserve.

## Carried-forward research evidence anchors

This packet relies only on already generated evidence surfaces:

- `900` dedicated validation:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
- `900` environment profile:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- `1435` policy validation:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/closeout.md`
  - `docs/governance/current_atr_1435_policy_validation_packet_2026-04-16.md`
- `900` vs `1435` handoff:
  - `docs/governance/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`
- `1435` future-boundary handoff:
  - `docs/governance/current_atr_1435_default_off_rollout_boundary_packet_2026-04-16.md`

No new evidence is produced by this packet.

## Execution-basis caveat carried forward

The cited evidence is intentionally not a single same-basis rerun:

- the `900` dedicated validation and `900` environment-profile artifacts were generated on `8e23ddb45d08784e8a8a340f83334f5842505e0e`
- the `1435` policy-validation artifacts were generated on the explicitly rebased execution basis `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`
- the docs-only boundary packet in this branch was authored later on `c9f35347fdb3c9019212478d2d7eac6939105c76`

Any later execution-only trial that runs on a newer HEAD must preserve the same rule:
if the execution basis changes, it must be described explicitly as a rebased execution basis rather than as the unchanged continuation of an older packet.

## Why `1435.209570` is the first proposed execution-only trial candidate

This packet carries forward the already stated tradeoff without collapsing it into a winner-take-all claim:

- `900` remains the stronger bounded candidate on the discovery-aligned `2024` window
- `1435.209570` remains the stronger and narrower candidate on the blind `2025` window
- `1435` remains above baseline on both windows
- `1435` is materially narrower than `900` on activation-set size

Therefore, `1435.209570` is carried forward here only as the **first proposed execution-only default-off trial candidate**.
This packet does **not** claim that `900` is obsolete, disproven, or invalid.
`900` remains the explicit tradeoff/reference candidate for any later review.

## Future execution-only boundary

If a later trial packet is opened for this candidate, that later request must satisfy all of the following:

1. default behavior remains unchanged when no explicit `1435` trial request is present
2. invocation is explicit opt-in only
3. the trial is `1435`-only; no combined `900` + `1435` trial is admissible in the same slice
4. the later trial is execution-only as a starting assumption, using the already existing seam
5. no widening beyond the already validated `1435` seam is admissible
6. any ambiguous, mixed, or partially widened state must fail closed

This packet does **not** authorize opening that trial now.
It defines only the future execution boundary.

## Hard stop and reopen rule

The later default-off trial is execution-only as the default assumption.
If that later work reveals any need to edit:

- `src/**`
- `tests/**`
- `config/**`
- `tmp/**`
- any other implementation or execution surface

then the work must stop immediately and reopen as a separate implementation packet with new governance review.

No future slice may silently absorb a “small code fix” under this precode boundary.

## Future minimum trial evidence requirements

If a later packet ever opens execution for this candidate, future evidence must record at minimum:

- exact git SHA used for that later trial
- carried-forward citations to the implementation anchors listed above
- carried-forward citations to the existing parity and enabled-path tests listed above
- proof that default behavior remains unchanged when the `1435` trial is absent
- proof that the enabled trial remains confined to:
  - `multi_timeframe.research_current_atr_high_vol_multiplier_override.enabled = true`
  - `multi_timeframe.research_current_atr_high_vol_multiplier_override.current_atr_threshold = 1435.209570`
  - `multi_timeframe.research_current_atr_high_vol_multiplier_override.high_vol_multiplier_override = 1.0`
- containment rules for any generated outputs
- explicit tradeoff language that `1435` is being trialed first for boundedness/blind-window reasons, not because `900` was disproven

These are future evidence requirements only.
This packet does **not** authorize generating such evidence now.

## What a later trial packet must still decide

This precode packet is intentionally incomplete.
A later execution-only trial packet must still decide, explicitly and separately:

- exact commands/selectors
- exact generated output set
- containment rules
- rollback rules
- gate outcomes required for success/failure
- whether existing tests are merely cited or also re-run as part of that later slice

No such execution lane is opened by this packet itself.

## Bottom line

This packet defines a docs-only precode boundary in which:

- the `current_atr` seam is recognized as already implemented
- existing parity/enabled-path tests are carried forward rather than re-verified here
- `1435.209570` is the first proposed execution-only default-off trial candidate
- `900` remains the explicit tradeoff/reference candidate
- any need for code/config/test changes forces a stop and reopen under a separate implementation packet

This packet defines the admissible next execution question.
It does not run it.
