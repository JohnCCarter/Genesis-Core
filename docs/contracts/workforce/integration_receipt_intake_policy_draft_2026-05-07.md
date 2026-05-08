# Integration receipt-intake policy draft

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Policy state: `review_only_blocked`
Documentary intake state: `blocked`
Acceptance state: `not_accepted`
Promotion state: `none`
Cross-year meaning state: `separate`
Economic validity inference: `forbidden`
Skill Usage: no suitable repository skill identified for this docs-only research-evidence slice.

This draft/specimen records a review-only blocked/not_accepted classification about receipt and artifact claims. It does not issue receipts, accept artifacts, verify truth, imply backend/storage existence, promote artifacts, or assign cross-year or economic meaning.

Receipt claim presence does not imply artifact acceptance. Registry presence does not imply truth. Worker output presence does not imply integration acceptance. Integration intake may classify, but not promote. Cross-year meaning remains separate from receipt intake. Economic validity is never inferred from artifact existence.

## Command packet

- **Mode:** `RESEARCH` — source: explicit user request on branch `feature/next-slice-2026-05-06`
- **Category:** `docs`
- **Risk:** `LOW` — why: docs-only integration-intake modeling with no runtime, results, backend, or implementation changes
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: receipt/registry vocabulary now exists as blocked docs-only language, so the next bounded step is to model how integration would review those claims without accepting them
- **Objective:** define the first blocked integration-side receipt-intake example for year-worker artifact claims
- **Candidate:** `blocked integration-side receipt-intake example`
- **Base SHA:** `044096e70ea5596181392e77217dab275d603e93`

### Research-evidence lane

- **Baseline / frozen references:** artifact receipt model/specimen, artifact registry index model, artifact receipt denial matrix, blocked dispatch package, blocked output contract, blocked integration intake, canonical integration queue draft, fail-closed runtime matrix, governance mode SSOT
- **Candidate / comparison surface:** current blocked output/intake chain versus a future integration-side review layer that can classify receipt claims without accepting them
- **Vad ska förbättras:** make receipt-intake review semantics explicit enough to separate classification from acceptance, promotion, cross-year meaning, and economic interpretation
- **Vad får inte brytas / drifta:** no receipt issuance, no backend/storage claim, no concrete hashes, no acceptance drift, no promotion language, no cross-year meaning assignment, no economic validity inference
- **Reproducerbar evidens som måste finnas:** editor diagnostics, YAML/Markdown validation, scoped `pre-commit`, detect-secrets via pre-commit if available, token audits, and manual wording audit for blocked/not_accepted semantics

### Scope

- **Scope IN:**
  - `docs/contracts/workforce/integration_receipt_intake_specimen_blocked_2026-05-07.yaml`
  - `docs/contracts/workforce/integration_receipt_intake_policy_draft_2026-05-07.md`
  - `docs/contracts/workforce/integration_receipt_intake_denial_matrix_2026-05-07.md`
  - read-only receipt/registry/output/intake/dispatch/gov anchors under `docs/contracts/workforce/` and `docs/governance/`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**`
  - `scripts/**`
  - `data/**`
  - `datasets/**`
  - `results/**`
  - `artifacts/**`
  - receipt issuance
  - backend/storage implementation
  - runtime execution
  - integration acceptance
  - promotion or cross-year meaning assignment
  - economic validity claims
- **Expected changed files:** `3`
- **Max files touched:** `3`

## Why this policy exists

The current blocked chain already says that:

- worker outputs remain advisory and year-local
- receipt and registry language is documentary only
- integration intake alone owns acceptance and meaning boundaries
- cross-year meaning sits outside worker-local and receipt-local surfaces

What is still missing as a dedicated specimen is the integration-side review layer that sits between:

- receipt claim presence
- registry bookkeeping presence
- worker output presence
- and any later integration acceptance decision

This policy draft fills that gap only.

## Relationship to neighboring surfaces

| Surface                   | What this intake layer may say                   | What it may not say                                     |
| ------------------------- | ------------------------------------------------ | ------------------------------------------------------- |
| artifact receipt model    | which claim format and placeholder rules apply   | that a receipt was issued                               |
| artifact receipt specimen | which refs and claim states are being reviewed   | that the claim is true                                  |
| registry index model      | which bookkeeping state is visible to intake     | that registry visibility equals acceptance              |
| worker output contract    | which artifact roles were expected or reported   | that worker output self-validates integration use       |
| dispatch package          | which slice lineage governed the claim           | that dispatch ancestry proves artifact admissibility    |
| runtime preflight         | which blocked runtime context preceded the claim | that preflight context proves artifact existence        |
| cross-year meaning        | remains out of scope for receipt intake          | that classification here implies synthesis or promotion |

## Review-only identity shapes

### `intake_id` pattern

This policy defines an intake identifier pattern only:

`intake::<slice_id>::<claim_slot>::<review_slot>`

This is documentary only and not a materialized record identifier.

### Receipt claim refs

Receipt claim refs may point only to documentary claim sources such as:

- `artifact_receipt_specimen_blocked_2026-05-07.yaml`
- a future reviewed non-authoritative receipt claim specimen

Receipt claim refs describe what is being reviewed. They do not prove that any claim is correct.

### Artifact registry refs

Registry refs may point only to the registry bookkeeping model or a future reviewed registry specimen.

Registry refs describe what bookkeeping context exists. They do not prove storage, truth, or acceptance.

### Worker output contract refs

Worker output contract refs identify the worker-side report surface that declared or expected an artifact role.

Worker output presence does not imply integration acceptance.

### Lineage refs

Integration receipt intake must stay anchored to documentary lineage refs only:

- `queue_item_ref`
- `envelope_ref`
- `dependency_manifest_ref`
- `runtime_preflight_ref`
- `dispatch_package_ref`
- `output_contract_ref`
- `integration_intake_ref`

These refs preserve context only.

## Expected versus reported artifact refs

### Expected artifact refs

Expected artifact refs come from declared slice context such as:

- the dispatch package
- the worker output contract
- the receipt specimen’s expected-artifact section

### Reported artifact refs

Reported artifact refs come from receipt-claim surfaces only.

Expected artifact refs and reported artifact refs must remain separate. Presence in one does not guarantee presence in the other.

## Integration classification vocabulary

This policy uses review-only vocabulary:

- `blocked` — intake cannot honestly advance
- `not_accepted` — the claim remains unaccepted for integration use
- `fail_closed` — a contradiction or policy breach forces a hard stop
- `out_of_scope` — the claim asks this layer to decide something it does not own

Classification here is documentary only.

Integration intake may classify, but not promote.

## Core rules

1. **Receipt claim presence does not imply artifact acceptance.**
2. **Registry presence does not imply truth.**
3. **Worker output presence does not imply integration acceptance.**
4. **Integration intake may classify, but not promote.**
5. **Cross-year meaning remains separate from receipt intake.**
6. **Economic validity is never inferred from artifact existence.**

## Blocked review behavior

### Missing receipt behavior

If an expected artifact role has no corresponding receipt claim ref, intake remains `blocked` and `not_accepted`.

### Undeclared artifact behavior

If a receipt claim points to an artifact role not declared by slice context, intake remains `blocked` and `not_accepted`.

### Hash mismatch behavior

If the governing hash policy indicates mismatch or placeholder-upgrade misuse, intake remains `fail_closed` and `not_accepted`.

### Duplicate or stale behavior

If multiple claims collide for the same role, or if a claim is stale against current lineage/base context, intake remains `blocked` and `not_accepted` until manual integration review says otherwise.

## Cross-year and economic boundaries

Receipt intake is not a cross-year synthesis surface.

Receipt intake is not an economic evaluation surface.

A claim may be present, referenced, and still remain:

- not accepted
- not promoted
- not cross-year comparable
- not economically meaningful

## What this policy does not prove

This draft does **not** prove:

- that any receipt exists
- that any registry entry exists
- that any artifact exists
- that any artifact has been accepted by integration
- that any claim is economically valid
- that any cross-year meaning may be assigned now
- that any later implementation must use a specific backend or persistence model

## Recommended next step

The next admissible step remains documentary only: connect this blocked integration-side intake vocabulary into a future non-authoritative integration queue or cross-year boundary specimen, still without issuing receipts, computing hashes, or accepting artifacts.
