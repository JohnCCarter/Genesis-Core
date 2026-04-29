# Slice evidence handoff skill bootstrap packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / pre-code / non-runtime customization bootstrap`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `LOW` — low runtime risk and low/medium governance-process risk; non-runtime workflow customization only, with no `src/**`, runtime, config authority, findings-bank truth, or live/paper surfaces changed.
- **Required Path:** `Small non-trivial RESEARCH customization path; reduced validation only.`
- **Lane:** `Research-evidence` — the cheapest admissible next step after the scout bootstrap is one repo-local skill spec that provides a repeatable evidence handoff checklist for chat/PR/audit form without creating new authority or write automation.
- **Objective:** add one repo-local skill spec that guides the recurring slice evidence handoff workflow: scope summary, file-level changes, exact gates, selectors/artifacts, residual risks, and READY_FOR_REVIEW evidence completeness already required by existing SSOT surfaces.
- **Candidate:** `slice evidence handoff workflow bootstrap`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Skill Usage

- **Applied workflow skill:** `agent-customization`
  - reason: this slice adds a workspace customization file under `.github/skills/`.
- **No repo-local implementation skill reused as process coverage**
  - reason: the work is customization/governance support, not runtime implementation.

### Research-evidence lane

- **Baseline / frozen references:**
  - `.github/agents/Codex53.agent.md`
  - `.github/agents/Opus46.agent.md`
  - `.github/pull_request_template.md`
  - `docs/governance/templates/command_packet.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T9A_IMPLEMENTATION_REPORT_2026-03-04.md`
- **Candidate / comparison surface:**
  - one new repo-local skill spec under `.github/skills/`
- **Vad ska förbättras:**
  - reduce drift in implementation reports and PR evidence summaries
  - make exact gates/selectors/artifacts easier to carry into Opus post-audit
  - keep READY_FOR_REVIEW evidence completeness visible and repeatable
- **Vad får inte brytas / drifta:**
  - no runtime/default/config-authority behavior change
  - no new governance authority or approval semantics
  - no auto-generated docs, PR text, or packet files
  - no weakening of existing SSOT requirements in Codex/Opus agent docs
- **Reproducerbar evidens som måste finnas:**
  - the skill spec must stay advisory-only and must cite existing SSOT/report surfaces rather than replacing them
  - the skill spec must require exact commands/gates/outcomes instead of generic claims
  - skill invocation must not be presented as proof of compliance by itself

### Proposed bootstrap surface

- add one repo-local skill spec whose job is to provide a repeatable evidence handoff checklist after a slice is implemented and validated
- the skill may guide collection of:
  - scope IN/OUT
  - file-level change summary
  - exact commands actually run + observed pass/fail
  - selectors/artifacts/paths
  - residual risks + follow-ups
  - READY_FOR_REVIEW evidence completeness
- the skill must not:
  - approve work
  - replace Opus review
  - auto-write PR or report files
  - hide failed or skipped gates
  - define, relax, or substitute for READY_FOR_REVIEW requirements

This bootstrap slice introduces a repo-local, non-authoritative skill spec/checklist for
capturing evidence already required by existing SSOT and reporting surfaces after a slice
has been implemented and validated. It does not create new authority, does not replace
governance mode resolution, required gates, reviewer obligations, or READY_FOR_REVIEW
evidence completeness, and must not auto-write PRs, reports, or packets.

Skill invocation is not itself proof of compliance; it only structures handoff evidence
that must already exist.

This skill helps assemble evidence already required by existing governance and review
surfaces; it cannot itself satisfy gates, confer READY_FOR_REVIEW, or grant approval.

### Registration surface

- this repository's existing skill registry pattern is the JSON file set under `.github/skills/*.json`
- no separate `dev manifest` file was found during local repo inspection for this slice
- therefore the new `.github/skills/<id>.json` file is treated as the additive repo-local registry entry for this bootstrap step
- broader discoverability or external manifest-completeness claims remain `föreslagen` until separately verified

### Scope

- **Scope IN:**
  - `docs/governance/slice_evidence_handoff_bootstrap_packet_2026-04-24.md`
  - `.github/skills/slice_evidence_handoff.json`
- **Scope OUT:**
  - `.github/agents/**`
  - `.claude/**`
  - `.codex/**`
  - `.github/copilot-instructions.md`
  - `.github/pull_request_template.md`
  - `CLAUDE.md`
  - `src/**`
  - `tests/**`
  - `scripts/**`
  - `config/**`
  - `registry/**`
  - `artifacts/**`
  - any runtime/backtest/paper/live/config-authority/family-rule surface
  - any report, PR, or packet auto-write automation
- **Expected changed files:**
  - one packet doc
  - one skill spec JSON file
- **Max files touched:** `2`

### Gates required

- editor validation for the changed `.md` and `.json` files (`Problems` clean)
- JSON parse validation for `.github/skills/slice_evidence_handoff.json`
- manual readback of the new skill wording to confirm advisory-only scope and no authority drift
- scoped git containment check for exactly the two in-scope files

### Stop Conditions

- any need to touch agent files or higher-order instruction files in the same slice
- any wording that turns the skill into approval authority, merge authority, or runtime authority
- any drift from evidence handoff guidance into auto-generation of report/PR/packet files
- any weakening of existing gate/evidence requirements from repo SSOT files

## Bottom line

This packet authorizes one small non-runtime bootstrap step: add a repo-local slice evidence handoff skill spec/checklist that guides evidence packaging for chat/PR/Opus handoff without creating authority or write automation.
