# Integration discrepancy reconciliation matrix

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft / blocked`
Scope: `docs-only`
Matrix state: `modeled_future_handling_only`
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

## Purpose

Use this matrix to keep discrepancy comparison fail-closed when expected artifact refs, reported artifact refs, receipt claim refs, registry refs, or prior intake states are incomplete, duplicated, stale, undeclared, mismatched, or pushed beyond the scope of this layer.

## Reconciliation matrix

| Case                                           | Expected-artifact context                     | Reported-artifact context                     | Receipt-claim context                          | Registry-ref context                         | Intake-state context                          | Comparison classification | Inference guard      | Review disposition      | Required fail-closed response                                            | Forbidden inference                                      |
| ---------------------------------------------- | --------------------------------------------- | --------------------------------------------- | ---------------------------------------------- | -------------------------------------------- | --------------------------------------------- | ------------------------- | -------------------- | ----------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------- |
| shape-aligned refs with unresolved receipt     | `declared_expected_role_present`              | `reported_role_shape_aligns`                  | `documentary_claim_surface_still_unresolved`   | `bookkeeping_ref_present_or_absent_only`     | `prior_review_surface_is_blocked`             | `structurally_consistent` | `forbidden_to_infer` | `unresolved`            | keep the alignment visible but do not close the evidentiary gap          | matching refs mean the artifact is correct or acceptable |
| partial surface match with registry mismatch   | `declared_expected_role_present`              | `reported_role_is_present`                    | `claim_surface_is_still_documentary_only`      | `bookkeeping_ref_does_not_align_with_claim`  | `prior_review_surface_is_blocked`             | `partially_consistent`    | `forbidden_to_infer` | `review_required`       | preserve the mismatch explicitly and require later human review          | registry bookkeeping repairs the discrepancy             |
| missing reported role for an expected artifact | `declared_expected_role_present`              | `reported_role_is_missing`                    | `no_claim_surface_for_expected_role`           | `bookkeeping_context_may_still_exist`        | `prior_review_surface_is_blocked`             | `discrepancy_detected`    | `forbidden_to_infer` | `review_required`       | keep the missing role explicit and deny silent completion                | expected status means the role exists and is acceptable  |
| receipt claim mismatch                         | `declared_expected_role_present`              | `reported_role_points_elsewhere`              | `claim_surface_conflicts_with_compared_role`   | `bookkeeping_context_may_be_partial_only`    | `prior_review_surface_is_blocked`             | `discrepancy_detected`    | `forbidden_to_infer` | `review_required`       | preserve the claim mismatch and deny silent reconciliation               | a cited claim outweighs the mismatch                     |
| undeclared reported artifact                   | `governing_slice_does_not_declare_the_role`   | `reported_role_is_present_anyway`             | `claim_surface_cites_an_undeclared_role`       | `bookkeeping_context_may_note_the_attempt`   | `prior_review_surface_is_blocked`             | `discrepancy_detected`    | `forbidden_to_infer` | `reconciliation_denied` | keep the undeclared role explicit and deny closure in this layer         | local usefulness overrides declaration discipline        |
| duplicate reported artifact context            | `single_expected_role_is_declared`            | `multiple_reported_refs_compete_for_one_role` | `multiple_claim_surfaces_compete_for_one_role` | `bookkeeping_context_may_show_repetition`    | `prior_review_surface_is_blocked`             | `discrepancy_detected`    | `forbidden_to_infer` | `review_required`       | keep duplicates grouped and refuse to choose a winner silently           | repeated reporting settles identity                      |
| stale artifact context                         | `current_slice_context_remains_declared`      | `reported_ref_points_to_displaced_context`    | `claim_surface_follows_older_context`          | `bookkeeping_context_refers_to_older_review` | `prior_review_surface_is_blocked`             | `intentionally_blocked`   | `forbidden_to_infer` | `review_required`       | keep the stale context explicit and deny current-slice closure           | older alignment is good enough                           |
| lineage mismatch across governing refs         | `declared_expected_role_depends_on_alignment` | `reported_ref_uses_non_aligned_lineage`       | `claim_surface_uses_non_aligned_lineage`       | `bookkeeping_ref_uses_non_aligned_lineage`   | `prior_review_surface_is_blocked_or_diverged` | `intentionally_blocked`   | `forbidden_to_infer` | `reconciliation_denied` | keep the lineage mismatch explicit and deny reconciliation in this layer | one matching ref rescues the rest                        |
| unresolved receipt context                     | `declared_expected_role_present`              | `reported_role_may_or_may_not_be_present`     | `claim_surface_missing_incomplete_or_deferred` | `bookkeeping_context_is_not_closing_the_gap` | `prior_review_surface_is_blocked`             | `unresolved`              | `forbidden_to_infer` | `review_required`       | keep the unresolved state visible and deny silent closure                | later evidence may be presumed now                       |
| matching refs used to request larger meaning   | `declared_expected_role_present`              | `reported_role_shape_aligns`                  | `claim_surface_is_still_documentary_only`      | `bookkeeping_context_may_look_orderly`       | `prior_review_surface_is_blocked`             | `structurally_consistent` | `forbidden_to_infer` | `reconciliation_denied` | deny any attempt to upgrade discrepancy labels into correctness meaning  | structural alignment implies runtime or dispatch meaning |
| cross-year meaning request                     | `current_slice_context_is_local_only`         | `reported_role_is_local_only`                 | `claim_surface_asks_for_broader_meaning`       | `bookkeeping_context_may_exist`              | `prior_review_surface_is_blocked`             | `partially_consistent`    | `forbidden_to_infer` | `reconciliation_denied` | route broader meaning outside triage and keep this layer non-promoting   | discrepancy handling may assign cross-year meaning       |

## Behavioral notes

### Comparison classification versus review disposition

`structurally_consistent` and `partially_consistent` are comparison labels only. They never stand alone as terminal outcomes in this matrix.

### Review-only reconciliation semantics

Reconciliation in this matrix means discrepancy mapping only. It may label relationships as aligned, partial, unresolved, blocked, or denied. It may not accept artifacts, assign truth, declare correctness, infer runtime fitness, authorize dispatch, or promote findings.

### Prohibited upgrade semantics

- matching refs do not upgrade to acceptance
- structural alignment does not upgrade to correctness
- registry bookkeeping does not upgrade to truth
- discrepancy handling does not upgrade to runtime correctness
- discrepancy handling does not upgrade to dispatch authorization
- review recommendation does not upgrade to promotion
- cross-year meaning remains outside this layer

## What this matrix does not prove

This matrix does **not** prove:

- that any artifact has been accepted
- that any compared surface is true or correct
- that matching refs are complete enough to close review
- that a discrepancy may be silently resolved
- that any artifact is economically valid
- that any runtime behavior is correct
- that any dispatch action is authorized
- that any cross-year meaning may be assigned here

## Recommended next step

If this matrix remains internally consistent after validation, the next admissible step is still documentary only: connect this discrepancy vocabulary to a future bounded integration queue review or cross-year boundary example, still without accepting artifacts, issuing receipts, implementing a registry backend, or inferring correctness.
