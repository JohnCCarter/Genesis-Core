# Skill Governance Charter (A′ additive-only)

Last update: 2026-02-28

## Purpose

This charter defines how JSON skills are governed in Genesis-Core to allow controlled autonomy without contract drift.

- **Opus 4.6** is the **SPEC owner** (contract/governance authority).
- **Codex 5.3** is the **RUNNER owner** (implementation/execution authority).

The system is **A′ (additive-only)**: skills may propose additive improvements, but may not mutate PASS definitions or broaden scope.

## Operational alignment and precedence

This charter governs **skill evolution**. Day-to-day implementation protocol is defined in
`.github/copilot-instructions.md` (including quick path, full gated protocol, and Opus engagement matrix).

If instruction conflicts appear, use repository precedence:

1. Explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

Quick path is allowed only for trivial changes per `.github/copilot-instructions.md`.
If quick-path eligibility is uncertain, escalate to full protocol and governance review.

## Skill families

### 1) SPEC

Contract-defining skill.

- PASS definition is locked.
- Scope is locked.
- Must/must_not semantics are authoritative.
- Any change affecting PASS/scope requires explicit governance review.

### 2) RUNNER

Execution/evidence skill bound to a SPEC contract.

- May improve execution reliability and evidence capture.
- May add non-breaking diagnostics, selectors, or artifacts.
- Must not alter PASS definition or allowed surfaces.

### 3) PLAYBOOK

Operational guidance only (prefer Markdown).

- No executable PASS change.
- No contract mutation.

## Scope principle

Allowed changes are limited to explicit skill surfaces (JSON metadata, execution wiring, documentation). Forbidden changes include:

- runtime default drift
- API contract drift
- scope broadening
- weakening must_not rules

## PASS stability and determinism

PASS definitions are stability-critical and treated as immutable contract surface.

- Determinism is required for comparable evidence.
- Equivalent inputs must produce equivalent governance outcomes.
- If drift is detected, stop and escalate.

## A′ evolution model (proposal, not mutation)

Allowed evolution is additive-only:

- add diagnostics/evidence artifacts
- improve failure observability
- tighten validation for existing contract

Not allowed:

- redefining PASS
- expanding contract scope
- relaxing must_not constraints

## Versioning rules

- **PATCH**: additive metadata/evidence improvements; no PASS/scope changes.
- **MINOR**: additive capabilities that remain contract-compatible and governance-approved.
- **MAJOR**: any intentional contract/PASS/scope break (requires explicit approved contract exception).
  The exception must be traceable in commit-contract and Opus verdict evidence.

## Research isolation and promotion

Research or branch-local skill updates must remain isolated until governance review is complete.

Promotion rule:

1. Validate in research/dev surface.
2. Produce deterministic evidence.
3. Obtain governance approval.
4. Promote without altering locked PASS/scope semantics.

## Ambiguity rule

If skill type is ambiguous, default to **SPEC** (safer) and record a TODO for governance clarification.
