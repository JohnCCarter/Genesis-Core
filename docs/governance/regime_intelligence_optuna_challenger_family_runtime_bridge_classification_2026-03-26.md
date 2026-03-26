# Regime Intelligence challenger family — runtime bridge classification

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `classification-only / bridge-input disposition / no promotion scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet classifies the newly created runtime bridge artifact and constrains what claims may be made from its execution result, but does not approve promotion, writeback, runtime/default change, or a new comparison contract
- **Required Path:** `Quick`
- **Objective:** Formally classify the slice8 runtime bridge artifact, decide whether it is execution-proof only or also a legitimate comparison/readiness input, and lock the allowed claim surface.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `e8d8511a`

### Scope

- **Scope IN:** docs-only classification of `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`; explicit relation to raw slice8; explicit disposition of comparison/readiness eligibility; explicit allowed and disallowed claims from the bridge run.
- **Scope OUT:** no source-code changes, no config authority changes, no champion changes, no promotion/writeback work, no new evidence class, no new runtime surface implementation, no comparison execution approval, no readiness opening.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_runtime_bridge_classification_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- every conclusion must remain bridge-specific
- no sentence may imply raw slice8 is directly runnable unchanged
- no sentence may imply the bridge file is automatically valid for the existing raw-slice8 comparison lane
- no sentence may imply readiness, promotion, or writeback eligibility
- no sentence may imply this packet creates a new general runtime-materialization contract

### Stop Conditions

- any wording that equates bridge execution with raw-slice8 direct runtime validity
- any wording that upgrades the bridge file into a comparison-eligible input for the existing raw-slice8 lane
- any wording that upgrades the bridge file into readiness-eligible input
- any wording that implies promotion-readiness, promotion approval, or writeback authority
- any wording that generalizes this packet into a repository-wide RI runtime contract

### Output required

- reviewable bridge-classification packet
- explicit artifact classification label
- explicit input-eligibility disposition
- explicit bridge-to-raw relation statement
- explicit allowed-claims matrix

## Purpose

This packet answers only the following narrow questions about the runtime bridge artifact:

- what kind of artifact it is
- how it relates to raw slice8
- whether it is a legitimate comparison/readiness input or only execution-proof
- which claims are allowed and disallowed from its successful runtime validation and backtest run

This packet does **not**:

- reopen promotion work
- reopen readiness work
- reopen the raw-slice8 comparison lane
- create a new RI canonical materialization contract for general use
- approve a new execution lane by itself

## Artifact under review

The artifact classified by this packet is:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

This artifact was created as a backtest-only candidate artifact after the previously verified runtime failures for raw slice8 materialization paths.

## Governing and technical basis

This classification is grounded in the following tracked basis:

- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`

Already verified technical facts carried into this packet:

1. raw slice8 `trial_001` merged config fails runtime validation with:
   - `invalid_strategy_family:legacy_regime_module`
2. forcing top-level `strategy_family=ri` on the raw slice8 merged config still fails runtime validation with:
   - `invalid_strategy_family:ri_requires_canonical_gates`
3. the bridge file passes runtime validation and executes through `scripts/run/run_backtest.py` with non-zero trades
4. the bridge file changes family-defining fields relative to raw slice8, including:
   - top-level family identity
   - gate tuple
   - threshold surface

## Decision labels

This packet records two decision labels.

### Artifact classification label

- `CLASSIFIED — derived runtime representation of raw slice8`

### Input-eligibility label

- `EXECUTION-PROOF ONLY — not comparison-eligible in the existing raw-slice8 lane; not readiness-eligible`

## What the bridge artifact is

The bridge artifact is classified as:

- a **derived runtime representation** of raw slice8

More specifically, it is a runtime-valid RI candidate artifact produced by **canonicalization / transformation** of family-defining RI runtime fields so that the artifact can pass current runtime validators and execute through `run_backtest.py`.

## What the bridge artifact is not

The bridge artifact is **not** classified as:

- raw slice8 itself
- a no-change serialization of raw slice8
- a proof that raw slice8 is directly runnable unchanged
- a same-head comparison input for the already-defined raw-slice8 comparison lane
- a readiness-eligible input
- a promotion-eligible artifact

## Exact relationship to raw slice8

The bridge artifact stands in the following relation to raw slice8.

### 1. It is derived, not identical

The bridge file is derived from the slice8 research artifact lineage, but it is not identical to the raw slice8 runtime shape.

### 2. It uses canonicalization / transformation of family-defining fields

The bridge file modifies family-defining fields that matter to runtime-family validation, including at minimum:

- top-level `strategy_family`
- RI runtime gate tuple
- RI threshold surface

This means the bridge artifact is not simply a packaging cleanup.

It is a material runtime-valid transformation.

### 3. It preserves some slice8-adjacent execution settings where possible

The bridge file preserves or carries forward some slice8/slice8-adjacent execution settings where that remains compatible with runtime validity.

That carry-forward does **not** erase the fact that the bridge is still a derived runtime representation rather than raw slice8 itself.

## Comparison/readiness disposition

This packet answers the three key eligibility questions explicitly.

### 1. Is the bridge file only runtime-validation / execution proof?

**Yes.**

Within the current governed state, the bridge file is legitimate as:

- runtime-validation proof that a runtime-valid RI artifact can be constructed and executed under current runtime semantics
- execution-proof that `RI is runnable`

### 2. Is the bridge file a comparison-eligible candidate input?

**No, not for the existing raw-slice8 comparison lane.**

Reason:

- the existing comparison lane is already defined as raw-slice8-specific and non-runtime
- the bridge file is a derived runtime representation, not raw slice8
- using it as a comparison input in that existing lane would silently replace the governed comparison subject

Therefore the bridge file is:

- **not comparison-eligible within the existing raw-slice8 comparison lane**

Any future derived-artifact comparison would require a separate governance opening.

### 3. Is the bridge file a readiness-eligible input?

**No.**

The bridge file is not readiness-eligible by this packet because successful runtime execution of a derived bridge artifact does not by itself answer:

- whether raw slice8 is directly runnable unchanged
- whether the governed comparison subject has been validly compared on a sanctioned lane
- whether promotion-readiness criteria are satisfied

## What the successful bridge run proves

The successful bridge run proves only the following bounded claim set.

### Allowed claim 1

- `RI is runnable under a runtime-valid canonical RI surface.`

### Allowed claim 2

- `A derived runtime-valid representation can be constructed from the slice8 line and executed without runtime-family validation errors.`

### Allowed claim 3

- `The current runtime validators admit the bridge artifact as family-consistent RI.`

## What the successful bridge run does not prove

The successful bridge run does **not** prove any of the following.

### Disallowed claim 1

- `raw slice8 is directly runnable unchanged`

### Disallowed claim 2

- `the existing raw-slice8 comparison lane can now switch from non-runtime to runtime`

### Disallowed claim 3

- `the bridge artifact is automatically comparison-eligible against the incumbent in the already-defined raw lane`

### Disallowed claim 4

- `the bridge artifact is readiness-eligible`

### Disallowed claim 5

- `promotion-ready`

### Disallowed claim 6

- `a general new RI runtime-materialization contract now exists`

## Why comparison eligibility is denied here

Comparison eligibility is denied in this packet for one narrow reason:

- the bridge artifact is not the same governed subject as raw slice8

The existing raw-slice8 comparison lane was already locked to a specific subject and a specific non-runtime surface.

Substituting a runtime-canonicalized derived representation into that lane would change:

- what is being compared, and
- what claims the comparison result would actually support

That subject-change cannot be smuggled in through bridge classification wording.

## Why readiness eligibility is denied here

Readiness eligibility is denied here because the bridge run establishes only execution proof.

It does not by itself establish:

- sanctioned same-head comparability
- raw-slice8 direct runtime admissibility
- promotion-grade evidence sufficiency
- promotion-readiness

## Claim matrix

| Claim                                                                 | Allowed? | Why                                                                                                   |
| --------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| `RI is runnable`                                                      | Yes      | The bridge artifact passes runtime validation and executes successfully as RI.                        |
| `raw slice8 is directly runnable`                                     | No       | The bridge is a derived runtime representation, not raw slice8 unchanged.                           |
| `bridge file is execution-proof`                                      | Yes      | This is the narrow purpose actually demonstrated by the bridge run.                                  |
| `bridge file is comparison-eligible in the current raw-slice8 lane`   | No       | The current lane is raw-slice8-specific and non-runtime; bridge substitution would change the subject. |
| `bridge file is readiness-eligible input`                             | No       | Execution proof alone is not readiness proof.                                                        |
| `promotion-ready`                                                     | No       | Promotion was not opened and no promotion-grade sufficiency is established here.                     |

## Explicit non-generalization boundary

This packet classifies only this specific bridge artifact case.

It does **not** establish:

- a new general evidence class
- a new general RI promotion path
- a new general runtime-materialization contract
- a repository-wide rule that any RI research artifact may be canonically transformed into a comparison-ready runtime artifact

## Next allowed step

The next allowed step after this packet, if any, remains separate from promotion and separate from the already-defined raw-slice8 comparison lane.

A future packet could, if explicitly desired, ask a new narrow question about whether a **derived runtime representation lane** should exist.

That question is not opened or answered here.

## Bottom line

The bridge file is now formally classified as:

- a **derived runtime representation** of raw slice8
- legitimate as **execution-proof only**

It supports the bounded claim:

- `RI is runnable`

It does **not** support the claims:

- `raw slice8 is directly runnable`
- `comparison-eligible in the existing raw-slice8 lane`
- `readiness-eligible`
- `promotion-ready`

That is the full governed meaning of the bridge artifact in the current tracked state.
