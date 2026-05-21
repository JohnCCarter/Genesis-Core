# Canonical Knowledge Register

> This document is derivative and citation-bound. It routes to existing canonical artifacts and does not create new authority, readiness, or research conclusions.

## Scope boundary for this slice

This first pass records only top-level governance, workflow, and documentation-routing conclusions that are directly supported by existing cited artifacts.

The following remain outside the populated scope of this slice and therefore are not classified here as active truth:

- domain-specific research conclusions
- packet-by-packet authority under `docs/decisions/**`
- note-by-note authority under `docs/analysis/**`
- lineage chains beyond top-level governance surfaces
- edge relationships beyond top-level authority boundaries

See `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md` for the fail-closed rules used here.

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

## CONCLUSION-ID: AUTH-008

Status:
`DORMANT`

Conclusion statement:
`GENESIS_WORKING_CONTRACT.md` is a retained historical branch-context anchor for `feature/editor-worker-orchestrator` and is not branch-current SSOT by default.

Canonical artifact reference:

- `GENESIS_WORKING_CONTRACT.md`
- headings: retained historical note, `Non-purpose`, `Authority order`

Observed evidence:

- The file states: `Retained historical working-contract / drift-reference anchor`.
- The file states: `This file is not SSOT`.
- The file states it is `not current execution guidance` for later branches by default.

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
May be used as historical context for the captured branch only. Must not be used as branch-current authority on other branches unless explicitly reopened.

## CONCLUSION-ID: AUTH-009

Status:
`DORMANT`

Conclusion statement:
`docs/governance/active_lane_index.md` is a historical branch-context pointer for `feature/editor-worker-orchestrator`, not a branch-current lane selector on other branches.

Canonical artifact reference:

- `docs/governance/active_lane_index.md`
- headings: `Status`, `Later-status note`, `What this file does not do`

Observed evidence:

- The file labels itself `historical branch-context pointer / complementary / no new authority`.
- The file states: `If the current branch is not feature/editor-worker-orchestrator, the branch, mode, and lane anchors below must not be read as branch-current execution guidance or lane-selection authority.`

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
May be used as a historical pointer for the captured branch context. Must not be used as current lane-selection authority on unrelated branches.

## CONCLUSION-ID: AUTH-010

Status:
`DORMANT`

Conclusion statement:
`docs/governance/worker_governance_envelope.md` is a retained historical or paused reference for the earlier editor-worker model and is not the current default governance workflow unless explicitly reopened.

Canonical artifact reference:

- `docs/governance/worker_governance_envelope.md`
- headings: status note, `Auktoritativa källor förblir`, `Retained worker model`

Observed evidence:

- The file states it is a `retained historical/paused reference`.
- The file states: `It is not the current default governance workflow`.
- The file states: `Auktoritativa källor förblir` and then points to higher-order sources.

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
May be used for traceability about the paused editor-worker model. Must not be used to activate or authorize that workflow by implication.
