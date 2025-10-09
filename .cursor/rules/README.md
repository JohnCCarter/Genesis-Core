# Project Rules Documentation

## File Structure

### `cursor-active-rules.mdc` (Active Rules)
- **Purpose**: Active rules loaded by Cursor AI (`alwaysApply: true`)
- **Content**: Core principles, workflow, and essential guidelines
- **Usage**: Automatically applied in every Cursor session
- **Size**: Concise (~85 lines) for quick reference

### `reference-guide.md` (Reference Documentation)
- **Purpose**: Comprehensive project documentation and guidelines
- **Content**: Detailed rules, architecture, standards, and examples
- **Usage**: Reference when detailed information is needed
- **Size**: Extensive (~220 lines) with full context

## Rule Hierarchy

```
cursor-active-rules.mdc    ← Active rules (Cursor loads this)
    ↓
reference-guide.md         ← Full documentation (reference)
```

## When to Update

### Update BOTH files when:
- Core principles change
- Security rules are modified
- Development workflow changes
- Critical patterns are established

### Update ONLY reference-guide.md when:
- Adding detailed examples
- Expanding troubleshooting sections
- Adding architectural details
- Documenting complex patterns

## Syncing Rules

When updating common sections, ensure consistency between:
- cursor-active-rules.mdc (concise)
- reference-guide.md (detailed)

Common sections to sync:
- Core Principles
- Security Rules
- Development Workflow
- FastAPI Endpoints
- Common Issues

---
**Last Updated**: 2025-10-09

