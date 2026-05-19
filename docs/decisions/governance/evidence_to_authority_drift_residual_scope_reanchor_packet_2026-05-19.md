# Evidence-to-authority drift residual-scope reanchor packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records one bounded residual-scope clarification only for baseline finding `#1`. It does **not** claim that evidence-to-authority drift is solved. It records that, after the recent branch-visible narrowing slices around adjacent governance/docs seams, the honest current residual for `#1` is no longer a known one-doc or three-doc truthfulness fix waiting to be picked up. The residual is now the broader family-level risk that bounded observational notes can still be retold too broadly later. Any future bounded `#1` slice would therefore first require a fresh selection audit of a specific still-misleading, frequently reused claim-bearing surface.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice clarifies residual scope in docs only and does not touch runtime, tests, config, or governance precedence
- **Required Path:** `Quick path / docs-only residual-scope clarification`
- **Lane:** `Research-evidence` — why: this slice narrows interpretation of current branch-visible governance/docs residuals without authorizing new adoption work or runtime changes
- **Skill usage:** `none required` — bounded docs-only truthfulness/reclassification slice
- **Objective:** record that the current branch-visible residual for `#1` is family-level evidence-to-authority drift rather than a still-banked small seam already identified in tracked docs
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`, `docs/decisions/governance/citation_framing_drift_later_branch_truthfulness_packet_2026-05-19.md`, `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md`, `docs/governance/templates/evidence_claim_header.md`, `docs/governance/runbooks/evidence_claim_adoption.md`

### Scope

- **Scope IN:** this packet; one later-branch residual-scope note under finding `#1` in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Scope OUT:** any claim that `#1` is closed; any repo-wide claim-header retrofit; any fresh selection audit across frequently cited evidence notes; any runtime/test/config/script change; any broader governance rewrite
- **Expected changed files:** `docs/decisions/governance/evidence_to_authority_drift_residual_scope_reanchor_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the new note narrows residual shape without claiming `#1` closure
- manual wording audit that the note does not reopen a broad adoption/governance workstream by implication

## Purpose

This packet answers one narrow question only:

- after the recent branch-visible truthfulness and boundary slices, what is the honest current-branch reading of what still remains under baseline finding `#1`?

## What changed in this slice

- one new docs-only packet records the current residual shape for `#1`
- the baseline now carries a dated later-branch note clarifying that the remaining `#1` problem is broader family-level retelling/adoption risk, not an unchanged banked small seam
- the historical 2026-05-18 baseline wording remains preserved rather than silently rewritten away

## What did not change

- no runtime, test, config, script, or queue behavior changed
- no governance precedence changed
- no claim is made that evidence-to-authority drift is solved
- no claim is made that the repo already completed the fresh sampled-note selection work a future `#1` slice would require

## Governing basis

### Observed

1. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still records `#1` as the rank-1 governance/docs risk and explicitly says mitigation happens per-citation, not per-doc.
2. `docs/governance/templates/evidence_claim_header.md` and `docs/governance/runbooks/evidence_claim_adoption.md` already exist as trigger-based guardrails intended to reduce evidence-to-authority drift for decision-influencing evidence.
3. `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md` already tightened the compact mandatory provenance envelope for decision-influencing evidence, especially `Input carrier`.
4. `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` records that, at its re-anchor base, the only genuinely open residual seam it found was the narrower three-doc citation-framing issue, and that this seam was later corrected without reopening the broader premortem lane.
5. `docs/decisions/governance/citation_framing_drift_later_branch_truthfulness_packet_2026-05-19.md` explicitly narrows only the exact `#3` seam and explicitly does **not** claim that the broader `#1` evidence-to-authority drift family is solved.
6. The repository also now carries separately bounded later-branch packets for adjacent governance/docs seams around stale active-lane pointers, paused editor-worker references, premortem closeout scope, and premortem anchor-role disambiguation, rather than leaving those all bundled inside a single vague `#1` complaint.

### Inferred

- the honest current residual for `#1` is no longer `one known small docs seam still waiting to be corrected`
- what remains is the broader family-level risk that bounded observational material can still be retold as broader authority later, even after several concrete small seams have already been consumed by tracked packets
- the next honest bounded `#1` implementation slice, if any, would first require fresh selection of a specific still-misleading, frequently reused claim-bearing note rather than reusing already-corrected seams
- a residual-scope clarification is therefore truer than either pretending `#1` is closed or repeatedly treating already-consumed sub-seams as if they were still the live problem

### Unverified

- whether a fresh future selection audit would identify one remaining still-misleading, frequently reused claim-bearing note worth a new bounded slice
- whether current trigger-based claim-header adoption is sufficient to reduce later retelling drift over time
- whether a future broader adoption or normalization effort should be proposed for frequently cited historical evidence notes

## Applied clarification

The baseline now carries a dated later-branch note stating that on `feature/risk-hardening-wave2`:

- `#1` remains open as a family-level governance/docs risk
- the recent branch-visible packets already consumed the easiest adjacent small seams that had concrete tracked surfaces
- the honest next-step shape for `#1` is fresh candidate-selection or broader adoption work, not an unchanged ready-made one-note fix

## Bottom line

`#1` is still real, but its honest current shape is narrower in one important sense: it is no longer best described as a still-banked small docs seam that simply has not been patched yet. On this branch, the remaining `#1` residual is the broader family-level retelling/adoption risk itself. That means the next truthful bounded slice would need fresh surface selection first; this packet does not perform that audit and does not claim closure.
