# Agent Rules for Skill Governance (A′)

Last update: 2026-02-28

## Shared rules

- Follow additive-only evolution.
- Do not mutate PASS definition.
- Do not broaden scope.
- Do not weaken must_not rules.
- Stop on detected contract/default drift.
- If ambiguous, classify as SPEC and request governance review.
- This file governs skill-contract boundaries; day-to-day implementation protocol is defined in `.github/copilot-instructions.md`.
- Follow repository precedence on conflicts: user request -> `.github/copilot-instructions.md` -> `docs/OPUS_46_GOVERNANCE.md` -> `AGENTS.md`.
- Quick path is allowed only for trivial changes per `.github/copilot-instructions.md`; if uncertain, escalate to full protocol.

## Opus 4.6 (SPEC owner)

Responsibilities:

- Own contract boundaries and PASS definition.
- Approve/reject scope changes.
- Enforce determinism and no-drift guarantees.
- Audit additive proposals before adoption.

Reject conditions:

- attempted PASS redefinition
- attempted scope broadening
- runtime/API default drift
- weakening must_not constraints
- unverifiable or non-deterministic evidence

## Codex 5.3 (RUNNER owner)

Allowed additive changes:

- improve execution reliability
- improve evidence collection/diagnostics
- improve deterministic failure visibility
- add non-breaking selectors/artifact hooks

Not allowed:

- changing PASS contract semantics
- changing locked scope
- introducing runtime/API behavior drift

## Proposal template

```text
[SKILL-PROPOSAL]
Type: Additive improvement
Reason: repeated failure pattern detected
Scope: within allowed_surfaces
Scope IN/OUT: ...
Path: quick-path | full-protocol
Behavior: No behavior change | Behavior change candidate
Impact: no contract change
Suggested change: ...
Evidence: ...
Verification: minimal checks | full gates
Requires: governance review (Opus)
```
