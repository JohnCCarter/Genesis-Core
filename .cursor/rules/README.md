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

## Rule Hierarchy

```
global-rules.mdc       ← Behavior & Workflow
workspace-rules.mdc    ← Project Tech & Security
    ↓
architecture.md        ← Full documentation (reference)
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

## Syncing Rules

When updating common sections, ensure consistency between:

- `workspace-rules.mdc` (concise)
- `architecture.md` (detailed)

---

**Last Updated**: 2026-01-15
