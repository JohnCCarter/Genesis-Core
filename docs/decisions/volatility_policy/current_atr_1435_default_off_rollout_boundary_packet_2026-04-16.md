# current_atr 1435 default-off rollout boundary packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows a future rollout discussion to one candidate and therefore carries wording-drift risk even though it remains docs-only and creates no runtime authority.
- **Required Path:** `Quick`
- **Objective:** Define the future admissibility boundary for a later, separate default-off rollout packet that may trial `current_atr >= 1435.209570`, without authorizing implementation, activation, artifact generation, or default/config changes now.
- **Candidate:** `future current_atr 1435 default-off rollout boundary`
- **Base SHA:** `f9a0b9cbbab78bc58952cc4f110e940bcd394ddc`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; carried-forward citations to the existing `900`, `900`-environment, `1435`, and `900-vs-1435` evidence surfaces; one explicit future admissibility boundary for a later `1435` default-off trial; one explicit non-authorization boundary; one future minimum-evidence checklist phrased as future requirement only.
- **Scope OUT:** no source-code changes; no tests; no runtime/config/result changes; no implementation of a rollout surface; no rollout activation; no artifact regeneration; no edits under `src/**`, `tests/**`, `tmp/**`, `results/**`, or `config/**`; no default/runtime/config-authority changes; no widening of the validated seam; no claim that `1435` is universally superior to `900`.
- **Expected changed files:** `docs/decisions/volatility_policy/current_atr_1435_default_off_rollout_boundary_packet_2026-04-16.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- `pre-commit run --files docs/decisions/volatility_policy/current_atr_1435_default_off_rollout_boundary_packet_2026-04-16.md`
- manual wording audit that the packet remains non-authorizing
- manual wording audit that `1435` is described as a future proposed default-off trial candidate only
- manual wording audit that the tradeoff against `900` remains explicit and unchanged
- manual wording audit that the mixed execution-basis caveat is preserved

### Stop Conditions

- any wording that authorizes implementation, rollout activation, runtime readiness, or default/config change now
- any wording that treats `1435` as universally superior to `900`
- any wording that hides the rebased execution-basis caveat for the `1435` packeted evidence
- any need to edit `src/**`, `tests/**`, `tmp/**`, `results/**`, or `config/**`
- any attempt to define a launchable lane without a later separate packet for implementation surface, selectors, gates, containment, and rollback

### Output required

- one reviewable docs-only default-off rollout boundary packet for `1435`
- one explicit statement that a later packet is still required for implementation, execution, and rollback design

### Skill Usage

- No repo-local execution skill is invoked for this slice.
- This is a docs-only governance boundary packet using existing evidence surfaces and wording discipline only.

## What this packet is

This packet is documentation-only and research-only.
It proposes `1435.209570` as the **first future default-off trial candidate** for a later, separate implementation packet.

It does **not** authorize:

- implementation
- rollout activation
- runtime readiness
- default/config change
- artifact generation
- replay regeneration
- promotion over `900` as a universal winner

Any such work requires a separate later packet with explicit scope, selectors, gates, containment, rollback, and approval.

## Carried-forward evidence anchors

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
  - `docs/decisions/volatility_policy/current_atr_1435_policy_validation_packet_2026-04-16.md`
- carried-forward comparison handoff:
  - `docs/decisions/volatility_policy/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`

No new replay, no new artifact, and no new code/config evidence is created by this packet.

## Execution-basis caveat

The carried-forward evidence is intentionally **not** a single same-basis rerun:

- the `900` dedicated validation and `900` environment-profile artifacts were generated on `8e23ddb45d08784e8a8a340f83334f5842505e0e`
- the `1435` policy-validation artifacts were generated on the explicitly rebased execution basis `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`
- the docs-only handoff commit `f9a0b9cbbab78bc58952cc4f110e940bcd394ddc` preserved that distinction and did not regenerate replay outputs

Nothing in this packet may be read as proof of a fresh unified rerun across those evidence surfaces.

## Why `1435.209570` is the first future proposed trial candidate

This packet carries forward the already stated tradeoff, without claiming universal dominance:

- `900` remains the stronger bounded candidate on the discovery-aligned `2024` window
- `1435.209570` remains the stronger and narrower candidate on the blind `2025` window
- `1435` stays above baseline on both windows
- `1435` is materially narrower than `900` on activation-set size
- `1435` was already recommended in the dedicated policy-validation closeout as a narrower research candidate for later discussion

Therefore, this packet identifies `1435.209570` only as the **first future bounded candidate** for a later default-off trial discussion.
It does **not** claim that `900` is obsolete, invalid, or disproven.
`900` remains the explicit tradeoff/reference candidate carried forward in any later discussion.

## Future invocation boundary

If a later implementation packet is ever opened for this candidate, that later request must satisfy all of the following:

1. default behavior remains unchanged when no explicit `1435` trial request is present
2. invocation is explicit opt-in only
3. only one candidate may be trialed in that packet: `1435.209570`
4. no combined or dual-candidate `900` + `1435` rollout is admissible in the same implementation slice
5. no widening beyond the already validated `1435` sizing seam is admissible
6. no adjacent compensation edits are admissible
7. any ambiguous, mixed, or partially widened state must fail closed

This packet does **not** authorize implementing such an invocation surface now.
It fixes only the future admissibility boundary.

## Future effective-diff boundary

Any later implementation packet must keep the effective behavioral delta confined to the already validated research seam represented by the `1435` candidate evidence:

- `multi_timeframe.research_current_atr_high_vol_multiplier_override.enabled = true`
- `multi_timeframe.research_current_atr_high_vol_multiplier_override.current_atr_threshold = 1435.209570`
- `multi_timeframe.research_current_atr_high_vol_multiplier_override.high_vol_multiplier_override = 1.0`

No later packet may use this boundary as permission to:

- reopen threshold mining
- add a broader volatility policy family
- change unrelated sizing gates
- stack a second intervention into the same rollout slice
- compensate with adjacent config edits outside the exact bounded seam

This packet does **not** authorize producing such diffs now.
It fixes only the future bounded-diff rule.

## Future minimum evidence requirements

If a later packet ever opens implementation or execution for this candidate, future evidence must record at minimum:

- exact git SHA used for the implementation packet
- carried-forward citations to the `900` validation, `900` environment profile, `1435` validation, and `900-vs-1435` handoff
- proof that default behavior is unchanged when the `1435` trial is absent
- proof that the enabled trial remains confined to the exact bounded seam above
- exact gates/selectors used by that later packet
- containment/rollback rules defined by that later packet
- explicit tradeoff language that `1435` is being trialed first for boundedness/blind-window reasons, not because `900` was disproven

These are future minimum evidence requirements only.
This packet does **not** authorize producing evidence or artifacts now.

## What a later packet must still decide

This boundary packet is intentionally incomplete by design.
A later implementation packet must still decide, explicitly and separately:

- implementation surface
- selectors and test scope
- gates and pass criteria
- containment rules
- rollback rules
- any runtime-flag/config exposure details

No such implementation lane is opened by this packet itself.

## Bottom line

This packet defines a docs-only future boundary in which:

- `1435.209570` is the first **proposed** future default-off trial candidate
- `900` remains an explicit tradeoff/reference candidate
- the mixed execution-basis caveat is preserved
- no implementation, activation, or default change is authorized now
- any later rollout trial still requires a separate packet with explicit implementation and rollback discipline

This packet defines the next bounded question.
It does not answer it in runtime.
