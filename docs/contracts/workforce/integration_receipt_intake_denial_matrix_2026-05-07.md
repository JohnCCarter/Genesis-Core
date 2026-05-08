# Integration receipt-intake denial matrix

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Matrix state: `modeled_future_handling_only`
Documentary intake state: `blocked`
Acceptance state: `not_accepted`
Promotion state: `none`
Cross-year meaning state: `separate`
Economic validity inference: `forbidden`
Skill Usage: no suitable repository skill identified for this docs-only research-evidence slice.

This matrix is a docs-only model of future integration-side receipt-intake handling. It does not issue receipts, does not accept artifacts, does not verify truth, and does not imply backend/storage existence.

Receipt claim presence does not imply artifact acceptance. Registry presence does not imply truth. Worker output presence does not imply integration acceptance. Integration intake may classify, but not promote. Cross-year meaning remains separate from receipt intake. Economic validity is never inferred from artifact existence.

## Purpose

Use this matrix to keep integration-side receipt intake fail-closed when receipt claims, registry context, or worker output context are incomplete, conflicting, stale, mismatched, undeclared, or promotion-seeking.

## Denial matrix

| Case                                              | Receipt-claim context                        | Registry context                             | Worker-output context                               | Intake classification | Acceptance outcome | Required fail-closed response                                         | Forbidden inference                                             |
| ------------------------------------------------- | -------------------------------------------- | -------------------------------------------- | --------------------------------------------------- | --------------------- | ------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------- |
| missing receipt claim                             | `missing_or_explicitly_empty`                | `format_only_or_not_evaluated`               | `artifact role may still be expected`               | `blocked`             | `not_accepted`     | keep the claim absent explicitly and deny intake advancement          | missing receipt claim means the artifact was accepted elsewhere |
| undeclared artifact claim                         | `reported_but_undeclared`                    | `claim_may_be_recorded_for_bookkeeping_only` | `output contract does not declare the role`         | `blocked`             | `not_accepted`     | reject the undeclared role and keep it out of accepted intake state   | artifact usefulness overrides declaration discipline            |
| hash mismatch context                             | `reported_unverified_or_policy_conflicted`   | `blocked_hash_mismatch_or_equivalent`        | `worker output presence unchanged`                  | `fail_closed`         | `not_accepted`     | preserve mismatch semantics and stop review from advancing            | receipt or registry presence outweighs mismatch                 |
| duplicate claim context                           | `multiple_conflicting_claims`                | `rejected_duplicate_artifact_or_equivalent`  | `one worker output may still look plausible`        | `blocked`             | `not_accepted`     | group the claims and require manual integration review                | registry bookkeeping resolves duplicates automatically          |
| stale claim context                               | `reported_claim_is_out_of_date`              | `rejected_stale_artifact_or_equivalent`      | `current output context differs from stale lineage` | `blocked`             | `not_accepted`     | keep the stale claim explicit and deny current intake use             | older matching role means the claim is still acceptable         |
| worker output present without acceptance evidence | `receipt claim absent_or_unaccepted`         | `registry may mention expectation only`      | `worker output ref exists`                          | `blocked`             | `not_accepted`     | keep worker-output presence separate from intake acceptance           | worker output presence is enough for integration acceptance     |
| registry present without truth                    | `claim may still be missing_or_rejected`     | `bookkeeping_present_only`                   | `worker output context may exist`                   | `blocked`             | `not_accepted`     | preserve registry presence as bookkeeping only                        | registry visibility proves truth                                |
| cross-year meaning request                        | `claim tries to exceed receipt-intake scope` | `registry context may exist`                 | `worker output may ask for larger meaning`          | `out_of_scope`        | `not_accepted`     | route larger meaning outside this layer and keep intake non-promoting | receipt intake may assign synthesis meaning                     |
| economic validity request                         | `artifact presence or claim is cited`        | `registry context may exist`                 | `worker output may contain observations`            | `out_of_scope`        | `not_accepted`     | forbid economic interpretation here                                   | artifact existence implies economic validity                    |

## Behavioral notes

### Missing receipt behavior

Missing receipt claims keep intake blocked even when artifact roles are expected elsewhere in the slice.

### Undeclared artifact behavior

Undeclared artifact claims remain not accepted even when they look locally relevant.

### Hash mismatch behavior

Hash mismatch semantics remain abstract and policy-based here. No concrete digest text is needed for the intake example to fail closed.

### Duplicate and stale behavior

Duplicate or stale claim contexts stay blocked until a separately reviewed integration decision resolves them.

### Classification without promotion

This layer may classify blocked/not_accepted/fail_closed/out_of_scope. It may not promote, admit, or assign cross-year meaning.

## What this matrix does not prove

This matrix does **not** prove:

- that any receipt claim exists
- that any artifact has been accepted
- that any registry bookkeeping entry is true
- that any worker output is sufficient for integration acceptance
- that any cross-year meaning may be assigned here
- that any artifact carries economic validity by existence alone

## Recommended next step

If this matrix remains internally consistent after validation, the next admissible step is still documentary only: connect this intake vocabulary into a future blocked integration queue or cross-year boundary specimen without issuing receipts, materializing hashes, or accepting artifacts.
