# Genesis Topology Work Queue

Date: 2026-05-22
Status: `derivative work queue / non-authorizing / docs-only planning aid / no behavior change`

> This file is a queue/controller artifact only. It does **not** authorize edits, archive moves,
> reclassification, deletes, runtime changes, or governance overrides by itself.
>
> Use sequence:
>
> 1. zone-level map
> 2. batch audit
> 3. risk bucket
> 4. batch patch
> 5. review
>
> Higher-order governance and explicit user request still control.

## Operating rule

Use `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md` as the zone-level controller,
not as a file-by-file blocker.

Batching rule:

- `GREEN` — status/header/routing/non-authorizing clarification work
- `YELLOW` — reference-audited archive/move/lifecycle work
- `RED` — runtime/config/authority/promotion-adjacent work

If a batch produces no patch-safe candidates, stop at the audit artifact and queue the next admissible
follow-up rather than forcing a cosmetic patch.

## Batch 001 — plan/\*\* historical roadmaps

- Zone: `plan/`
- Default speed/risk bucket: `YELLOW`
- Current artifact: `docs/audit/archive_move_reference_audit_batch_001.md`
- Focus: historical roadmap candidates already surfaced as `MOVE_TO_ARCHIVE_LATER` or `SUPERSEDE_WITH_POINTER`
- Current result: mixed bucket (`READY_ARCHIVE_MOVE`, `KEEP_PROVENANCE`, `BLOCKED_REFERENCE_FOUND`)
- Next admissible step: separate move-class slice only where the reference surface is small enough

## Batch 002 — docs/analysis/\*\* non-authorizing status gaps

- Zone: `docs/analysis/`
- Default speed/risk bucket: `GREEN`
- Focus: add or sharpen non-authorizing / historical routing notes where analysis surfaces still read like live work orders
- Expected outputs: status-header audit, small header/pointer patch batches
- Guardrail: do not rewrite research conclusions or reframe bounded evidence as current authority

## Batch 003 — docs/decisions/\*\* slice-local / historical decisions

- Zone: `docs/decisions/`
- Default speed/risk bucket: `GREEN` to `YELLOW` depending on packet fan-out
- Focus: identify decision packets that are historical, branch-local, or slice-local but still read as current governance instructions
- Expected outputs: status-header audit, historical decision pointer batches
- Guardrail: do not alter governance precedence or packet conclusions

## Batch 004 — docs/audit/\*\* evidence-only classification

- Zone: `docs/audit/`
- Default speed/risk bucket: `GREEN`
- Focus: classify audit/signoff/evidence documents that need clearer evidence-only framing
- Expected outputs: evidence-only status/header batches, retained historical framing patches
- Guardrail: do not turn audit docs into new authority surfaces

## Batch 005 — archive candidates

- Zone: `docs/archive/` plus historical files outside archive taxonomy
- Default speed/risk bucket: `YELLOW`
- Current artifact: `docs/audit/archive_move_preflight_batch_005.md`
- Focus: determine which already-historical surfaces are ready for archive placement versus still needed as active provenance anchors
- Expected outputs: archive move reference audits, move-ready buckets
- Current result: the smallest move-ready candidate remains `plan/ri-family-admission-roadmap-2026-03-24.md`, but execution is deferred because a required provenance reference surface is locally modified
- Next admissible step: open the bounded move-class slice once `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` is clean or explicitly in scope
- Guardrail: no move without inbound-reference and map/provenance checks

## Batch 006 — config classification

- Zone: `config/` and config-adjacent documentation surfaces
- Default speed/risk bucket: `RED`
- Focus: separate live authority, retained reference, legacy/superseded config notes, and non-authorizing documentation around config behavior
- Expected outputs: classification audit only unless a stricter governed slice is explicitly opened
- Guardrail: do not change config semantics, live-update authority, or default interpretation in a docs batch

## Batch 007 — scripts lifecycle

- Zone: `scripts/`
- Default speed/risk bucket: `YELLOW`
- Focus: classify active, deprecated, archived, and retained-support scripts and the docs that describe them
- Expected outputs: lifecycle inventory, docs-only routing/status batches, later archive-prep recommendations
- Guardrail: do not move or rewrite script behavior in the audit/controller phase

## Queue discipline

- keep batches small and zone-bounded
- prefer one audit artifact per batch before any patch burst
- patch only the classes explicitly allowed by the audit bucket
- leave unrelated local changes untouched
- if a candidate is ambiguous, classify it fail-closed and move on
