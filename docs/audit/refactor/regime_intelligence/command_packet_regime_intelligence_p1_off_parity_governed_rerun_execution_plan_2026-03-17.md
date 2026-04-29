## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: docs-only execution planning for future sign-off evidence; imprecise wording here could bless an invalid rerun path without any runtime code change
- **Required Path:** `Full`
- **Objective:** Define the exact future execution flow for `RI P1 OFF parity governed rerun` under frozen spec `ri_p1_off_parity_v1`, including planned inputs, baseline/candidate handling, metadata bundle, and required gates, without executing the rerun.
- **Candidate:** `ri p1 off parity governed rerun execution plan`
- **Base SHA:** `1c2f38ad`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md`
  - `docs/decisions/regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md`
- **Scope OUT:**
  - `src/**`
  - `src/core/config/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `tests/**`
  - `tools/**`
  - `scripts/**`
  - `results/**` writes in this prep step
  - `docs/audit/refactor/regime_intelligence/evidence/**` writes in this prep step
  - `artifacts/**`
  - `logs/**`
  - `tmp/**`
  - `archive/**`
  - updates to existing rerun prep docs in this step
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md docs/decisions/regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md`

### Stop Conditions

- Any requirement to execute the rerun in this slice
- Any requirement to create, recover, or approve a baseline artifact in this slice
- Any requirement to write into `results/**`, `docs/audit/refactor/regime_intelligence/evidence/**`, `logs/**`, `tmp/**`, or `artifacts/**` during this prep step
- Any requirement to modify `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
- Any attempt to state the planned target window as already approved baseline fact instead of a frozen execution target pending provenance verification
- Any attempt to redefine the canonical P1 OFF artifact away from `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- Any attempt to use ignored-only locations as the sole retained evidence chain in the future execution contract
- Any omission of exact future selectors/skills from the gate bundle

### Output required

- **Implementation Report**
- **PR evidence template**
- **Execution-plan packet** with exact future flow, planned target window, and sign-off gate bundle

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice is preparation only; it does **not** execute, approve, recover, or sign off the rerun
- Planned execution inputs may be frozen from repo-visible contract/examples, but execution must STOP unless baseline approval provenance for that exact window is verified first
- Canonical parity artifact remains `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- `results/evaluation/ri_p1_off_parity_v1_baseline.json` is treated here as a reserved canonical reference path, not as a currently verified tracked artifact
- Future execution must preserve canonical vs supplemental evidence separation and hash-link both
