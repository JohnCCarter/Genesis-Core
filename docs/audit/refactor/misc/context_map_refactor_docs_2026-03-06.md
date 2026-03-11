## Context Map â€” Refactor Docs Track (Batch 1)

### Files to modify

| File                                                             | Purpose                                   | Planned change                                         |
| ---------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------ |
| `docs/audit/refactor/readme.md`                                  | Entry point/index for refactor phase docs | Expand into actionable index with active artifact list |
| `docs/audit/refactor/command_packet_refactor_docs_2026-03-06.md` | Batch-level governance contract           | Define docs-only scope and stop conditions             |
| `docs/audit/refactor/context_map_refactor_docs_2026-03-06.md`    | Discovery map for docs track              | Capture files, dependencies, and risks                 |

### Read-only references

| File                                                                | Relationship                                                 |
| ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `docs/audit/refactor/command_packet_shard_a_refactor_2026-03-06.md` | Existing script-focused contract (historical/parallel track) |
| `docs/audit/refactor/context_map_shard_a_refactor_2026-03-06.md`    | Existing script-focused context map                          |
| `docs/audit/refactor/overlays/genesis_refactor_agent_overlay_shard_a.md`     | Shard A overlay policy                                       |
| `docs/audit/cleanup/*`                                              | Historical baseline; read-only in this batch                 |

### Risks

- [ ] Mixing docs-track contract with script-track contract
- [ ] Accidental edits outside `docs/audit/refactor/**`
- [ ] Ambiguous ownership of cleanup vs refactor evidence

### Batch-specific parity rule

- Documentation changes must not imply or claim runtime behavior changes.
- Existing script-focused refactor evidence remains intact and readable.
