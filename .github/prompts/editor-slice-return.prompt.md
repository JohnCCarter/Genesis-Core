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

Normalize the supplied material into the standard Genesis-Core worker return package.
If information is missing, mark it explicitly as missing instead of inventing it.

## Output format

### Status

- `pass | null | blocked | fail-closed`

### Summary

- one concise paragraph on what the slice did and what changed or was learned

### Base and scope

- `base_sha_confirmed`
- scope summary (IN / OUT)
- scope adherence report

### Artifacts

- artifact or packet paths
- any branch or worktree identifiers if relevant

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
- If the slice suggests a follow-up, describe it as the next admissible slice rather than an automatic continuation.
