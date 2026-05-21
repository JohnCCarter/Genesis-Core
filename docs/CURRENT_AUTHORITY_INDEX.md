# Current Authority Index

> This document is derivative and citation-bound. It routes to existing canonical artifacts and does not create new authority, readiness, or research conclusions.

## Purpose

This index answers one bounded question for the current slice:

- which already-existing documentation surfaces are currently usable as authority-bearing governance references or active supplemental guidance within their cited role
- which surfaces are explicitly non-authorizing or retained historical references
- which domains remain outside the classified scope of this first pass

## Scope boundary

This first slice classifies only top-level governance, workflow, and documentation-routing surfaces.

This file does **not**:

- summarize the entire repository
- classify domain-specific research conclusions
- classify every packet under `docs/decisions/**`
- classify every note under `docs/analysis/**`
- authorize runtime, promotion, readiness, or config interpretation

Where support is absent or ambiguous, this index treats the surface as `UNRESOLVED`.

Canonical support for this scope boundary:

- `docs/governance_mode.md` (`Fail-closed policy`)
- `docs/README.md` (`Kärnregel`, `Viktig försiktighetsregel`)
- `docs/governance/README.md` (`SSOT och precedence`, `Operativa dokument i docs/governance/** är kompletterande, inte överstyrande`)
- `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md`

## Reading rule

Read these surfaces in their cited role only.
Do not infer authority from filename prominence, recency, folder location, or reuse frequency alone.

Canonical support:

- `docs/README.md` (`Historiska dokument...`, `Viktig försiktighetsregel`)
- `docs/governance/README.md` (`Historiska packet-, signoff- och closeout-dokument... läsas med respekt för innehållets faktiska roll, inte enbart efter mappnamnet`)

## Active governance and workflow references

| Surface                                                             | Status   | What it may be used for                                                             | What it may not be used for                                           | Canonical support                                                                                                                                                                                             |
| ------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.github/copilot-instructions.md`                                   | `ACTIVE` | Practical workflow/governance precedence and operating-contract guidance            | Replacing explicit user direction for the current task                | `.github/copilot-instructions.md` (`Source of truth`)                                                                                                                                                         |
| `docs/governance_mode.md`                                           | `ACTIVE` | Governance mode resolution and mode-specific operating expectations                 | General workflow precedence outside mode resolution                   | `docs/governance_mode.md` (`This document is the single source of truth (SSOT) for Governance Mode resolution and policy enforcement`)                                                                        |
| `docs/OPUS_46_GOVERNANCE.md`                                        | `ACTIVE` | Expanded governance working manual subordinate to `.github/copilot-instructions.md` | Overriding higher-order precedence or mode resolution                 | `docs/OPUS_46_GOVERNANCE.md` (`Kanonisk referens är .github/copilot-instructions.md`)                                                                                                                         |
| `AGENTS.md`                                                         | `ACTIVE` | Constitutional governance boundaries and stable role/precedence framing             | Overriding `.github/copilot-instructions.md` or explicit user request | `AGENTS.md` (`Constitutional Governance Layer`, `Authority precedence in conflicts`)                                                                                                                          |
| `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` | `ACTIVE` | Workflow-lane framing (`concept`, `research-evidence`, `runtime-integration`)       | Creating a new mode system or runtime/default/promotion authority     | `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` (`This document is practical workflow guidance`, `What this model is not`)                                                                |
| `docs/repository-layout-policy.md`                                  | `ACTIVE` | Supplemental file-placement and layout guidance                                     | Overriding higher-order governance or mode documents                  | `.github/copilot-instructions.md` (`For repository layout and file placement guidance, also see docs/repository-layout-policy.md`) and `docs/repository-layout-policy.md` (`This document is subordinate...`) |

## Non-authorizing routing and taxonomy references

| Surface                     | Status            | What it may be used for                                                 | What it may not be used for                                                                     | Canonical support                                                                                                                           |
| --------------------------- | ----------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/README.md`            | `NON_AUTHORIZING` | Documentation taxonomy and reading-order guidance                       | Standing SSOT or independent authority source                                                   | `docs/README.md` (`Den här README:n är den praktiska kartan... Den är inte en egen SSOT`)                                                   |
| `docs/governance/README.md` | `NON_AUTHORIZING` | Governance-zone index and placement guidance                            | Independent SSOT or override surface                                                            | `docs/governance/README.md` (`Den här README:n är ett index, inte en egen SSOT`)                                                            |
| `docs/analysis/README.md`   | `NON_AUTHORIZING` | Analysis-zone routing, placement guidance, and retained-context framing | Establishing conclusions, branch-current work order, readiness, promotion, or runtime authority | `docs/analysis/README.md` (`Routing status (2026-05-21, feature/knowledge-authority-layer)`, `Later-branch truthfulness note`)              |
| `docs/decisions/README.md`  | `NON_AUTHORIZING` | Decision-zone routing, placement guidance, and taxonomy framing         | Approval, readiness, promotion, runtime authority, or governance SSOT                           | `docs/decisions/README.md` (`Routing status (2026-05-21, feature/knowledge-authority-layer)`, `Den här mappen är ... inte governance-SSOT`) |

## Retained historical or paused references

| Surface      | Status    | What it may be used for                                                                                                                | What it may not be used for                                                    | Canonical support                                                                                                                                      |
| ------------ | --------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `handoff.md` | `DORMANT` | Historical branch-context handoff traceability for the captured `feature/risk-hardening-wave3` note and retained older takeover blocks | Branch-current live anchor or current execution guidance on unrelated branches | `handoff.md` (`Later-status note (2026-05-21, feature/knowledge-authority-layer)`, `Äldre block längre ned i filen ska fortsatt bevaras som historik`) |

## Explicitly unresolved in this slice

The following surfaces remain `UNRESOLVED` at the classification level in this first pass:

- domain-specific packets under `docs/decisions/**`
- domain-specific notes under `docs/analysis/**`
- domain-specific contract surfaces outside the governance/top-level routing set above
- research lineage chains beyond the top-level governance surfaces
- edge relationships beyond explicit top-level authority boundaries

The explicit `NON_AUTHORIZING` status of `docs/analysis/README.md` and `docs/decisions/README.md`
does not assign status to the documents they route to.

This file does not infer a status for those domains from absence, recency, folder, or convenience.

## No entries recorded in this slice

No surfaces are recorded as `SUPERSEDED`, `DEPRECATED`, or `REJECTED` in this first pass.
If later work identifies such status, that classification must be citation-bound and added in a separate bounded slice.
