# Artifact receipt denial matrix

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Matrix state: `modeled_future_handling_only`
Dispatch allowed: `false`
Execution authority: `none`
Proof authority: `none`
Shared truth effect: `none`
Skill Usage: no suitable repository skill identified for this docs-only research-evidence slice.

This matrix is a docs-only model of future receipt and registry denial handling. It does not implement receipt issuance, does not persist registry entries, and does not prove that any artifact exists.

Receipt presence does not imply truth. Registry presence does not imply integration acceptance. Artifact existence does not imply economic validity. Only integration plane may classify meaning.

## Purpose

Use this matrix to keep future receipt and registry handling fail-closed when artifact claims are missing, stale, duplicated, mismatched, undeclared, or otherwise non-admissible.

## Denial matrix

| Case                      | Receipt-claim state   | Registry state                 | Integration-intake consequence | Required fail-closed response                                                           | Forbidden inference                                                       |
| ------------------------- | --------------------- | ------------------------------ | ------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| missing expected artifact | `not_reported`        | `blocked_missing_artifact`     | `blocked`                      | keep the expected artifact explicit and deny honest intake                              | no receipt claim means the artifact existed but was omitted accidentally  |
| rejected artifact claim   | `rejected`            | `rejected_artifact_claim`      | `fail_closed`                  | preserve the rejection explicitly and require manual review                             | rejection means the artifact can still be used if cited elsewhere         |
| duplicate artifact claim  | `reported_unverified` | `rejected_duplicate_artifact`  | `blocked`                      | group the conflicting claims and deny intake pending review                             | registry presence resolves the duplicate automatically                    |
| stale artifact claim      | `reported_unverified` | `rejected_stale_artifact`      | `blocked`                      | compare lineage/base context and deny stale claims                                      | an older artifact is acceptable because its role matches                  |
| hash mismatch             | `reported_unverified` | `blocked_hash_mismatch`        | `fail_closed`                  | record the mismatch and block intake                                                    | receipt presence outweighs hash disagreement                              |
| undeclared artifact claim | `reported_unverified` | `rejected_undeclared_artifact` | `blocked`                      | reject claims not declared by slice context                                             | artifact existence makes declaration unnecessary                          |
| incomplete receipt shape  | `format_only`         | `blocked_incomplete_receipt`   | `blocked`                      | require missing lineage/policy fields before any review continues                       | partial receipt shape is good enough for truth                            |
| forbidden producer        | `reported_unverified` | `rejected_forbidden_producer`  | `fail_closed`                  | reject claims from a non-declared producer ref                                          | any producer may speak for the slice if the artifact role looks plausible |
| lineage mismatch          | `reported_unverified` | `blocked_lineage_mismatch`     | `fail_closed`                  | block when queue/envelope/dependency/preflight/dispatch/output/intake refs do not align | one matching ref is enough to rescue the claim                            |
| intake validation failure | `reported_unverified` | `receipt_claim_recorded`       | `blocked`                      | keep bookkeeping separate from acceptance and deny integration use                      | registry recording implies intake accepted the artifact                   |

## Behavioral notes

### Missing artifact behavior

Missing expected artifacts remain explicit. The registry may record that the expected role exists, but it may not silently convert absence into success.

### Rejected artifact behavior

Rejected claims stay visible as rejected. They are not deleted from bookkeeping merely to make the slice appear cleaner.

### Duplicate artifact behavior

Duplicates remain blocked until integration reviews which claim, if any, belongs to the bounded slice.

### Stale artifact behavior

A stale artifact remains denied when the active slice lineage or governing base context has moved on.

### Hash mismatch behavior

Hash mismatch blocks honest intake even if every other field looks tidy.

### Undeclared artifact behavior

An undeclared artifact claim is rejected even if the artifact role sounds useful.

## What this matrix does not prove

This matrix does **not** prove:

- that receipt issuance already exists
- that registry persistence already exists
- that any specific artifact role exists today
- that any denied case has been automated
- that integration would accept a future artifact after review
- that bookkeeping states may classify larger meaning

## Recommended next step

If this matrix remains internally consistent after validation, the next admissible step is still documentary only: connect the receipt/registry vocabulary into a future blocked output/intake specimen without creating artifacts, receipts, hashes, or implementation code.
