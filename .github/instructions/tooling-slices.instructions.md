---
name: "Tooling slices"
description: "Use when editing Genesis-Core workspace customizations, prompt files, instruction files, workflow metadata, or MCP path-parity config for editor-agent operations."
applyTo: "{.github/**/*.md,.github/**/*.yml,.github/**/*.yaml,.github/**/*.json,config/mcp_settings*.json}"
---

# Tooling slice rules

- Treat `.github/**` and `config/mcp_settings*.json` as operational tooling surfaces, not as new governance SSOT.
- Keep diffs minimal and parity-oriented.
- New prompt and instruction files should be thin adapters to existing SSOT docs and runbooks; link to them instead of restating full governance.
- Prefer prompt files for reusable bounded work orders and `.instructions.md` files for path- or task-specific rules. Do not create a new custom agent unless tool restrictions or context isolation are actually required.
- Keep YAML frontmatter valid and concise. Descriptions should include clear trigger phrases the agent can match.
- When editing MCP settings, limit the change to the declared path or tool parity objective. Do not broaden allowed paths or blocked patterns beyond the exact need.
- Do not introduce standing worker identities, self-dispatch authority, or hidden automation assumptions in workspace customizations.
- If a tooling change would alter runtime behavior, governance precedence, or shared-truth write paths, stop and escalate.
