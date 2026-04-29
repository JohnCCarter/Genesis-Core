## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: docs-only prep for a future governed parity rerun; incorrect evidence design here would create governance drift later even without runtime changes now
- **Required Path:** `Full`
- **Objective:** Define an execution-ready governance slice for `RI P1 OFF parity governed rerun` that can later restore repo-verifiable sign-off evidence under frozen spec `ri_p1_off_parity_v1` without changing runtime behavior.
- **Candidate:** `ri p1 off parity governed rerun`
- **Base SHA:** `1c2f38ad`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md`
  - `docs/decisions/regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md`
- **Scope OUT:**
  - `src/**`
  - `src/core/config/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `tests/**`
  - `tools/**`
  - `scripts/**`
  - `results/**` generated outputs in this prep step
  - `artifacts/**`
  - `logs/**`
  - `tmp/**`
  - `archive/**`
  - updates to existing analysis docs in this prep step
  - changes to default `multi_timeframe.regime_intelligence.authority_mode`
  - changes to authority precedence/fallback semantics
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md docs/decisions/regime_intelligence_p1_off_parity_governed_rerun_2026-03-17.md`

### Stop Conditions

- Any requirement to modify `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
- Any requirement to execute the rerun in this prep step
- Any requirement to add or modify tests, tools, or scripts in this prep step
- Any attempt to redefine the canonical P1 OFF parity artifact away from `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- Any attempt to treat `docs/audit/.../evidence/...` as a replacement for the canonical artifact rather than supplemental governance evidence
- Any need to rely on `logs/**`, `tmp/**`, `artifacts/**`, or other ignored-only paths as the sole retained evidence chain
- Any guessed or unverified baseline provenance being written as if approved fact
- Any need to modify ignore rules, runtime defaults, or governance enforcement logic in order to complete this prep slice

### Output required

- **Implementation Report**
- **PR evidence template**
- **Execution-prep rerun definition** with explicit canonical/supplemental artifact roles

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice prepares execution only; it does **not** execute the rerun
- Frozen spec anchor remains `ri_p1_off_parity_v1`
- Canonical machine-readable parity artifact remains `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- Supplemental governance evidence for future execution may be retained under `docs/audit/refactor/regime_intelligence/evidence/...`, but must reference the canonical artifact by path and SHA256
- Future execution must define explicit baseline input, explicit candidate input, reviewable window/input provenance, and required run metadata before any sign-off claim is made
- If the future execution slice cannot preserve a replayable evidence chain outside ignored-only paths, it must stop and return for fresh governance review
