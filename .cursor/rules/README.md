# Project Rules Documentation

## File Structure

### `global-rules.mdc` (Global Rules)

- **Purpose**: General behavioral rules for the AI assistant
- **Content**: Language choice, Plan Mode triggers, working principles
- **Usage**: Applied everywhere to ensure consistent collaboration style

### `workspace-rules.mdc` (Genesis-Core Rules)

- **Purpose**: Project-specific technical rules
- **Content**: Tech stack, stabilization policy, security, API endpoints, and repo governance (agents/skills/registry)
- **Usage**: Applied specifically when working on Genesis-Core code

### `architecture.md` (Architecture & Reference)

- **Purpose**: Comprehensive project documentation and guidelines
- **Content**: Architecture, API reference, configuration details
- **Usage**: Reference when detailed information is needed

### `.github/copilot-instructions.md` (Operating Contract)

- **Purpose**: Practical governance contract for day-to-day agent operation
- **Content**: Commit protocol, quick path for trivial changes, Opus engagement matrix, gate expectations
- **Usage**: Primary operational reference for non-trivial changes and conflict resolution

### `.github/agents/*.agent.md` and `.cursor/skills/*/SKILL.md` (Role Specs)

- **Purpose**: Role-specific execution specs for Codex/Opus across tools
- **Content**: Responsibilities, non-negotiables, verdict/output contract, mode controller
- **Usage**: Must remain aligned with `.github/copilot-instructions.md`

### `CHANGELOG.md` (Project History)

- **Purpose**: Human-readable history of verified project changes from current baseline forward
- **Content**: Dated, concise entries for shipped or agreed changes
- **Usage**: Informational only; not a policy source of truth
- **Legacy**: Pre-reset history marker is `docs/archive/CHANGELOG-legacy.md` (full history remains in git)

## Rule Hierarchy

```
global-rules.mdc                    ← Behavior & Workflow
workspace-rules.mdc                 ← Project Tech & Security
    ↓
.github/copilot-instructions.md     ← Operating Contract (day-to-day)
    ↓
.github/agents/*.agent.md           ← Role execution specs
.cursor/skills/*/SKILL.md           ← Cursor mirrors of role specs
    ↓
architecture.md                     ← Full documentation (reference)
```

## When to Update

### Update `global-rules.mdc` when:

- Interaction style needs to change
- New general workflow steps are added

### Update `workspace-rules.mdc` when:

- Tech stack changes
- Security policies are updated
- Key endpoints or files change

### Update `architecture.md` when:

- Adding architectural details
- Expanding troubleshooting sections
- Documenting complex patterns

### Update `.github/copilot-instructions.md` when:

- Commit protocol or gate policy changes
- Quick-path criteria changes
- Opus engagement requirements change

### Update `.github/agents/*.agent.md` and `.cursor/skills/*/SKILL.md` when:

- Role responsibilities or output contracts change
- Verdict taxonomy changes (for example `APPROVED_WITH_NOTES`)
- Gate policy wording must mirror operating contract

### Update `CHANGELOG.md` when:

- A verified change is introduced or completed
- You need a concise human-facing release/history note
- The entry can be written without redefining policy or governance rules

## Syncing Rules

When updating common sections, ensure consistency between:

- `workspace-rules.mdc` (concise)
- `architecture.md` (detailed)
- `.github/copilot-instructions.md` (operational contract)
- `.github/agents/*.agent.md` and `.cursor/skills/*/SKILL.md` (mirrored role specs)
- `CHANGELOG.md` (informational history, non-SSOT)

Suggested order:

1. Update `.github/copilot-instructions.md` first
2. Mirror changes to `.github/agents/*.agent.md`
3. Mirror equivalent changes to `.cursor/skills/*/SKILL.md`
4. Update this README if hierarchy or ownership changed

---

**Last Updated**: 2026-02-28
