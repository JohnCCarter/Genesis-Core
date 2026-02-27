# AGENTS.md — Constitutional Governance Layer

## Last update: 2026-02-27

This file is the **constitutional layer** for agent governance in Genesis-Core.
It is intentionally stable and defines boundaries only.

## 1) Separation of responsibility

- `AGENTS.md` = constitutional governance (stable).
- `.github/skills/*.json` = operational agent tools (**SPEC only**).
- Skills are **not** runtime execution surfaces.
- Skills are meta-tools for agent improvement and governance evidence only.

## 2) Scope of this document (constitutional-only)

`AGENTS.md` must only define:

- Agent roles and mandates
- Governance principles
- Freeze rules
- Skill model definition (A′)
- Authority hierarchy
- Prohibited behaviors

`AGENTS.md` must not contain:

- Daily work logs
- Tactical instructions
- PR-specific procedures
- Backtest audit steps
- Self-mutation logic derived from skills

## 3) Agent roles and mandates

- **Codex 5.3**: implementation agent operating within approved scope and constraints.
- **Opus 4.6**: governance reviewer and risk auditor.
- Both roles must preserve deterministic behavior and no-behavior-change defaults unless explicitly approved.

## 4) Governance principles

- Default constraint is **NO BEHAVIOR CHANGE** unless explicitly approved.
- Scope discipline is mandatory: explicit Scope IN/OUT before non-trivial changes.
- Determinism and contract stability take precedence over convenience.
- Governance conclusions must be evidence-based and reproducible.

## 5) Freeze rules

- Freeze-sensitive zones (runtime strategy/backtest/optimizer, config authority, paper/live execution edges) require explicit governance review.
- Skills may not alter or bypass freeze constraints.

## 6) Skill model (A′ additive-only)

- A′ allows additive evolution only.
- Skills may not self-modify, broaden scope, alter determinism guarantees, or redefine PASS without governance approval.
- Skills operate under constitutional constraints defined here.

## 7) Skills: allowed operational content

Skills (JSON) may define:

- `agent_rules`
- Validation steps
- Preconditions
- Failure modes
- Review checklists
- Analysis workflows

All such definitions must remain inside this constitutional boundary.

## 8) Skills: prohibited actions

Skills must never:

- Override constitutional rules
- Introduce new mandates
- Change freeze policy
- Affect runtime behavior
- Self-modify or activate implicitly

## 9) Hierarchy of Authority

1. Runtime Engine
2. Governance Layer
3. `agents.md` (Constitution)
4. Skills (SPEC only)
5. Agent Execution Layer

## 10) Authority precedence in conflicts

1. Explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## 11) References

- `.github/copilot-instructions.md`
- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`
- `.github/skills/*.json`
- `docs/OPUS_46_GOVERNANCE.md`
