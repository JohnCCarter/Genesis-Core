<!-- Generated from global-rules.mdc and workspace-rules.mdc -->

# Genesis-Core Combined Rules

## GLOBAL RULES (User-Assistant Interaction)

### Master Rule: Context Management

If the current chat approaches context limits, stop and request a new chat session. Include a short summary of where we are and the next steps.

### Working Principles

- **Methodical Approach**: Always work step by step. Do not rush.
- **Clear Commands**: Provide clear, concise commands (PowerShell/Bash) and examples.
- **Separation**: Separate “Discussion” from “Code/Commands”.
- **Transparency**: Be transparent about uncertainties.
- **Completion**: Confirm when something is completed (e.g., ✅ Fixed).
- **Language**: Prefer Swedish responses unless specified otherwise.

### Plan Mode Recommendations

Proactively suggest activating Plan Mode when:

- New features or architectural decisions are requested.
- Large refactorings spanning multiple files (3+ files).
- Complex changes requiring multiple implementation paths.

---

## WORKSPACE RULES (Genesis-Core Technical)

### Stabilization Phase Policy

**Code stability > New features**. Every line of code must either:
✅ Solve a concrete problem OR ✅ Increase reliability, performance, or readability

### Change Policy

- **Bug fixes**: ✅ Always allowed - Write test immediately after.
- **Refactoring**: ✅ Small, documented steps without behavior change.
- **New features**: ⚠️ Only after clear specification and justification.
- **Experimental**: 🚫 Separate branch only.

### Code Standards

- **Python**: 3.11+ (modern syntax, dict not Dict, X|None not Optional[X]).
- **Style**: Line length 100 chars, black formatting, ruff linting.
- **Structure**: `src/core/{config,indicators,io,observability,risk,strategy,utils}`.
- **Testing**: pytest with comprehensive coverage.
- **No Emojis in Code**: Do not use emojis in source files.

### Critical Security Rules

- **NEVER commit**: `.env`, `.nonce_tracker.json`, `dev.overrides.local.json`.
- **Secrets**: API keys only from environment variables.
- **Safety**: Force TEST symbols for paper trading.
- **Signing**: Use compact JSON: `json.dumps(body, separators=(",",":"))`.

### Development Workflow

1. **Research**: `read_file` → `codebase_search` → `grep` → `todo_write`.
2. **Edit**: Use edit tools (never output code). Prefer editing over creating.
3. **Verify**: `pytest` → `black --check` → `ruff check` → `bandit`.
4. **Docs**: Check existing `README.md`/`AGENTS.md` before creating new ones.

### FastAPI Endpoints

`/ui`, `/strategy/evaluate`, `/public/candles`, `/auth/check`, `/paper/submit`, `/debug/auth`

### Common Issues

- "invalid key": Check JSON serialization.
- "Ingen giltig order": Verify model exists.
- Nonce errors: Use `bump_nonce()`.
