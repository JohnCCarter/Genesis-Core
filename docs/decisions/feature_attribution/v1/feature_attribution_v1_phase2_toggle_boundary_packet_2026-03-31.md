# Feature Attribution v1 — Phase 2 toggle-boundary packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase2-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet freezes future admissibility boundaries for a possible Feature Attribution v1 toggle/neutralization lane and therefore carries governance-drift risk even though it remains docs-only and non-authorizing.
- **Required Path:** `Quick`
- **Objective:** Define the future deterministic toggle/neutralization boundary for Feature Attribution v1 without authorizing implementation, execution, artifact generation, or evidence production.
- **Candidate:** `future Feature Attribution v1 toggle-boundary contract`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; inherited-lock confirmation from Phase 0 and Phase 1; exact future selector-source boundary; default-off and explicit-opt-in future invocation rule; exact effective-config diff boundary; cluster atomicity rule; illustrative fail-closed invalid-state set; future minimum evidence requirements phrased as future requirements only; analogy-only repository anchors.
- **Scope OUT:** no source-code changes; no tests; no runtime/config/result changes; no toggle implementation; no execution authority; no artifact generation authority; no schema/API/CLI/config-surface changes; no changes under `src/**`, `tests/**`, `config/**`, `results/**`, or `config/strategy/champions/**`; no fib reopening; no Phase 1 reclassification; no adoption of `src/core/strategy/components/attribution.py`.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against the controlling Phase 0 and Phase 1 packets
- manual wording audit that the packet remains non-authorizing
- manual wording audit that no selector, alias, or execution surface is newly authorized
- manual wording audit that all evidence language is phrased as a future requirement rather than a present authorization

For interpretation discipline inside this packet:

- Phase 0 and Phase 1 remain controlling
- default behavior must remain unchanged
- only admitted or admitted-cluster rows from Phase 1 may be discussed as future toggle candidates
- citation-only and excluded rows remain non-toggleable
- mixed, aliased, partial-cluster, or alternate-route proposals must fail closed

### Stop Conditions

- any wording that authorizes implementation, execution, artifact generation, evidence production, or config/runtime/schema/API changes
- any wording that creates, renames, aliases, extends, or reinterprets a Phase 1 row into a new selector namespace
- any wording that treats analogy anchors as adopted runtime logic by reference
- any wording that reopens fib-derived seams
- any wording that permits partial cluster toggling or adjacent compensation edits
- any wording that treats future evidence requirements as present artifact authority

### Output required

- one reviewable Phase 2 RESEARCH toggle-boundary packet
- one fail-closed selector-source rule tied to Phase 1 only
- one future invocation boundary for exactly one admitted Phase 1 row at a time
- one future effective-config diff boundary
- one future minimum-evidence rule set expressed as future requirement only

## What this packet is

This packet is documentation-only and research-only.
It defines future admissibility boundaries for a possible Feature Attribution v1 toggle/neutralization seam, but does **not** authorize implementation, execution, artifact generation, schema changes, config-surface changes, or evidence production.
Any such work requires a separate later packet with explicit scope, gates, selectors, and approval.

This packet freezes only the future boundary for:

- how a later request may identify a target unit
- how that later request must remain default-off and explicit-opt-in
- how that later request must constrain effective-config drift
- how mixed or ambiguous states must fail closed
- what minimum evidence fields a future request would have to retain

This packet does **not** start a toggle lane.
It only fences it.

## Inherited controlling packets

This packet inherits and does not weaken:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`

The following remain locked and unchanged:

- research-only
- additive-only
- no-default-behavior-change
- fib non-reopen
- canonical baseline anchor = `config/strategy/champions/tBTCUSD_3h.json`
- canonical baseline observational context = `tBTCUSD`, `3h`, `2023-01-01 -> 2024-12-31`
- reserved namespace only = `results/research/feature_attribution_v1/`
- citation-only and excluded rows remain non-toggleable

## Selector-source boundary

The only admissible future target selectors under this packet are the exact admitted or admitted-cluster row labels already defined in the controlling Phase 1 matrix.
This packet does **not** create, rename, extend, alias, or reinterpret any row label, selector namespace, unit identifier, or key-path set.

If a later packet ever introduces a machine-readable `unit_id`, it must remain one-to-one with an exact controlling Phase 1 row label.
No such machine-readable identifier is created here.

## Currently admissible future selector rows

The currently admissible future selector rows are exactly these Phase 1 rows and no others:

| Controlling Phase 1 row label          | Selector class | Toggle admissibility under this packet |
| -------------------------------------- | -------------- | -------------------------------------- |
| `Base entry confidence seam`           | single seam    | future-admissible                      |
| `Regime probability threshold cluster` | atomic cluster | future-admissible                      |
| `Signal-adaptation threshold cluster`  | atomic cluster | future-admissible                      |
| `Minimum-edge gate seam`               | single seam    | future-admissible                      |
| `Hysteresis gate seam`                 | single seam    | future-admissible                      |
| `Cooldown gate seam`                   | single seam    | future-admissible                      |
| `Regime sizing multiplier cluster`     | atomic cluster | future-admissible                      |
| `HTF regime sizing multiplier cluster` | atomic cluster | future-admissible                      |
| `Volatility sizing cluster`            | atomic cluster | future-admissible                      |
| `HTF block seam`                       | single seam    | future-admissible                      |
| `LTF override cluster`                 | atomic cluster | future-admissible                      |

The following are **not** future toggle candidates under this packet:

- all Phase 1 `citation-only` rows
- all Phase 1 `excluded` rows
- any newly proposed seam not already classified in Phase 1
- any alias or decomposition of an admitted cluster into leaf-level subselectors

## Future invocation boundary

For any later implementation or execution request, the invocation boundary must satisfy all of the following:

1. default behavior remains unchanged when no explicit attribution request is present
2. invocation is explicit opt-in only
3. exactly one controlling Phase 1 row label may be selected per request
4. stacked, combined, chained, or compensating selector requests are forbidden
5. citation-only rows and excluded rows must fail closed if requested
6. admitted-cluster rows are atomic and may not be partially overridden
7. alternate-route, shadow-route, wrapper-route, or POC-route substitution is forbidden

This packet does not authorize implementing such an invocation surface now.
It fixes only the future admissibility rule.

## Future effective-config diff boundary

For any future implementation or execution request, the effective-config diff must be confined to the exact Phase 1 key-path set of the selected admitted row, with admitted-cluster rows treated atomically.

This means:

- a single-seam row may alter only its exact cited Phase 1 key path
- an admitted-cluster row may alter only its exact cited Phase 1 cluster membership as a whole
- adjacent thresholds, multipliers, gates, exits, route order, or baseline config anchors must not be edited as compensation
- effective-config comparison must be performed on the effective config rather than on partial input fragments alone

This packet does **not** authorize generating such diffs or artifacts now.
It fixes only the future admissibility rule.

## Fail-closed invalid states

Invalid-state examples in this packet are illustrative and non-exhaustive.
Any ambiguous, mixed, overlapping, aliased, partially clustered, or alternate-route proposal must fail closed unless a later packet explicitly reopens and defines that boundary.

Illustrative invalid states include:

- unknown selector label
- selector label that maps to a Phase 1 `citation-only` row
- selector label that maps to a Phase 1 `excluded` row
- more than one admitted selector requested in the same run
- partial leaf override of an admitted cluster
- target-selector change plus adjacent non-target config edits
- selector aliasing or row-label reinterpretation
- alternate-route substitution using a wrapper, shadow path, or `src/core/strategy/components/attribution.py`
- baseline anchor mutation under `config/strategy/champions/tBTCUSD_3h.json`

## Future minimum evidence requirements

If a later packet ever opens implementation or execution, future evidence must record at minimum:

- baseline git SHA
- controlling Phase 0 packet path
- controlling Phase 1 packet path
- controlling Phase 2 packet path
- selected exact Phase 1 row label
- selected exact Phase 1 key-path set
- effective-config fingerprints for baseline and candidate
- an effective-config diff report limited to the selected path set
- result artifact references and any comparison artifact references required by the later packet

These are future minimum evidence requirements only.
This packet does **not** authorize producing evidence or artifacts now.
It does not define a final artifact schema or manifest format.

## Analogy-only repository anchors

Repository references in this packet are analogy-only anchors.
They are cited to illustrate patterns of explicit opt-in, fail-closed rejection, diff discipline, and matrix-style evidence, but their runtime logic, APIs, comparison semantics, and implementation details are **not** adopted by reference into Feature Attribution v1 by this packet.

Analogy-only anchors:

- `tests/backtest/test_run_backtest_mode_flags.py` — explicit opt-in and fail-closed mixed-state discipline
- `src/core/utils/diffing/config_equivalence.py` — exact effective-config diff discipline
- `docs/analysis/regime_intelligence/core/regime_intelligence_parity_artifact_matrix_2026-03-17.md` — matrix-style evidence discipline
- `src/core/decision/comparison.py` — cautionary reminder that comparison/promotion logic exists elsewhere and is not imported into this lane

## Explicit preservation of non-reopen boundaries

Nothing in this packet reopens:

- fib-derived entry seams
- citation-only rows
- excluded rows
- composable attribution POC adoption
- comparison/promotion/readiness logic
- champion mutation or promotion authority

Any later packet that seeks to reopen any of the above must do so explicitly and separately.

## Bottom line

Phase 2 now freezes a docs-only future toggle boundary for Feature Attribution v1 by stating that:

- only exact admitted Phase 1 row labels may ever become future selectors
- future invocation must be explicit opt-in and one-row-at-a-time
- admitted clusters are atomic
- effective-config drift must stay inside the selected Phase 1 path set
- mixed or ambiguous states must fail closed
- evidence language is future-facing only
- analogy anchors are not adopted by reference

This packet defines the fence.
It does not open the gate.
