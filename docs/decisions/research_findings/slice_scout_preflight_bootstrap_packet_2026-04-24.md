# Slice scout + preflight skill bootstrap packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / pre-code / non-runtime customization bootstrap`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `LOW` — low runtime risk and low/medium governance-process risk; non-runtime agent/skill customization only, with no `src/**`, runtime, config authority, registry semantics, findings-bank truth, or live/paper surfaces changed.
- **Required Path:** `Small non-trivial RESEARCH customization path; reduced validation only.`
- **Lane:** `Research-evidence` — the cheapest admissible first step is to add one read-only scout agent plus one slice workflow skill spec above the already implemented findings lookup/packet-starter tooling.
- **Objective:** bootstrap the first reusable multi-agent slice workflow surface by adding a read-only scout agent and a matching repo-local skill spec that enforce findings-first slice framing without introducing write automation or new authority.
- **Candidate:** `slice scout + slice preflight packet starter bootstrap`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Skill Usage

- **Applied workflow skill:** `agent-customization`
  - reason: this slice creates workspace customization files under `.github/agents/` and `.github/skills/`.
- **No repo-local implementation skill reused as process coverage**
  - reason: the work is customization/governance support, not runtime Python implementation.

### Research-evidence lane

- **Baseline / frozen references:**
  - `.github/agents/Codex53.agent.md`
  - `.github/agents/Opus46.agent.md`
  - `scripts/preflight/findings_preflight_lookup.py`
  - `scripts/preflight/findings_packet_starter.py`
  - `.github/skills/python_engineering.json`
- **Candidate / comparison surface:**
  - one new read-only custom agent under `.github/agents/`
  - one new repo-local skill spec under `.github/skills/`
- **Vad ska förbättras:**
  - reduce duplicate slice framing work
  - make findings-bank reuse the default first move for new slices
  - separate read-only scouting from later implementation and review steps
- **Vad får inte brytas / drifta:**
  - no runtime/default/config-authority behavior change
  - no automatic packet or docs file writing
  - no mutation of findings-bank truth surfaces
  - no governance/promotion/readiness authority claims in agent or skill wording
- **Reproducerbar evidens som måste finnas:**
  - the scout agent must be explicitly read-only in both tool surface and body instructions
  - the skill spec must encode advisory-only, findings-first rules without widening into runtime authority

### Proposed bootstrap surface

- add one custom agent whose job is slice reconnaissance only:
  - find prior findings
  - surface blockers, positive anchors, `do_not_repeat`, and `next_admissible_step`
  - recommend the smallest admissible next slice
- add one repo-local skill spec that captures the recurring workflow around findings preflight and packet-start framing
- reuse the existing `scripts/preflight/` helpers instead of inventing new runtime or write automation

### Registration surface

- this repository's existing skill registry pattern is the JSON file set under `.github/skills/*.json`
- no separate `dev manifest` file was found during local repo inspection for this slice
- therefore the new `.github/skills/<id>.json` file is treated as the additive repo-local registry entry for this bootstrap step
- broader discoverability or external manifest-completeness claims remain `föreslagen` until separately verified

### Scope

- **Scope IN:**
  - `docs/decisions/research_findings/slice_scout_preflight_bootstrap_packet_2026-04-24.md`
  - `.github/agents/slice-scout.agent.md`
  - `.github/skills/slice_preflight_packet_starter.json`
- **Scope OUT:**
  - `.claude/**`
  - `.codex/**`
  - `.github/copilot-instructions.md`
  - `CLAUDE.md`
  - `src/**`
  - `tests/**`
  - `scripts/**`
  - `config/**`
  - `registry/**`
  - `artifacts/**`
  - any runtime/backtest/paper/live/config-authority/family-rule surface
  - any packet auto-write or docs auto-edit automation
- **Expected changed files:**
  - one packet doc
  - one scout agent file
  - one skill spec JSON file
- **Max files touched:** `3`

### Gates required

- editor validation for the changed `.md` and `.json` files (`Problems` clean)
- JSON parse validation for `.github/skills/slice_preflight_packet_starter.json`
- manual readback of the new `.agent.md` instructions to confirm read-only scope and no authority drift

### Stop Conditions

- any need to add edit/write tools to the scout agent
- any wording that turns the skill or agent into governance/runtime authority
- any need to touch `.claude/**`, `.codex/**`, or higher-order instruction files in the same bootstrap slice
- any drift from findings-first advisory framing into automatic packet generation

## Bottom line

This packet authorizes one small non-runtime bootstrap step: add a read-only slice scout agent and one matching repo-local skill spec for findings-first slice framing, with no write automation and no authority drift.
