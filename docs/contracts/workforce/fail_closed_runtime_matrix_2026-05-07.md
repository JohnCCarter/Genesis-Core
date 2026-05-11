# Fail-closed runtime matrix

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft`
Scope: `docs-only`
Runtime authority: `none`
Dispatch authority: `none`
Promotion authority: `none`
Skill Usage: no suitable repository skill identified for this docs-only workforce failure-matrix slice.

This matrix is a proposed manual draft for the research-evidence lane only. It is non-authoritative and is **not consumed by runtime, dispatch, validation, promotion, or shared-truth workflows**.

Its purpose is narrow:

> make the year-worker chain fail-closed behavior legible at a glance so that missing inputs, drift, and authority violations block or downgrade the slice before any larger meaning is assigned.

## Matrix

| Failure case | Worker status | Dispatch allowed? | Integration action | Recommended next step |
| --- | --- | --- | --- | --- |
| missing required artifact | `blocked` or `fail_closed` | `false` | `blocked` | register or capture the missing artifact through the approved mechanism, rebuild dependency closure, and re-run preflight |
| missing baseline config | `fail_closed` | `false` | `blocked` | restore the immutable baseline config reference, pin its hash, and reopen admissibility review |
| hash mismatch | `fail_closed` | `false` or `revoke_to_false` | `blocked` | identify the mismatched object, rebuild the affected manifest or artifact, and do not retry with ambiguous provenance |
| overlay contains forbidden key | `fail_closed` | `false` | `blocked` | regenerate the overlay from the whitelist only and treat the original attempt as tuning drift |
| merged config drift | `fail_closed` | `false` or `revoke_to_false` | `rerun_required` | compare the effective config against the pinned baseline, bind the canonical hash method if needed, and rerun only after parity is re-established |
| command not reproducible | `fail_closed` | `false` or `revoke_to_false` | `rerun_required` | rebuild the runtime execution manifest and command template, then rerun from clean preflight |
| output artifact missing | `blocked` | `false` for intake | `rerun_required` | capture the missing artifact in the declared namespace or rerun the bounded slice to produce it explicitly |
| undeclared input used | `fail_closed` | `false` or `revoke_to_false` | `blocked` | discard the run for integration purposes, declare the missing input explicitly, and rebuild closure before any rerun |
| worker writes forbidden path | `fail_closed` | `false` or `revoke_to_false` | `blocked` | discard or quarantine the output, investigate scope violation, and reopen only with a narrowed envelope |
| worker makes global claim | `blocked` | `false` for intake acceptance | `blocked` | strip global or cross-year meaning from the output contract and return the slice to integration for manual classification only |
| validation fails | `fail_closed` | `false` or `revoke_to_false` | `rerun_required` or `blocked` | fix the exact failed validation condition, then restart from preflight rather than continuing from partial state |

## Reading rule

The matrix is intentionally asymmetric:

- worker status explains what happened inside the slice
- `dispatch allowed?` explains whether the chain may continue or stay continued
- integration action explains how intake should classify the returned result
- recommended next step stays bounded and does not imply new authority

## Notes on revocation

Some rows use `revoke_to_false`.
That means:

- the slice may have crossed an earlier review gate
- but a later failure invalidates the current run for honest continuation or intake
- therefore the operational posture returns to blocked/fail-closed rather than “continue and explain later”

## What this matrix does not prove

This matrix does **not** prove:

- that the repository already enforces these failure transitions automatically
- that every future failure case is exhausted here
- that a worker may classify its own output as globally meaningful
- that any row in this matrix authorizes shared-truth updates or runtime changes

## Recommended next step

Use this matrix together with the chain design, output contract draft, and integration queue draft to keep one blocked year-worker dry-run packet honest from queue admission through intake classification.
