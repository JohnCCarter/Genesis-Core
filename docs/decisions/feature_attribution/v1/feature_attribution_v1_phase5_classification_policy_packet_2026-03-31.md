# Feature Attribution v1 — Phase 5 classification-policy packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase5-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `HIGH` — why: classification language can easily drift into hidden decision, ranking, or promotion authority if not kept descriptive-only.
- **Required Path:** `Quick`
- **Objective:** Define descriptive future classification labels for one-unit-vs-locked-baseline attribution analysis without authorizing ranking, decision, promotion, runtime change, or implementation action.
- **Candidate:** `future Feature Attribution v1 descriptive label policy`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; descriptive label vocabulary; one-unit-vs-locked-baseline only; qualitative label semantics with no numeric cutoffs; invalid-state classification boundary; explicit non-authority and non-ranking clauses.
- **Scope OUT:** no source-code changes; no tests; no numeric thresholds; no comparison/promotion/cutover/family replacement authority; no ranking or leaderboard semantics; no runtime/config/result changes; no fib reopening.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase5_classification_policy_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against controlling Phase 1, Phase 2, and Phase 3 packets
- manual wording audit that labels remain descriptive only
- manual wording audit that no numeric decision cutoffs are introduced

For interpretation discipline inside this packet:

- neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes ranking, promotion, implementation, or runtime action
- labels apply only to one selected admitted Phase 1 row against the locked baseline
- labels do not imply removal, adoption, or tuning of any row
- `invalid` remains contract/provenance oriented, not a performance verdict by itself

### Stop Conditions

- any wording that introduces numeric cutoffs or hidden decision thresholds
- any wording that ranks multiple units against each other
- any wording that turns labels into implementation recommendations, runtime authority, or promotion authority
- any wording that reopens fib-derived rows or citation-only / excluded rows

### Output required

- one reviewable Phase 5 RESEARCH classification-policy packet
- one descriptive label set
- one invalid-state boundary
- one explicit non-ranking / non-authority clause

## What this packet is

This packet is docs-only, research-only, and non-authorizing.
Neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes implementation, execution, ranking, promotion, cutover, family replacement, runtime change, or artifact generation.

The labels frozen here are descriptive analysis outputs only.
They are not runtime authority, promotion authority, ranking authority, or implementation authority.

## Inherited controlling packets

This packet inherits and does not weaken:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase3_baseline_metrics_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase4_runner_boundary_packet_2026-03-31.md`

## Classification scope boundary

Any future classification under this lane must remain:

- one admitted Phase 1 row only
- one locked baseline only
- one candidate-vs-baseline comparison only
- descriptive only
- non-ranking
- non-promotional

No label in this packet may be used to:

- choose a winner across multiple rows
- justify immediate implementation
- justify runtime removal or runtime adoption
- justify promotion, cutover, or family replacement

## Descriptive label set

The only descriptive labels admitted by this packet are:

| Label          | Descriptive meaning                                                                                                                   | Explicit non-authority limit                                        |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `additive`     | the observed future evidence would describe the selected unit as contributing directional value relative to the locked baseline       | does not authorize implementation, retention, ranking, or promotion |
| `neutral`      | the observed future evidence would describe the selected unit as not showing clear directional change relative to the locked baseline | does not authorize removal, disablement, or de-prioritization       |
| `adverse`      | the observed future evidence would describe the selected unit as directionally unfavorable relative to the locked baseline            | does not authorize removal, rollback, or policy action              |
| `inconclusive` | the observed future evidence would be insufficient, mixed, or ambiguous for descriptive labeling                                      | does not authorize retries, extra runs, or threshold changes        |
| `invalid`      | the future request or evidence would violate contract, provenance, selector, or gate discipline                                       | does not act as a performance label; it is a contract label         |

## No numeric cutoff rule

This packet intentionally defines no numeric thresholds, no scalar cutoffs, no composite score, and no hidden decision rule.

If a later packet ever seeks to introduce numeric classification cutoffs, that later packet must reopen the policy boundary explicitly and separately.

## Future label-input boundary

Any future label assignment may draw only from:

- the locked minimum baseline metric set from Phase 3
- the corresponding candidate metric projection under the same labels
- the selected Phase 1 row label
- contract-validity and provenance-validity information from the controlling packet chain
- any clearly separated citation-only diagnostics that do not replace the locked minimum metric set

No label assignment may depend on:

- cross-unit leaderboards
- multi-unit bundles
- family-comparison semantics
- promotion/cutover semantics
- untracked runtime-only diagnostics

## Invalid-state boundary

`invalid` is reserved for future states such as:

- non-admitted selector use
- multiple selectors in one request
- baseline provenance failure
- effective-config diff escaping the selected row path set
- missing required gate bundle in a later approved execution slice
- unresolved evidence chain breakage

`invalid` is therefore a contract-status label, not a performance-status label.

## Bottom line

Phase 5 freezes a descriptive-only classification policy for Feature Attribution v1 by stating that:

- labels are descriptive only
- labels apply only one admitted row at a time against the locked baseline
- no numeric cutoffs are introduced
- `invalid` is a contract label, not a performance label
- no ranking, promotion, cutover, or implementation authority is created

This packet names future labels.
It does not let those labels decide anything.
