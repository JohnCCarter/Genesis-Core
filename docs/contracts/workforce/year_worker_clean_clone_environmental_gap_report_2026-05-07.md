# Year worker clean-clone environmental gap report

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Simulation state: `blocked`
Dispatch allowed: `false`
Execution authority: `none`
Proof authority: `none`
Shared truth effect: `none`

This artifact is a simulation/specimen only. It is non-authoritative, non-operational, and fail-closed on unresolved refs. It does **not** authorize dispatch, execution, materialization, admission, or proof of runtime admissibility.

## Purpose

This report enumerates the environmental gaps that a clean clone can identify honestly but cannot resolve from declared docs/manifests/contracts alone.

## Gap matrix

| Gap                                 | Current clean-clone state | Why it is unresolved                                                               | Fail-closed effect                                       | Future implementation needed                                                      | Forbidden inference                                          |
| ----------------------------------- | ------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| runtime implementation binding      | descriptive only          | runtime manifest shows shape, not a runnable authorized path                       | execution remains prohibited                             | blocked preflight/runtime simulation and later reviewed execution binding         | `scripts/run/run_backtest.py` ref implies runnable authority |
| generated overlay materialization   | absent                    | overlay object is shape-only and dependency manifest marks payload missing         | dispatch remains blocked                                 | materialized overlay carrier with reviewed generation rule and receipt            | overlay draft equals real overlay payload                    |
| hash canonicalization               | absent                    | bundle objects expose placeholder hashes only                                      | hash-based advancement stops                             | deterministic canonical hash/binding scheme for bundle/manifests/effective config | placeholder hashes are close enough to real binding          |
| artifact registry / receipt model   | absent                    | intake and output objects have no produced artifact receipts                       | intake remains specimen-only                             | explicit receipt/registry mapping between declared namespace and produced outputs | namespace examples prove outputs exist                       |
| replay reproducibility              | absent                    | no runtime was executed and no replay evidence exists                              | operational reproducibility cannot be claimed            | non-executing preflight simulation first, then bounded reviewed runtime evidence  | structural coherence proves replay correctness               |
| resumability / idempotency          | absent                    | no run state or partial-state contract exists yet                                  | partial-run handling cannot be reasoned about honestly   | explicit resume contract, idempotency keys, and blocked-state semantics           | a clean clone would naturally behave idempotently            |
| cloud dispatch/runtime integration  | absent                    | no orchestration or dispatch layer exists in this slice                            | dispatch must remain false                               | separately governed dispatch/runtime integration design and implementation        | docs-only chain implies cloud readiness                      |
| baseline config attestation         | descriptive only          | queue/runtime refs name the baseline but do not attest clean-clone operational use | config identity remains non-operational                  | reviewed attestation/binding of config identity for dispatch use                  | repo path plus selector implies admissible config            |
| runtime entrypoint attestation      | descriptive only          | dependency manifest explicitly marks attestation missing                           | command path remains non-operational                     | reviewed runner-attestation and preflight checks                                  | tracked script path implies execution approval               |
| output namespace materialization    | absent                    | runtime/output objects reference non-materialized example namespaces               | no receipts, no produced artifacts, no intake validation | explicit output namespace materialization/capture step                            | example namespace is an actual artifact root                 |
| comparable multi-year synthesis set | absent                    | cross-year object requires verified comparable tuples                              | synthesis admission stays blocked                        | comparable-year intake bundle and verified tuple policy in use                    | one blocked year implies recurring or contradictory effect   |

## Missing implementation classes

### 1. Runtime-facing implementation

Still missing:

- non-executing preflight contract tied to real file presence
- reviewed executable command binding
- runtime-environment contract tied to actual receipts

### 2. Provenance implementation

Still missing:

- manifest-hash attestation receipts
- canonical effective-config hashing
- produced-output provenance receipts

### 3. Operational continuity implementation

Still missing:

- resumability semantics
- idempotency keys / duplicate-run prevention semantics
- explicit re-entry behavior after a blocked preflight

### 4. Cloud integration implementation

Still missing:

- dispatch review mechanism
- worker start/stop lifecycle semantics
- artifact-store / receipt-store semantics for cloud-visible outputs

## What the clean clone can say honestly today

The clean clone can say:

- the blocked chain is structurally coherent
- the missing pieces are explicit
- no hidden local state is required to _understand_ where the chain blocks
- the chain is honest about not being operationally complete

The clean clone cannot say:

- that the missing pieces are already solved elsewhere
- that runtime behavior would be reproducible if attempted
- that dispatch can be enabled once docs are present
- that integration can verify artifacts that do not yet exist

## Observed

- every major environmental gap is already hinted by a declared blocked object
- the missing pieces cluster around runtime, provenance, and cloud integration rather than lineage shape
- no gap is silently papered over by local-state assumptions

## Inferred

- the chain is sufficiently specified for blocked preflight-only review because the remaining gaps are already explicit enough to test structurally

## Unverified

- whether future implementations can preserve the same fail-closed clarity without expanding local assumptions

## What this report does not prove

- that any missing implementation should be built next
- that the current docs are the final shape of runtime integration
- that the future receipt/registry layer will be minimal or simple

## Recommended next step

Author a still-blocked runtime preflight simulation artifact that classifies which preflight checks are satisfiable from clean-clone docs-only inputs and which remain blocked by intentionally missing runtime/provenance implementation.
