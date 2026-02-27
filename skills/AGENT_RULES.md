# Agent Rules for Skill Governance (A′)

## Shared rules

- Follow additive-only evolution.
- Do not mutate PASS definition.
- Do not broaden scope.
- Do not weaken must_not rules.
- Stop on detected contract/default drift.
- If ambiguous, classify as SPEC and request governance review.

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
Impact: no contract change
Suggested change: ...
Evidence: ...
Requires: governance review (Opus)
```
