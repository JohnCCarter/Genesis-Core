# Compatibility Delta — Pre-Fib Candidate Boundary

## 1. Scope Definition

This document answers one narrow compatibility question only:

- whether the locked **pre-fib marginal candidate-boundary** surface would be structurally compatible, invariant-safe, and governance-admissible **if introduced** into Genesis-Core.

Locked input finding carried into this document without re-evaluation:

- surface: **pre-fib candidate-boundary**
- cohort: **near-threshold cohort**
- carrier: **slice-2 replay carrier (`tBTCUSD 3h`, `2023/2024`)**
- causal anchor: **`raw_authoritative_branch_output`**
- locked finding status:
  - candidate-level divergence: **YES**
  - adjudicable divergence: **YES**
  - binding behavior: **YES**
  - `raw_authoritative_branch_output`: **`causally_active_on_this_replay_surface`**

This document treats those findings as already locked.
It does **not** re-run, extend, validate, or challenge them.

Explicitly out of scope:

- uplift discussion
- performance claims
- parameter selection
- implementation plan
- config ideas
- design proposals
- runtime or architecture changes

## 2. System Mapping (Observed vs Hypothetical)

### Candidate formation layer

**Observed (current system)**

- The bounded upstream chain is already documented as pre-fib and ends at `decision_gates.select_candidate(...)`.
- Existing diagnostics record candidate/no-candidate and direction divergence at the pre-fib boundary on the fixed `tBTCUSD 3h` slice8 research surface.
- Current tracked analysis therefore already recognizes a pre-fib candidate boundary as a meaningful observation layer in the system.

**Hypothetical (if introduced)**

- The surface would conceptually interact at the same pre-fib candidate-boundary layer.
- Its hypothetical role would be to influence the near-threshold cohort before fib/post-fib/sizing enter the path.
- No further mapping is asserted here beyond that boundary placement.

### Regime / authority flow

**Observed (current system)**

- Current governance artifacts map the pre-fib chain as `authority_mode_resolver -> evaluate -> prob_model -> decision_gates.select_candidate(...)`.
- Existing research diagnostics also record authority/calibration propagation before candidate formation.
- The current system therefore already has an observed regime/authority flow upstream of the candidate boundary.

**Hypothetical (if introduced)**

- The locked causal anchor `raw_authoritative_branch_output` would conceptually interact inside that same authority/regime flow.
- The hypothetical interaction point would be upstream of fib and downstream of authority resolution, because the surface is defined as pre-fib and candidate-boundary-oriented.
- No code location, design shape, or implementation mechanism is proposed here.

### Decision boundary

**Observed (current system)**

- `decision_gates.select_candidate(...)` is already documented as the final pre-fib decision boundary.
- Existing slice definitions treat threshold-pass state, candidate/no-candidate state, and direction/no-direction outcome as the relevant pre-fib decision outputs.
- The current system therefore already contains an observed decision boundary where pre-fib divergence can be adjudicated.

**Hypothetical (if introduced)**

- The surface would conceptually interact at that same near-threshold decision boundary.
- The hypothetical interaction would remain pre-fib and candidate-boundary-scoped.
- No claim is made here about how such interaction would be encoded or implemented.

## 3. Invariant Check

| Invariant                              | Classification                              | Minimal basis                                                                                                                                                                                                                                                                                                          |
| -------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Determinism (same input → same output) | **unclear (requires future investigation)** | Genesis-Core explicitly guards determinism at both governance and test level. Because the locked surface is causally active at the candidate boundary, determinism compatibility cannot be established from the locked finding alone without knowing its concrete representation.                                      |
| No lookahead bias                      | **compatible**                              | The locked surface is defined on a replay carrier and a pre-fib candidate boundary, not on downstream performance interpretation. Existing repository rules explicitly require no lookahead and forbid using HTF context without `reference_ts`. The locked finding does not by itself imply a future-data dependency. |
| As-of semantics                        | **compatible**                              | Existing repository rules require as-of merge discipline and reference-timestamped HTF usage. The locked surface is framed as pre-fib and authority/candidate-boundary-local rather than as a post-hoc outcome layer. No inherent as-of contradiction is visible from the locked finding alone.                        |
| Pipeline ordering stability            | **compatible**                              | The current system already documents a stable upstream ordering through authority, evaluation, probability, and candidate selection. The locked surface is framed as interacting conceptually within that existing pre-fib chain rather than implying a new external stage by itself.                                  |
| Feature cache invariance               | **unclear (requires future investigation)** | Genesis-Core treats feature cache invariance as a protected invariant. The locked finding does not specify whether introducing this surface would alter cache identity, cache keys, or materialized feature state. That compatibility cannot be established conservatively from the replay finding alone.              |

## 4. Behavioral Classification

**Classification:** `behavior-changing`

Minimal justification:

- the locked finding already states that candidate-level divergence is present,
- that divergence is adjudicable,
- that binding behavior is present, and
- that `raw_authoritative_branch_output` is causally active on the replay surface.

On that basis alone, introducing this surface would not be behavior-neutral at the pre-fib candidate boundary.
It is therefore not classifiable here as purely additive A′ evolution.

## 5. Governance Impact

Possible governance implications only:

- **new packet class?**
  - possible implication: no new class may be required if existing compatibility/admission packet shapes are sufficient.
  - possible implication: a narrower packet subtype may be needed if pre-fib candidate-boundary surfaces anchored in authority output require explicit treatment distinct from ordinary parameter-surface work.

- **extension of existing family?**
  - possible implication: yes, if the surface would be treated as part of canonical candidate formation rather than replay-only evidence.
  - possible implication: no, if the surface can be classified entirely within already governed family boundaries.

- **new admission layer?**
  - possible implication: yes, if future work would require explicit admissibility handling for authority-derived candidate-boundary surfaces.
  - possible implication: no, if current admission logic can already classify such a surface without reinterpretation.

No governance decision is made here.

## 6. Compatibility Verdict

`compatible_with_constraints`

Conservative basis:

- the locked surface maps conceptually onto already observed pre-fib authority/candidate-boundary layers in the current system,
- no direct structural contradiction is visible against no-lookahead, as-of, or pipeline-ordering rules from the locked finding alone,
- but determinism and feature-cache invariance remain unresolved at compatibility level without future investigation of concrete representation.

## 7. Open Questions (Minimal)

Only the following questions appear strictly necessary before any future step:

1. Would the surface preserve deterministic replay semantics once represented concretely at the candidate boundary?
2. Would the surface preserve existing feature-cache invariance, or would it introduce cache-identity ambiguity?
3. Would current family/admission boundaries classify this surface without reinterpretation, or would an explicit governance clarification be required?
4. Would the surface remain fully as-of safe once tied to concrete authority-output material rather than replay-only observation?
