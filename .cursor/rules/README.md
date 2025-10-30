# Project Rules Documentation

## File Structure

### `cursor-active-rules.mdc` (Active Rules)
- **Purpose**: Active rules loaded av Cursor AI (`alwaysApply: true`)
- **Content**: Komprimerade basinstruktioner + hänvisningar till referensguiden
- **Metadata**: Inkluderar `description` för tydlig identifiering
- **Usage**: Automatisk kontext i varje session
- **Size**: Kompakt (~50 rader) för snabb läsning

### `reference-guide.md` (Reference Documentation)
- **Purpose**: Omfattande projektregler och riktlinjer
- **Content**: Detaljerade regler, arkitektur, standarder och exempel
- **Usage**: Slå upp när mer kontext behövs
- **Size**: Utförlig (~280 rader) med full kontext

### `AGENTS.md` (Handoff & status)
- **Purpose**: Snabb översikt för nästa agent
- **Content**: Senaste leveranser, experiment, arbetsflöde och nästa steg
- **Usage**: Läs vid handoff eller när projektläget behöver uppdateras
- **Size**: Beror på aktuell status (uppdateras vid handoff)

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
- cursor-active-rules.mdc (sammandrag)
- reference-guide.md (detaljer)

Common sections to sync:
- Core Principles
- Security Rules
- Development Workflow
- FastAPI Endpoints
- Common Issues

---
**Last Updated**: 2025-10-30
