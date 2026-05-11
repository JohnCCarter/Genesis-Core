---
name: "Tooling slices"
description: "Use when editing Genesis-Core workspace customizations, prompt files, instruction files, workflow metadata, or explicitly requested MCP config surfaces."
applyTo: "{.github/**/*.md,.github/**/*.yml,.github/**/*.yaml,.github/**/*.json,config/mcp_settings*.json}"
---

# Tooling slice rules

- Treat `.github/**` as workspace customization surfaces for editor-agent operations. They may reference existing SSOT docs and runbooks, but they do not become new governance SSOT.
- Treat `config/mcp_settings*.json` as separate Genesis-Core MCP server config surfaces only when a task explicitly includes them.
- Do not imply that editor-agent prompt or instruction discovery depends on the Genesis-Core MCP server; VS Code discovers `.github/prompts/**` and `.github/instructions/**` natively.
- Keep diffs minimal and preserve the intended behavior of the current tooling or config surface.
- New prompt and instruction files should be thin adapters to existing SSOT docs and runbooks; link to them instead of restating full governance.
- Prefer prompt files for reusable bounded work orders and `.instructions.md` files for path- or task-specific rules. Do not create a new custom agent unless tool restrictions or context isolation are actually required.
- Keep YAML frontmatter valid and concise. Descriptions should include specific and unambiguous trigger phrases the agent can match reliably.
- If YAML frontmatter is malformed, fix the frontmatter in the touched customization file before making deeper customization changes.
- When editing MCP settings, limit the change to the declared MCP objective. Do not broaden allowed paths, blocked patterns, or tool permissions beyond the exact need.
- Do not introduce standing worker identities, self-dispatch authority, hidden automation assumptions, or implied MCP dependencies in workspace customizations.
- If a tooling change would alter runtime behavior, governance precedence, shared-truth write paths, or MCP server authority without explicit scope, stop and revert the unintended change or escalate before proceeding.
