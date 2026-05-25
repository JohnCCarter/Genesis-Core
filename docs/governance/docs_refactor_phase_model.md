# Docs refactor phase model

Date: 2026-05-22
Status: `operational guidance / docs-only / non-authorizing / no-runtime-authority`

This document is practical workflow guidance for phasing documentation refactor work in Genesis-Core.

It does **not** change:

- governance precedence (`.github/copilot-instructions.md` remains the practical SSOT)
- governance mode resolution (`docs/governance_mode.md` remains SSOT)
- authority classification rules in the derivative knowledge layer
- the requirement for separate governed slices before move/archive/delete actions

This is a docs-refactor phase model, not a new authority layer.

## Purpose

The repository needs a cheaper way to reduce wrong context and docs sprawl without losing evidence, provenance, or governance safety.

The purpose of this model is therefore to separate three different kinds of documentation refactor work that otherwise drift together:

1. safe framing and routing changes
2. structural refactor actions that can alter paths or reader entry points
3. destructive cleanup actions that can remove evidence or lineage if handled carelessly

The operating principle is simple:

- clarify fast
- move carefully
- delete only with proof

## What this model is not

This document does **not**:

- authorize deletion by itself
- authorize archive moves by itself
- authorize renames, merges, or path changes by itself
- replace reference checks or canonical-path checks
- replace command packets, governed slices, or review where those are otherwise required
- prove that a document has no evidentiary, provenance, or lineage value

If a cited source conflicts with this model, the cited source controls.

## Relationship to current docs surfaces

Use this model together with the existing orientation and audit surfaces:

- `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md` for zone-level speed/risk orientation
- `docs/audit/DOCUMENTATION_DISPOSITION_MAP.md` for evidence-backed disposition recommendations on explicitly reviewed documents
- `docs/CURRENT_AUTHORITY_INDEX.md` for bounded current-use classification of selected surfaces
- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` for documentation-surface provenance/orientation context

Those surfaces help orientation and planning.
They do **not** silently authorize move/archive/delete actions.

## GREEN phase — safe docs-only clarification

### Purpose

Use `GREEN` when the change is documentation-only and no behavior change is possible.
The goal is to reduce reader confusion immediately without changing document placement, canonical paths, or evidence retention.

### Typical GREEN actions

- add top-level status headers
- add authority notes and routing notes
- mark documents as `historical`, `dormant`, or `non-authorizing` when directly supported
- add source-backed superseded pointers
- update routing maps
- update disposition maps
- sharpen provenance disclaimers
- add explicit `UNRESOLVED` or `UNKNOWN_KEEP` boundaries when support is incomplete

### GREEN guardrails

`GREEN` work must remain:

- docs-only
- non-runtime
- non-config
- non-test
- non-promotional
- non-deleting
- non-authorizing unless explicitly bounded by the task

### GREEN must not

`GREEN` must not, by implication or convenience:

- move documents
- rename documents
- merge documents into a new canonical target
- delete documents
- rewrite historical evidence into current live instruction
- create new authority from routing or mapping surfaces

## YELLOW phase — structural docs refactor with checks first

### Purpose

Use `YELLOW` when the action is still docs-focused, but it can alter paths, references, reader entry points, or canonical interpretation if done casually.

This includes actions that are allowed, but only after explicit checks.

### Typical YELLOW actions

- move documents into archive taxonomy
- rename documents or folders
- merge overlapping documents into one retained canonical target
- relocate documents between zones
- add stronger supersession pointers as part of a move/merge slice

### Required YELLOW checks

Before a `YELLOW` action, verify at minimum:

1. **path checks** — no important inbound path references are silently broken
2. **reference checks** — docs, packets, inventories, templates, and adjacent artifacts are updated or explicitly retained
3. **canonical checks** — the target or successor is explicit rather than inferred from folder placement alone
4. **provenance checks** — historical, evidentiary, branch-specific, or lineage value is preserved
5. **reader-entry checks** — the move/rename does not destroy the safest route for a later reader to understand current vs historical context

### YELLOW fail-closed rule

If any of the checks above are incomplete, conflicting, or hard to prove quickly, do **not** force the action downward into `GREEN`.
Keep it as `YELLOW`, pause, and hold the surface as `UNKNOWN_KEEP`, `UNRESOLVED`, or a later candidate until the checks are done.

## RED phase — deletion only with strict evidence

### Purpose

Use `RED` only when the proposed action is deletion or another irreversible removal of a documentation surface.

Deletion is intentionally expensive because missing documentation can erase provenance, hide historical reasoning, or break later evidence interpretation.

### RED evidence floor

Delete only when all are directly supported:

1. the document has **no active governance or current-use role**
2. the document has **no canonical role** as a retained target, source, or required pointer
3. the document has **no evidentiary value** for audits, signoffs, investigations, or bounded historical claims
4. the document has **no provenance or lineage value** for explaining how a current surface came to be
5. the document has **no required inbound references** or retained path expectations
6. duplication, abandonment, or supersession is explicit rather than merely convenient to assume

### RED fail-closed rule

If any one of the items above is uncertain, the safe action is **not** delete.
Use `UNKNOWN_KEEP`, retain the document, and open a later bounded slice if cleanup still appears worthwhile.

## Practical checklist

When deciding a docs refactor action, ask in order:

1. Is this only a status/routing/framing clarification with no path or evidence loss risk?
   - If yes, it is probably `GREEN`.
2. Does this alter paths, names, archive placement, or canonical reader entry points?
   - If yes, it is probably `YELLOW` and needs checks first.
3. Does this remove a document entirely?
   - If yes, it is `RED` and requires strict evidence.
4. Is the support mixed, ambiguous, or incomplete?
   - If yes, bias upward and fail closed rather than forcing a cheaper phase.

## Safe defaults

When in doubt:

- prefer `KEEP` over speculative cleanup
- prefer `UNKNOWN_KEEP` over delete
- prefer explicit pointers over silent relocation
- prefer a later bounded slice over an all-at-once cleanup wave

## Bottom line

Genesis-Core should reduce wrong context quickly, but not by erasing evidence or inventing certainty.

Use:

- `GREEN` for safe docs-only clarification
- `YELLOW` for move/archive/rename/merge work after reference checks
- `RED` for deletion only when strict evidence shows the document has no active, canonical, evidentiary, provenance, or lineage value
