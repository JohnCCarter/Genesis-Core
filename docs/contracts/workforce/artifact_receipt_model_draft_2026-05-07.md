# Artifact receipt model draft

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Model state: `format_only_blocked`
Receipt state: `not_materialized`
Registry state: `not_materialized`
Dispatch allowed: `false`
Execution performed: `false`
Automation used: `false`
Simulation authority: `none`
Proof authority: `none`
Shared truth effect: `none`
Skill Usage: no suitable repository skill identified for this docs-only research-evidence slice.

This artifact is a docs-only, non-authoritative model for future year-worker artifact receipts and registry indexing. It does not create a receipt, does not register an artifact, does not choose a storage backend, does not attest hash correctness, and does not imply integration acceptance.

Receipt presence is evidentiary only and does not attest artifact existence, hash correctness, semantic correctness, or integration acceptance. Registry presence is bookkeeping only and does not classify trading meaning, research merit, or economic validity. Only the integration intake plane may accept, reject, or classify meaning.

## Command packet

- **Mode:** `RESEARCH` — source: explicit user request on branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: docs-only receipt/registry modeling with no runtime, results, implementation, backend, or config changes
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the chain already names output/intake seams, so the next bounded step is to model receipt and registry semantics without creating artifacts or runtime behavior
- **Objective:** define the first docs-only, non-authoritative artifact receipt and registry model for year-workers
- **Candidate:** `artifact receipt and registry model draft`
- **Base SHA:** `044096e70ea5596181392e77217dab275d603e93`

### Research-evidence lane

- **Baseline / frozen references:** blocked lineage bundle, runtime-preflight docs, dispatch-assembly docs, dry-run output contract/intake docs, canonical output contract draft, canonical integration queue draft, chain design, fail-closed matrix
- **Candidate / comparison surface:** current blocked chain with explicit output/intake gaps versus a future documentary receipt/registry layer that still remains non-implementing and non-authoritative
- **Vad ska förbättras:** make artifact receipt identity, denial, placeholder discipline, and integration-owned meaning explicit enough to review safely
- **Vad får inte brytas / drifta:** no fake receipts, no fake hashes, no backend decision, no runtime or dispatch activation, no registry implementation claim, no truth/promotion language
- **Reproducerbar evidens som måste finnas:** editor diagnostics, YAML validation, scoped `pre-commit`, detect-secrets via pre-commit if available, token audits, and wording audit for fail-closed semantics

### Scope

- **Scope IN:**
  - `docs/contracts/workforce/artifact_receipt_model_draft_2026-05-07.md`
  - `docs/contracts/workforce/artifact_receipt_specimen_blocked_2026-05-07.yaml`
  - `docs/contracts/workforce/artifact_registry_index_model_draft_2026-05-07.yaml`
  - `docs/contracts/workforce/artifact_receipt_denial_matrix_2026-05-07.md`
  - read-only lineage, dispatch, output, intake, and governance anchors under `docs/contracts/workforce/` and `docs/governance/`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**`
  - `scripts/**`
  - `data/**`
  - `datasets/**`
  - `results/**`
  - `artifacts/**`
  - storage backend implementation
  - registry implementation
  - runtime execution
  - artifact production
  - dispatch activation
- **Expected changed files:** `4`
- **Max files touched:** `4`

## Why this model exists

The current year-worker chain already defines:

- queue and envelope ancestry
- blocked dependency and runtime-preflight seams
- a dispatch package that stays denied
- a worker output contract that may eventually report produced artifacts
- an integration intake surface that alone owns acceptance and meaning

What it does **not** yet define as a dedicated model is the receipt/registry seam between:

- worker-reported artifact claims
- hash/reporting discipline
- bookkeeping of expected versus reported artifacts
- fail-closed handling of duplicates, stale artifacts, missing artifacts, undeclared artifacts, and mismatched hashes

This draft fills that documentary gap only.

## Relationship to the year-worker chain

| Chain surface          | What the receipt/registry layer may say                                     | What it may not say                                |
| ---------------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| queue item             | which bounded slice the artifact claim belongs to                           | queue presence authorizes artifact truth           |
| envelope               | which scope and constraints governed the producing slice                    | envelope scope proves artifact validity            |
| dependency manifest    | which declared prerequisites should have existed before production          | dependency naming proves an artifact was produced  |
| runtime preflight      | whether a producing context was blocked, unresolved, or separately reviewed | preflight classification proves an artifact exists |
| dispatch package       | which documentary package declared the slice and its refs                   | dispatch packaging proves receipt admissibility    |
| worker output contract | which artifact roles were expected or claimed by the worker                 | worker reporting self-validates truth or meaning   |
| integration intake     | where receipt and registry claims must be checked                           | intake ref alone implies acceptance                |

## Required invariants

The following rules are mandatory for any later implementation that might derive from this draft:

1. **Receipt presence does not imply truth.**
2. **Registry presence does not imply integration acceptance.**
3. **Artifact existence does not imply economic validity.**
4. **Only integration plane may classify meaning.**
5. **No receipt or registry entry may backfill missing lineage, missing provenance, or missing hashes.**
6. **No worker-produced artifact may self-promote into cross-year truth or readiness language.**

## Receipt identity model

### `receipt_id` format

The model defines a **pattern**, not a materialized value:

`receipt::<slice_id>::<artifact_role>::<producer_slot>::<sequence_slot>`

Meaning of slots:

- `slice_id` — bounded year-worker identity
- `artifact_role` — declared artifact category such as `worker_output_contract` or another declared output role
- `producer_slot` — symbolic reference to the producing surface, not a backend or process identifier
- `sequence_slot` — deterministic slot within the bounded slice, not a timestamp-based runtime nonce

### `artifact_id` format

The model defines a **pattern**, not a materialized value:

`artifact::<slice_id>::<artifact_role>::<namespace_slot>`

Meaning of slots:

- `slice_id` — bounded year-worker identity
- `artifact_role` — declared artifact role
- `namespace_slot` — deterministic slot inside the artifact namespace pattern

### Artifact namespace

The model defines a **pattern**, not a storage decision:

`namespace::<slice_id>::<artifact_family>::<generation_slot>`

This namespace pattern is documentary only. It does **not** choose a filesystem layout, object store, bucket, URI, or persistence backend.

## Producer refs and lineage refs

### Producer refs

A future receipt may identify only documentary producer refs such as:

- the worker output contract that reported an artifact claim
- the integration intake surface that received and reviewed the claim

Producer refs identify **claim origin**, not truth.

### Lineage refs

Each future receipt or registry entry must link back by ref to the governing chain surfaces:

- `queue_item_ref`
- `envelope_ref`
- `dependency_manifest_ref`
- `runtime_preflight_ref`
- `dispatch_package_ref`
- `output_contract_ref`
- `integration_intake_ref`

Those refs preserve ancestry only. They do not upgrade authority.

## Content hash policy

### Algorithm policy

The model permits a declared hash policy such as:

- `algorithm: sha256`
- `content_hash_format: sha256:<64-lowercase-hex>`

This is a **format declaration only**. It is not a reported digest.

### Hash-state discipline

Any future receipt/registry layer must distinguish at least these states:

- `policy_only` — only the hash policy is known
- `not_reported` — no digest was reported
- `reported_unverified` — a digest was reported but not yet accepted by integration
- `mismatch_detected` — reported digest conflicts with governing lineage or artifact expectation
- `forbidden_placeholder_upgrade` — a placeholder was incorrectly treated as a real digest

### Placeholder discipline

Before real artifact production and intake review, only placeholder-safe fields are allowed:

- `receipt_id_pattern`
- `artifact_id_pattern`
- `artifact_namespace_pattern`
- `content_hash_policy`
- `content_hash_placeholder_token`

Forbidden in this draft:

- a concrete `receipt_id`
- a concrete `artifact_id`
- a concrete digest string
- any fake receipt, fake hash, or implied acceptance token

## Expected versus produced artifacts

### Expected artifacts

Expected artifacts are the artifacts that a dispatch package and/or worker output contract declares as relevant for a bounded slice.

Expected artifacts belong to a role catalog such as:

- `worker_output_contract`
- `supporting_worker_artifact::<artifact_role>`

Expected artifacts may be declared even when nothing was produced.

### Reported or produced artifacts

A later worker may report artifact claims, but those claims remain only **reported receipt claims** until integration validates them.

Therefore this model separates:

- `declared_expected` artifacts
- `reported_receipt_claims`
- `integration intake validation`

A worker report, receipt claim, or registry presence must never collapse those three layers into one.

## Denial and fail-closed behavior

The companion denial matrix defines the detailed handling for:

- missing artifact
- rejected artifact
- duplicate artifact
- stale artifact
- hash mismatch
- undeclared artifact
- incomplete receipt
- forbidden producer
- lineage mismatch
- intake validation failure

All such cases fail closed until integration explicitly reviews them.

## Integration intake validation

Any future integration intake that consumes receipt or registry claims must validate at minimum:

- queue item lineage matches the dispatch package
- envelope lineage matches the dispatch package
- dependency manifest lineage matches the dispatch package
- runtime preflight lineage is contextually compatible with the reported artifact claim
- worker output contract declared the relevant artifact role
- artifact namespace pattern stays inside the declared slice
- hash policy is present and not silently upgraded from a placeholder
- no receipt or registry claim is treated as proof of economic validity or larger meaning

Integration intake is the only plane allowed to decide whether a receipt claim is:

- blocked
- fail-closed
- or later acceptable for integration use

This draft does not implement that decision.

## What a receipt does not prove

A receipt does **not** prove:

- that an artifact truly exists
- that the artifact content is correct
- that the content hash is correct
- that the artifact is semantically meaningful
- that the artifact is economically valid
- that the artifact is admissible for integration
- that the artifact is comparable across years
- that the producing worker stayed within governance without separate review
- that dispatch, execution, or promotion was valid

## What this draft does not decide

This draft does **not** decide:

- storage backend
- filesystem or object-store layout
- runtime implementation details
- registry persistence mechanism
- whether receipts are issued by worker, intake, or another future reviewed layer
- whether a later implementation should store receipt claims inline or by separate index record

## Recommended next step

The next admissible step remains documentary only: relate this receipt/registry model back into a future blocked year-worker output/intake specimen, still without producing artifacts, receipts, hashes, or implementation code.
