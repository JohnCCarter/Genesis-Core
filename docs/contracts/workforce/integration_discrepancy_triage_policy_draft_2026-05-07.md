# Integration discrepancy-triage policy draft

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Policy state: `review_only_blocked`
Reconciliation state: `blocked`
Acceptance state: `not_accepted`
Promotion state: `none`
Cross-year meaning state: `separate`
Economic validity inference: `forbidden`
Runtime correctness inference: `forbidden`
Dispatch authorization inference: `forbidden`
Skill Usage: no matching repository skill has been identified for this docs-only discrepancy-triage example. No skill-coverage claim is made for this slice; a future skill is only `föreslagen` if this pattern becomes recurring.

This document is a blocked, non-authoritative review artifact for discrepancy triage only. Any comparison, classification, or reconciliation label here describes observed reference relationships only and does not imply acceptance, truth, correctness, completeness, economic validity, dispatch authorization, registry authority, or runtime readiness. Missing or mismatched evidence remains blocked and review-required.

Reconciliation does not imply acceptance. Classification does not imply truth. Matching refs do not imply correctness. Artifact existence does not imply economic validity. Integration plane may classify discrepancies but may not silently resolve missing evidence. Cross-year meaning remains outside discrepancy triage. Triage may recommend review, never promotion.

## Command packet

- **Mode:** `RESEARCH` — source: explicit user request on branch `feature/next-slice-2026-05-06`
- **Category:** `docs`
- **Risk:** `LOW` — why: docs-only discrepancy comparison and reconciliation modeling with no runtime, backend, or implementation changes
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: receipt, registry, and intake vocabulary already exist as blocked docs-only language, so the next bounded step is to model discrepancy comparison without acceptance drift
- **Objective:** define the first blocked discrepancy-triage and reconciliation example for the integration plane
- **Candidate:** `blocked discrepancy-triage and reconciliation example`

### Research-evidence lane

- **Baseline / frozen references:** artifact receipt model/specimen, artifact registry index model, artifact receipt denial matrix, blocked integration receipt-intake policy/specimen/matrix, blocked dispatch package, blocked output contract, integration queue draft, governance mode SSOT
- **Candidate / comparison surface:** expected artifact refs versus reported artifact refs, receipt claim refs, registry refs, and prior intake states for the same bounded slice context
- **Vad ska förbättras:** make discrepancy and reconciliation vocabulary explicit enough to map mismatches without suggesting silent repair, acceptance, or correctness
- **Vad får inte brytas / drifta:** no receipt issuance, no registry backend, no concrete hashes, no concrete artifact IDs, no truth language, no promotion language, no runtime correctness inference, no dispatch authorization inference, no cross-year meaning assignment
- **Reproducerbar evidens som måste finnas:** diagnostics, YAML and Markdown checks, scoped `pre-commit`, detect-secrets via pre-commit if available, banned-token scans, and manual semantics review that all cases remain blocked or review-required

### Scope

- **Scope IN:**
  - `docs/contracts/workforce/integration_discrepancy_triage_policy_draft_2026-05-07.md`
  - `docs/contracts/workforce/integration_discrepancy_triage_specimen_blocked_2026-05-07.yaml`
  - `docs/contracts/workforce/integration_discrepancy_reconciliation_matrix_2026-05-07.md`
  - read-only terminology anchors under `docs/contracts/workforce/`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**`
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - runtime execution
  - artifact production
  - receipt issuance
  - registry implementation
  - storage/backend selection
  - integration acceptance
  - truth assignment
  - economic validity claims
  - dispatch authorization
  - cross-year synthesis

## Why this policy exists

The current blocked workforce chain already separates:

- receipt and registry language from acceptance
- worker output presence from integration acceptance
- integration intake from cross-year meaning
- artifact existence from economic interpretation

What was still missing was a dedicated discrepancy-triage layer showing how integration may compare expected and reported documentary surfaces without closing any evidentiary gaps. This draft fills only that gap.

## Relationship to neighboring surfaces

| Surface                           | What discrepancy triage may say                       | What it may not say                                  |
| --------------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| artifact receipt model            | which claim shapes and placeholder rules are relevant | that a receipt was issued                            |
| artifact receipt specimen         | which reported claim surface is being compared        | that a claim is true                                 |
| artifact registry index model     | which bookkeeping refs are visible to comparison      | that registry visibility equals truth or acceptance  |
| integration receipt-intake policy | which blocked intake boundary already governs review  | that intake already resolved the discrepancy         |
| worker output contract            | which artifact roles were declared or reported        | that worker reporting self-validates integration use |
| dispatch package                  | which slice lineage declared the expected roles       | that dispatch ancestry authorizes reconciliation     |
| cross-year meaning                | remains outside discrepancy triage                    | that discrepancy handling implies synthesis meaning  |

## Review-only identity shape

### `triage_id` pattern

This policy defines a discrepancy-triage identifier pattern only:

`triage::<slice_slot>::<comparison_slot>::<review_slot>`

This is documentary only and not a materialized record identifier.

## Comparison surfaces

### Expected artifact refs

Expected artifact refs come from declared slice context such as:

- the dispatch package
- the worker output contract
- the artifact receipt specimen's expected-artifact section

### Reported artifact refs

Reported artifact refs come from documentary reporting surfaces only, such as:

- receipt-claim specimens
- worker output contract reporting sections
- future non-authoritative discrepancy examples

### Receipt claim refs

Receipt claim refs identify the claim surface being compared. They do not prove issuance, persistence, or correctness.

### Registry refs

Registry refs identify bookkeeping context only. They do not prove truth, acceptance, or backend existence.

### Intake-state refs

Intake-state refs identify prior blocked review context only. They do not silently resolve the present discrepancy.

## Required classification vocabulary

### `structurally_consistent`

`structurally_consistent` means only that compared reference shapes and declared relations do not conflict within the limited claims presented. It does not imply authenticity, correctness, completeness, acceptance, registry validity, runtime fitness, or economic meaning.

### `partially_consistent`

`partially_consistent` means some compared claims align structurally while others remain missing, stale, duplicated, undeclared, or otherwise unresolved. It remains blocked and review-oriented only.

### `unresolved`

`unresolved` means the available documentary evidence is insufficient to close comparison honestly.

### `intentionally_blocked`

`intentionally_blocked` means policy forbids closure or upgrade in this slice even if some compared surfaces look orderly.

### `forbidden_to_infer`

`forbidden_to_infer` means truth, correctness, economic meaning, runtime correctness, and dispatch authorization remain outside this layer.

### `discrepancy_detected`

`discrepancy_detected` means compared refs, claim surfaces, or lineage context do not align.

### `reconciliation_denied`

`reconciliation_denied` means the integration plane may not close the identified gap in this slice.

### `review_required`

`review_required` means a later human review step would be required before any other layer could say more.

## Review-only reconciliation semantics

In this slice, reconciliation means discrepancy mapping only. It may say which compared refs line up structurally, which gaps remain open, and which contradictions stay explicit. It may not accept artifacts, assign truth, declare correctness, infer runtime fitness, authorize dispatch, or promote findings.

No case in this policy may terminate on `structurally_consistent` or `partially_consistent` alone. Every case remains paired with `forbidden_to_infer` and a blocked review disposition such as `unresolved`, `review_required`, or `reconciliation_denied`.

## Comparison and discrepancy behavior

### Expected versus reported artifact comparison

Expected and reported artifact refs must remain separate surfaces. A role may be expected yet unreported, reported yet undeclared, or structurally aligned but still unresolved.

### Receipt claim mismatch handling

If receipt claim refs describe a different role, contradictory reporting surface, or absent claim where one is expected, classification becomes `discrepancy_detected` or `unresolved`. Disposition remains `review_required` or `reconciliation_denied`.

### Registry reference mismatch handling

If registry refs do not align with the compared reporting context, triage may label the result `partially_consistent` or `discrepancy_detected`, but the blocked disposition remains explicit. Registry context may not repair the gap.

### Stale artifact handling

A stale artifact context exists when compared refs point to an older or displaced slice lineage rather than the currently reviewed bounded slice context. The safe outcome remains `intentionally_blocked` and `review_required`.

### Duplicate artifact handling

Duplicate reported refs for one expected role become `discrepancy_detected` and `review_required`. Triage may not select a winner silently.

### Undeclared artifact handling

If a reported role is not declared by the governing slice context, classification becomes `discrepancy_detected` and disposition becomes `reconciliation_denied`.

### Lineage mismatch handling

If queue, envelope, dependency, runtime-preflight, dispatch, output, or intake lineage refs do not align, triage becomes `intentionally_blocked` and `reconciliation_denied`.

### Unresolved receipt handling

If the compared receipt-claim surface is missing, incomplete, or still documentary-only, triage becomes `unresolved` and `review_required`.

## Prohibited upgrade semantics

- Reconciliation does not imply acceptance.
- Classification does not imply truth.
- Matching refs do not imply correctness.
- Artifact existence does not imply economic validity.
- Triage may not silently resolve missing evidence.
- Triage may not infer runtime correctness.
- Triage may not infer dispatch authorization.
- Cross-year meaning remains outside discrepancy triage.
- Triage may recommend review, never promotion.

## What this policy does not prove

This draft does **not** prove:

- that any artifact has been accepted
- that any compared surface is true
- that matching refs are correct or complete
- that any discrepancy can be silently reconciled
- that any artifact is economically meaningful
- that any runtime behavior is correct
- that any dispatch action is authorized
- that any cross-year meaning may be assigned here

## Recommended next step

The next admissible step remains documentary only: connect this blocked discrepancy vocabulary to a future bounded integration queue review example or cross-year boundary note, still without issuing receipts, implementing a registry, accepting artifacts, or inferring correctness.
