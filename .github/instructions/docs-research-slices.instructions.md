---
name: "Docs research slices"
description: "Use when editing Genesis-Core docs, analysis notes, governance runbooks, packets, or evidence summaries for bounded research slices."
applyTo: "{docs/**/*.md,workforce_roadmap.md,GENESIS_WORKING_CONTRACT.md,handoff.md}"
---

# Docs research slice rules

- Treat these files as evidence or governance surfaces unless the task explicitly says otherwise.
- Keep authority order unchanged: user request, `.github/copilot-instructions.md`, `docs/OPUS_46_GOVERNANCE.md`, `AGENTS.md`.
- Prefer the smallest admissible slice. Do not widen subject, lane, or claims.
- Reuse existing terminology: `editor worker`, `autonomous slice worker`, `dispatch`, `envelope`, `bounded slice`.
- Separate `observed`, `inferred`, and `unverified` when a document reports findings.
- For docs-only updates, say what changed and what did not change. Do not imply runtime readiness, promotion, or shared-truth authority unless the task explicitly authorizes it.
- Link to SSOT docs instead of duplicating long governance text when a pointer is enough.
- If a document is historical, preserve its historical framing instead of rewriting it as current live instruction.
- Stop and escalate if the requested edit would modify governance precedence, resolved mode rules, or high-sensitivity runtime expectations.
