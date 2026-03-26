# Regime Intelligence challenger family — blocker resolution packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `resolution-only / blocker semantics defined / no promotion contract opened`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet resolves blocker semantics for the slice8 comparison line, but it does not approve runtime comparison, promotion, or writeback
- **Required Path:** `Quick`
- **Objective:** Resolve the remaining blocker semantics after the governed promotion-readiness stop-state without opening a promotion-decision contract.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `9e38586d`

### Scope

- **Scope IN:** docs-only resolution of four slice8-specific blocker questions: runtime-materialization legitimacy, metadata-quirk disposition, sanctioned family identity, and writeback-authority scope.
- **Scope OUT:** no source-code changes, no config changes, no tests, no runtime materialization approval, no promotion-decision packet opening, no promotion approval, no writeback approval, no runtime/default change, no new canonical comparison/materialization contract.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_blocker_resolution_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- all conclusions must remain slice8-specific
- all conclusions must remain non-runtime and non-canonical
- all conclusions must remain non-promotion-authorizing
- the next allowed step must remain below promotion-decision contract opening

### Stop Conditions

- any wording that authorizes runtime comparison for slice8
- any wording that treats non-runtime comparison evidence as automatically promotion-grade
- any wording that turns `merged_config.strategy_family=legacy` into the sanctioned identity for comparison reasoning
- any wording that opens writeback or champion replacement authority
- any wording that opens a promotion-decision contract

### Output required

- reviewable blocker-resolution packet
- explicit resolutions for the four blocker questions
- explicit next allowed step
- explicit non-authorization boundary

## This packet does not open promotion

This packet does **not** approve:

- runtime comparison
- promotion-readiness approval
- a promotion-decision packet
- promotion
- champion replacement
- champion writeback
- runtime/default change
- a canonical RI comparison/materialization contract

Its only job is to resolve blocker semantics for the current slice8 comparison line.

## Governing stop-state and upstream basis

This packet treats the following stop-state as valid and carried forward:

- `docs/governance/regime_intelligence_optuna_challenger_family_promotion_readiness_assessment_2026-03-26.md`

Relevant tracked upstream chain:

- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_non_runtime_comparison_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_promotion_readiness_opening_decision_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_promotion_readiness_assessment_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`

## Resolution summary

This packet resolves the four open blocker questions as follows:

1. **Slice8 runtime materialization is not currently a legitimate comparison surface** for the governed slice8-vs-incumbent line.
2. **`merged_config.strategy_family=legacy` is dispositioned as disclosed artifact-local metadata quirk only**.
3. **The sanctioned family identity for comparison reasoning is the governed slice8 candidate identity, not the trial artifact's `merged_config.strategy_family` field**.
4. **Writeback authority is not required for this blocker-resolution layer or comparison-only reasoning, but remains required for any future promotion execution or champion update**.

All four conclusions are:

- slice8-specific
- non-runtime
- non-canonical
- non-promotion-authorizing

## Decision 1 — runtime materialization legitimacy

### Decision

For the current governed slice8-vs-incumbent comparison line, **slice8 runtime materialization is not currently a legitimate comparison surface at all**.

### Why

The blocker summary already recorded two attempted local materialization paths and two verified runtime failures:

- `invalid_strategy_family:legacy_regime_module`
- `invalid_strategy_family:ri_requires_canonical_gates`

The downstream comparison-input surface decision then selected the non-runtime path rather than a runtime or sanctioned-canonical-materialization path.

The non-runtime surface packet later made that decision concrete by explicitly authorizing only the slice8-specific governed artifact-matrix surface.

### Boundaries

This decision means:

- no local runtime materialization path is currently sanctioned for the slice8 comparison line
- no runtime-config comparison surface may be treated as legitimate merely because a local override was attempted
- no future runtime comparison path may be inferred from this packet

This decision does **not** mean:

- runtime materialization can never be revisited in some later separately governed path
- the RI family identity is rejected
- the non-runtime comparison result is invalid

## Decision 2 — metadata quirk disposition

### Decision

The field:

- `merged_config.strategy_family=legacy`

is hereby dispositioned as **disclosed artifact-local metadata quirk only** for the current slice8 comparison line.

### Why

That field appears in candidate-adjacent trial artifacts, but it conflicts with the governed slice8 candidate identity already carried by the slice8 YAML and candidate-definition chain.

Treating it as authoritative would collapse the governed comparison into a trial-artifact packaging anomaly rather than the already tracked slice8 candidate surface.

### Consequence of this disposition

For the current slice8 line, the metadata quirk:

- must remain disclosed
- must not be hidden or silently normalized
- must not be treated as the sanctioned family identity
- must not be used as authority source for comparison reasoning
- remains unresolved for any later promotion-grade reasoning until technically or governantly dispositioned again

### Boundary

This disposition is narrow.

It is enough for blocker semantics and comparison-only reasoning.

It is **not** enough by itself to clear promotion readiness.

## Decision 3 — sanctioned family identity

### Decision

The sanctioned family identity for comparison reasoning on this slice8 line is:

- `strategy_family=ri`
- `multi_timeframe.regime_intelligence.enabled=true`
- `multi_timeframe.regime_intelligence.version=v2`
- `multi_timeframe.regime_intelligence.authority_mode=regime_module`

This identity is carried by the governed slice8 candidate chain, not by the trial artifact's `merged_config.strategy_family` field.

### Why

The candidate-definition packet already names slice8 as the lead RI research candidate with its fixed family identity carried by the slice8 YAML and governing packet chain.

The non-runtime comparison surface and summary also already treat the candidate as the slice8 RI line rather than as a `legacy` family winner.

### Boundary

This sanctioned identity applies:

- only to the current slice8 comparison line
- only for governed comparison reasoning on the approved non-runtime surface

It does **not** create:

- a new repository-wide canonical RI comparison contract
- a runtime-materialization approval
- a general reinterpretation rule for every future artifact carrying `merged_config.strategy_family`

## Decision 4 — writeback authority scope

### Decision

Writeback authority is **not required** for:

- this blocker-resolution packet
- maintaining the current governed stop-state
- comparison-only reasoning on the already approved non-runtime surface

Writeback authority **is required** for:

- any future promotion execution
- any champion update
- any writeback into `config/strategy/champions/tBTCUSD_3h.json`

### Why this is narrow

This decision does **not** say that promotion-grade reasoning is already open.

It says only that blocker-resolution semantics and comparison-only reasoning can exist without writeback authority.

That is different from saying promotion can proceed without it.

### Boundary

This packet gives:

- no writeback authority
- no champion replacement authority
- no promotion-decision contract

## What these resolutions do and do not unlock

### They do unlock

- a cleaner governed interpretation of the current stop-state
- explicit separation between artifact-local metadata noise and sanctioned slice8 family identity
- explicit separation between comparison-only reasoning and later writeback authority

### They do not unlock

- runtime comparison
- promotion-decision packet opening
- promotion readiness approval
- promotion execution
- champion replacement

## Next allowed step

The next allowed step after this packet is still **not** a promotion-decision packet.

The next allowed step is one of the following narrow options:

1. a separate packet that determines whether the now-resolved blocker semantics are sufficient to narrow the remaining readiness blockers further, or
2. a separate packet that dispositions whether any additional supplementary non-runtime evidence is required before promotion-decision readiness can be reconsidered.

## Bottom line

This packet resolves the blocker semantics without widening authority.

Its key result is:

- the sanctioned slice8 comparison surface remains non-runtime,
- the `merged_config.strategy_family=legacy` field is treated as disclosed artifact-local metadata quirk only,
- the sanctioned family identity for comparison reasoning remains the governed RI slice8 identity,
- and writeback authority remains unnecessary for blocker-resolution semantics but mandatory for any later promotion execution.

That is the farthest this packet goes.

It does **not** open a promotion decision contract.
