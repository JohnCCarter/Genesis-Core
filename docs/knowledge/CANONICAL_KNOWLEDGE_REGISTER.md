# Canonical Knowledge Register

> This document is derivative and citation-bound. It routes to existing canonical artifacts and does not create new authority, readiness, or research conclusions.

## Scope boundary for this slice

This first pass records only top-level governance, workflow, and documentation-routing conclusions that are directly supported by existing cited artifacts, plus one derivative documentation-surface provenance/orientation conclusion and one derivative repo-zone topology/lifecycle/authority conclusion.

The following remain outside the populated scope of this slice and therefore are not classified here as active truth:

- domain-specific research conclusions
- packet-by-packet authority under `docs/decisions/**`
- note-by-note authority under `docs/analysis/**`
- deep lineage chains beyond the directly cited documentation surfaces in `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- edge relationships beyond top-level authority boundaries

See `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md` for the fail-closed rules used here.
If a cited source conflicts with a register entry, the cited source controls.
Register inclusion, omission, ordering, or conclusion-ID placement do not by themselves imply lineage, dependency, approval, or current applicability.

## CONCLUSION-ID: AUTH-001

Status:
`ACTIVE`

Conclusion statement:
`docs/governance_mode.md` is the single source of truth for governance mode resolution and mode-specific operating expectations.

Canonical artifact reference:

- `docs/governance_mode.md`
- heading: `Governance Mode (SSOT)`

Observed evidence:

- The file states: `This document is the single source of truth (SSOT) for Governance Mode resolution and policy enforcement.`
- The file defines deterministic mode resolution and fail-closed handling.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used to resolve branch/override/freeze mode questions. Must not be expanded into a general workflow-precedence source beyond mode resolution unless another cited artifact says so.

## CONCLUSION-ID: AUTH-002

Status:
`ACTIVE`

Conclusion statement:
`.github/copilot-instructions.md` is the practical source-of-truth surface for workflow/governance precedence and operating-contract behavior, subordinate only to the explicit user request for the current task.

Canonical artifact reference:

- `.github/copilot-instructions.md`
- heading: `Source of truth`

Observed evidence:

- The file states that it is the practical SSOT for workflow/governance precedence and operating contract behavior.
- The file lists precedence beginning with the explicit user request for the current task.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for workflow/governance precedence and operating-contract interpretation. Must not be used to override an explicit user request.

## CONCLUSION-ID: AUTH-003

Status:
`ACTIVE`

Conclusion statement:
`docs/OPUS_46_GOVERNANCE.md` is an expanded governance working manual that remains subordinate to `.github/copilot-instructions.md` and does not replace mode resolution from `docs/governance_mode.md`.

Canonical artifact reference:

- `docs/OPUS_46_GOVERNANCE.md`
- headings: `Overview`, `Source of truth vid konflikt`

Observed evidence:

- The file states: `Kanonisk referens är .github/copilot-instructions.md`.
- The file states that `docs/governance_mode.md` remains SSOT for mode resolution.
- The file presents an expanded working manual and gated-commit workflow.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used as an expanded operational manual where it does not conflict with higher-order sources. Must not be used to replace `.github/copilot-instructions.md` or `docs/governance_mode.md`.

## CONCLUSION-ID: AUTH-004

Status:
`ACTIVE`

Conclusion statement:
`AGENTS.md` is the constitutional governance layer and remains part of the active precedence stack, but below the higher-order sources named in `.github/copilot-instructions.md`.

Canonical artifact reference:

- `AGENTS.md`
- headings: `Constitutional Governance Layer`, `Hierarchy of Authority`, `Authority precedence in conflicts`

Observed evidence:

- The file describes itself as the constitutional governance layer.
- The file defines authority precedence in conflicts and places itself below `.github/copilot-instructions.md` and `docs/OPUS_46_GOVERNANCE.md`.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used to interpret constitutional boundaries and prohibited behavior. Must not be used as if it outranked `.github/copilot-instructions.md`.

## CONCLUSION-ID: AUTH-005

Status:
`ACTIVE`

Conclusion statement:
`docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` is the canonical practical definition of the three workflow lanes, but it is workflow guidance only and does not create a new mode or runtime authority.

Canonical artifact reference:

- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md`
- headings: `Status`, `What this model is not`, `Canonical usage rule`

Observed evidence:

- The file labels itself `docs-only / workflow guidance / no-runtime-authority`.
- The file says it does not change governance mode resolution, authority precedence, strict-only surfaces, or runtime/default/promotion authority.
- The file calls itself the canonical practical definition of the three-lane workflow model.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used to classify lane framing. Must not be used to authorize runtime, readiness, promotion, or a new mode system.

## CONCLUSION-ID: AUTH-006

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/README.md` is a practical documentation taxonomy map and not an independent SSOT or authority source.

Canonical artifact reference:

- `docs/README.md`
- headings: `Documentation taxonomy`, `Viktig försiktighetsregel`

Observed evidence:

- The file states: `Den här README:n är den praktiska kartan över dokumentytorna i Genesis-Core.`
- The file states: `Den är inte en egen SSOT och ändrar inte authority-precedence.`
- The file instructs readers to read in layer order rather than infer authority from document existence.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for documentation routing and taxonomy. Must not be used as a standalone authority source for runtime, readiness, or promotion decisions.

## CONCLUSION-ID: AUTH-007

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/governance/README.md` is a governance-zone index and complementary guide, not an independent SSOT.

Canonical artifact reference:

- `docs/governance/README.md`
- headings: `Governance docs index`, `SSOT och precedence`

Observed evidence:

- The file states: `Den här README:n är ett index, inte en egen SSOT.`
- The file states that `docs/governance/**` documents are complementary rather than overriding.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used to route readers to governance-zone materials and precedence notes. Must not be used as an independent authority source.

## CONCLUSION-ID: AUTH-011

Status:
`ACTIVE`

Conclusion statement:
`docs/repository-layout-policy.md` is an active but subordinate practical reference for repository layout and file-placement guidance.

Canonical artifact reference:

- `.github/copilot-instructions.md`
- heading: `Applicability and scope`
- `docs/repository-layout-policy.md`
- headings: `Status`, `Purpose`, `Relationship to higher-order documents`

Observed evidence:

- `.github/copilot-instructions.md` states: `For repository layout and file placement guidance, also see docs/repository-layout-policy.md. It is a subordinate practical reference and must not override higher-order governance or mode documents.`
- `docs/repository-layout-policy.md` states: `This document is a repository-structure policy, not a constitutional or governance source of truth.`
- `docs/repository-layout-policy.md` states: `This document is subordinate to the repository's higher-order governance sources.`

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for repository layout and file-placement guidance within its subordinate scope. Must not be used to override higher-order governance or mode documents.

## CONCLUSION-ID: AUTH-012

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/analysis/README.md` is a non-authorizing routing surface for `docs/analysis/` and retained historical context framing; it does not, by itself, establish conclusions, readiness, promotion status, runtime authority, or branch-current work order.

Canonical artifact reference:

- `docs/analysis/README.md`
- headings: `Routing status (2026-05-21, feature/knowledge-authority-layer)`, `Later-branch truthfulness note (2026-05-21, feature/risk-hardening-wave3)`, `Syfte för mappen`

Observed evidence:

- The file states: `denna README är en NON_AUTHORIZING routingyta för analysartefakter i docs/analysis/.`
- The file states it `inte i sig` establishes `slutsatser, readiness, promotion-status, runtime authority eller branch-current arbetsordning`.
- The file describes `docs/analysis/` as a surface for `synteser, diagnoser och findings` and not for governance-SSOT.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for routing and placement within `docs/analysis/`. Must not be used to assign status to individual notes or to establish conclusions, readiness, promotion status, runtime authority, or branch-current work order.

## CONCLUSION-ID: AUTH-013

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/decisions/README.md` is a non-authorizing routing surface for `docs/decisions/`; it guides placement and navigation for decision-record documents but does not, by itself, confer approval, readiness, promotion status, runtime authority, or governance SSOT status.

Canonical artifact reference:

- `docs/decisions/README.md`
- headings: `Routing status (2026-05-21, feature/knowledge-authority-layer)`, `Syfte`

Observed evidence:

- The file states: `denna README är en NON_AUTHORIZING routingyta för beslutsdokument i docs/decisions/.`
- The file states it does not `ge i sig approval, readiness, promotion-status, runtime authority eller SSOT-status`.
- The file states the folder is `inte governance-SSOT`.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for routing and placement within `docs/decisions/`. Must not be used to confer approval or to assign status to individual packets, signoffs, closeouts, or adjacent decision documents.

## CONCLUSION-ID: AUTH-014

Status:
`DORMANT`

Conclusion statement:
`handoff.md` is a retained branch-context handoff surface. Its wave3 live note is limited to `feature/risk-hardening-wave3`; on unrelated branches, including `feature/knowledge-authority-layer`, it is historical context and not current execution guidance.

Canonical artifact reference:

- `handoff.md`
- headings: `Later-status note (2026-05-21, feature/knowledge-authority-layer)`, `Uppdatering 2026-05-21 — wave3 #2 + #12 re-resolved`

Observed evidence:

- The file states: `wave3-noten nedan är retained branch-context history för feature/risk-hardening-wave3`.
- The file states: `På unrelated branches, inklusive feature/knowledge-authority-layer, är den inte current execution guidance eller live execution anchor`.
- The file preserves older takeover blocks as retained history rather than rewriting them as current branch instruction.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used for historical branch-context traceability only. Must not be used as branch-current work order or execution guidance on unrelated branches.

## CONCLUSION-ID: AUTH-015

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` is a derivative, citation-bound, non-exhaustive orientation map for documentation-surface provenance and lineage; it may aid navigation across directly cited documentation surfaces but does not create authority, classify the entire repository, or prove dependency/supersession from chronology, prominence, folder placement, or index inclusion alone.

Canonical artifact reference:

- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- headings: `Purpose`, `Scope boundary`, `Reading rule`, `Explicit unresolved boundary`

Observed evidence:

- The file states: `This document is a derivative, citation-bound orientation map.`
- The file states it `does not create authority, does not classify the entire repository, and leaves uncited or deep corpora unresolved unless directly classified by a cited source`.
- The file states it may be used for `navigation and provenance/origin context` and `may not be used as an independent SSOT, authority source, or proof that one document silently governs another`.
- The file explicitly leaves packet-by-packet `docs/decisions/**`, note-by-note `docs/analysis/**`, and deeper uncited corpora unresolved.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used as a derivative documentation provenance/orientation aid only. Must not be used as an independent authority source, exhaustive repository classification, or proof of lineage/dependency without direct cited support. If this entry conflicts with the cited artifact, the cited artifact controls.

## CONCLUSION-ID: AUTH-016

Status:
`NON_AUTHORIZING`

Conclusion statement:
`docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md` is a derivative, citation-bound, repo-zone orientation map for topology, lifecycle posture, authority posture, risk posture, and advisory next-step bias across directly supported Genesis-Core zones; it does not create authority, does not override cited sources, and leaves unsupported or mixed-signal areas `UNRESOLVED`.

Canonical artifact reference:

- `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
- headings: `Purpose`, `Scope boundary`, `Reading rule`, `Explicit unresolved boundary`

Observed evidence:

- The file states: `This document is a derivative, citation-bound orientation map.`
- The file states it `does not create authority, does not override cited sources, and any unsupported area remains UNRESOLVED`.
- The file states that `Next-step bias` is `an advisory working cue` and `not an approval state, permission grant, or governance override`.
- The file limits itself to repo-zone orientation and explicitly excludes file-by-file classification, runtime approval, promotion readiness, and governance precedence changes.

Inferred interpretation:

- `NONE`

Unverified assumptions:

- `NONE`

Decision impact:
`GOVERNANCE_ONLY`

Supersedes:

- `NONE`

Superseded by:

- `NONE`

Confidence:
`HIGH`

Authority note:
May be used as a derivative repo-zone topology/lifecycle/authority aid only. Must not be used as an independent authority source, approval surface, exhaustive file-by-file classifier, or permission grant to modify a zone. If this entry conflicts with the cited artifact, the cited artifact controls.
