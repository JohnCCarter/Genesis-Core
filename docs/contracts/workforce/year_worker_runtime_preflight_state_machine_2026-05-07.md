# Year worker runtime preflight state machine

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Simulation state: `blocked`
Execution authority: `none`
Proof authority: `none`
Shared truth effect: `none`
Skill Usage: no suitable repository skill identified for this docs-only research-evidence slice.

This artifact is a blocked, non-executing research-evidence simulation/specimen. It is non-authoritative and must not be used to authorize dispatch, render a runnable command, infer cloud runtime support, or claim execution/replay correctness. Any unresolved reference, missing binding, or authority ambiguity fails closed to `intentionally_blocked` or `forbidden_to_infer`.

Local existence, Git-tracked state, pinned provenance, and descriptive runtime references are evidentiary only; they do not establish admissibility.

This layer sits between clean-clone reconstruction evidence and any later runtime activity for analysis only. It is not an executable pipeline stage and does not alter the authority of existing workforce documents.

## Purpose

This state machine models the preflight-shaped analytical progression that can be described from the blocked bundle and clean-clone anchors.

It does not model an executable worker lifecycle.

## Phase set

| Phase | State name                          | Exit classification        | Allowed next edge | Why the edge is still analytical only                        |
| ----- | ----------------------------------- | -------------------------- | ----------------- | ------------------------------------------------------------ |
| A     | `lineage_loading`                   | `structurally_satisfiable` | `A -> B`          | lineage visibility only establishes ordered blocked ancestry |
| B     | `manifest_loading`                  | `structurally_satisfiable` | `B -> C`          | manifest visibility only establishes declared surfaces       |
| C     | `structural_integrity_checks`       | `structurally_satisfiable` | `C -> D`          | continuity only establishes document shape                   |
| D     | `authority_boundary_validation`     | `structurally_satisfiable` | `D -> E`          | boundary review only establishes authority separation        |
| E     | `overlay_admissibility_validation`  | `partially_satisfiable`    | `E -> F`          | overlay policy can be reviewed without a carrier artifact    |
| F     | `runtime_binding_validation`        | `unresolved`               | `F -> G`          | binding gaps are assessed, not closed                        |
| G     | `execution_prohibition_enforcement` | `intentionally_blocked`    | `G -> H`          | prohibition remains the only honest continuation             |
| H     | `blocked_preflight_complete`        | `intentionally_blocked`    | `none`            | terminal analytical state only                               |

## State semantics

### A. `lineage_loading`

This state confirms that the blocked bundle root, deterministic order, and lineage summary remain repo-visible and mutually linked.

### B. `manifest_loading`

This state confirms that the envelope, dependency, repo snapshot, runtime, overlay, worker-year reporting, and integration-side specimens are all declared and readable.

### C. `structural_integrity_checks`

This state confirms that the chain retains declared continuity and blocked-state transparency without needing undeclared repair.

### D. `authority_boundary_validation`

This state confirms that queue, envelope, runtime, overlay, worker-year reporting, and integration retain their previously declared authority boundaries.

### E. `overlay_admissibility_validation`

This state confirms only that whitelist and anti-tuning rules are legible enough to classify the overlay surface as reviewable, while the carrier artifact remains absent.

### F. `runtime_binding_validation`

This state is binding-gap assessment only. It may classify binding surfaces as named, partially named, or unresolved. It must not claim that those bindings exist, are available, are supported in cloud runtime, or can be executed.

### G. `execution_prohibition_enforcement`

This state confirms that the preflight layer still forbids runtime activity, artifact production claims, replay-correctness claims, and any authority drift toward dispatch.

### H. `blocked_preflight_complete`

This is the only completion state in the model. It is explicitly blocked and descriptive only.

## Transition rules

| From | To  | Transition condition                                           | Fail-closed trigger                                       |
| ---- | --- | -------------------------------------------------------------- | --------------------------------------------------------- |
| A    | B   | lineage order and root/terminal references remain visible      | missing root, broken order, or implicit repair need       |
| B    | C   | required manifests remain declared and readable                | any missing required manifest                             |
| C    | D   | structural continuity remains explicit without healing         | silent state upgrade or undeclared continuity patch       |
| D    | E   | authority boundaries remain separated and non-inheriting       | any claim that descriptive layers grant runtime authority |
| E    | F   | overlay policy remains reviewable while carrier remains absent | overlay policy used as proof of carrier existence         |
| F    | G   | runtime binding gaps remain explicit and unresolved            | descriptive refs treated as closed bindings               |
| G    | H   | blocked continuation remains the only honest analytical result | any claim of runtime activity or replay correctness       |

## Terminal rule

`blocked_preflight_complete` is a terminal analytical state.

It has **no** outgoing edge to:

- dispatch assembly
- runtime activity
- produced-artifact generation
- provenance attestation
- readiness language

## Forbidden edges

The following edges are outside the model and must remain absent:

- `H -> dispatch`
- `H -> execution`
- `H -> artifact_generation`
- `H -> readiness`
- `F -> runtime_activity`
- `E -> overlay_materialization`
- `D -> authority_inheritance`

## What this state machine does not prove

This state machine does **not** prove:

- that a runtime-facing implementation exists
- that any binding gap is closed
- that cloud runtime support exists
- that artifact evidence will appear later without new implementation
- that the blocked terminal can be upgraded by local state alone

## Recommended next step

If this analytical state machine remains internally consistent after validation, the next bounded step is still a blocked dispatch-assembly simulation that consumes `blocked_preflight_complete` as an input classification rather than as any kind of runtime-enabling verdict.
