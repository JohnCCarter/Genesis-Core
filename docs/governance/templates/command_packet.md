# Command Packet (v1.1)

Kopiera mallen nedan för varje ny uppgift.

## COMMAND PACKET

- **Mode:** `(STRICT/RESEARCH/SANDBOX)` — source: `docs/governance_mode.md`
- **Risk:** `(LOW/MED/HIGH)` — why:
- **Required Path:** `(Quick/Lite/Full)`
- **Objective:**
- **Candidate:** (om relevant)
- **Base SHA:**

### Scope

- **Scope IN:**
- **Scope OUT:**
- **Expected changed files:**
- **Max files touched:**

### Gates required

- `pre-commit run --all-files`
- `pytest -q`
- Selectors (om relevant):
  - determinism replay
  - feature cache invariance
  - pipeline hash guard
  - freeze guard checks

### Stop Conditions

- Scope drift
- Behavior change utan explicit undantag
- Hash/determinism regression
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
