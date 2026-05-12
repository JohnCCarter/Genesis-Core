---
name: editor-slice-return
description: "Normalize a completed Genesis-Core editor-worker slice into the standard return package. Use when a slice is done, blocked, parked, or ready for integration review."
argument-hint: "Paste the slice summary, artifact paths, comparisons, blockers, and next-step recommendation."
---

# Editor Slice Return

Use this prompt after one bounded editor-worker slice has finished, stopped, or been blocked.

Before producing the return, read and follow:

- [Worker governance envelope](../../docs/governance/worker_governance_envelope.md)
- [Editor slice worker dispatch runbook](../../docs/governance/runbooks/editor_slice_worker_dispatch.md)

Convert the supplied material into the standard Genesis-Core worker return package structure.
If information is missing, mark it as `[MISSING]` instead of inventing it. If the input is malformed, say so explicitly and identify the field that needs correction.

## Output format

### Status

- `pass | null | blocked | fail-closed`
- If status is missing or unsupported, write `[MISSING]` and note the valid values.

### Summary

- one concise paragraph on what the slice did and what changed or was learned

### Base and scope

- `base_sha_confirmed`
- scope summary (IN / OUT)
- scope adherence report

### Artifacts

- artifact or packet paths
- any execution-surface identifiers if relevant (for example shared checkout, or dedicated branch/worktree when explicit isolation was used)

### Findings

- observed
- inferred
- unverified
- what_this_does_not_prove
- contradictions_found
- assumptions_rejected

### Next step

- recommended_next_step
- recommended_integration_class
- blocked_by (if relevant)
- handoff_state (if relevant)
- next_admissible_slice_candidate (if relevant)
- access_frame_delta (if relevant)

## Output rules

- Keep epistemic separation hard: observed is directly supported, inferred is interpretation, unverified is still open.
- Do not upgrade the slice result into shared truth, readiness, or runtime authority.
- Treat shared checkout as the default local execution surface; mention dedicated branch/worktree only when explicit isolation was part of the slice contract or return provenance.
- If the slice suggests a follow-up, describe it as the next admissible slice rather than an automatic continuation.
