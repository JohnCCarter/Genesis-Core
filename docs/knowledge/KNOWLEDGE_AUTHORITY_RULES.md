# Knowledge Authority Rules

> This document is derivative and citation-bound. It routes to existing canonical artifacts and does not create new authority, readiness, or research conclusions.

## Purpose

This file is the rulebook for the bounded Knowledge Authority Layer introduced in this slice.
It governs only the derivative surfaces below:

- `docs/CURRENT_AUTHORITY_INDEX.md`
- `docs/knowledge/CANONICAL_KNOWLEDGE_REGISTER.md`
- `docs/knowledge/RESEARCH_LINEAGE_MAP.md`
- `docs/knowledge/EDGE_MAP.md`

It does **not** override repository governance SSOT.

Canonical support:

- `.github/copilot-instructions.md` (`Source of truth`)
- `docs/governance_mode.md` (`Fail-closed policy`)
- `docs/OPUS_46_GOVERNANCE.md` (`Kanonisk referens är .github/copilot-instructions.md`)
- `AGENTS.md` (`Authority precedence in conflicts`)

## Source hierarchy for this layer

For this derivative layer, authority must be read in the following order:

1. explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`
5. use `docs/governance_mode.md` as the SSOT only when the claim concerns governance mode resolution or mode-specific operating expectations; outside that claim type it does not reorder the general authority chain
6. cited canonical artifact for the specific classified item
7. this layer's derivative routing documents

This layer may classify existing knowledge.
It may **not** create new knowledge.

Canonical support:

- `.github/copilot-instructions.md` (`Source of truth`)
- `docs/governance_mode.md` (`This document is the single source of truth (SSOT) for Governance Mode resolution and policy enforcement`)
- `AGENTS.md` (`Authority precedence in conflicts`)

## Core rules

### Rule 1 — Derivative only

These files may classify, point, mark, and link.
They may not synthesize multiple documents into a new active conclusion.

Canonical support:

- `docs/README.md` (`Den här README:n är den praktiska kartan... Den är inte en egen SSOT`)
- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` (`What this model is not`)

### Rule 2 — Fail closed

If support is incomplete, conflicting, or ambiguous, classification must be `UNRESOLVED`.
No silent fallback status is allowed.

Canonical support:

- `docs/governance_mode.md` (`Fail-closed policy`)
- `docs/governance_mode.md` (`If no prior rule resolves a mode, use STRICT`)

### Rule 3 — No silent inheritance

Authority may not be inferred from:

- recency alone
- filename prominence
- directory location alone
- repeated citation frequency
- broad narrative convenience

Canonical support:

- `docs/README.md` (`Historiska dokument kan fortfarande ligga i äldre mappar`)
- `docs/governance/README.md` (`Äldre material i andra ytor ska fortfarande läsas med respekt för innehållets faktiska roll, inte enbart efter mappnamnet`)

### Rule 4 — Artifact and conclusion are classified separately

A document surface may be active, dormant, or non-authorizing as a surface without making every statement inside it independently authoritative.
A register entry must therefore classify a bounded conclusion explicitly rather than inherit status silently from the file.

Canonical support:

- `docs/README.md` (`Separera alltid följande roller`)
- `docs/README.md` (`Analysis- och evidensnoter förblir icke-auktoriserande i sig`)

### Rule 5 — `ACTIVE` is expensive

A conclusion may be `ACTIVE` only when all are true:

- it has a clear canonical artifact reference
- it is not explicitly superseded
- it does not depend on ambiguous synthesis
- its decision impact is explicitly classified
- inferred or unverified material does not carry the authority

This is a layer-local rule for `docs/knowledge/**` and `docs/CURRENT_AUTHORITY_INDEX.md`.

### Rule 6 — `NON_AUTHORIZING` is strong

`NON_AUTHORIZING` means a surface or conclusion may be informative, historical, or evidentiary, but must not be used as active authority for decisions, promotion, readiness, runtime behavior, or behavior interpretation.

Canonical support:

- `docs/README.md` (`Analysis- och evidensnoter förblir icke-auktoriserande i sig`)
- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` (`What this model is not`)
- `docs/governance/README.md` (`Operativa dokument i docs/governance/** är kompletterande, inte överstyrande`)

## Status model

The following statuses are the only allowed conclusion/file-classification states in this layer:

- `ACTIVE`
- `SUPERSEDED`
- `REJECTED`
- `DEPRECATED`
- `UNRESOLVED`
- `DORMANT`
- `NON_AUTHORIZING`

Additional rule:

- `UNKNOWN` is allowed for `Confidence`
- `UNKNOWN` is **not** allowed as a `Status`
- if the correct status is unclear, use `UNRESOLVED`

Layer-local status meanings:

| Status            | Meaning in this layer                                                                   |
| ----------------- | --------------------------------------------------------------------------------------- |
| `ACTIVE`          | Directly supported, currently usable conclusion or surface within its cited role        |
| `SUPERSEDED`      | Explicitly replaced by a later cited artifact or conclusion                             |
| `REJECTED`        | Explicitly falsified, invalidated, or no longer valid by cited support                  |
| `DEPRECATED`      | Retained but no longer primary; not automatically historical or invalid                 |
| `UNRESOLVED`      | Evidence is incomplete, conflicting, or ambiguous                                       |
| `DORMANT`         | Retained historical or paused surface; not current by default                           |
| `NON_AUTHORIZING` | Informative or evidentiary only; may not authorize decisions or behavior interpretation |

## Conclusion definition

A conclusion is a bounded, source-backed statement with identifiable decision relevance and a canonical artifact reference.

If a statement cannot be expressed that narrowly, it should not become an active register entry in this layer.

## Register-entry requirements

Every conclusion entry in `docs/knowledge/CANONICAL_KNOWLEDGE_REGISTER.md` must contain:

- `Status`
- `Conclusion statement`
- `Canonical artifact reference`
- `Observed evidence`
- `Inferred interpretation`
- `Unverified assumptions`
- `Decision impact`
- `Supersedes`
- `Superseded by`
- `Confidence`
- `Authority note`

Use `NONE` explicitly where a field has no content.
Do not leave silent blanks in claim-bearing fields.

## Confidence rules

Allowed values:

- `HIGH`
- `MEDIUM`
- `LOW`
- `UNKNOWN`

Layer-local guardrails:

- `HIGH` may be used only when the conclusion is directly supported by canonical artifact evidence
- inferred or ambiguous conclusions may not be `HIGH`
- if the evidence is only partial, use `MEDIUM`, `LOW`, or `UNKNOWN`
- if a conclusion would otherwise need `LOW` or `UNKNOWN` while also claiming `ACTIVE`, re-check whether `UNRESOLVED` or `NON_AUTHORIZING` is the more honest status

## Supersession discipline

For this layer, chronology alone does not establish supersession.
A conclusion or surface may be marked `SUPERSEDED` only when later cited support explicitly replaces the earlier one or makes its replacement relationship clear enough to cite directly.
Otherwise use `UNRESOLVED`.

## Coverage rule

Uncovered domains must be declared explicitly rather than implied complete.
This first slice covers only top-level governance and documentation-routing surfaces.
Domain-specific research, packet, and edge classification remains out of scope unless directly added in a later bounded slice.

Canonical support:

- `docs/README.md` (`Kärnregel`, `Snabb placeringsguide`)
- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` (`Short decision checklist`)

## Stub rule for lineage and edge maps

`docs/knowledge/RESEARCH_LINEAGE_MAP.md` and `docs/knowledge/EDGE_MAP.md` may contain active entries only when those entries are directly supported by already-classified artifacts.
If such support is not yet present in the current slice, the file must remain an explicit stub and state that no active entries are recorded.
