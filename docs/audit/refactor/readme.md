# Audit Refactor Phase

This folder is the active workspace for refactor-phase audit notes, command packets, and context maps.

## Folder policy

- Cleanup-phase artifacts belong under `docs/audit/cleanup/`.
- Refactor-phase artifacts belong under `docs/audit/refactor/`.
- Do not mix cleanup lock/evidence with refactor design notes.

For Shard A historical cleanup governance, see:

- `docs/audit/cleanup/hard_rules_cleanup.md`
- `docs/audit/cleanup/Genesis_cleanup_agent_overlay.md`
- `docs/audit/cleanup/genesis_cleanup_agent_overlay_shard_a.md`

## Active artifacts in this folder

### Shared baseline

- `hard_rules_refactor.md`
  Shared fail-closed baseline for refactor governance across shards.

### Refactor governance overlays

- `genesis_refactor_agent_overlay_shard_a.md`
  Shard A refactor policy (scope, validation model, forbidden actions).

### Existing script-track artifacts

- `command_packet_shard_a_refactor_2026-03-06.md`
  Script-focused command packet for Shard A batch work.
- `context_map_shard_a_refactor_2026-03-06.md`
  Script-focused context map for the same batch.

### Docs-track artifacts (this working stream)

- `command_packet_refactor_docs_2026-03-06.md`
  Docs-only command packet to keep refactor documentation work scoped.
- `context_map_refactor_docs_2026-03-06.md`
  Context map for docs-only refactor governance updates.

## Working rules for this stream

1. Edit only under `docs/audit/refactor/**` unless a new contract explicitly expands scope.
2. Treat `docs/audit/cleanup/**` as read-only historical baseline.
3. Keep changes no-behavior-change and documentation-only unless a separate implementation packet says otherwise.
