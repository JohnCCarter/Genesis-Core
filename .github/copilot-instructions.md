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

### Context7 (MCP) auto-docs rule

To avoid needing the user to type “use context7” in every prompt:

- When a question involves **external libraries/APIs** (especially known pain points like **Optuna** and **Pydantic**), automatically consult Context7 docs via MCP before finalizing an answer.
- Prefer Context7 for API signatures, defaults, gotchas, and migration notes (e.g., Pydantic v1→v2, Optuna storage/heartbeat/sampler/pruner args).
- Do **not** use Context7 for questions that are purely about Genesis-Core internal code; use workspace search/read instead.

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

### Git LFS (results sharing policy)

- Use Git LFS **only** for curated, noteworthy result bundles (policy B).
- Location/pattern: `results/archive/bundles/*.zip` (tracked via `.gitattributes`).
- Do **not** LFS-track raw `results/**`, `*.db`, `cache/**`, or large intermediate artifacts unless explicitly agreed.
- Bundles must be minimal and reproducible: include config(s) + a short summary/provenance; never include secrets.
- Prefer adding an anchor in `docs/daily_summaries/` pointing to the bundle filename and run identifiers.

### Phase discipline (Implementation vs Validation vs Optimization)

To avoid “we changed something but can’t prove what/why” regressions, keep work explicitly in one of these phases:

- **Implementation (code/config changes)**
  - Goal: change behavior or reliability.
  - Requirements: small diffs, add/adjust unit tests immediately.
  - Avoid long runs; focus on fast, deterministic checks.

- **Validation (prove behavior on a fixed window)**
  - Goal: prove that a specific code/config state produces expected results.
  - Requirements: record _what was run_ (config path, symbol/timeframe, start/end, canonical env flags) and _what happened_ (key metrics + run_id).
  - Artifacts: do **not** rely on `results/**` being committed (most of it is gitignored). Prefer committing a small summary under
    `results/evaluation/` and/or an anchor note in `docs/daily_summaries/`.

- **Optimization (Optuna/backtest campaigns)**
  - Goal: explore parameter space; produce candidates.
  - Requirements (before >30 min runs): preflight + validate config, baseline run with champion params, canonical comparability.
  - Artifacts: keep raw runs local/ignored; for cross-machine sharing use a curated zip bundle under `results/archive/bundles/*.zip`
    (LFS-tracked) + a short pointer/summary in `docs/daily_summaries/`.

### Development Workflow

1. **Research**: `read_file` → `codebase_search` → `grep` → `todo_write`.
2. **Edit**: Use edit tools (never output code). Prefer editing over creating.
3. **Verify**: `pytest` → `black --check` → `ruff check` → `bandit`.
4. **Docs**: Check existing `README.md`/`AGENTS.md` before creating new ones.

### Repo Governance (Agents, Skills, Registry)

- **Repo-local subagents** live under `.github/agents/` and define bounded roles (planning, audit, governance QA, ops runs).
  Prefer these over editing any editor/extension-bundled agent files.
- **Skills** are defined under `.github/skills/` and referenced by repo governance.
- **Registry** lives under `registry/` (manifests/schemas/compacts/audit). If you change registry content, run
  `python scripts/validate_registry.py`.

### FastAPI Endpoints

`/ui`, `/strategy/evaluate`, `/public/candles`, `/auth/check`, `/paper/submit`, `/debug/auth`, `/health`, `/metrics`,
`/account/wallets`, `/account/positions`, `/account/orders`, `/config/runtime`, `/config/runtime/validate`,
`/config/runtime/propose`

### Common Issues

- "invalid key": Check JSON serialization.
- "Ingen giltig order": Verify model exists.
- Nonce errors: Use `bump_nonce()`.
