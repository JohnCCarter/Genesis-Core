# Session Start Protocol

Minimum load sequence for any Genesis-Core session. Do not read full governance docs unless running a gated commit.

## Step 1 — Load state (always)
1. Read `~/.claude/state/genesis-core/SESSION_HANDOFF.md` (if exists from prior session)
2. Read `~/.claude/state/genesis-core/CURRENT_STATE.md`
3. Read `docs/governance/QUICK_REF.md`

## Step 2 — Load task (if active work)
4. Read `~/.claude/state/genesis-core/ACTIVE_TASK.md`
5. Read `~/.claude/state/genesis-core/GOVERNANCE_STATUS.md`

## Step 3 — Resolve mode
6. Check current git branch (or env var `GENESIS_GOV_MODE`)
7. Apply QUICK_REF mode resolution table
8. State banner: `Mode: <MODE> (source=<reason>)`

## Step 4 — Load task packet (only if continuing a specific slice)
9. Read the command packet for the active slice (path in ACTIVE_TASK.md → Artifact)
10. Do NOT read: AGENTS.md, OPUS_46_GOVERNANCE.md, governance_mode.md, copilot-instructions.md
    — these are stable; QUICK_REF.md covers what you need for routine sessions

## When to load full governance docs
- About to run a gated commit → read OPUS_46_GOVERNANCE.md (3-gate protocol)
- Ambiguity about mode resolution → read docs/governance_mode.md
- Constitutional question → read AGENTS.md
- Operational contract dispute → read .github/copilot-instructions.md
