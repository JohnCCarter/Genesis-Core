# Feature Attribution v1 — Phase 7 determinism-contract-test packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase7-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `HIGH` — why: future gate bundles can easily drift into hidden execution-readiness or approval authority if not explicitly constrained.
- **Required Path:** `Quick`
- **Objective:** Define the future prerequisite determinism and contract-test bundle for Feature Attribution v1 without authorizing execution, approval, readiness, or golden-value semantics.
- **Candidate:** `future Feature Attribution v1 prerequisite gate bundle`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; future prerequisite gate families; future selector references; skill-spec anchors; explicit necessary-not-sufficient clause; conditional gate inclusion rules; explicit non-readiness and non-approval boundary.
- **Scope OUT:** no source-code changes; no tests run; no command definitions; no readiness approval; no golden-value thresholds; no PASS authority; no runtime/config/result changes; no fib reopening.
- **Expected changed files:** `docs/decisions/feature_attribution_v1_phase7_determinism_contract_test_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against controlling Phase 2 through Phase 6 packets
- manual wording audit that the bundle remains prerequisite-only
- manual wording audit that no gate passing is treated as approval or readiness by itself

For interpretation discipline inside this packet:

- neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes execution, approval, or readiness
- any future gate bundle named here is necessary but not sufficient
- conditional selectors remain conditional and must not be treated as always-on without a later execution packet
- skill citations are SPEC anchors only and not substitutes for invariance gates

### Stop Conditions

- any wording that equates green gates with execution approval
- any wording that defines golden-value thresholds or acceptance scores here
- any wording that allows skill execution to replace determinism or invariance tests
- any wording that imports runtime authority by reference from test or skill names

### Output required

- one reviewable Phase 7 RESEARCH determinism-contract-test packet
- one prerequisite-only gate bundle
- one necessary-not-sufficient clause
- one conditional-selector rule set

## What this packet is

This packet is docs-only, research-only, and non-authorizing.
Neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes execution, approval, readiness, implementation, or follow-on action.

Any future gate bundle defined here is a prerequisite set only.
Passing those future gates does not authorize execution, review approval, promotion, or follow-on implementation.

## Inherited controlling packets

This packet inherits and does not weaken all prior Feature Attribution v1 governance packets from Phase 0 through Phase 6.

## Future prerequisite gate families

If a later packet ever opens execution, the future prerequisite gate bundle must name at minimum the following gate families:

- determinism replay
- pipeline invariant
- config-authority contract stability
- selected-unit diff-scope validation
- artifact-integrity validation if retained artifacts are later authorized
- feature parity validation only when the selected unit touches feature computation surfaces

## Named repository anchors

The following tracked repository surfaces are the current named anchors for those future gate families:

- `tests/backtest/test_backtest_determinism_smoke.py` — determinism replay anchor
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` — pipeline invariant anchor
- `tests/governance/test_config_authority_hash_contract.py` — config-authority contract anchor
- `.github/skills/feature_parity_check.json` — conditional feature-parity spec anchor
- `.github/skills/ri_off_parity_artifact_check.json` — conditional artifact-integrity spec anchor
- `.github/skills/backtest_run.json` — execution-discipline spec anchor only

These names are future prerequisite anchors only.
They do not authorize running any test or skill now.
They do not import approval semantics by reference.

## Conditional selector rules

Future gate selection must remain conditional as follows:

- determinism replay and pipeline invariant are always prerequisite candidates for any later execution packet
- config-authority contract stability is required whenever effective-config projection or diff proof is part of the future request
- feature parity selectors are required only if the selected row touches feature computation surfaces
- artifact-integrity selectors are required only if a later packet separately authorizes retained artifacts or comparator outputs

This packet does not decide those conditions for any concrete row now.
It freezes only how a later execution packet must reason about them.

## No golden-threshold rule

This packet defines no golden values, no scalar acceptance thresholds, no PASS scoring model, and no auto-approval logic.

A later packet may only freeze such values, if ever needed, by explicitly reopening this boundary.

## No substitution rule

No future skill invocation may substitute for:

- determinism replay
- pipeline invariance
- config-authority checks
- explicitly named contract tests

Skills remain supplemental SPEC anchors only.

## Bottom line

Phase 7 freezes the future prerequisite gate bundle for Feature Attribution v1 by stating that:

- gate families are named in advance
- selectors and skills remain prerequisite anchors only
- some selectors are conditional rather than always-on
- passing future gates would be necessary but not sufficient
- no readiness, approval, or PASS authority is created

This packet names future prerequisites.
It does not approve a gate result.
