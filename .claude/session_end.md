# Session End Protocol

Export session state before closing. Next session recovers from these files — not from chat memory.

State files live at `~/.claude/state/genesis-core/` — NOT in this repo.

## Step 1 — Update CURRENT_STATE.md

Write to: `~/.claude/state/genesis-core/CURRENT_STATE.md`

- Update "What's in progress" bullets
- Update "What's blocked"
- Update "Next admissible step"
- Update "Last updated" date

## Step 2 — Update ACTIVE_TASK.md

Write to: `~/.claude/state/genesis-core/ACTIVE_TASK.md`

- Update Status field
- Check off gates that passed
- Update Artifact path if packet was created

## Step 3 — Update GOVERNANCE_STATUS.md

Write to: `~/.claude/state/genesis-core/GOVERNANCE_STATUS.md`

- Update gate checkboxes
- Record Opus review verdict + date if a review happened

## Step 3a — If the active work was a bounded slice handoff

Record explicitly before handoff:

- return `status`
- `blocked_by` or equivalent blocker state
- `next_admissible_step` only as advisory routing
- whether explicit new instruction or a refreshed task packet is required before follow-on work

Never imply that work auto-continues merely because it produced usable output.

## Step 4 — Write SESSION_HANDOFF.md

Write to: `~/.claude/state/genesis-core/SESSION_HANDOFF.md`
Fill the template:

```
# Session Handoff — <date>
Mode: <MODE> (source: <reason>)

## Completed this session
- <bullet list>

## State left open
- <mid-flight files or none>

## Next session: load these files first
1. ~/.claude/state/genesis-core/CURRENT_STATE.md
2. ~/.claude/state/genesis-core/ACTIVE_TASK.md (if active)
3. .claude/QUICK_REF.md
4. <command packet path if relevant>

## Do NOT re-read
- AGENTS.md, OPUS_46_GOVERNANCE.md, governance_mode.md, copilot-instructions.md
```

If the session involved a bounded slice handoff, also include:

- the slice or task identifier
- artifact or packet paths returned
- explicit return classification if already adjudicated
- whether the next step is `stop`, `park`, `new task`, or `integration review`

## Step 5 — Commit artifacts (optional)

If substantive artifacts were created (evidence packets, analysis files), commit them.
Do NOT commit state files — they are not tracked by git.

```
git add artifacts/
git commit -m "chore(governance): session artifacts <date>"
```
